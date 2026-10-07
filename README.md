# Digital Image Tampering Detection / Image Forensics

This project is a web-based forensic tool for detecting digital image tampering. It analyzes uploaded images using various techniques to identify potential manipulation.

## Implemented

The Phase 1 foundation includes:
- **Image Validation**: Proper format and corruption checking.
- **Error Level Analysis (ELA)**: Multi-quality ELA (90, 95, 98) generation.
- **Feature Extraction**: Basic statistical data from image pixels.
- **Metadata Analysis**: EXIF extraction.
- **Streamlit App**: Dark-themed responsive interface.

Phase 2A adds CASIA-compatible dataset discovery and inspection, forensic feature
extraction, duplicate-grouped train/validation/test splits, and training-only
feature scaling. It does not train a classifier or report model accuracy.

## Dataset Feature Pipeline

Place the CASIA v2.0 dataset under `dataset/` using either the familiar
`dataset/original/` and `dataset/tampered/` folders, or CASIA's `Au/` and `Tp/`
class folders (including when they are nested under a CASIA root folder). The
authentic label is `0` and the tampered label is `1`. Supported file extensions
include JPG/JPEG, PNG, BMP, TIFF, and WEBP. No dataset is included in this
repository.

Run the pipeline from the repository root:

```bash
python -m src.dataset_pipeline
```

Optional `--dataset-root`, `--features-dir`, `--evaluation-dir`, and
`--random-state` arguments allow using another dataset location and controlling
the reproducible split. Inspection details, the raw and scaled feature tables,
and extraction failures are written under `results/features/`; split
assignments and the fitted `StandardScaler` artifact are written under
`results/evaluation/`. The scaler is fitted using training rows only. Exact and
perceptually near-duplicate images are kept in the same split. Missing EXIF
metadata is not used as a tampering feature or evidence.

The inspection report counts supported image files, reports detected formats
and dimensions, lists corrupt images and duplicate filenames, and identifies
missing class directories and unsupported files. Failed feature extractions
remain in the feature table with an error status and are also written to a
separate failure table.

Run the focused pipeline tests with:

```bash
python -m unittest discover -s tests
```

Use a configured environment that has the packages in `requirements.txt`
installed before running the commands above.

## Setup Instructions

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   streamlit run app/app.py
   ```
