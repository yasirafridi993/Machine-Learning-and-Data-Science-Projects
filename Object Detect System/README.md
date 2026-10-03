# AI Vision Detector

A complete, professional AI object detection desktop application built with
**Python**, **Flet** (UI), **YOLOv8 / Ultralytics** (detection), **OpenCV**,
**PyTorch**, and **SQLite**. Detect objects in real time from your webcam, in
still images, or in video files — with a modern, responsive dashboard that
adapts from a wide desktop window down to a narrow mobile-sized one.

![Dashboard screenshot placeholder](assets/images/screenshot-dashboard.png)
![Live detection screenshot placeholder](assets/images/screenshot-live.png)

## Features

- **Live webcam detection** — start/stop, bounding boxes, confidence, live
  FPS counter, object count, and one-click snapshot saving.
- **Image detection** — pick a photo, run YOLOv8, view the annotated result
  and a per-label confidence breakdown, save to history.
- **Video detection** — pick a video, process it frame-by-frame with a live
  progress bar, and save an annotated output video plus summary statistics.
- **Detection history** — every saved session is logged to SQLite; filter by
  source type, inspect per-object detail, delete individual sessions, or
  clear everything.
- **Lightweight analytics** — dashboard cards, a "most detected objects" bar
  chart, and a detections-by-source pie chart.
- **Automatic GPU/CPU selection** — uses CUDA automatically when available,
  otherwise falls back to CPU.
- **Responsive UI** — a sidebar navigation rail on wide/desktop windows that
  becomes a bottom navigation bar on narrow/mobile-sized windows, with
  light and dark themes.
- **Graceful error handling** — missing camera, missing/invalid model
  weights, unreadable images/videos, and database errors all show a
  friendly in-app message instead of crashing.

## Requirements

- Python 3.10–3.14
- A webcam (optional — only needed for the Live Detection screen)
- ~250 MB free disk space for the default `yolov8n.pt` weights and
  dependencies
- Internet access the **first** time you run the app, so Ultralytics can
  download the default pretrained weights (unless you supply your own
  weights file, see below)

## Installation

```bash
# 1. Clone or copy this project, then move into it
cd object_detection_system

# 2. Create a virtual environment with an installed supported Python version
py -3.14 -m venv .venv          # Windows; use an installed version from 3.10 to 3.14
# macOS/Linux: python3.14 -m venv .venv

# 3. Install dependencies
.venv\Scripts\python.exe -m pip install -r requirements.txt  # Windows
# macOS/Linux: .venv/bin/python -m pip install -r requirements.txt

# 4. (Optional) copy the example environment file and adjust settings
cp .env.example .env
```

### Using your own trained model

Drop a custom-trained `.pt` file into `models/` and set `YOLO_MODEL` in
`.env` (or as an environment variable) to its filename. If loading fails for
any reason, the app automatically falls back to the pretrained `yolov8n.pt`.

## How to run

```bash
python main.py
```

The app opens as a desktop window. Resize it narrower than ~760px wide to
see the layout switch to the compact mobile-style navigation.

### Running as a mobile app

Flet can package this UI for Android via `flet build apk`. Note that the
**Live Detection** screen currently reads the webcam with OpenCV's
`cv2.VideoCapture`, which works for the desktop app but is not the right API
for a compiled Android build's camera. To ship live detection on Android,
replace the capture loop in `camera_service.py` with a native camera source
(for example, streaming frames from Flet's camera/media APIs or a platform
channel) while keeping `detection_service.py` unchanged — the detection
logic itself is already UI- and capture-source-agnostic.

## Usage

1. **Dashboard** — see totals, top detected objects, and recent activity.
   Use the quick-action buttons to jump straight into a detection mode.
2. **Live** — click "Start detection" to begin streaming annotated webcam
   frames; click "Save snapshot" at any time to log the current frame and
   detections to history; "Stop detection" ends the session and logs a
   summary.
3. **Image** — choose an image, click "Run detection", review the results,
   then "Save result" to keep the annotated image and log it to history.
4. **Video** — choose a video, click "Run detection", watch the progress
   bar, then review the summary statistics once processing finishes. The
   annotated video is saved automatically to `outputs/videos/`.
5. **History** — browse, filter, inspect, or delete past detection
   sessions.

## Project structure

```
object_detection_system/
│
├── main.py                  # App startup, theme, and responsive navigation
├── database.py               # SQLite operations (parameterized queries)
├── models.py                  # Plain data models (DetectedObject, DetectionResult)
├── detection_service.py      # YOLOv8 model loading and inference
├── camera_service.py         # Webcam handling (OpenCV VideoCapture)
├── analytics_service.py      # Lightweight statistics built on the database
├── config.py                  # Paths, thresholds, theme, and UI constants
├── requirements.txt
│
├── ui/
│   ├── dashboard.py           # Overview cards + charts + recent activity
│   ├── live_detection.py      # Real-time webcam detection screen
│   ├── image_detection.py     # Single-image detection screen
│   ├── video_detection.py     # Video file detection screen
│   ├── results.py             # Detection history / results screen
│   └── components.py          # Shared widgets (stat cards, empty/error states, dialogs)
│
├── models/                    # Place custom .pt weight files here
├── outputs/
│   ├── screenshots/           # Saved annotated images/snapshots
│   └── videos/                # Saved annotated output videos
├── data/                      # SQLite database file lives here
├── assets/
│   ├── icons/
│   └── images/
│
├── tests/
│   └── test_database.py       # Unit tests for the database layer
│
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

## Supported detection modes

| Mode   | Input             | Output                                          |
|--------|-------------------|--------------------------------------------------|
| Live   | Webcam stream     | Annotated live preview, optional saved snapshot   |
| Image  | .jpg/.jpeg/.png/.bmp/.webp | Annotated image + detection breakdown     |
| Video  | .mp4/.avi/.mov/.mkv/.webm  | Annotated video + summary statistics      |

## Running tests

```bash
pip install pytest
pytest tests/
```

`tests/test_database.py` exercises the SQLite layer directly (save, fetch,
filter, delete, clear, and aggregate statistics) and does not require
Flet, OpenCV, or PyTorch to be installed.

## Troubleshooting

- **"Could not access the camera"** — check that no other application is
  using the webcam, that camera permission is granted to this app/terminal,
  and that `CAMERA_INDEX` in `.env` matches your device.
- **"Required AI libraries are not installed"** — run
  `pip install -r requirements.txt` inside your active virtual environment.
- **Model download fails on first run** — Ultralytics needs internet access
  once to fetch `yolov8n.pt`; alternatively, supply your own weights file in
  `models/` (see "Using your own trained model" above).
- **Slow detection on CPU** — this is expected without a CUDA-capable GPU;
  try a smaller model (`yolov8n.pt`) or lower `LIVE_DETECTION_TARGET_FPS`.

## License

Released under the MIT License — see [LICENSE](LICENSE).
