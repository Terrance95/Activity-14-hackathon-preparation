import os
import io
from PIL import Image, ImageChops, ImageEnhance
import numpy as np

def generate_ela(img: Image.Image, quality: int, scale: float = 15.0) -> Image.Image:
    """
    Generates an Error Level Analysis (ELA) image.
    
    Args:
        img: Original PIL Image (in RGB mode).
        quality: JPEG compression quality (e.g., 90, 95, 98).
        scale: Multiplier to enhance the visualization of the difference.
        
    Returns:
        PIL Image representing the ELA visualization.
    """
    # Create a temporary in-memory buffer to save the recompressed image
    buffer = io.BytesIO()
    
    # Needs to be purely RGB for JPEG save
    temp_img = img.convert('RGB')
    
    # Save/recompress it at the chosen JPEG quality
    temp_img.save(buffer, 'JPEG', quality=quality)
    buffer.seek(0)
    
    # Open the recompressed version
    recompressed_img = Image.open(buffer)
    
    # Compare original with recompressed version
    # ImageChops.difference computes the absolute value of pixel-by-pixel difference
    diff = ImageChops.difference(temp_img, recompressed_img)
    
    # Calculate the pixel-level difference and extract max intensity for scaling
    # We find the extents to scale the differences if we want dynamic scaling
    extrema = diff.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    
    if max_diff == 0:
        max_diff = 1 # avoid division by zero if images are identical
    
    # Scale difference for visualization
    # Optional scale factor: scale dynamically based on max difference or fixed multiplier
    # Defaulting to an enhancer multiplier for robust ELA brightness
    enhancer = ImageEnhance.Brightness(diff)
    ela_image = enhancer.enhance(scale)
    
    return ela_image

def perform_multi_quality_ela(img: Image.Image):
    """
    Convenience function to generate ELA at multiple qualities.
    
    Args:
        img: Original PIL Image.
        
    Returns:
        dict: A dictionary containing ELA images at qualities 90, 95, and 98.
    """
    return {
        'ELA_90': generate_ela(img, quality=90, scale=15.0),
        'ELA_95': generate_ela(img, quality=95, scale=20.0),
        'ELA_98': generate_ela(img, quality=98, scale=25.0),
    }
