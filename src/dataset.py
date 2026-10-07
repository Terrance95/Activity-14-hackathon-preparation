"""Dataset discovery, label assignment, and integrity inspection."""

from __future__ import annotations

import logging
import os
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image

logger = logging.getLogger(__name__)

SUPPORTED_IMAGE_EXTENSIONS = {
    ".bmp",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}

_DIRECTORY_LABELS = {
    "au": 0,
    "auth": 0,
    "authentic": 0,
    "genuine": 0,
    "original": 0,
    "real": 0,
    "tp": 1,
    "fake": 1,
    "forged": 1,
    "manipulated": 1,
    "tampered": 1,
}
LABEL_NAMES = {0: "authentic", 1: "tampered"}


@dataclass(frozen=True)
class ImageRecord:
    path: Path
    label: int
    relative_path: str


@dataclass
class DatasetInspection:
    root: str
    total_images: int
    original_images: int
    tampered_images: int
    image_formats: dict[str, int]
    formats_by_extension: dict[str, int]
    image_dimensions: dict[str, int]
    missing_class_directories: list[str]
    corrupt_images: list[dict[str, str]]
    duplicate_filenames: dict[str, list[str]]
    unsupported_files: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def _label_for_directory(name: str) -> int | None:
    return _DIRECTORY_LABELS.get(name.casefold())


def load_dataset(root: str | Path) -> list[ImageRecord]:
    """Load labeled image paths from `original`/`tampered` or CASIA `Au`/`Tp`."""
    dataset_root = Path(root).expanduser().resolve()
    if not dataset_root.is_dir():
        raise FileNotFoundError(f"Dataset directory does not exist: {dataset_root}")

    labeled_directories: list[tuple[Path, int]] = []
    root_label = _label_for_directory(dataset_root.name)
    if root_label is not None:
        labeled_directories.append((dataset_root, root_label))
    for current, directories, _ in os.walk(dataset_root):
        current_path = Path(current)
        for name in directories:
            label = _label_for_directory(name)
            if label is not None:
                labeled_directories.append((current_path / name, label))

    labeled_files: dict[Path, set[int]] = defaultdict(set)
    for directory, label in labeled_directories:
        for path in directory.rglob("*"):
            if path.is_file() and path.suffix.casefold() in SUPPORTED_IMAGE_EXTENSIONS:
                labeled_files[path.resolve()].add(label)

    conflicts = {
        path: sorted(labels)
        for path, labels in labeled_files.items()
        if len(labels) > 1
    }
    if conflicts:
        details = ", ".join(
            f"{path} (labels {labels})" for path, labels in sorted(conflicts.items())
        )
        raise ValueError(f"Images found under conflicting label directories: {details}")

    return [
        ImageRecord(
            path=path,
            label=next(iter(labels)),
            relative_path=path.relative_to(dataset_root).as_posix(),
        )
        for path, labels in sorted(labeled_files.items(), key=lambda item: str(item[0]))
    ]


def inspect_dataset(
    root: str | Path, records: list[ImageRecord] | None = None
) -> DatasetInspection:
    """Inspect all supported image files and report unreadable/unsupported content."""
    dataset_root = Path(root).expanduser().resolve()
    if records is None:
        records = load_dataset(dataset_root)
    class_directories: dict[int, set[Path]] = {0: set(), 1: set()}
    for current, directories, _ in os.walk(dataset_root):
        for name in directories:
            label = _label_for_directory(name)
            if label is not None:
                class_directories[label].add(Path(current) / name)
    root_label = _label_for_directory(dataset_root.name)
    if root_label is not None:
        class_directories[root_label].add(dataset_root)

    image_formats: Counter[str] = Counter()
    formats_by_extension: Counter[str] = Counter()
    dimensions: Counter[str] = Counter()
    corrupt_images: list[dict[str, str]] = []
    duplicate_paths: dict[str, list[str]] = defaultdict(list)
    supported_paths = {record.path for record in records}
    unsupported_files: list[str] = []

    for record in records:
        duplicate_paths[record.path.name.casefold()].append(record.relative_path)
        formats_by_extension[record.path.suffix.casefold().lstrip(".")] += 1
        try:
            with Image.open(record.path) as image:
                actual_format = image.format or "UNKNOWN"
                width, height = image.size
                image.load()
            image_formats[actual_format.upper()] += 1
            dimensions[f"{width}x{height}"] += 1
        except Exception as error:
            message = f"{type(error).__name__}: {error}"
            logger.warning("Unable to inspect image %s: %s", record.path, message)
            corrupt_images.append(
                {"path": record.relative_path, "error": message}
            )

    for class_directory in class_directories.values():
        for path in class_directory:
            for candidate in path.rglob("*"):
                if (
                    candidate.is_file()
                    and candidate.name != ".gitkeep"
                    and candidate.resolve() not in supported_paths
                    and candidate.suffix.casefold() not in SUPPORTED_IMAGE_EXTENSIONS
                ):
                    unsupported_files.append(
                        candidate.resolve().relative_to(dataset_root).as_posix()
                    )

    duplicate_filenames = {
        name: sorted(paths)
        for name, paths in sorted(duplicate_paths.items())
        if len(paths) > 1
    }
    return DatasetInspection(
        root=str(dataset_root),
        total_images=len(records),
        original_images=sum(record.label == 0 for record in records),
        tampered_images=sum(record.label == 1 for record in records),
        image_formats=dict(sorted(image_formats.items())),
        formats_by_extension=dict(sorted(formats_by_extension.items())),
        image_dimensions=dict(sorted(dimensions.items())),
        missing_class_directories=[
            LABEL_NAMES[label]
            for label in (0, 1)
            if not class_directories[label]
        ],
        corrupt_images=corrupt_images,
        duplicate_filenames=duplicate_filenames,
        unsupported_files=sorted(set(unsupported_files)),
    )
