# 🎓 AI Face Recognition Attendance System

A professional AI-powered attendance management system built using **Python**, **OpenCV**, and **Face Recognition**. The system automatically recognizes registered users through a webcam and marks their attendance in real-time.

---

## 📌 Features

- 👤 Face Registration System
- 📷 Capture Multiple Face Images
- 🧠 Face Encoding and Training
- 🎥 Real-Time Face Detection and Recognition
- ✅ Automatic Attendance Marking
- 🗂 SQLite Database Integration
- 📄 CSV Attendance Export
- 🖥 User-Friendly GUI using Tkinter
- 🔐 Admin Authentication System
- 📊 Attendance Analytics and Statistics
- 🔍 Search Attendance Records
- 🌙 Dark Mode Support
- 🔔 Notifications and Sound Alerts
- ⚡ Optimized for Real-Time Performance

---

## 🛠 Technologies Used

- Python
- OpenCV
- face_recognition
- NumPy
- Pandas
- Tkinter
- SQLite
- Pillow (PIL)
- Pickle
- Datetime

---

## 📂 Project Structure

```text
FaceAttendanceSystem/
│
├── dataset/           # Registered user images
├── trainer/           # Trained face encodings
├── attendance/        # Attendance records
├── database/          # SQLite database files
├── exports/           # Exported CSV reports
├── assets/            # Icons and UI resources
├── gui/               # GUI components
├── utils/             # Utility functions
├── main.py            # Main application
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment:

**Windows**

```bash
venv\Scripts\activate
```

**Mac/Linux**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

### Register a New User

- Launch the application.
- Click on **Register User**.
- Enter the user's details.
- Capture face images using the webcam.

### Train the Model

- Click on **Train Model**.
- The system will generate face encodings from registered images.

### Start Attendance

- Click on **Start Attendance**.
- The webcam will open.
- Recognized users will automatically be marked as **Present**.

### Export Attendance

- Click **Export CSV** to save attendance reports.

---

## 🗄 Database Schema

### Users Table

| Field | Description |
|---------|-------------|
| id | Primary Key |
| name | User Name |
| student_id | Student/Employee ID |
| image_path | Face Image Path |
| created_at | Registration Date |

### Attendance Table

| Field | Description |
|---------|-------------|
| id | Primary Key |
| student_id | Student/Employee ID |
| name | User Name |
| date | Attendance Date |
| time | Attendance Time |
| status | Present/Absent |

---

## 📸 Screenshots

Add screenshots of:

- Login Screen
- Registration Module
- Training Module
- Real-Time Recognition
- Attendance Dashboard

Example:

```
screenshots/login.png
screenshots/dashboard.png
screenshots/attendance.png
```

---

## 🚀 Future Improvements

- Anti-Spoofing Detection
- QR Code + Face Hybrid Attendance
- Email Attendance Reports
- Cloud Database Integration
- Mobile Application Support
- Face Mask Recognition
- Multi-Camera Support

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome.

Feel free to fork this repository and submit pull requests.

---

## 📜 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Yasir Afridi**

Computer Science Student | Python Developer | AI Enthusiast

GitHub: https://github.com/your-username

LinkedIn: Add Your LinkedIn Profile

---

### ⭐ If you found this project useful, please consider giving it a star on GitHub!
