"""
File handling utilities.
"""
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp'}


def find_image_files(directory: Path) -> List[Path]:
    """
    Recursively find all image files in a directory.
    
    Args:
        directory: Path to search
    
    Returns:
        List of image file paths
    """
    if not directory.exists():
        logger.warning(f"Directory does not exist: {directory}")
        return []
    
    if not directory.is_dir():
        logger.warning(f"Path is not a directory: {directory}")
        return []
    
    image_files = []
    for ext in IMAGE_EXTENSIONS:
        image_files.extend(directory.rglob(f'*{ext}'))
        image_files.extend(directory.rglob(f'*{ext.upper()}'))
    
    return sorted(set(image_files))


def ensure_directory(path: Path) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure exists
    """
    path.mkdir(parents=True, exist_ok=True)
