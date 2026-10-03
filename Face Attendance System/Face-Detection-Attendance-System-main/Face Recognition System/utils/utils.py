"""
Utility Functions Module
Common utility functions used throughout the application
"""

import cv2
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from config import LOG_FILE, LOG_LEVEL
from utils.constants import (
    DATE_FORMAT, TIME_FORMAT, DATETIME_FORMAT, ERROR_CAMERA_NOT_FOUND
)

# ================== LOGGING SETUP ==================
def setup_logging():
    """
    Setup logging configuration for the application.
    """
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ================== VALIDATION FUNCTIONS ==================
def validate_name(name):
    """
    Validate person's name.
    
    Args:
        name (str): Name to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not name or len(name.strip()) < 2:
        return False, "Name must be at least 2 characters long."
    if len(name) > 50:
        return False, "Name must be less than 50 characters."
    if not name.replace(" ", "").isalpha():
        return False, "Name should only contain alphabetic characters and spaces."
    return True, ""

def validate_student_id(student_id):
    """
    Validate student ID format.
    
    Args:
        student_id (str): Student ID to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not student_id or len(student_id.strip()) < 3:
        return False, "Student ID must be at least 3 characters long."
    if len(student_id) > 20:
        return False, "Student ID must be less than 20 characters."
    if not student_id.replace("-", "").isalnum():
        return False, "Student ID can only contain alphanumeric characters and hyphens."
    return True, ""

def validate_email(email):
    """
    Validate email format.
    
    Args:
        email (str): Email to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format."
    return True, ""

def validate_password(password):
    """
    Validate password strength.
    
    Args:
        password (str): Password to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit."
    return True, ""

# ================== SECURITY FUNCTIONS ==================
def hash_password(password):
    """
    Hash a password using SHA-256.
    
    Args:
        password (str): Password to hash
        
    Returns:
        str: Hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed_password):
    """
    Verify a password against its hash.
    
    Args:
        password (str): Password to verify
        hashed_password (str): Hashed password to compare against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return hash_password(password) == hashed_password

# ================== DATE & TIME FUNCTIONS ==================
def get_current_date():
    """Get current date in standard format."""
    return datetime.now().strftime(DATE_FORMAT)

def get_current_time():
    """Get current time in standard format."""
    return datetime.now().strftime(TIME_FORMAT)

def get_current_datetime():
    """Get current date and time in standard format."""
    return datetime.now().strftime(DATETIME_FORMAT)

def parse_date(date_str):
    """
    Parse date string to datetime object.
    
    Args:
        date_str (str): Date string in format YYYY-MM-DD
        
    Returns:
        datetime: Parsed datetime object
    """
    try:
        return datetime.strptime(date_str, DATE_FORMAT)
    except ValueError as e:
        logger.error(f"Error parsing date: {e}")
        return None

def format_date(date_obj):
    """
    Format datetime object to date string.
    
    Args:
        date_obj (datetime): Datetime object
        
    Returns:
        str: Formatted date string
    """
    return date_obj.strftime(DATE_FORMAT) if date_obj else ""

# ================== FILE OPERATIONS ==================
def ensure_directory_exists(directory_path):
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        directory_path (str or Path): Directory path
        
    Returns:
        bool: True if directory exists or was created successfully
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory_path}: {e}")
        return False

def get_image_files(directory_path):
    """
    Get all image files from a directory.
    
    Args:
        directory_path (str or Path): Directory to search
        
    Returns:
        list: List of image file paths
    """
    from utils.constants import SUPPORTED_FORMATS
    
    try:
        image_files = []
        for ext in SUPPORTED_FORMATS:
            image_files.extend(Path(directory_path).glob(f"*{ext}"))
            image_files.extend(Path(directory_path).glob(f"*{ext.upper()}"))
        return sorted(image_files)
    except Exception as e:
        logger.error(f"Error reading image files from {directory_path}: {e}")
        return []

