"""
Attendance & Recognition Module
Handles real-time OpenCV face recognition and attendance marking.
"""

import logging
from datetime import datetime, timedelta

import cv2

from config import (
    CAMERA_FPS,
    CAMERA_HEIGHT,
    CAMERA_INDEX,
    CAMERA_WIDTH,
    FACE_IMAGE_SIZE,
    FACE_MIN_NEIGHBORS,
    FACE_SCALE_FACTOR,
    MIN_FACE_SIZE,
    RECTANGLE_COLOR_KNOWN,
    RECTANGLE_COLOR_UNKNOWN,
    RECTANGLE_THICKNESS,
    TEXT_COLOR_BGR,
)
from modules.trainer import face_trainer
from utils.constants import DATETIME_FORMAT, STATUS_PRESENT
from utils.database import db_manager

logger = logging.getLogger(__name__)


class AttendanceSystem:
    """
    Handles real-time face recognition and attendance marking.
    """

    def __init__(self):
        """Initialize attendance system."""
        self.running = False
        self.current_frame = None
        self.last_marked_time = {}
        self.recognized_count = 0
        self.unknown_count = 0
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    @staticmethod
    def _distance_to_confidence(distance, threshold):
        """Convert LBPH distance to a 0-1 confidence-like score."""
        if threshold <= 0:
            return 0.0
        confidence = 1.0 - (distance / threshold)
        return max(0.0, min(1.0, confidence))

    def _prepare_face(self, gray_frame, face_box):
        """Crop, resize, and normalize a detected face."""
        x, y, w, h = face_box
        face = gray_frame[y:y + h, x:x + w]
        face = cv2.resize(face, FACE_IMAGE_SIZE)
        return cv2.equalizeHist(face)

    def start_recognition(self, confidence_threshold=None, process_callback=None):
        """
        Start real-time face recognition and attendance marking.

        Args:
            confidence_threshold (float): Optional LBPH distance threshold.
            process_callback (callable): Callback for GUI stat updates.

        Returns:
            dict: Result with success status.
        """
        if not face_trainer.load_trained_model():
            return {
                "success": False,
                "message": "No trained model found. Please train the model first.",
            }
        threshold = confidence_threshold or face_trainer.get_distance_threshold()

        cap = cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened():
            return {"success": False, "message": "Camera not found"}

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)

        self.running = True
        self.recognized_count = 0
        self.unknown_count = 0

        logger.info("Face recognition started")

        try:
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    logger.error("Failed to read frame")
                    break

                frame = cv2.flip(frame, 1)
                self.current_frame = frame.copy()

                results = self._process_frame(frame, threshold)
                if process_callback:
                    process_callback(
                        {
                            "frame": frame,
                            "face_count": results["face_count"],
                            "recognized": self.recognized_count,
                            "unknown": self.unknown_count,
                            "last_frame": results,
                        }
                    )

                cv2.imshow("Face Recognition Attendance - Press ESC to exit", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    break

            return {
                "success": True,
                "message": "Recognition session ended",
                "recognized_count": self.recognized_count,
                "unknown_count": self.unknown_count,
            }

        except Exception as exc:
            logger.error("Error during recognition: %s", exc, exc_info=True)
            return {"success": False, "message": f"Recognition error: {exc}"}

        finally:
            self.running = False
            cap.release()
            cv2.destroyAllWindows()
            logger.info(
                "Face recognition stopped. Recognized=%s Unknown=%s",
                self.recognized_count,
                self.unknown_count,
            )

    def _process_frame(self, frame, threshold):
        """
        Process a single frame for face recognition.

        Args:
            frame: OpenCV BGR frame.
            threshold (float): Maximum LBPH distance for a match.

        Returns:
            dict: Recognition results for the frame.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=FACE_SCALE_FACTOR,
            minNeighbors=FACE_MIN_NEIGHBORS,
            minSize=(MIN_FACE_SIZE, MIN_FACE_SIZE),
        )

        frame_recognized = 0
        frame_unknown = 0

        for face_box in faces:
            x, y, w, h = face_box
            prepared_face = self._prepare_face(gray, face_box)
            label_id, distance = face_trainer.recognizer.predict(prepared_face)

            student_id = face_trainer.label_map.get(int(label_id))
            is_known = student_id is not None and distance <= threshold

            if is_known:
                confidence = self._distance_to_confidence(distance, threshold)
                user = db_manager.get_user_by_student_id(student_id)
                display_name = user["name"] if user else student_id
                text = f"{display_name} ({confidence * 100:.1f}%)"
                color = RECTANGLE_COLOR_KNOWN
                frame_recognized += 1
                self.recognized_count += 1
                self._mark_attendance(student_id, confidence)
            else:
                confidence = 0.0
                text = "Unknown"
                color = RECTANGLE_COLOR_UNKNOWN
                frame_unknown += 1
                self.unknown_count += 1

            self._draw_face_label(frame, x, y, w, h, text, color)

        return {
            "face_count": len(faces),
            "recognized": frame_recognized,
            "unknown": frame_unknown,
        }

    @staticmethod
    def _draw_face_label(frame, x, y, w, h, text, color):
        """Draw face rectangle and label on a frame."""
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, RECTANGLE_THICKNESS)

        label_top = y - 32 if y > 40 else y + h + 8
        label_bottom = label_top + 28
        cv2.rectangle(frame, (x, label_top), (x + w, label_bottom), color, -1)
        cv2.putText(
            frame,
            text,
            (x + 6, label_bottom - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            TEXT_COLOR_BGR,
            1,
            cv2.LINE_AA,
        )

    def _mark_attendance(self, student_id, confidence):
        """
        Mark attendance for a recognized face.

        Args:
            student_id (str): Student ID.
            confidence (float): Recognition confidence score.
        """
        try:
            if student_id in self.last_marked_time:
                last_time = datetime.strptime(self.last_marked_time[student_id], DATETIME_FORMAT)
                if datetime.now() - last_time < timedelta(minutes=5):
                    return

            user = db_manager.get_user_by_student_id(student_id)
            if not user:
                logger.warning("User not found while marking attendance: %s", student_id)
                return

            db_manager.mark_attendance(
                student_id,
                user["name"],
                STATUS_PRESENT,
                confidence,
            )

            self.last_marked_time[student_id] = datetime.now().strftime(DATETIME_FORMAT)
            logger.info("Attendance checked for %s (%s)", user["name"], student_id)

        except Exception as exc:
            logger.error("Error marking attendance: %s", exc, exc_info=True)

    def stop_recognition(self):
        """Stop face recognition."""
        self.running = False
        logger.info("Recognition stop requested")

    def get_today_stats(self):
        """
        Get today's attendance statistics.

        Returns:
            dict: Attendance statistics.
        """
        from utils.utils import get_current_date

        try:
            today = get_current_date()
            all_attendance = db_manager.get_today_attendance()
            all_users = db_manager.get_all_users()
            marked_users = len(set(att["student_id"] for att in all_attendance))
            unmarked_users = len(all_users) - marked_users
            stats = db_manager.get_attendance_statistics(today, today)

            return {
                "date": today,
                "total_users": len(all_users),
                "present": stats.get("total_present", 0),
                "absent": max(0, unmarked_users),
                "late": stats.get("total_late", 0),
                "records": all_attendance,
            }

        except Exception as exc:
            logger.error("Error getting today's stats: %s", exc)
            return {}

    def get_session_stats(self):
        """
        Get current session statistics.

        Returns:
            dict: Session statistics.
        """
        total = self.recognized_count + self.unknown_count
        return {
            "recognized_count": self.recognized_count,
            "unknown_count": self.unknown_count,
            "total_detections": total,
            "recognition_rate": (self.recognized_count / total * 100) if total else 0,
        }


# Create global attendance instance
attendance_system = AttendanceSystem()
