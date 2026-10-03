# Configuration Guide

## Customizing the Face Recognition Attendance System

All configuration settings are in `config.py`. This guide explains each setting and how to customize them.

## 🎯 Quick Configuration

### Change Recognition Sensitivity
```python
# config.py
FACE_TOLERANCE = 0.6  # Lower = stricter
# Range: 0.0 (very strict) to 1.0 (very loose)
# Default: 0.6 (recommended)
```

### Change Number of Images Per User
```python
# config.py
IMAGES_PER_PERSON = 20  # Number of images to capture
# Range: 10-50 (minimum 10 recommended)
# Default: 20 (recommended)
```

### Change Camera Resolution
```python
# config.py
CAMERA_WIDTH = 640   # Width in pixels
CAMERA_HEIGHT = 480  # Height in pixels
# Common resolutions:
# 640x480 (default, fast)
# 1280x720 (HD)
# 1920x1080 (Full HD, slower)
```

### Change GUI Theme Colors
```python
# config.py
BG_COLOR = "#1e1e1e"      # Main background (dark gray)
ACCENT_COLOR = "#0d7377"  # Primary accent (teal)
SUCCESS_COLOR = "#27ae60" # Success messages (green)
DANGER_COLOR = "#e74c3c"  # Danger/warning (red)
```

---

## 📋 Detailed Configuration Reference

### ================== PROJECT PATHS ==================

```python
# AUTO-GENERATED - These are set automatically
BASE_DIR = Path(__file__).parent          # Project root
DATASET_DIR = BASE_DIR / "dataset"        # Face images
TRAINER_DIR = BASE_DIR / "trainer"        # Model files
ATTENDANCE_DIR = BASE_DIR / "attendance"  # Logs
DATABASE_DIR = BASE_DIR / "database"      # Database
EXPORTS_DIR = BASE_DIR / "exports"        # CSV exports
ASSETS_DIR = BASE_DIR / "assets"          # Icons
```

### ================== DATABASE CONFIGURATION ==================

```python
# Database file location
DATABASE_FILE = DATABASE_DIR / "face_attendance.db"

# Trained model file
ENCODINGS_FILE = TRAINER_DIR / "encodings.pkl"

# CSV attendance export
ATTENDANCE_CSV = EXPORTS_DIR / "attendance.csv"
```

**When to change**: Only if you want database in different location

### ================== FACE RECOGNITION ==================

```python
# Number of face images to capture per user
IMAGES_PER_PERSON = 20
# Recommended: 15-30 (more = better accuracy but slower training)

# Face detection model
FACE_DETECTION_MODEL = "hog"  # 'hog' (fast) or 'cnn' (accurate)
# HOG: ~2-3 seconds per image, CPU-based
# CNN: ~15-30 seconds per image, GPU accelerated, more accurate

# Tolerance for face matching (0-1)
FACE_TOLERANCE = 0.6
# Lower values = stricter matching (fewer false positives)
# Higher values = looser matching (more recognition)
# Typical range: 0.5-0.7

# Minimum face size for detection
MIN_FACE_SIZE = 50  # pixels
# Smaller = detects smaller faces (slower)
# Larger = only large faces (faster)
```

**Recommendations**:
- For **office use**: FACE_TOLERANCE = 0.5-0.55 (strict)
- For **school use**: FACE_TOLERANCE = 0.6 (standard)
- For **events**: FACE_TOLERANCE = 0.65-0.7 (loose)

### ================== CAMERA CONFIGURATION ==================

```python
# Camera FPS (Frames Per Second)
CAMERA_FPS = 30
# 15-30 is typical for webcams
# Higher = smoother but more CPU usage

# Camera resolution
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
# 640x480: Fast, lower quality
# 1280x720: Balanced
# 1920x1080: Slower, better quality

# Delay between captures (milliseconds)
CAPTURE_DELAY = 100
# Milliseconds to wait before accepting another frame
# Lower = faster capture, higher = smoother
```

### ================== GUI CONFIGURATION ==================

