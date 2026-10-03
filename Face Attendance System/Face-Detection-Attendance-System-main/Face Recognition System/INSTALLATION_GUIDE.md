# Installation Guide

## 1. Create Environment

```powershell
python -m venv venv
.\venv\Scripts\activate
```

## 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

`opencv-contrib-python` enables OpenCV LBPH recognition. If your machine only has `opencv-python`, the app can still train with the built-in LBP histogram fallback.

## 3. Run Application

```powershell
python main.py
```

## 4. Camera Setup

Default camera index is `0`.

If your webcam does not open, edit `config.py`:

```python
CAMERA_INDEX = 1
```

Try `1`, `2`, or another available camera index.

## 5. First Use

1. Open the app.
2. Register a user.
3. Press `SPACE` in the webcam window to capture face images.
4. Train the model.
5. Start attendance recognition.
6. Press `ESC` in the webcam window to stop.

## Troubleshooting

### Camera not found

- Check webcam permissions.
- Close other apps using the camera.
- Change `CAMERA_INDEX` in `config.py`.

### Model not trained

- Register at least one user.
- Capture face images.
- Run `Train Model`.

### Better recognition accuracy

- Capture 15-20 images per person.
- Use good lighting.
- Capture slight left/right/up/down angles.
- Avoid sunglasses, masks, and strong backlight.
