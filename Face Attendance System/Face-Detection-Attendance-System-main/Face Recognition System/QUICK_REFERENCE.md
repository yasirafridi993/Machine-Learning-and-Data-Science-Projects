# Quick Reference

## Run

```powershell
python main.py
```

## Install

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Main Workflow

```text
Register User -> Capture Faces -> Train Model -> Start Attendance -> Export Data
```

## Important Keys

- `SPACE`: capture a face image during registration.
- `ESC`: close the OpenCV camera window.

## Important Paths

```text
dataset/                 Captured face images
trainer/                 Trained model files
database/face_attendance.db
exports/                 CSV exports
app.log                  Runtime logs
```

## Main Files

```text
main.py                  App entry point
config.py                Project settings
gui/dashboard.py         Tkinter interface
modules/registration.py  Face capture
modules/trainer.py       Model training
modules/attendance.py    Recognition and attendance
modules/export.py        CSV exports
utils/database.py        SQLite operations
```

## Sanity Checks

```powershell
python -m compileall .
python -c "from gui.dashboard import FaceAttendanceDashboard; print('gui ok')"
python -c "from utils.database import db_manager; print(db_manager.get_attendance_statistics())"
```
