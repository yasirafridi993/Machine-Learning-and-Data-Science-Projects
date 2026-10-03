# Project Index

## Start Here

- `README.md`: overview, structure, workflow.
- `INSTALLATION_GUIDE.md`: setup and troubleshooting.
- `QUICK_REFERENCE.md`: commands and key files.
- `CONFIGURATION_GUIDE.md`: configurable settings.

## Application Code

- `main.py`: starts the Tkinter app.
- `config.py`: paths, camera settings, thresholds, colors.
- `gui/dashboard.py`: pages for registration, training, attendance, users, analytics, export, and settings.
- `gui/theme.py`: shared Tkinter styles.

## Core Modules

- `modules/registration.py`: validates users and captures face images.
- `modules/trainer.py`: trains OpenCV LBPH if available, otherwise trains the fallback LBP histogram model.
- `modules/attendance.py`: performs real-time webcam recognition and marks attendance.
- `modules/export.py`: exports users and attendance records to CSV.

## Utilities

- `utils/database.py`: SQLite schema and queries.
- `utils/utils.py`: logging, validation, image, camera, and formatting helpers.
- `utils/constants.py`: statuses, messages, formats, and shared constants.

## Generated Data

- `dataset/`: captured face images grouped by student ID.
- `trainer/`: trained model and label map.
- `database/face_attendance.db`: local SQLite database.
- `exports/`: CSV exports.
- `app.log`: runtime log file.
