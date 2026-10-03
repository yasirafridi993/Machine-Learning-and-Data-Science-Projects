"""
detection_service.py
Loads the YOLOv8 model and runs inference on frames, images, and videos.
Automatically uses the GPU when available (CUDA) and falls back to CPU.
All OpenCV / Ultralytics / PyTorch usage is isolated here so the UI layer
never touches computer-vision code directly.
"""
import logging
import time
from pathlib import Path
from typing import Callable, List, Optional, Tuple

import cv2
import numpy as np

import config
from models import DetectedObject

logger = logging.getLogger(__name__)


class DetectionServiceError(Exception):
    """Raised for any recoverable detection/model failure the UI should
    surface as a friendly message instead of crashing."""


class DetectionService:
    """Thin, UI-agnostic wrapper around an Ultralytics YOLO model."""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or config.DEFAULT_MODEL_PATH
        self.device = "cpu"
        self.model = None
        self._load_model()

    # -- Setup ---------------------------------------------------------------

    def _load_model(self) -> None:
        try:
            import torch  # deferred import: heavy, and only needed here
            from ultralytics import YOLO
        except ImportError as e:
            raise DetectionServiceError(
                "Required AI libraries are not installed. Run "
                "'pip install -r requirements.txt' and try again."
            ) from e

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        try:
            self.model = YOLO(self.model_path)
        except Exception as primary_error:
            logger.warning(
                "Could not load model '%s' (%s). Falling back to yolov8n.pt.",
                self.model_path,
                primary_error,
            )
            try:
                self.model = YOLO("yolov8n.pt")
                self.model_path = "yolov8n.pt"
            except Exception as fallback_error:
                raise DetectionServiceError(
                    "Failed to load the YOLO model. Check your internet "
                    "connection (needed once, to download pretrained weights) "
                    f"or place a valid .pt file in the models/ folder. Details: {fallback_error}"
                ) from fallback_error

        try:
            self.model.to(self.device)
        except Exception:
            # Some Ultralytics versions manage device placement internally;
            # a failure here is not fatal.
            logger.debug("Model.to(%s) was not applied directly.", self.device)

    @property
    def is_ready(self) -> bool:
        return self.model is not None

    @property
    def device_label(self) -> str:
        return "GPU (CUDA)" if self.device == "cuda" else "CPU"

    # -- Inference -------------------------------------------------------------

    def detect_frame(
        self,
        frame: np.ndarray,
        conf: Optional[float] = None,
        iou: Optional[float] = None,
        draw: bool = True,
    ) -> Tuple[np.ndarray, List[DetectedObject], float]:
        """Run detection on a single BGR frame (numpy array).
        Returns (annotated_frame, detected_objects, elapsed_ms)."""
        if self.model is None:
            raise DetectionServiceError("Detection model is not loaded.")
        if frame is None or frame.size == 0:
            raise DetectionServiceError("Received an empty frame.")

        conf = config.CONFIDENCE_THRESHOLD if conf is None else conf
        iou = config.IOU_THRESHOLD if iou is None else iou

        start = time.perf_counter()
        try:
            results = self.model.predict(
                source=frame, conf=conf, iou=iou, device=self.device, verbose=False
            )
        except Exception as e:
            raise DetectionServiceError(f"Detection failed: {e}") from e
        elapsed_ms = (time.perf_counter() - start) * 1000.0

        objects: List[DetectedObject] = []
        annotated = frame.copy() if draw else frame
        result = results[0]
        names = result.names if hasattr(result, "names") else {}

        boxes = getattr(result, "boxes", None)
        if boxes is not None:
            for box in boxes:
                xyxy = box.xyxy[0].tolist()
                cls_id = int(box.cls[0])
                conf_score = float(box.conf[0])
                label = names.get(cls_id, str(cls_id))
                objects.append(
                    DetectedObject(label=label, confidence=conf_score, bbox=tuple(xyxy))
                )
                if draw:
                    _draw_box(annotated, xyxy, label, conf_score)

        return annotated, objects, elapsed_ms

    def detect_image_file(self, image_path: str) -> Tuple[np.ndarray, List[DetectedObject], float]:
        path = Path(image_path)
        if not path.exists():
            raise DetectionServiceError(f"Image not found: {image_path}")
        if path.suffix.lower() not in config.SUPPORTED_IMAGE_EXT:
            raise DetectionServiceError(f"Unsupported image type: {path.suffix}")

        frame = cv2.imread(str(path))
        if frame is None:
            raise DetectionServiceError(
                f"Could not read image (it may be corrupted): {path.name}"
            )
        return self.detect_frame(frame)

    def detect_video_file(
        self,
        video_path: str,
        output_path: str,
        progress_callback: Optional[Callable[[float], None]] = None,
    ) -> Tuple[str, List[DetectedObject], float]:
        path = Path(video_path)
        if not path.exists():
            raise DetectionServiceError(f"Video not found: {video_path}")
        if path.suffix.lower() not in config.SUPPORTED_VIDEO_EXT:
            raise DetectionServiceError(f"Unsupported video type: {path.suffix}")

        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            raise DetectionServiceError(f"Could not open video: {path.name}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        if not writer.isOpened():
            cap.release()
            raise DetectionServiceError("Could not create output video file.")

        all_objects: List[DetectedObject] = []
        total_time_ms = 0.0
        frame_idx = 0

        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                annotated, objects, elapsed_ms = self.detect_frame(frame)
                writer.write(annotated)
                all_objects.extend(objects)
                total_time_ms += elapsed_ms
                frame_idx += 1
                if progress_callback and total_frames > 0:
                    try:
                        progress_callback(min(frame_idx / total_frames, 1.0))
                    except Exception:
                        pass  # never let a UI callback error kill processing
        finally:
            cap.release()
            writer.release()

        if frame_idx == 0:
            raise DetectionServiceError("The video contained no readable frames.")

        return output_path, all_objects, total_time_ms


def _draw_box(frame: np.ndarray, xyxy, label: str, confidence: float) -> None:
    x1, y1, x2, y2 = [int(v) for v in xyxy]
    color = (113, 204, 46)  # BGR, matches the app's accent green
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    text = f"{label} {confidence:.2f}"
    (tw, th), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    label_y = max(y1, th + 8)
    cv2.rectangle(frame, (x1, label_y - th - 8), (x1 + tw + 6, label_y), color, -1)
    cv2.putText(
        frame, text, (x1 + 3, label_y - 5),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (15, 15, 15), 1, cv2.LINE_AA,
    )