```python
# Window dimensions
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# Sidebar width
SIDEBAR_WIDTH = 250

# Fonts
MAIN_FONT = ("Segoe UI", 11)
TITLE_FONT = ("Segoe UI", 18, "bold")
BUTTON_FONT = ("Segoe UI", 10)
```

**Note**: Fonts work best on Windows with Segoe UI installed

### ================== COLOR SCHEME ==================

```python
# Dark Mode Colors
BG_COLOR = "#1e1e1e"              # Main background
SIDEBAR_COLOR = "#2d2d2d"          # Sidebar
ACCENT_COLOR = "#0d7377"           # Primary accent (teal)
ACCENT_LIGHT = "#14a085"           # Light accent
TEXT_COLOR = "#ffffff"             # Primary text (white)
TEXT_SECONDARY = "#b0b0b0"         # Secondary text (gray)
DANGER_COLOR = "#e74c3c"           # Danger (red)
SUCCESS_COLOR = "#27ae60"          # Success (green)
WARNING_COLOR = "#f39c12"          # Warning (orange)
BORDER_COLOR = "#404040"           # Borders
```

**Color Customization Examples**:

Light Mode:
```python
BG_COLOR = "#ffffff"
SIDEBAR_COLOR = "#f0f0f0"
TEXT_COLOR = "#000000"
TEXT_SECONDARY = "#666666"
ACCENT_COLOR = "#2196F3"  # Blue
```

High Contrast:
```python
BG_COLOR = "#000000"
TEXT_COLOR = "#ffffff"
ACCENT_COLOR = "#ffff00"
DANGER_COLOR = "#ff0000"
SUCCESS_COLOR = "#00ff00"
```

### ================== AUTHENTICATION ==================

```python
# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin@2024"

# Session timeout (seconds)
SESSION_TIMEOUT = 3600  # 1 hour
```

**IMPORTANT**: Change these before production!

### ================== DETECTION SETTINGS ==================

```python
# Recognition confidence threshold (0-1)
RECOGNITION_CONFIDENCE_THRESHOLD = 0.6

# Minimum match threshold
MIN_MATCH_THRESHOLD = 0.5
```

### ================== LOGGING ==================

```python
# Log file location
LOG_FILE = BASE_DIR / "app.log"

# Logging level
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

**Logging Levels**:
- DEBUG: Detailed information (use for troubleshooting)
- INFO: General information (recommended)
- WARNING: Warning messages only
- ERROR: Errors only

### ================== DISPLAY SETTINGS ==================

```python
# Show FPS counter
SHOW_FPS = True

# Show confidence percentage
SHOW_CONFIDENCE = True

# Rectangle settings
RECTANGLE_THICKNESS = 2  # pixels
RECTANGLE_COLOR_KNOWN = (0, 255, 0)      # Green (BGR)
RECTANGLE_COLOR_UNKNOWN = (0, 0, 255)    # Red (BGR)
TEXT_COLOR_BGR = (255, 255, 255)         # White
```

**Color Format**: OpenCV uses BGR (not RGB)
- (0, 255, 0) = Green
- (0, 0, 255) = Red
- (255, 0, 0) = Blue
- (255, 255, 255) = White
- (0, 0, 0) = Black

### ================== EXPORT SETTINGS ==================

```python
# Export format
EXPORT_FORMAT = "csv"  # Currently CSV only

