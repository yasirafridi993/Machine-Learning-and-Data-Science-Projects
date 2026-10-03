"""
Face Training Module
Builds a face recognition model from captured face images.
"""

import logging
import pickle
from datetime import datetime

import cv2
import numpy as np

from config import (
    DATASET_DIR,
    ENCODINGS_FILE,
    FACE_IMAGE_SIZE,
    FACE_MIN_NEIGHBORS,
    FACE_SCALE_FACTOR,
    LABELS_FILE,
    LBPH_CONFIDENCE_THRESHOLD,
    MIN_FACE_SIZE,
    MODEL_FILE,
    SIMPLE_LBP_DISTANCE_THRESHOLD,
    SIMPLE_MODEL_FILE,
)
from utils.utils import get_image_files, load_image

logger = logging.getLogger(__name__)


class SimpleLBPRecognizer:
    """
    Small fallback recognizer for systems without opencv-contrib-python.

    It stores Local Binary Pattern histograms for each training image and uses
    nearest-neighbor chi-square distance at prediction time.
    """

    model_type = "simple_lbp"

    def __init__(self):
        self.features = None
        self.labels = None

    @staticmethod
    def _lbp_histogram(gray_image, grid_x=8, grid_y=8):
        """Create a grid-based LBP histogram feature vector."""
        gray = gray_image.astype(np.uint8)
        center = gray[1:-1, 1:-1]
        lbp = np.zeros_like(center, dtype=np.uint8)

        neighbors = [
            gray[:-2, :-2],
            gray[:-2, 1:-1],
            gray[:-2, 2:],
            gray[1:-1, 2:],
            gray[2:, 2:],
            gray[2:, 1:-1],
            gray[2:, :-2],
            gray[1:-1, :-2],
        ]

        for bit, neighbor in enumerate(neighbors):
            lbp |= ((neighbor >= center).astype(np.uint8) << (7 - bit))

        height, width = lbp.shape
        cell_h = max(1, height // grid_y)
        cell_w = max(1, width // grid_x)
        histograms = []

        for gy in range(grid_y):
            for gx in range(grid_x):
                y1 = gy * cell_h
                x1 = gx * cell_w
                y2 = height if gy == grid_y - 1 else (gy + 1) * cell_h
                x2 = width if gx == grid_x - 1 else (gx + 1) * cell_w
                cell = lbp[y1:y2, x1:x2]
                hist, _ = np.histogram(cell, bins=256, range=(0, 256))
                hist = hist.astype("float32")
                hist /= hist.sum() + 1e-7
                histograms.append(hist)

        return np.concatenate(histograms).astype("float32")

    @staticmethod
    def _chi_square_distance(left, right):
        """Calculate chi-square distance between two histogram features."""
        return float(0.5 * np.sum(((left - right) ** 2) / (left + right + 1e-7)))

    def train(self, images, labels):
        """Train fallback recognizer with prepared grayscale face images."""
        self.features = np.array([self._lbp_histogram(image) for image in images], dtype="float32")
        self.labels = np.array(labels, dtype=np.int32)

    def write(self, file_path):
        """Persist fallback model."""
        with open(file_path, "wb") as model_file:
            pickle.dump({"features": self.features, "labels": self.labels}, model_file)

    def read(self, file_path):
        """Load fallback model."""
        with open(file_path, "rb") as model_file:
            data = pickle.load(model_file)
        self.features = data["features"]
        self.labels = data["labels"]

    def predict(self, image):
        """Predict the nearest label and distance for one prepared face."""
        if self.features is None or self.labels is None or len(self.features) == 0:
            raise RuntimeError("Fallback recognizer is not trained.")

        feature = self._lbp_histogram(image)
        distances = np.array(
            [self._chi_square_distance(feature, known_feature) for known_feature in self.features],
            dtype="float32",
        )
        best_index = int(np.argmin(distances))
        return int(self.labels[best_index]), float(distances[best_index])


class FaceTrainer:
    """
    Handles face preprocessing and model training.
    """

    def __init__(self):
        """Initialize face trainer."""
        self.recognizer = None
        self.label_map = {}
        self.model_metadata = {}
        self.model_type = None
        self.model_file = None
        self.distance_threshold = None
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    @staticmethod
    def _opencv_lbph_available():
        """Check whether OpenCV contrib face recognizers are available."""
        face_module = getattr(cv2, "face", None)
        return face_module is not None and hasattr(face_module, "LBPHFaceRecognizer_create")

    @classmethod
    def _create_recognizer(cls, preferred_model_type=None):
        """Create the best available recognizer."""
        if preferred_model_type == "simple_lbp":
            return SimpleLBPRecognizer(), "simple_lbp", SIMPLE_MODEL_FILE, SIMPLE_LBP_DISTANCE_THRESHOLD

        if preferred_model_type in (None, "opencv_lbph") and cls._opencv_lbph_available():
            recognizer = cv2.face.LBPHFaceRecognizer_create(
                radius=1,
                neighbors=8,
                grid_x=8,
                grid_y=8,
            )
            return recognizer, "opencv_lbph", MODEL_FILE, LBPH_CONFIDENCE_THRESHOLD

        if preferred_model_type == "opencv_lbph":
            raise RuntimeError(
                "This model was trained with opencv-contrib-python, but cv2.face is unavailable."
            )

        logger.warning("cv2.face is unavailable. Using fallback LBP histogram recognizer.")
        return SimpleLBPRecognizer(), "simple_lbp", SIMPLE_MODEL_FILE, SIMPLE_LBP_DISTANCE_THRESHOLD

    def _prepare_face(self, image):
        """
        Convert an image to a normalized grayscale face image.

        Captured dataset images are already cropped faces, but this method also
        supports full images by cropping the largest detected face first.
        """
        if image is None:
            return None

        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=FACE_SCALE_FACTOR,
            minNeighbors=FACE_MIN_NEIGHBORS,
            minSize=(MIN_FACE_SIZE, MIN_FACE_SIZE),
        )

        if len(faces) > 0:
            x, y, w, h = max(faces, key=lambda face: face[2] * face[3])
            gray = gray[y:y + h, x:x + w]

        prepared = cv2.resize(gray, FACE_IMAGE_SIZE)
        return cv2.equalizeHist(prepared)

    def train_model(self, progress_callback=None):
        """
        Train the recognizer from all registered face images.

        Args:
            progress_callback (callable): Optional callback for progress updates.

        Returns:
            dict: Training result with success status.
        """
        try:
            recognizer, model_type, model_file, distance_threshold = self._create_recognizer()
        except RuntimeError as exc:
            return {"success": False, "message": str(exc)}

        try:
            face_images = []
            numeric_labels = []
            label_map = {}
            failed_images = 0
            processed_images = 0

            user_dirs = sorted([path for path in DATASET_DIR.iterdir() if path.is_dir()])
            if not user_dirs:
                return {
                    "success": False,
                    "message": "No users registered. Please register users first.",
                }

            image_files_by_user = {user_dir: get_image_files(user_dir) for user_dir in user_dirs}
            total_images = sum(len(files) for files in image_files_by_user.values())
            if total_images == 0:
                return {
                    "success": False,
                    "message": "No face images found in dataset. Register users first.",
                }

            for label_id, user_dir in enumerate(user_dirs, start=1):
                student_id = user_dir.name
                label_map[label_id] = student_id
                image_files = image_files_by_user[user_dir]

                if not image_files:
                    logger.warning("No images found for user: %s", student_id)
                    continue

                logger.info("Training user %s with %s images", student_id, len(image_files))

                for image_file in image_files:
                    image = load_image(image_file)
                    prepared_face = self._prepare_face(image)

                    if prepared_face is None:
                        failed_images += 1
                    else:
                        face_images.append(prepared_face)
                        numeric_labels.append(label_id)
                        processed_images += 1

                    if progress_callback:
                        progress_callback(
                            {
                                "processed": processed_images,
                                "failed": failed_images,
                                "total": total_images,
                                "current_user": student_id,
                            }
                        )

            if not face_images:
                return {
                    "success": False,
                    "message": "Failed to prepare any face images. Check dataset image quality.",
                }

            recognizer.train(face_images, np.array(numeric_labels, dtype=np.int32))
            recognizer.write(str(model_file))

            metadata = {
                "label_map": label_map,
                "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "image_size": FACE_IMAGE_SIZE,
                "model_type": model_type,
                "model_file": model_file.name,
                "distance_threshold": distance_threshold,
                "processed_images": processed_images,
                "failed_images": failed_images,
                "total_users": len(label_map),
            }
            with open(LABELS_FILE, "wb") as labels_file:
                pickle.dump(metadata, labels_file)

            self.recognizer = recognizer
            self.label_map = label_map
            self.model_metadata = metadata
            self.model_type = model_type
            self.model_file = model_file
            self.distance_threshold = distance_threshold

            logger.info(
                "Model trained. type=%s users=%s processed=%s failed=%s",
                model_type,
                len(label_map),
                processed_images,
                failed_images,
            )

            return {
                "success": True,
                "message": f"Model trained successfully! Processed {processed_images} face images.",
                "model_type": model_type,
                "processed_images": processed_images,
                "failed_images": failed_images,
                "total_users": len(label_map),
            }

        except Exception as exc:
            logger.error("Error during model training: %s", exc, exc_info=True)
            return {"success": False, "message": f"Training failed: {exc}"}

    def load_trained_model(self):
        """
        Load the trained model and label map from disk.

        Returns:
            bool: True if loaded successfully, False otherwise.
        """
        try:
            if not self.is_model_trained():
                logger.warning("Trained model files not found")
                return False

            with open(LABELS_FILE, "rb") as labels_file:
                metadata = pickle.load(labels_file)

            model_type = metadata.get("model_type")
            if not model_type:
                model_type = "opencv_lbph" if MODEL_FILE.exists() else "simple_lbp"

            recognizer, model_type, model_file, default_threshold = self._create_recognizer(model_type)
            if not model_file.exists():
                logger.error("Model file missing: %s", model_file)
                return False

            recognizer.read(str(model_file))

            self.recognizer = recognizer
            self.model_metadata = metadata
            self.label_map = {
                int(label_id): student_id
                for label_id, student_id in metadata.get("label_map", {}).items()
            }
            self.model_type = model_type
            self.model_file = model_file
            self.distance_threshold = float(metadata.get("distance_threshold", default_threshold))

            logger.info("Model loaded. type=%s labels=%s", self.model_type, len(self.label_map))
            return True

        except Exception as exc:
            logger.error("Error loading trained model: %s", exc, exc_info=True)
            return False

    def is_model_trained(self):
        """
        Check if model and labels are available.

        Returns:
            bool: True if trained model files exist.
        """
        return LABELS_FILE.exists() and (MODEL_FILE.exists() or SIMPLE_MODEL_FILE.exists())

    def get_distance_threshold(self):
        """Return the active model distance threshold."""
        if self.distance_threshold is not None:
            return self.distance_threshold
        if self.model_metadata:
            return float(self.model_metadata.get("distance_threshold", LBPH_CONFIDENCE_THRESHOLD))
        return LBPH_CONFIDENCE_THRESHOLD

    def get_model_stats(self):
        """
        Get statistics about the trained model.

        Returns:
            dict: Model statistics.
        """
        try:
            if not self.is_model_trained():
                return {"is_trained": False, "message": "Model not trained yet"}

            if not self.model_metadata:
                self.load_trained_model()

            model_file = self.model_file or (MODEL_FILE if MODEL_FILE.exists() else SIMPLE_MODEL_FILE)
            return {
                "is_trained": True,
                "model_type": self.model_type or self.model_metadata.get("model_type", ""),
                "total_users": len(self.label_map),
                "processed_images": self.model_metadata.get("processed_images", 0),
                "failed_images": self.model_metadata.get("failed_images", 0),
                "trained_at": self.model_metadata.get("trained_at", ""),
                "file_size_mb": round(model_file.stat().st_size / (1024 * 1024), 2),
            }
        except Exception as exc:
            logger.error("Error getting model stats: %s", exc)
            return {"is_trained": False, "message": str(exc)}

    def delete_trained_model(self):
        """
        Delete trained model files.

        Returns:
            bool: True if one or more model files were deleted.
        """
        deleted = False
        for file_path in (MODEL_FILE, SIMPLE_MODEL_FILE, LABELS_FILE, ENCODINGS_FILE):
            try:
                if file_path.exists():
                    file_path.unlink()
                    deleted = True
            except Exception as exc:
                logger.error("Error deleting model file %s: %s", file_path, exc)

        self.recognizer = None
        self.label_map = {}
        self.model_metadata = {}
        self.model_type = None
        self.model_file = None
        self.distance_threshold = None
        return deleted


# Create global trainer instance
face_trainer = FaceTrainer()
