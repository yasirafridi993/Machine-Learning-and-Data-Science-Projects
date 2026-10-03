"""
config.py
Centralized configuration for paths, model settings, and UI constants.
Values can be overridden via environment variables (see .env.example).
"""
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

MODELS_DIR = BASE_DIR / "models"
OUTPUTS_DIR = BASE_DIR / "outputs"
SCREENSHOTS_DIR = OUTPUTS_DIR / "screenshots"
VIDEOS_DIR = OUTPUTS_DIR / "videos"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "detections.db"
ASSETS_DIR = BASE_DIR / "assets"

for _dir in (MODELS_DIR, SCREENSHOTS_DIR, VIDEOS_DIR, DATA_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Model / detection settings
# ---------------------------------------------------------------------------
# YOLO will auto-download this weight file on first run if it isn't present
# locally (requires internet access once). Point YOLO_MODEL at a custom
# .pt file placed inside models/ to use your own trained weights instead.
DEFAULT_MODEL_NAME = os.getenv("YOLO_MODEL", "yolov8n.pt")


def resolve_model_path() -> str:
    """Prefer a local weight file inside models/, otherwise fall back to the
    bare model name so Ultralytics can download/cache the pretrained model."""
    local_path = MODELS_DIR / DEFAULT_MODEL_NAME
    if local_path.exists():
        return str(local_path)
    return DEFAULT_MODEL_NAME


DEFAULT_MODEL_PATH = resolve_model_path()
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.45"))
IOU_THRESHOLD = float(os.getenv("IOU_THRESHOLD", "0.45"))

# ---------------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------------
DEFAULT_CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
LIVE_DETECTION_TARGET_FPS = int(os.getenv("LIVE_DETECTION_TARGET_FPS", "20"))

# ---------------------------------------------------------------------------
# App / UI
# ---------------------------------------------------------------------------
APP_NAME = "AI Vision Detector"
APP_VERSION = "1.0.0"

WINDOW_WIDTH = 1320
WINDOW_HEIGHT = 840
WINDOW_MIN_WIDTH = 380
WINDOW_MIN_HEIGHT = 640

# Below this page width, the UI switches to the compact mobile layout
# (bottom navigation bar, single-column content, stacked cards).
MOBILE_BREAKPOINT = 760

SUPPORTED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
SUPPORTED_VIDEO_EXT = {".mp4", ".avi", ".mov", ".mkv", ".webm"}

# Brand palette
COLOR_PRIMARY = "#6C5CE7"
COLOR_PRIMARY_DARK = "#4834D4"
COLOR_ACCENT = "#00D9A6"
COLOR_DANGER = "#FF5C5C"
COLOR_WARNING = "#FFB800"
COLOR_BG_LIGHT = "#F5F6FA"
COLOR_BG_DARK = "#0F1117"
COLOR_SURFACE_DARK = "#181B23"