# Include photos in export
INCLUDE_PHOTOS_IN_EXPORT = False
```

### ================== SOUND SETTINGS ==================

```python
# Enable sound notifications
ENABLE_SOUND_NOTIFICATIONS = True
```

---

## 🎨 Preset Configurations

### Office/Corporate
```python
FACE_TOLERANCE = 0.5
IMAGES_PER_PERSON = 30
CAMERA_FPS = 15
FACE_DETECTION_MODEL = "cnn"  # More accurate
ACCENT_COLOR = "#1e90ff"  # Professional blue
```

### School/Educational
```python
FACE_TOLERANCE = 0.6
IMAGES_PER_PERSON = 20
CAMERA_FPS = 30
FACE_DETECTION_MODEL = "hog"  # Faster
ACCENT_COLOR = "#0d7377"  # Teal
```

### Event/Venue
```python
FACE_TOLERANCE = 0.7  # Looser
IMAGES_PER_PERSON = 15  # Fewer images
CAMERA_FPS = 20
FACE_DETECTION_MODEL = "hog"  # Speed
ACCENT_COLOR = "#e74c3c"  # Red
```

### Development/Testing
```python
FACE_DETECTION_MODEL = "hog"  # Fast
LOG_LEVEL = "DEBUG"  # Detailed logging
SHOW_FPS = True
SHOW_CONFIDENCE = True
```

---

## 🔧 Performance Tuning

### For Faster Recognition
```python
FACE_DETECTION_MODEL = "hog"
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
RESIZE_FACTOR = 0.25
```

### For Better Accuracy
```python
FACE_DETECTION_MODEL = "cnn"
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
IMAGES_PER_PERSON = 30
FACE_TOLERANCE = 0.5
```

### For Low-End Hardware
```python
IMAGES_PER_PERSON = 10
CAMERA_FPS = 15
CAMERA_WIDTH = 480
CAMERA_HEIGHT = 360
RESIZE_FACTOR = 0.5
```

---

## 🔒 Security Configuration

```python
# Change admin password (IMPORTANT!)
ADMIN_PASSWORD = "YourSecurePassword123!"  # Use strong password

# Enable detailed logging for audit
LOG_LEVEL = "DEBUG"

# Change session timeout
SESSION_TIMEOUT = 1800  # 30 minutes
```

---

## 📱 Mobile Camera Setup

If using USB camera instead of built-in:

```python
# Try different camera indices
# In modules/attendance.py, change:
cap = cv2.VideoCapture(1)  # Try 0, 1, 2, etc.

# Adjust resolution for USB camera
CAMERA_WIDTH = 320   # Lower for better performance
CAMERA_HEIGHT = 240
```

---

## 🌐 Network Setup

For multiple computers sharing database:

```python
# Use network path
DATABASE_FILE = Path("//network/shared/face_attendance.db")

# Or use PostgreSQL instead of SQLite
# (Requires modification to database.py)
```

---

## 🎯 Optimization Checklist

- [ ] Set FACE_TOLERANCE for your use case
- [ ] Configure camera resolution for your setup
- [ ] Choose appropriate FACE_DETECTION_MODEL
- [ ] Set IMAGES_PER_PERSON for accuracy vs. speed
- [ ] Adjust GUI colors to match your brand
- [ ] Change admin credentials
- [ ] Set appropriate LOG_LEVEL
- [ ] Configure SESSION_TIMEOUT
- [ ] Test with actual users/lighting

---

## 🐛 Troubleshooting Configuration

### Issue: Recognition too strict
**Solution**: Increase FACE_TOLERANCE to 0.65-0.7

### Issue: Recognition too loose
**Solution**: Decrease FACE_TOLERANCE to 0.5

### Issue: Slow recognition
**Solution**: 
- Use HOG instead of CNN
- Lower CAMERA_WIDTH and CAMERA_HEIGHT
- Increase CAPTURE_DELAY

### Issue: Slow training
**Solution**:
- Reduce IMAGES_PER_PERSON
- Use HOG model
- Close other applications

### Issue: Low accuracy
**Solution**:
- Increase IMAGES_PER_PERSON
- Improve lighting
- Lower FACE_TOLERANCE
- Use CNN model

---

## 📝 Configuration Backup

Always backup your config before making changes:

```bash
# Linux/macOS
cp config.py config.py.backup

# Windows
copy config.py config.py.backup
```

---

## ✅ Verification

After changing configuration:

1. **Start the app**: `python main.py`
2. **Check for errors**: Look at console output
3. **Review logs**: Check app.log
4. **Test recognition**: Try marking attendance
5. **Verify settings**: Check if changes took effect

---

## 🆘 Need Help?

- Check README.md for general usage
- See QUICK_REFERENCE.md for common tasks
- Review app.log for error messages
- Check API_DOCUMENTATION.md for technical details

---

**Version**: 1.0  
**Last Updated**: 2024  
**Recommended Settings**: See Preset Configurations section
