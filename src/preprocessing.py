import os
from PIL import Image, UnidentifiedImageError
import numpy as np

SUPPORTED_FORMATS = {
    'JPEG': 'JPEG',
    'JPG': 'JPEG',
    'PNG': 'PNG',
    'WEBP': 'WEBP',
    'BMP': 'BMP'
}

def validate_and_load_image(uploaded_file):
    """
    Validates the uploaded file, checks if it's a valid image, converts to RGB,
    and handles corrupted or invalid files safely.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        dict: Containing 'valid' (bool), 'image' (PIL.Image or None), 'error' (str or None),
              and 'info' (dict with basic image information)
    """
    result = {
        'valid': False,
        'image': None,
        'error': None,
        'info': {}
    }
    
    if uploaded_file is None:
        result['error'] = "No file uploaded."
        return result
        
    try:
        # Load image via Pillow
        img = Image.open(uploaded_file)
        
        # Force image load to catch corrupted files
        img.verify()
        
        # We must reopen after verify() because verify() closes the file/stream in some Pillow versions
        uploaded_file.seek(0)
        img = Image.open(uploaded_file)
        
        format_name = img.format.upper() if img.format else "UNKNOWN"
        
        # Check against supported formats
        if format_name not in SUPPORTED_FORMATS.values() and format_name not in SUPPORTED_FORMATS.keys():
             result['error'] = f"Unsupported image format: {format_name}. Supported formats: JPG, PNG, WEBP, BMP."
             return result
             
        # Convert to RGB unconditionally for standard processing
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Basic Image Information
        result['info'] = {
            'filename': uploaded_file.name,
            'format': format_name,
            'width': img.width,
            'height': img.height,
            'channels': len(img.getbands()),
            'file_size_bytes': uploaded_file.size,
            'color_mode': img.mode
        }
        
        result['valid'] = True
        result['image'] = img
        return result
        
    except UnidentifiedImageError:
        result['error'] = "File is not a valid image or is corrupted."
        return result
    except Exception as e:
        result['error'] = f"An unexpected error occurred during image validation: {str(e)}"
        return result
