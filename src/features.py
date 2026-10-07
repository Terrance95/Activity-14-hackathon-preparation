import cv2
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
    
    return features


def _entropy(gray: np.ndarray) -> float:
    histogram = np.bincount(gray.ravel(), minlength=256).astype(np.float64)
    probabilities = histogram[histogram > 0] / gray.size
    return float(-np.sum(probabilities * np.log2(probabilities)))


def _texture_features(gray: np.ndarray) -> dict[str, float]:
    quantized = gray // 16
    cooccurrence = np.zeros((16, 16), dtype=np.float64)

    for first, second in (
        (quantized[:, :-1], quantized[:, 1:]),
        (quantized[:-1, :], quantized[1:, :]),
    ):
        if first.size:
            cooccurrence += np.bincount(
                (first.ravel() * 16 + second.ravel()).astype(np.int64),
                minlength=16 * 16,
            ).reshape(16, 16)

    cooccurrence += cooccurrence.T
    total = cooccurrence.sum()
    if total:
        cooccurrence /= total

    levels = np.arange(16, dtype=np.float64)
    differences = levels[:, None] - levels[None, :]
    return {
        "texture_glcm_contrast": float(np.sum(cooccurrence * differences**2)),
        "texture_glcm_homogeneity": float(
            np.sum(cooccurrence / (1.0 + np.abs(differences)))
        ),
        "texture_glcm_energy": float(np.sum(cooccurrence**2)),
    }


def extract_forensic_features(img: Image.Image) -> dict[str, float | int]:
    """Extract numeric image, ELA, edge, texture, and entropy features."""
    from src.ela import perform_multi_quality_ela

    features: dict[str, float | int] = extract_basic_features(img)
    gray = np.asarray(img.convert("L"), dtype=np.uint8)

    features["image_entropy"] = _entropy(gray)

    edges = cv2.Canny(gray, threshold1=100, threshold2=200)
    gradient_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gradient_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    gradient_magnitude = cv2.magnitude(gradient_x, gradient_y)
    laplacian = cv2.Laplacian(gray, cv2.CV_32F)
    features.update(
        {
            "edge_density": float(np.mean(edges > 0)),
            "edge_gradient_mean": float(np.mean(gradient_magnitude)),
            "edge_gradient_std": float(np.std(gradient_magnitude)),
            "texture_laplacian_variance": float(np.var(laplacian)),
            **_texture_features(gray),
        }
    )

    for quality, ela_image in zip(
        (90, 95, 98), perform_multi_quality_ela(img).values()
    ):
        ela = np.asarray(ela_image.convert("L"), dtype=np.uint8)
        prefix = f"ela_q{quality}"
        features.update(
            {
                f"{prefix}_mean": float(np.mean(ela)),
                f"{prefix}_std": float(np.std(ela)),
                f"{prefix}_variance": float(np.var(ela)),
                f"{prefix}_min": int(np.min(ela)),
                f"{prefix}_max": int(np.max(ela)),
                f"{prefix}_median": float(np.median(ela)),
                f"{prefix}_bright_pixel_ratio": float(np.mean(ela > 200)),
            }
        )

    return features
