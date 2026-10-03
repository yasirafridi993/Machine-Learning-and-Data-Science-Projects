"""
models.py
Plain data models shared between the detection services, the database layer,
and the UI. Kept free of any Flet or OpenCV imports so it can be reused
anywhere in the app without pulling in heavy dependencies.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple


@dataclass
class DetectedObject:
    """A single detected object within one frame/image."""
    label: str
    confidence: float
    bbox: Tuple[float, float, float, float]  # x1, y1, x2, y2


@dataclass
class DetectionResult:
    """The outcome of running detection on one source (webcam frame,
    image file, or video file)."""
    source_type: str  # "webcam" | "image" | "video"
    source_name: str
    objects: List[DetectedObject] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    output_path: Optional[str] = None
    processing_time_ms: float = 0.0

    @property
    def object_count(self) -> int:
        return len(self.objects)

    @property
    def average_confidence(self) -> float:
        if not self.objects:
            return 0.0
        return sum(o.confidence for o in self.objects) / len(self.objects)

    @property
    def highest_confidence(self) -> float:
        if not self.objects:
            return 0.0
        return max(o.confidence for o in self.objects)

    @property
    def object_counts_by_label(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for obj in self.objects:
            counts[obj.label] = counts.get(obj.label, 0) + 1
        return counts


@dataclass
class DetectionSessionRecord:
    """A row as stored in / read from the detection_sessions table."""
    id: int
    source_type: str
    source_name: str
    object_count: int
    avg_confidence: float
    max_confidence: float
    processing_time_ms: float
    output_path: Optional[str]
    timestamp: str
