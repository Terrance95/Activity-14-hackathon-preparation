"""Build forensic feature tables and leakage-safe dataset splits."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
from collections import defaultdict
from pathlib import Path

import cv2
import joblib
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler

from src.dataset import inspect_dataset, load_dataset
from src.features import extract_forensic_features

logger = logging.getLogger(__name__)
_SPLIT_NAMES = ("train", "validation", "test")
_SPLIT_RATIOS = (0.70, 0.15, 0.15)


class _UnionFind:
    def __init__(self, size: int) -> None:
        self.parents = list(range(size))

    def find(self, item: int) -> int:
        while self.parents[item] != item:
            self.parents[item] = self.parents[self.parents[item]]
            item = self.parents[item]
        return item

    def union(self, first: int, second: int) -> None:
        first_root, second_root = self.find(first), self.find(second)
        if first_root != second_root:
            self.parents[max(first_root, second_root)] = min(first_root, second_root)


class _PerceptualHashIndex:
    def __init__(self) -> None:
        self.root: tuple[int, int, dict] | None = None

    @staticmethod
    def _distance(first: int, second: int) -> int:
        return (first ^ second).bit_count()

    def add(self, value: int, index: int) -> None:
        if self.root is None:
            self.root = (value, index, {})
            return
        node = self.root
        while True:
            distance = self._distance(value, node[0])
            if distance == 0:
                node[2].setdefault(-1, []).append(index)
                return
            child = node[2].get(distance)
            if child is None:
                node[2][distance] = (value, index, {})
                return
            node = child

    def query(self, value: int, radius: int) -> list[int]:
        matches: list[int] = []
        if self.root is None:
            return matches
        pending = [self.root]
        while pending:
            node = pending.pop()
            distance = self._distance(value, node[0])
            if distance <= radius:
                matches.append(node[1])
                matches.extend(node[2].get(-1, []))
            lower, upper = distance - radius, distance + radius
            pending.extend(
                child
                for edge, child in node[2].items()
                if edge >= 0 and lower <= edge <= upper
            )
        return matches


def _image_hashes(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with Image.open(path) as image:
        gray = np.asarray(image.convert("L").resize((32, 32)), dtype=np.float32)
    transformed = cv2.dct(gray)
    low_frequency = transformed[:8, :8]
    median = float(np.median(low_frequency.reshape(-1)[1:]))
    bits = low_frequency > median
    perceptual_hash = 0
    for bit in bits.ravel():
        perceptual_hash = (perceptual_hash << 1) | int(bit)
    return digest, perceptual_hash


def _duplicate_group_ids(
    hashes: list[tuple[str, int]], hamming_threshold: int = 4
) -> list[str]:
    union_find = _UnionFind(len(hashes))
    index = _PerceptualHashIndex()
    for current, (_, perceptual_hash) in enumerate(hashes):
        for match in index.query(perceptual_hash, hamming_threshold):
            union_find.union(current, match)
        index.add(perceptual_hash, current)

    members: dict[int, list[str]] = defaultdict(list)
    for item, (content_hash, _) in enumerate(hashes):
        members[union_find.find(item)].append(content_hash)
    group_ids = {
        root: hashlib.sha256("|".join(sorted(content_hashes)).encode()).hexdigest()[:16]
        for root, content_hashes in members.items()
    }
    return [group_ids[union_find.find(item)] for item in range(len(hashes))]


def _split_indices(
    labels: np.ndarray, groups: np.ndarray, random_state: int
) -> dict[str, np.ndarray]:
    group_count = len(np.unique(groups))
    if group_count < 3:
        raise ValueError(
            "At least three distinct image/near-duplicate groups are required "
            "to create train, validation, and test splits."
        )

    all_indices = np.arange(len(labels))
    best_score = float("inf")
    best_splits: dict[str, np.ndarray] | None = None
    inner_validation_ratio = _SPLIT_RATIOS[1] / sum(_SPLIT_RATIOS[:2])
    present_labels = np.unique(labels)
    target_counts = {
        name: len(labels) * ratio
        for name, ratio in zip(_SPLIT_NAMES, _SPLIT_RATIOS)
    }
    target_class_counts = {
        (name, label): int(np.count_nonzero(labels == label)) * ratio
        for name, ratio in zip(_SPLIT_NAMES, _SPLIT_RATIOS)
        for label in present_labels
    }

    for attempt in range(256):
        outer = GroupShuffleSplit(
            n_splits=1, test_size=_SPLIT_RATIOS[2], random_state=random_state + attempt
        )
        train_validation, test = next(
            outer.split(all_indices, labels, groups)
        )
        inner = GroupShuffleSplit(
            n_splits=1,
            test_size=inner_validation_ratio,
            random_state=random_state + 10_000 + attempt,
        )
        train_local, validation_local = next(
            inner.split(
                train_validation,
                labels[train_validation],
                groups[train_validation],
            )
        )
        splits = {
            "train": train_validation[train_local],
            "validation": train_validation[validation_local],
            "test": test,
        }

        score = 0.0
        for name, indices in splits.items():
            actual_count = len(indices)
            score += ((actual_count - target_counts[name]) / max(target_counts[name], 1)) ** 2
            for label in present_labels:
                target = target_class_counts[(name, label)]
                actual = int(np.count_nonzero(labels[indices] == label))
                score += 2.0 * ((actual - target) / max(target, 1)) ** 2
                if actual == 0:
                    score += 10.0
        if score < best_score:
            best_score = score
            best_splits = splits

    if best_splits is None:
        raise RuntimeError("Unable to create non-empty grouped dataset splits.")
    return best_splits


def process_dataset(
    dataset_root: str | Path,
    features_dir: str | Path,
    evaluation_dir: str | Path,
    random_state: int = 42,
) -> dict[str, Path]:
    """Inspect a dataset, extract features, split by duplicate group, and scale."""
    records = load_dataset(dataset_root)
    features_path = Path(features_dir)
    evaluation_path = Path(evaluation_dir)
    features_path.mkdir(parents=True, exist_ok=True)
    evaluation_path.mkdir(parents=True, exist_ok=True)

    inspection = inspect_dataset(dataset_root, records=records)
    inspection_path = features_path / "dataset_inspection.json"
    inspection_path.write_text(
        json.dumps(inspection.to_dict(), indent=2), encoding="utf-8"
    )
    if not records:
        raise ValueError(
            f"No supported images found in {dataset_root}. "
            "Place authentic/original and tampered images in labeled directories."
        )

    rows: list[dict] = []
    valid_hashes: list[tuple[str, int]] = []
    valid_row_indices: list[int] = []
    for record in records:
        row: dict = {
            "image_path": record.relative_path,
            "label": record.label,
            "extraction_status": "failed",
            "extraction_error": "",
            "duplicate_group": "",
            "split": "not_assigned",
        }
        try:
            with Image.open(record.path) as image:
                image.load()
                features = extract_forensic_features(image.convert("RGB"))
            content_hash, perceptual_hash = _image_hashes(record.path)
            row.update(features)
            row["extraction_status"] = "ok"
            valid_hashes.append((content_hash, perceptual_hash))
            valid_row_indices.append(len(rows))
        except Exception as error:
            row["extraction_error"] = f"{type(error).__name__}: {error}"
            logger.exception("Feature extraction failed for %s", record.path)
        rows.append(row)

    group_ids = _duplicate_group_ids(valid_hashes)
    for group_id, row_index in zip(group_ids, valid_row_indices):
        rows[row_index]["duplicate_group"] = group_id

    feature_columns = sorted(
        {
            key
            for index in valid_row_indices
            for key, value in rows[index].items()
            if isinstance(value, (int, float, np.integer, np.floating))
            and key != "label"
        }
    )
    raw_table = pd.DataFrame(rows)
    raw_table.to_csv(features_path / "features.csv", index=False)
    failures = raw_table[raw_table["extraction_status"] != "ok"]
    failures.to_csv(features_path / "feature_failures.csv", index=False)

    valid_labels = np.asarray([rows[index]["label"] for index in valid_row_indices])
    splits = _split_indices(
        valid_labels,
        np.asarray(group_ids),
        random_state=random_state,
    )
    for split_name, indices in splits.items():
        for valid_index in indices:
            raw_table.at[valid_row_indices[int(valid_index)], "split"] = split_name
    raw_table.to_csv(features_path / "features.csv", index=False)

    valid_rows = raw_table.iloc[valid_row_indices]
    train_indices = splits["train"]
    scaler = StandardScaler()
    scaler.fit(valid_rows.iloc[train_indices][feature_columns])
    artifact_path = evaluation_path / "feature_scaler.joblib"
    joblib.dump({"scaler": scaler, "feature_columns": feature_columns}, artifact_path)

    scaled_rows = raw_table.copy()
    successful_positions = np.asarray(valid_row_indices)
    scaled_values = scaler.transform(
        raw_table.iloc[successful_positions][feature_columns]
    )
    scaled_rows.loc[:, feature_columns] = np.nan
    scaled_rows.loc[successful_positions, feature_columns] = scaled_values
    scaled_rows.to_csv(features_path / "scaled_features.csv", index=False)
    raw_table[["image_path", "label", "duplicate_group", "split"]].to_csv(
        evaluation_path / "splits.csv", index=False
    )

    logger.info(
        "Processed %d images: %d succeeded, %d failed",
        len(records),
        len(valid_row_indices),
        len(failures),
    )
    return {
        "inspection": inspection_path,
        "features": features_path / "features.csv",
        "scaled_features": features_path / "scaled_features.csv",
        "failures": features_path / "feature_failures.csv",
        "splits": evaluation_path / "splits.csv",
        "scaler": artifact_path,
    }


def _default_path(*parts: str) -> Path:
    return Path(__file__).resolve().parents[1].joinpath(*parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset-root", type=Path, default=_default_path("dataset")
    )
    parser.add_argument(
        "--features-dir", type=Path, default=_default_path("results", "features")
    )
    parser.add_argument(
        "--evaluation-dir",
        type=Path,
        default=_default_path("results", "evaluation"),
    )
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    outputs = process_dataset(
        args.dataset_root,
        args.features_dir,
        args.evaluation_dir,
        random_state=args.random_state,
    )
    for name, path in outputs.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
