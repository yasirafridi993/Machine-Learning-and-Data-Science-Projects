# Build Summary

This project is a complete local desktop face attendance system.

## Implemented

- Tkinter desktop dashboard.
- SQLite database creation and access layer.
- User registration and webcam face capture.
- Model training with OpenCV LBPH when `cv2.face` is available.
- Built-in LBP histogram fallback when OpenCV contrib is unavailable.
- Real-time webcam recognition and attendance marking.
- Attendance duplicate prevention through the database unique key.
- User listing, attendance listing, analytics, settings, and CSV exports.
- Clean `README.md`, installation guide, quick reference, and `.gitignore`.

## Verification

The following checks pass:

```powershell
python -m compileall .
python -c "from gui.dashboard import FaceAttendanceDashboard; print('gui-import-ok')"
python -c "from utils.database import db_manager; print(db_manager.get_attendance_statistics())"
```

Current environment note: OpenCV is installed, but `cv2.face` is not available, so this machine will use the fallback recognizer unless `opencv-contrib-python` is installed.

## Run

```powershell
python main.py
```
