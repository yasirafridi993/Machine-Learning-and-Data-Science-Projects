# API Documentation

## `modules.registration.FaceRegistration`

- `register_user(name, student_id, email=None, phone=None)`: validates input, captures face images, and stores the user in SQLite.
- `get_dataset_stats()`: returns user/image counts for the dataset.
- `verify_user_images(student_id)`: counts images for one user.
- `delete_user_images(student_id)`: removes captured images for one user.
- `re_register_user(student_id, name)`: replaces a user's captured images.

## `modules.trainer.FaceTrainer`

- `train_model(progress_callback=None)`: trains the best available recognizer.
- `load_trained_model()`: loads model and label metadata.
- `is_model_trained()`: checks whether model files exist.
- `get_model_stats()`: returns model type, user count, image count, and trained time.
- `get_distance_threshold()`: returns the active model threshold.
- `delete_trained_model()`: removes trained model files.

Model types:

- `opencv_lbph`: used when `opencv-contrib-python` provides `cv2.face`.
- `simple_lbp`: built-in fallback using LBP histograms and nearest-neighbor distance.

## `modules.attendance.AttendanceSystem`

- `start_recognition(confidence_threshold=None, process_callback=None)`: opens webcam recognition and marks attendance.
- `stop_recognition()`: requests recognition stop.
- `get_today_stats()`: returns today's attendance summary.
- `get_session_stats()`: returns current recognition session counts.

## `modules.export.CSVExporter`

- `export_attendance(start_date=None, end_date=None, filename=None)`: exports attendance records.
- `export_users(filename=None)`: exports registered users.
- `export_attendance_summary(start_date=None, end_date=None, filename=None)`: exports per-user summary.
- `get_export_files()`: lists CSV exports.

## `utils.database.DatabaseManager`

- `add_user(...)`, `get_user_by_student_id(...)`, `get_all_users()`, `update_user(...)`, `delete_user(...)`, `user_exists(...)`.
- `mark_attendance(...)`, `get_today_attendance()`, `get_attendance_by_date_range(...)`, `get_attendance_by_student(...)`, `get_attendance_statistics(...)`.
- `clear_all_data()`, `get_database_size()`, `vacuum_database()`.
