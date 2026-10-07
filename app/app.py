import streamlit as st
import pandas as pd
import sys
import os

# Add src to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.preprocessing import validate_and_load_image
from src.ela import perform_multi_quality_ela
from src.features import extract_basic_features
from src.metadata import extract_metadata

# --- STREAMLIT APP CONFIGURATION ---
st.set_page_config(
    page_title="Digital Image Tampering Detection",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme via markdown (if system theme doesn't enforce it)
st.markdown(
    """
    <style>
    /* Add some professional styling */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .reportview-container {
        background: #0E1117;
    }
    .warning-box {
        padding: 10px;
        background-color: #332b00;
        border-left: 5px solid #ffcc00;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Digital Image Tampering Detection / Image Forensics")
st.markdown("### 🔍 Upload an image to analyze forensic evidence (Phase 1 Prototype)")

# --- UPLOAD SECTION ---
uploaded_file = st.file_uploader("Upload an image (JPG, JPEG, PNG, WEBP, BMP)", type=['jpg', 'jpeg', 'png', 'webp', 'bmp'])

if uploaded_file is not None:
    st.markdown("---")
    
    # 1. Image Validation
    with st.spinner("Validating and loading image..."):
        validation_result = validate_and_load_image(uploaded_file)
        
    if not validation_result['valid']:
        st.error(f"Validation Failed: {validation_result['error']}")
    else:
        st.success("Image successfully validated.")
        img = validation_result['image']
        img_info = validation_result['info']
        
        # 2. Basic Image Information & Original Display
        st.subheader("1. Original Image & Basic Information")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(img, caption="Original Uploaded Image", use_column_width=True)
            
        with col2:
            st.write("**File Information:**")
            info_df = pd.DataFrame([img_info]).T
            info_df.columns = ["Value"]
            st.table(info_df)
            
        st.markdown("---")
        
        # 3. Analyze
        if st.button("Begin Full Analysis", type="primary"):
            
            with st.spinner("Performing Error Level Analysis..."):
                ela_images = perform_multi_quality_ela(img)
                
            with st.spinner("Extracting Statistical Features..."):
                features = extract_basic_features(img)
                
            with st.spinner("Parsing Metadata..."):
                metadata = extract_metadata(uploaded_file)
                
            # 4. Show ELA Q90/Q95/Q98
            st.subheader("2. Error Level Analysis (ELA)")
            st.markdown("""
            *Error Level Analysis highlights regions of the image that are at different compression levels. 
            Bright white regions indicate higher error levels (recent modifications), while darker regions indicate lower error levels (solid surfaces or older compressions).*
            """)
            
            ela_col1, ela_col2, ela_col3 = st.columns(3)
            with ela_col1:
                st.image(ela_images['ELA_90'], caption="ELA Quality 90", use_column_width=True)
            with ela_col2:
                st.image(ela_images['ELA_95'], caption="ELA Quality 95", use_column_width=True)
            with ela_col3:
                st.image(ela_images['ELA_98'], caption="ELA Quality 98", use_column_width=True)
                
            st.markdown("---")
                
            # 5. Show Basic Image Features
            st.subheader("3. Basic Image Statistics")
            st.write("Numerical statistics derived from pixel intensities.")
            features_df = pd.DataFrame([features]).T
            features_df.columns = ["Value"]
            st.dataframe(features_df, use_container_width=True)
            
            st.markdown("---")
            
            # 6. Show Metadata
            st.subheader("4. EXIF Metadata")
            st.markdown("""
            <div class="warning-box">
                <strong>IMPORTANT:</strong> Metadata must NEVER be treated as proof of tampering. Missing metadata does not automatically mean an image is fake, as many valid platforms (like social media) strip metadata for privacy.
            </div>
            """, unsafe_allow_html=True)
            
            if metadata['exif_available']:
                st.write("**Found Metadata:**")
                st.json(metadata)
            else:
                st.info("No EXIF metadata found in this image.")
                
            st.markdown("---")
            
            # 7. Phase 2 Placeholder
            st.subheader("5. Machine Learning Classification")
            st.info("🚧 **ML CLASSIFICATION COMING IN NEXT PHASE**")
            st.write("""
            Phase 2 will implement deep feature extraction, model inference (Random Forest / SVM), region localization, and final forensic report generation.
            We do not fabricate machine learning accuracy or verdicts in this foundation phase.
            """)
            
            with st.expander("Technical details about next phase"):
                st.write("- Extract CASIA v2.0 dataset features")
                st.write("- Perform Cross-Validation and Feature Fusion")
                st.write("- Output Explainable AI (XAI) overlays")
