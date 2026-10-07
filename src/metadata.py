import exifread
from PIL import Image
from PIL.ExifTags import TAGS

def extract_metadata(uploaded_file) -> dict:
    """
    Extracts available EXIF metadata from the uploaded image file.
    
    IMPORTANT: Missing metadata must NOT automatically mean an image is tampered.
    
    Args:
        uploaded_file: Streamlit UploadedFile object containing the image.
        
    Returns:
        dict: Parsed metadata fields and raw EXIF status.
    """
    # Reset file pointer
    uploaded_file.seek(0)
    
    # Using exifread for robust extraction without relying on Pillow's internal parsing which can miss things
    tags = exifread.process_file(uploaded_file, details=False)
    
    metadata_info = {
        'exif_available': False,
        'camera_make': 'Unknown',
        'camera_model': 'Unknown',
        'software': 'Unknown',
        'date_time': 'Unknown',
        'image_dimensions': 'Unknown'
    }
    
    if not tags:
        return metadata_info
        
    metadata_info['exif_available'] = True
    
    # safely fetch fields
    if 'Image Make' in tags:
        metadata_info['camera_make'] = str(tags['Image Make'])
    if 'Image Model' in tags:
        metadata_info['camera_model'] = str(tags['Image Model'])
    if 'Image Software' in tags:
        metadata_info['software'] = str(tags['Image Software'])
    if 'Image DateTime' in tags:
        metadata_info['date_time'] = str(tags['Image DateTime'])
    
    # fetch dimensions if present in EXIF
    width = tags.get('EXIF ExifImageWidth', tags.get('Image ImageWidth', None))
    length = tags.get('EXIF ExifImageLength', tags.get('Image ImageLength', None))
    
    if width and length:
        metadata_info['image_dimensions'] = f"{width} x {length}"
        
    return metadata_info
