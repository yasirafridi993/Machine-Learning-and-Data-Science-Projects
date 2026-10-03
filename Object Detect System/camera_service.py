"""
camera_service.py
Thin, thread-safe wrapper around OpenCV VideoCapture for the live-detection
screen. Isolated from the UI so camera lifecycle/errors are handled in one
place.

Note on mobile: this uses cv2.VideoCapture, which reads a locally attached
webcam. That works for the Flet desktop app (Windows/macOS/Linux). Native
Android camera streaming from a compiled Flet APK requires a platform camera
API rather than OpenCV's VideoCapture; see the README for notes on adapting
this service for a packaged Android build.
"""
import logging
import threading
from typing import Optional

import cv2
import numpy as np

import config

logger = logging.getLogger(__name__)


class CameraError(Exception):
    """Raised for camera-not-found / permission / read failures."""


class CameraService:
    def __init__(self, camera_index: Optional[int] = None):
        self.camera_index = (
            config.DEFAULT_CAMERA_INDEX if camera_index is None else camera_index
        )
        self._cap: Optional[cv2.VideoCapture] = None
        self._lock = threading.Lock()

    def open(self) -> None:
        with self._lock:
            if self._cap is not None:
                return
            cap = cv2.VideoCapture(self.camera_index)
            if not cap.isOpened():
                cap.release()
                raise CameraError(
                    "Could not access the camera. Make sure it is connected, "
                    "not in use by another application, and that camera "
                    "permission has been granted to this app."
                )
            self._cap = cap

    def read(self) -> np.ndarray:
        with self._lock:
            if self._cap is None:
                raise CameraError("Camera is not open.")
            ok, frame = self._cap.read()
        if not ok or frame is None:
            raise CameraError("Lost connection to the camera while reading a frame.")
        return frame

    @property
    def is_open(self) -> bool:
        with self._lock:
            return self._cap is not None and self._cap.isOpened()

    def close(self) -> None:
        with self._lock:
            if self._cap is not None:
                self._cap.release()
                self._cap = None
