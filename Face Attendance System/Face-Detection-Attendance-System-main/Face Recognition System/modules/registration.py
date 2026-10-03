"""
Face Registration Module
Handles user registration and face image capture
"""

import cv2
import logging
from pathlib import Path
from config import (
    CAMERA_FPS,
    CAMERA_HEIGHT,
    CAMERA_INDEX,
    CAMERA_WIDTH,
    DATASET_DIR,
    FACE_MIN_NEIGHBORS,
    FACE_SCALE_FACTOR,
    IMAGES_PER_PERSON,
    MIN_FACE_SIZE,
)
from utils.database import db_manager
from utils.utils import ensure_directory_exists, validate_name, validate_student_id, save_image
from utils.constants import IMAGE_EXTENSION, ERROR_CAMERA_NOT_FOUND, ERROR_NO_FACE_DETECTED

logger = logging.getLogger(__name__)

class FaceRegistration:
    """
    Handles face registration and image capture for new users.
    """
    
    def __init__(self):
        """Initialize face registration."""
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.capture_count = 0
        self.max_captures = IMAGES_PER_PERSON
    
    def register_user(self, name, student_id, email=None, phone=None):
        """
        Register a new user and capture face images.
        
        Args:
            name (str): User's name
            student_id (str): Unique student ID
            email (str): User's email
            phone (str): User's phone
            
        Returns:
            dict: Registration result with success status and message
        """
        # Validate inputs
        is_valid, error_msg = validate_name(name)
        if not is_valid:
            return {'success': False, 'message': error_msg}
        
        is_valid, error_msg = validate_student_id(student_id)
        if not is_valid:
            return {'success': False, 'message': error_msg}
        
        # Check if student already exists
        if db_manager.user_exists(student_id):
            return {'success': False, 'message': f'Student ID {student_id} already registered.'}
        
        # Create user dataset directory
        user_dir = DATASET_DIR / student_id
        if not ensure_directory_exists(user_dir):
            return {'success': False, 'message': 'Failed to create user directory.'}
        
        # Capture face images
        capture_result = self._capture_faces(user_dir, name, student_id)
        
        if not capture_result['success']:
            return capture_result
        
        # Add user to database
        user_id = db_manager.add_user(name, student_id, email, phone)
        
        if user_id:
            logger.info(f"User registered successfully: {name} ({student_id})")
            return {
                'success': True,
                'message': f'User {name} registered successfully with {capture_result["capture_count"]} face images!',
                'user_id': user_id,
                'image_count': capture_result['capture_count']
            }
        else:
            return {'success': False, 'message': 'Failed to save user to database.'}
    
    def _capture_faces(self, user_dir, name, student_id):
        """
        Capture multiple face images for a user.
        
        Args:
            user_dir (Path): Directory to save face images
            name (str): User name
            student_id (str): Student ID
            
        Returns:
            dict: Capture result with success status
        """
        cap = cv2.VideoCapture(CAMERA_INDEX)
        
        if not cap.isOpened():
            logger.error(ERROR_CAMERA_NOT_FOUND)
            return {'success': False, 'message': ERROR_CAMERA_NOT_FOUND}
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
        
        self.capture_count = 0
        captured_faces = 0
        
        try:
            while self.capture_count < self.max_captures:
                ret, frame = cap.read()
                
                if not ret:
                    logger.error("Failed to read frame from camera")
                    break
                
                # Flip frame for mirror effect
                frame = cv2.flip(frame, 1)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=FACE_SCALE_FACTOR,
                    minNeighbors=FACE_MIN_NEIGHBORS,
                    minSize=(MIN_FACE_SIZE, MIN_FACE_SIZE),
                )
                
                # Draw rectangles around faces
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Add text
                cv2.putText(
                    frame,
                    f"Capturing: {self.capture_count}/{self.max_captures}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )
                cv2.putText(
                    frame,
                    f"Face(s) detected: {len(faces)}",
                    (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )
                cv2.putText(
                    frame,
                    "Press SPACE to capture, ESC to exit",
                    (10, CAMERA_HEIGHT - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    1
                )
                
                cv2.imshow(f'Register {name} - Press SPACE to capture', frame)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == 27:  # ESC
                    logger.info("Registration cancelled by user")
                    break
                elif key == 32 and len(faces) > 0:  # SPACE
                    # Capture face
                    image_path = user_dir / f"{student_id}_{self.capture_count + 1:03d}{IMAGE_EXTENSION}"
                    x, y, w, h = max(faces, key=lambda face: face[2] * face[3])
                    face_roi = frame[y:y+h, x:x+w]
                    
                    if save_image(face_roi, image_path):
                        self.capture_count += 1
                        captured_faces += 1
                        logger.info(f"Face captured: {image_path}")
            
            cap.release()
            cv2.destroyAllWindows()
            
            if captured_faces == 0:
                logger.warning(f"No faces captured for {name}")
                return {'success': False, 'message': 'No faces were captured. Registration failed.'}
            
            logger.info(f"Registration complete for {name}: {captured_faces} faces captured")
            return {'success': True, 'capture_count': captured_faces}
            
        except Exception as e:
            logger.error(f"Error during face capture: {e}")
            cap.release()
            cv2.destroyAllWindows()
            return {'success': False, 'message': f'Error during capture: {str(e)}'}
    
    def get_registration_count(self):
        """
        Get count of registered users.
        
        Returns:
            int: Number of registered users
        """
        return len(db_manager.get_all_users())
    
    def get_dataset_stats(self):
        """
        Get statistics about the dataset.
        
        Returns:
            dict: Dataset statistics
        """
        try:
            users = db_manager.get_all_users()
            total_users = len(users)
            total_images = 0
            
            for user_dir in DATASET_DIR.iterdir():
                if user_dir.is_dir():
                    images = list(user_dir.glob(f"*{IMAGE_EXTENSION}"))
                    total_images += len(images)
            
            return {
                'total_users': total_users,
                'total_images': total_images,
                'avg_images_per_user': total_images // total_users if total_users > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting dataset stats: {e}")
            return {}
    
    def verify_user_images(self, student_id):
        """
        Verify and count images for a user.
        
        Args:
            student_id (str): Student ID
            
        Returns:
            int: Number of valid images found
        """
        try:
            user_dir = DATASET_DIR / student_id
            if not user_dir.exists():
                return 0
            
            images = list(user_dir.glob(f"*{IMAGE_EXTENSION}"))
            return len(images)
        except Exception as e:
            logger.error(f"Error verifying user images: {e}")
            return 0
    
    def delete_user_images(self, student_id):
        """
        Delete all face images for a user.
        
        Args:
            student_id (str): Student ID
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            user_dir = DATASET_DIR / student_id
            if not user_dir.exists():
                return True
            
            for image_file in user_dir.glob(f"*{IMAGE_EXTENSION}"):
                image_file.unlink()
            
            user_dir.rmdir()
            logger.info(f"User images deleted: {student_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting user images: {e}")
            return False
    
    def re_register_user(self, student_id, name):
        """
        Re-register a user (capture new face images).
        
        Args:
            student_id (str): Student ID
            name (str): User name
            
        Returns:
            dict: Re-registration result
        """
        # Delete existing images
        self.delete_user_images(student_id)
        
        # Create new directory
        user_dir = DATASET_DIR / student_id
        if not ensure_directory_exists(user_dir):
            return {'success': False, 'message': 'Failed to create user directory.'}
        
        # Capture new faces
        return self._capture_faces(user_dir, name, student_id)


# Create global registration instance
face_registration = FaceRegistration()
