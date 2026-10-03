"""
Constants Module
Global constants used throughout the application
"""

# ================== STATUS CODES ==================
STATUS_PRESENT = "Present"
STATUS_ABSENT = "Absent"
STATUS_LATE = "Late"
STATUS_LEAVE = "Leave"

# ================== ERROR MESSAGES ==================
ERROR_CAMERA_NOT_FOUND = "Camera not found. Please connect a webcam."
ERROR_NO_FACE_DETECTED = "No face detected. Please position your face in the frame."
ERROR_DUPLICATE_REGISTRATION = "This ID is already registered. Use a different ID."
ERROR_DATABASE_CONNECTION = "Failed to connect to database."
ERROR_INVALID_CREDENTIALS = "Invalid username or password."
ERROR_SESSION_EXPIRED = "Your session has expired. Please login again."
ERROR_NO_TRAINED_MODEL = "No trained model found. Please train the model first."
ERROR_IMAGE_LOADING = "Failed to load face images."
ERROR_ENCODING_FAILED = "Failed to encode faces."

# ================== SUCCESS MESSAGES ==================
SUCCESS_REGISTRATION = "User registered successfully!"
SUCCESS_TRAINING = "Model trained successfully!"
SUCCESS_ATTENDANCE_MARKED = "Attendance marked successfully!"
SUCCESS_LOGOUT = "Logged out successfully!"
SUCCESS_DATA_EXPORTED = "Data exported successfully!"

# ================== DATABASE COLUMN NAMES ==================
# Users table
COL_USER_ID = "id"
COL_USER_NAME = "name"
COL_USER_STUDENT_ID = "student_id"
COL_USER_IMAGE_PATH = "image_path"
COL_USER_CREATED_AT = "created_at"
COL_USER_EMAIL = "email"
COL_USER_PHONE = "phone"

# Attendance table
COL_ATTENDANCE_ID = "id"
COL_ATTENDANCE_STUDENT_ID = "student_id"
COL_ATTENDANCE_NAME = "name"
COL_ATTENDANCE_DATE = "date"
COL_ATTENDANCE_TIME = "time"
COL_ATTENDANCE_STATUS = "status"
COL_ATTENDANCE_CONFIDENCE = "confidence"

# ================== TIME FORMATS ==================
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# ================== IMAGE SPECIFICATIONS ==================
IMAGE_EXTENSION = ".jpg"
SUPPORTED_FORMATS = [".jpg", ".jpeg", ".png", ".bmp"]
IMAGE_QUALITY = 95
RESIZE_FACTOR = 0.25  # For faster processing

# ================== ATTENDANCE RULES ==================
MARKING_THRESHOLD_MINUTES = 5  # Minutes to mark duplicate attendance
ATTENDANCE_TIME_WINDOW = 60  # Minutes to auto-mark as late
LATE_TIME = "09:30"  # Time after which attendance is marked as late

# ================== UI TEXT ==================
BTN_REGISTER = "Register User"
BTN_TRAIN = "Train Model"
BTN_START_ATTENDANCE = "Start Attendance"
BTN_EXPORT_CSV = "Export CSV"
BTN_VIEW_ATTENDANCE = "View Attendance"
BTN_SETTINGS = "Settings"
BTN_LOGOUT = "Logout"
BTN_EXIT = "Exit"
BTN_CANCEL = "Cancel"
BTN_SAVE = "Save"
BTN_DELETE = "Delete"
BTN_REFRESH = "Refresh"
BTN_SEARCH = "Search"

# ================== VALIDATION RULES ==================
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 50
MIN_ID_LENGTH = 3
MAX_ID_LENGTH = 20
MIN_PASSWORD_LENGTH = 6

# ================== PERFORMANCE SETTINGS ==================
FACE_ENCODING_BATCH_SIZE = 5
IMAGE_PROCESSING_THREADS = 4
CACHE_SIZE = 100

# ================== NOTIFICATION SOUNDS ==================
SOUND_SUCCESS = "ding"
SOUND_ERROR = "alert"
SOUND_NOTIFICATION = "chime"

# ================== PAGINATION ==================
RECORDS_PER_PAGE = 20

# ================== API TIMEOUTS (if using external services) ==================
API_TIMEOUT = 30
CAMERA_TIMEOUT = 5
DATABASE_TIMEOUT = 10

# ================== CACHE SETTINGS ==================
CACHE_VALIDITY_MINUTES = 30
AUTO_REFRESH_INTERVAL_SECONDS = 5