def file_exists(file_path):
    """
    Check if a file exists.
    
    Args:
        file_path (str or Path): File path to check
        
    Returns:
        bool: True if file exists, False otherwise
    """
    return Path(file_path).exists()

def delete_file(file_path):
    """
    Delete a file.
    
    Args:
        file_path (str or Path): File to delete
        
    Returns:
        bool: True if deleted successfully, False otherwise
    """
    try:
        Path(file_path).unlink()
        return True
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        return False

# ================== CAMERA FUNCTIONS ==================
def check_camera_available(camera_index=0):
    """
    Check if camera is available.
    
    Args:
        camera_index (int): Camera index (default: 0)
        
    Returns:
        bool: True if camera is available, False otherwise
    """
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        logger.warning(ERROR_CAMERA_NOT_FOUND)
        return False
    cap.release()
    return True

def get_available_cameras():
    """
    Get list of available camera indices.
    
    Returns:
        list: List of available camera indices
    """
    available_cameras = []
    for i in range(5):  # Check first 5 indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()
    return available_cameras

# ================== IMAGE PROCESSING ==================
def resize_image(image, scale_factor):
    """
    Resize an image by scale factor.
    
    Args:
        image: OpenCV image
        scale_factor (float): Scale factor (0-1)
        
    Returns:
        Image: Resized image
    """
    height, width = image.shape[:2]
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    return cv2.resize(image, (new_width, new_height))

def load_image(image_path):
    """
    Load an image from file.
    
    Args:
        image_path (str or Path): Path to image
        
    Returns:
        Image: OpenCV image or None if failed
    """
    try:
        image = cv2.imread(str(image_path))
        if image is None:
            logger.error(f"Failed to load image: {image_path}")
            return None
        return image
    except Exception as e:
        logger.error(f"Error loading image {image_path}: {e}")
        return None

def save_image(image, output_path):
    """
    Save an image to file.
    
    Args:
        image: OpenCV image
        output_path (str or Path): Output file path
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        from config import IMAGE_QUALITY
        cv2.imwrite(str(output_path), image, [cv2.IMWRITE_JPEG_QUALITY, IMAGE_QUALITY])
        return True
    except Exception as e:
        logger.error(f"Error saving image to {output_path}: {e}")
        return False

def convert_bgr_to_rgb(image):
    """
    Convert BGR image to RGB.
    
    Args:
        image: OpenCV image in BGR format
        
    Returns:
        Image: Image in RGB format
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def convert_rgb_to_bgr(image):
    """
    Convert RGB image to BGR.
    
    Args:
        image: Image in RGB format
        
    Returns:
        Image: OpenCV image in BGR format
    """
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

# ================== STRING FORMATTING ==================
def format_confidence(confidence):
    """
    Format confidence score as percentage.
    
    Args:
        confidence (float): Confidence score (0-1)
        
    Returns:
        str: Formatted confidence percentage
    """
    return f"{confidence * 100:.2f}%"

def truncate_text(text, max_length):
    """
    Truncate text to maximum length.
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        
    Returns:
        str: Truncated text
    """
    if len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text

# ================== ERROR HANDLING ==================
def handle_exception(exception, error_message="An error occurred"):
    """
    Handle exceptions and log them.
    
    Args:
        exception (Exception): Exception object
        error_message (str): Custom error message
    """
    logger.error(f"{error_message}: {str(exception)}")

# ================== STATISTICS FUNCTIONS ==================
def calculate_attendance_percentage(total_days, present_days):
    """
    Calculate attendance percentage.
    
    Args:
        total_days (int): Total working days
        present_days (int): Days marked present
        
    Returns:
        float: Attendance percentage
    """
    if total_days == 0:
        return 0.0
    return (present_days / total_days) * 100

def round_percentage(percentage):
    """
    Round percentage to 2 decimal places.
    
    Args:
        percentage (float): Percentage value
        
    Returns:
        float: Rounded percentage
    """
    return round(percentage, 2)
