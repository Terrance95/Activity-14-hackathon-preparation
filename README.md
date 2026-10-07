<<<<<<< HEAD
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
=======
# PORTFOLIO BUILDING – B25CS0311

## Activity 14: Hackathon Preparation

### Team Name: PixelGuard

---

## 1. Activity Objective

The objective of this activity is to prepare for a hackathon by forming a team, selecting a suitable hackathon problem, brainstorming possible solutions, and defining a clear problem statement and technology stack before beginning the development phase.

This preparation focuses on understanding the problem, planning the solution, and assigning responsibilities among team members.

---

## 2. Team Formation

### Team: PixelGuard

| Sl. No. | Team Member               | Roll Number | Primary Role                      |
| ------- | ------------------------- | ----------- | --------------------------------- |
| 1       | T S HARSHAVARDHAN NAYAKA  | R25EJ159    | Project Development & Integration |
| 2       | Vighnesh P K KANHIRAKANDI | R25EJ174    | Project Development & Testing     |
| 3       | Terrance Paul S           | R25EJ162    | Project Development & Research    |
| 4       | SHASHANK G NAIK           | 26017900366 | UI, Documentation & Presentation  |

### Team Approach

The team will work collaboratively during the hackathon. The responsibilities listed above represent the primary areas of contribution, while members may support one another across development, testing, research, interface work, documentation, and presentation whenever required.

---

## 3. Selected Hackathon

### Semester End Examination Hackathon – Abhinava

**Date:** 07 October 2026
**Duration:** 9:00 AM – 9:00 PM
**Venue:** SVB and SMVB Block

The team selected the Semester End Examination Hackathon – Abhinava as the hackathon for preparation.

The hackathon requires teams to develop a working prototype within the given time period and submit the project files through Git.

### Selected Problem

**Image Tampering Detection: Real vs Edited (Image Processing)**

The selected problem focuses on identifying whether a digital image has been manipulated using techniques such as copy-paste, image splicing, or retouching.

---

## 4. Problem Statement Selection

Before selecting the final problem, the team brainstormed three possible problem ideas.

| Idea                                          | Feasibility | Potential Impact | Decision     |
| --------------------------------------------- | ----------- | ---------------- | ------------ |
| Campus Lost & Found Board                     | High        | High             | Not Selected |
| Phishing URL Detection Using Machine Learning | Medium–High | High             | Not Selected |
| Image Tampering Detection – Real vs Edited    | High        | High             | **Selected** |

### Reason for Selection

The Image Tampering Detection problem provides a clear and manageable scope for a time-limited hackathon. It allows the team to work with image processing, Error Level Analysis, feature extraction, and machine-learning classification. The output can also be demonstrated visually through an ELA heatmap and a classification result.

---

## 5. Final Problem Statement

Digital images can be manipulated through techniques such as copy-paste, image splicing, and retouching, making it difficult to determine whether an image is authentic or edited. We propose to build an image tampering detection tool that accepts an image as input and analyses it using Error Level Analysis (ELA) to highlight regions with inconsistent compression. Features obtained from the image analysis will be used to train a simple machine-learning classifier to classify an image as real or potentially edited. The system will provide an ELA heatmap and a classification result so that users can visually inspect the image and understand the detected inconsistencies.

---

## 6. Proposed Technology Stack

### Programming Language

* Python

### Image Processing

* OpenCV
* Pillow

### Machine Learning

* scikit-learn

### Development Environment

* Google Colab

### Dataset

* CASIA v2
* Or a suitable small tampered-image dataset from Kaggle

---

## 7. Proposed System Flow

```text
Input Image
     ↓
Image Preprocessing
     ↓
Error Level Analysis (ELA)
     ↓
Feature Extraction
     ↓
Machine Learning Classifier
     ↓
Prediction
     ↓
ELA Heatmap + Classification Result
```

---

## 8. Proposed Features

The planned prototype will include the following features:

1. **Image Input**

   * Allow the user to provide an image for analysis.

2. **Image Preprocessing**

   * Prepare the image for further analysis.

3. **Error Level Analysis (ELA)**

   * Analyse compression inconsistencies within the image.
   * Generate an ELA representation/heatmap.

4. **Feature Extraction**

   * Extract useful features from the processed image.

5. **Machine Learning Classification**

   * Use a simple classifier to distinguish between real and potentially edited images.

6. **Result Display**

   * Display the ELA heatmap.
   * Display the classification result.

7. **Performance Evaluation**

   * Measure classifier performance using accuracy.
   * Generate a confusion matrix.

---

## 9. Expected Deliverables

At the end of the hackathon preparation and subsequent build phase, the planned solution is expected to include:

* A working image tampering detection prototype.
* ELA heatmap generation.
* Machine-learning based classification.
* Classification accuracy.
* Confusion matrix.
* Image upload/input functionality.
* Prediction/verdict display.
* Sample test results and screenshots.
* Source code.
* README documentation.
* Presentation slides.
* Live demonstration of the working prototype.

---

## 10. Team Responsibility Plan

| Team Member               | Primary Responsibility              |
| ------------------------- | ----------------------------------- |
| T S HARSHAVARDHAN NAYAKA  | Project development and integration |
| Vighnesh P K KANHIRAKANDI | Project development and testing     |
| Terrance Paul S           | Project development and research    |
| SHASHANK G NAIK           | UI, documentation and presentation  |

The team will follow a collaborative workflow, allowing members to assist in different areas whenever required during development and integration.

---

## 11. Preparation Plan

The team will approach the hackathon preparation and development in the following stages:

### Stage 1 – Understand the Problem

* Understand image tampering and common manipulation techniques.
* Study the purpose of Error Level Analysis.
* Identify the expected input and output.

### Stage 2 – Environment and Dataset Setup

* Set up the Python environment in Google Colab.
* Obtain and organise a suitable image dataset.
* Prepare the dataset for training and testing.

### Stage 3 – Core Development

* Implement image preprocessing.
* Implement ELA.
* Extract relevant features.
* Train a simple machine-learning classifier.

### Stage 4 – Integration

* Connect image input with the analysis pipeline.
* Generate the ELA heatmap.
* Display the classification result.
* Integrate the required interface/output.

### Stage 5 – Testing and Evaluation

* Test the system using sample real and tampered images.
* Calculate accuracy.
* Generate the confusion matrix.
* Check the reliability of the output.

### Stage 6 – Documentation and Presentation

* Prepare the README.
* Prepare the presentation slides.
* Organise sample outputs and screenshots.
* Prepare a short demonstration of the working prototype.

---

## 12. Preparation Conclusion

The team has formed a four-member team named **PixelGuard** and selected the **Image Tampering Detection: Real vs Edited** problem for the Semester End Examination Hackathon – Abhinava.

The preparation has defined the problem, identified the target users and use case, compared alternative ideas, selected an appropriate technology stack, planned the system flow, and assigned broad responsibilities among the team members.

The next phase will focus on implementing and testing the proposed solution during the hackathon.

---

## Activity 14 Evidence

This repository serves as the shared GitHub workspace for the team's Activity 14 hackathon preparation.

**Repository:**
https://github.com/harshavardhannayaka20072007-png/Activity-14-hackathon-preparation

**Activity:** Activity 14 – Hackathon Preparation

**Team:** PixelGuard

**Selected Problem:** Image Tampering Detection: Real vs Edited
>>>>>>> d5d1956e6de244922e31416e084d340155ec3e56
