# Digital Image Tampering Detection / Image Forensics

This project is a web-based forensic tool for detecting digital image tampering. It analyzes uploaded images using various techniques to identify potential manipulation.

## Phase 1 Implementation

Currently deployed Phase 1 features include:
- **Image Validation**: Proper format and corruption checking.
- **Error Level Analysis (ELA)**: Multi-quality ELA (90, 95, 98) generation.
- **Feature Extraction**: Basic statistical data from image pixels.
- **Metadata Analysis**: EXIF extraction.
- **Streamlit App**: Dark-themed responsive interface.

*Note: Machine learning classification and explainability features are planned for Phase 2.*

## Setup Instructions

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   streamlit run app/app.py
   ```
