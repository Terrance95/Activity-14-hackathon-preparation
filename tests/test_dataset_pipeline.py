import tempfile
import unittest
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from PIL import Image

from src.dataset import inspect_dataset, load_dataset
from src.dataset_pipeline import process_dataset
from src.features import extract_forensic_features


class DatasetPipelineTests(unittest.TestCase):
    def _image(self, seed: int) -> Image.Image:
        pixels = np.random.default_rng(seed).integers(
            0, 256, size=(24, 32, 3), dtype=np.uint8
        )
        return Image.fromarray(pixels, mode="RGB")

    def test_casia_layout_inspection_features_and_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            authentic = root / "CASIA2" / "Au"
            tampered = root / "CASIA2" / "Tp"
            authentic.mkdir(parents=True)
            tampered.mkdir(parents=True)

            self._image(1).save(authentic / "shared.jpg")
            self._image(2).save(authentic / "au-2.png")
            self._image(3).save(authentic / "au-3.bmp")
            self._image(4).save(tampered / "shared.jpg")
            Image.open(authentic / "shared.jpg").save(tampered / "copy.webp")
            self._image(5).save(tampered / "tp-3.jpg")
            (tampered / "broken.jpg").write_bytes(b"not an image")
            (authentic / "notes.txt").write_text("unsupported", encoding="utf-8")

            records = load_dataset(root)
            self.assertEqual(len(records), 7)
            self.assertEqual(
                sum(record.label == 0 for record in records), 3
            )
            self.assertEqual(
                sum(record.label == 1 for record in records), 4
            )

            report = inspect_dataset(root)
            self.assertEqual(report.total_images, 7)
            self.assertEqual(report.original_images, 3)
            self.assertEqual(report.tampered_images, 4)
            self.assertEqual(len(report.corrupt_images), 1)
            self.assertEqual(report.unsupported_files, ["CASIA2/Au/notes.txt"])
            self.assertIn("shared.jpg", report.duplicate_filenames)

            sample = Image.open(authentic / "au-2.png")
            features = extract_forensic_features(sample)
            self.assertIn("image_entropy", features)
            self.assertIn("edge_density", features)
            self.assertIn("texture_glcm_contrast", features)
            for quality in (90, 95, 98):
                self.assertIn(f"ela_q{quality}_mean", features)
            self.assertTrue(all(np.isfinite(value) for value in features.values()))

            outputs = process_dataset(
                root,
                root / "outputs" / "features",
                root / "outputs" / "evaluation",
                random_state=123,
            )
            table = pd.read_csv(outputs["features"])
            self.assertEqual(len(table), len(records))
            self.assertEqual(table["label"].value_counts().to_dict(), {1: 4, 0: 3})
            self.assertEqual((table["extraction_status"] == "failed").sum(), 1)
            self.assertEqual(
                set(table.loc[table["extraction_status"] == "ok", "split"]),
                {"train", "validation", "test"},
            )

            source_image = table.loc[
                table["image_path"].str.endswith("Au/shared.jpg")
            ].iloc[0]
            duplicate_image = table.loc[
                table["image_path"].str.endswith("Tp/copy.webp")
            ].iloc[0]
            self.assertEqual(
                source_image["duplicate_group"], duplicate_image["duplicate_group"]
            )
            self.assertEqual(source_image["split"], duplicate_image["split"])

            scaler_payload = joblib.load(outputs["scaler"])
            scaler = scaler_payload["scaler"]
            feature_columns = scaler_payload["feature_columns"]
            train_features = table.loc[table["split"] == "train", feature_columns]
            np.testing.assert_allclose(scaler.mean_, train_features.mean().to_numpy())
            self.assertTrue(outputs["scaled_features"].is_file())
            self.assertTrue(outputs["splits"].is_file())
            self.assertTrue(outputs["failures"].is_file())

            repeated_outputs = process_dataset(
                root,
                root / "repeat" / "features",
                root / "repeat" / "evaluation",
                random_state=123,
            )
            repeated_table = pd.read_csv(repeated_outputs["features"])
            pd.testing.assert_frame_equal(
                table[["image_path", "label", "duplicate_group", "split"]],
                repeated_table[
                    ["image_path", "label", "duplicate_group", "split"]
                ],
            )

    def test_missing_dataset_directory_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing = Path(temporary_directory) / "missing"
            with self.assertRaises(FileNotFoundError):
                load_dataset(missing)

    def test_failed_extraction_is_saved_before_unsplittable_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "original").mkdir()
            (root / "tampered").mkdir()
            (root / "original" / "broken.jpg").write_bytes(b"not an image")

            features_dir = root / "results" / "features"
            with self.assertRaisesRegex(ValueError, "three distinct"):
                process_dataset(
                    root,
                    features_dir,
                    root / "results" / "evaluation",
                )

            table = pd.read_csv(features_dir / "features.csv")
            failures = pd.read_csv(features_dir / "feature_failures.csv")
            self.assertEqual(len(table), 1)
            self.assertEqual(len(failures), 1)
            self.assertEqual(table.loc[0, "extraction_status"], "failed")


if __name__ == "__main__":
    unittest.main()
