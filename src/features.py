import numpy as np
from PIL import Image

def extract_basic_features(img: Image.Image) -> dict:
    """
    Extracts basic numerical features and statistics from an image.
    
    Args:
        img: Original PIL Image.
        
    Returns:
        dict: Dictionary containing computed features.
    """
    # Convert image to numpy array for efficient math
    img_array = np.array(img.convert('RGB'))
    
    # Overall image statistics
    mean_brightness = np.mean(img_array)
    std_deviation = np.std(img_array)
    variance = np.var(img_array)
    min_pixel_val = np.min(img_array)
    max_pixel_val = np.max(img_array)
    
    # Calculate bright pixel ratio (pixels > 200 out of 255)
    bright_pixels = np.sum(img_array > 200)
    total_pixels = img_array.size
    bright_pixel_ratio = bright_pixels / total_pixels if total_pixels > 0 else 0
    
    # Image geometry features
    width, height = img.size
    aspect_ratio = width / height if height > 0 else 0
    
    features = {
        'mean_brightness': round(float(mean_brightness), 4),
        'standard_deviation': round(float(std_deviation), 4),
        'variance': round(float(variance), 4),
        'min_pixel_value': int(min_pixel_val),
        'max_pixel_value': int(max_pixel_val),
        'bright_pixel_ratio': round(float(bright_pixel_ratio), 4),
        'image_width': width,
        'image_height': height,
        'aspect_ratio': round(float(aspect_ratio), 4)
    }
    
    # Placeholder layout for future feature extraction modules
    # - edge features
    # - texture features
    # - entropy
    # - ELA-derived features
    
    return features
