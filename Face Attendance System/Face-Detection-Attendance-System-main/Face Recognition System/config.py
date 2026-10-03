"""
Configuration Module
Stores all configuration settings for the Face Recognition Attendance System
"""

from pathlib import Path

# ================== PROJECT PATHS ==================
BASE_DIR = Path(__file__).parent
DATASET_DIR = BASE_DIR / "dataset"
TRAINER_DIR = BASE_DIR / "trainer"
ATTENDANCE_DIR = BASE_DIR / "attendance"
DATABASE_DIR = BASE_DIR / "database"
EXPORTS_DIR = BASE_DIR / "exports"
ASSETS_DIR = BASE_DIR / "assets"

# Create directories if they don't exist
for directory in [DATASET_DIR, TRAINER_DIR, ATTENDANCE_DIR, DATABASE_DIR, EXPORTS_DIR, ASSETS_DIR]:
    directory.mkdir(exist_ok=True, parents=True)

# ================== DATABASE CONFIGURATION ==================
DATABASE_FILE = DATABASE_DIR / "face_attendance.db"
MODEL_FILE = TRAINER_DIR / "lbph_model.yml"
SIMPLE_MODEL_FILE = TRAINER_DIR / "lbp_fallback_model.pkl"
LABELS_FILE = TRAINER_DIR / "labels.pkl"
# Kept for compatibility with older builds of this project.
ENCODINGS_FILE = TRAINER_DIR / "encodings.pkl"
ATTENDANCE_CSV = EXPORTS_DIR / "attendance.csv"

# ================== FACE RECOGNITION CONFIGURATION ==================
# Number of images to capture during registration
IMAGES_PER_PERSON = 20
# Camera device index. Change to 1 or 2 if you use an external camera.
CAMERA_INDEX = 0
# LBPH confidence distance threshold. Lower values are stricter.
LBPH_CONFIDENCE_THRESHOLD = 80.0
# Fallback LBP histogram distance threshold used when cv2.face is unavailable.
SIMPLE_LBP_DISTANCE_THRESHOLD = 18.0
# Face image size used for training and recognition.
FACE_IMAGE_SIZE = (200, 200)
# Face detection scale factor for Haar cascade.
FACE_SCALE_FACTOR = 1.2
# Face detection minimum neighbors. Higher values reduce false positives.
FACE_MIN_NEIGHBORS = 5
# Minimum face size for detection (pixels)
MIN_FACE_SIZE = 50
# JPEG quality used when saving captured face images.
IMAGE_QUALITY = 95

# ================== CAMERA CONFIGURATION ==================
CAMERA_FPS = 30
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAPTURE_DELAY = 100  # milliseconds between captures

# ================== GUI CONFIGURATION ==================
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
SIDEBAR_WIDTH = 250
MAIN_FONT = ("Segoe UI", 11)
TITLE_FONT = ("Segoe UI", 18, "bold")
BUTTON_FONT = ("Segoe UI", 10)

# ================== COLOR SCHEME - DARK MODE ==================
BG_COLOR = "#1e1e1e"
SIDEBAR_COLOR = "#2d2d2d"
ACCENT_COLOR = "#0d7377"
ACCENT_LIGHT = "#14a085"
TEXT_COLOR = "#ffffff"
TEXT_SECONDARY = "#b0b0b0"
DANGER_COLOR = "#e74c3c"
SUCCESS_COLOR = "#27ae60"
WARNING_COLOR = "#f39c12"
BORDER_COLOR = "#404040"

# ================== AUTHENTICATION ==================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin@2024"  # In production, use hashed passwords
SESSION_TIMEOUT = 3600  # 1 hour in seconds

# ================== DETECTION SETTINGS ==================
RECOGNITION_CONFIDENCE_THRESHOLD = 0.6
MIN_MATCH_THRESHOLD = 0.5

# ================== LOGGING ==================
LOG_FILE = BASE_DIR / "app.log"
LOG_LEVEL = "INFO"

# ================== DISPLAY SETTINGS ==================
SHOW_FPS = True
SHOW_CONFIDENCE = True
RECTANGLE_THICKNESS = 2
RECTANGLE_COLOR_KNOWN = (0, 255, 0)  # Green (BGR format)
RECTANGLE_COLOR_UNKNOWN = (0, 0, 255)  # Red (BGR format)
TEXT_COLOR_BGR = (255, 255, 255)  # White

# ================== EXPORT SETTINGS ==================
EXPORT_FORMAT = "csv"  # Options: 'csv', 'xlsx'
INCLUDE_PHOTOS_IN_EXPORT = False

# ================== SOUND SETTINGS ==================
ENABLE_SOUND_NOTIFICATIONS = True
