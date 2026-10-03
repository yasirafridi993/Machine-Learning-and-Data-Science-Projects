# Face Recognition Attendance System

A desktop attendance system built with Python, Tkinter, OpenCV, SQLite, and CSV export. It captures face images from a webcam, trains a face recognizer, and marks daily attendance when a registered face is recognized.

## Features

- User registration with name, student ID, email, phone, and face image capture.
- Webcam-based face dataset collection.
- OpenCV LBPH model training when `cv2.face` is available.
- Built-in LBP histogram fallback when OpenCV contrib is not installed.
- Real-time face recognition and automatic attendance marking.
- Duplicate attendance prevention for the same student on the same day.
- SQLite database for users and attendance records.
- Dashboard pages for users, attendance records, analytics, settings, and CSV export.
- Local logs in `app.log`.

## Folder Structure

```text
Face Recognition System/
|-- main.py
|-- config.py
|-- requirements.txt
|-- README.md
|-- assets/
|-- attendance/
|-- database/
|   `-- face_attendance.db
|-- dataset/
|   `-- <student_id>/
|       `-- captured face images
|-- exports/
|   `-- generated CSV files
|-- gui/
|   |-- __init__.py
|   |-- dashboard.py
|   `-- theme.py
|-- modules/
|   |-- __init__.py
|   |-- attendance.py
|   |-- export.py
|   |-- registration.py
|   `-- trainer.py
|-- trainer/
|   |-- lbph_model.yml
|   |-- lbp_fallback_model.pkl
|   `-- labels.pkl
`-- utils/
    |-- __init__.py
    |-- constants.py
    |-- database.py
    `-- utils.py
```

## Installation

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

If your webcam is not camera `0`, change `CAMERA_INDEX` in `config.py`.

## Run

```powershell
python main.py
```

## Workflow

1. Open the app with `python main.py`.
2. Go to `Register User`.
3. Fill name and student ID.
4. Click `Register and Capture Faces`.
5. In the camera window, press `SPACE` to capture each face image and `ESC` to stop early.
6. Go to `Train Model` and click `Start Training`.
7. Go to `Start Attendance` and click `Start Recognition`.
8. Press `ESC` in the camera window to stop recognition.
9. View records in `View Attendance` or export CSV files from `Export Data`.

## Important Files

- `config.py`: camera, paths, UI colors, recognition thresholds.
- `modules/registration.py`: face capture and user registration.
- `modules/trainer.py`: OpenCV LBPH training.
- `modules/attendance.py`: webcam recognition and attendance marking.
- `utils/database.py`: SQLite tables and queries.
- `gui/dashboard.py`: Tkinter desktop interface.

## Notes

- Use clear lighting while capturing faces.
- Capture multiple angles for each user for better recognition.
- The trained model is local and saved in `trainer/`.
- Database records are stored locally in `database/face_attendance.db`.
