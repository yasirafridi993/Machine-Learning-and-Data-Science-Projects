"""
ui/live_detection.py
Real-time webcam detection. Runs capture + inference on a background thread
so the UI stays responsive, and streams annotated frames to a ft.Image via
base64. Shows FPS, live object count, and a rolling list of currently
detected labels with confidence.

See camera_service.py for a note on adapting this for a packaged Android
build, where OpenCV VideoCapture is not the right camera API.
"""
import base64
import logging
import threading
import time
from typing import Optional

import cv2
import flet as ft

import config
from camera_service import CameraService, CameraError
from database import DatabaseManager
from detection_service import DetectionService, DetectionServiceError
from models import DetectionResult
from ui.components import empty_state, error_banner, confidence_chip, section_title

logger = logging.getLogger(__name__)


class LiveDetectionView(ft.Column):
    def __init__(self, page: ft.Page, detection_service: Optional[DetectionService], db: DatabaseManager):
        super().__init__(scroll=ft.ScrollMode.AUTO, spacing=16, expand=True)
        self.page = page
        self.detection_service = detection_service
        self.db = db
        self.camera = CameraService()

        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._is_running = False
        self._last_frame = None
        self._last_objects = []
        self._session_object_counter: dict = {}
        self._session_total_frames = 0

        self.video_image = ft.Image(fit=ft.ImageFit.CONTAIN, border_radius=12, visible=False)
        self.status_area = ft.Container(
            content=empty_state(
                ft.icons.VIDEOCAM_OUTLINED, "Camera is off",
                "Press \"Start detection\" to begin live object detection.",
            ),
            alignment=ft.alignment.center,
        )
        self.fps_text = ft.Text("FPS: --", size=12, color=ft.colors.ON_SURFACE_VARIANT)
        self.count_text = ft.Text("Objects: 0", size=12, color=ft.colors.ON_SURFACE_VARIANT)
        self.device_text = ft.Text(
            f"Device: {detection_service.device_label}" if detection_service and detection_service.is_ready else "Device: unavailable",
            size=12, color=ft.colors.ON_SURFACE_VARIANT,
        )
        self.start_stop_button = ft.FilledButton(
            "Start detection", icon=ft.icons.PLAY_ARROW_ROUNDED, on_click=self._toggle,
        )
        self.snapshot_button = ft.OutlinedButton(
            "Save snapshot", icon=ft.icons.CAMERA_ROUNDED, on_click=self._save_snapshot, disabled=True,
        )
        self.live_objects_column = ft.Column(spacing=6)

        self.controls = [
            section_title("Live Detection", "Real-time webcam object detection"),
            ft.Row(wrap=True, spacing=10, controls=[self.start_stop_button, self.snapshot_button]),
            self._video_card(),
            self._info_card(),
        ]

    # -- Layout ---------------------------------------------------------------

    def _video_card(self) -> ft.Container:
        return ft.Container(
            padding=16, border_radius=16, bgcolor=ft.colors.SURFACE_VARIANT, height=420,
            content=ft.Stack(
                expand=True,
                controls=[
                    ft.Container(content=self.status_area, alignment=ft.alignment.center, expand=True),
                    self.video_image,
                ],
            ),
        )

    def _info_card(self) -> ft.Container:
        return ft.Container(
            padding=16, border_radius=16, bgcolor=ft.colors.SURFACE_VARIANT,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(spacing=20, controls=[self.fps_text, self.count_text, self.device_text]),
                    ft.Divider(height=1),
                    section_title("Currently visible objects"),
                    self.live_objects_column,
                ],
            ),
        )

    # -- Start / stop ---------------------------------------------------------------

    def _toggle(self, e) -> None:
        if self._is_running:
            self._stop()
        else:
            self._start()

    def _start(self) -> None:
        if self.detection_service is None or not self.detection_service.is_ready:
            self._show_error("The detection model isn't ready. Check the startup error and restart the app.")
            return
        try:
            self.camera.open()
        except CameraError as err:
            self._show_error(str(err))
            return

        self._stop_event.clear()
        self._session_object_counter = {}
        self._session_total_frames = 0
        self._is_running = True
        self.start_stop_button.text = "Stop detection"
        self.start_stop_button.icon = ft.icons.STOP_ROUNDED
        self.snapshot_button.disabled = False
        self.status_area.visible = False
        self.video_image.visible = True
        self.update()

        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def _stop(self) -> None:
        self._stop_event.set()
        self._is_running = False
        if self._thread is not None:
            self._thread.join(timeout=2)
        self.camera.close()

        # Log a summary session for the run, if anything was detected.
        if self._session_object_counter:
            try:
                from models import DetectedObject
                objects = [
                    DetectedObject(label=label, confidence=0.0, bbox=(0, 0, 0, 0))
                    for label, count in self._session_object_counter.items()
                    for _ in range(count)
                ]
                result = DetectionResult(
                    source_type="webcam",
                    source_name=f"Live session ({self._session_total_frames} frames)",
                    objects=objects,
                )
                self.db.save_detection_result(result)
            except Exception:
                logger.exception("Failed to log live detection session summary")

        self.start_stop_button.text = "Start detection"
        self.start_stop_button.icon = ft.icons.PLAY_ARROW_ROUNDED
        self.snapshot_button.disabled = True
        self.video_image.visible = False
        self.status_area.visible = True
        self.status_area.content = empty_state(
            ft.icons.VIDEOCAM_OUTLINED, "Camera stopped", "Press \"Start detection\" to begin again.",
        )
        self.fps_text.value = "FPS: --"
        self.count_text.value = "Objects: 0"
        self.live_objects_column.controls = []
        self.update()

    def _show_error(self, message: str) -> None:
        self.status_area.visible = True
        self.status_area.content = error_banner(message)
        self.video_image.visible = False
        self.update()

    # -- Capture loop (background thread) ---------------------------------------------------------------

    def _capture_loop(self) -> None:
        frame_interval = 1.0 / max(config.LIVE_DETECTION_TARGET_FPS, 1)
        fps_smoothed = 0.0

        while not self._stop_event.is_set():
            loop_start = time.perf_counter()
            try:
                frame = self.camera.read()
                annotated, objects, _ = self.detection_service.detect_frame(frame)
            except (CameraError, DetectionServiceError) as err:
                self._stop_event.set()
                self._is_running = False
                self.camera.close()
                self._show_error(str(err))
                self.start_stop_button.text = "Start detection"
                self.start_stop_button.icon = ft.icons.PLAY_ARROW_ROUNDED
                self.snapshot_button.disabled = True
                break
            except Exception as err:
                logger.exception("Unexpected error in live detection loop")
                self._show_error(f"Unexpected error: {err}")
                break

            self._last_frame = annotated
            self._last_objects = objects
            self._session_total_frames += 1
            for obj in objects:
                self._session_object_counter[obj.label] = self._session_object_counter.get(obj.label, 0) + 1

            elapsed = time.perf_counter() - loop_start
            fps = 1.0 / elapsed if elapsed > 0 else 0.0
            fps_smoothed = fps if fps_smoothed == 0 else (fps_smoothed * 0.8 + fps * 0.2)

            ok, buf = cv2.imencode(".jpg", annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            if ok:
                b64 = base64.b64encode(buf.tobytes()).decode("ascii")
                self.video_image.src_base64 = b64

            self.fps_text.value = f"FPS: {fps_smoothed:.1f}"
            self.count_text.value = f"Objects: {len(objects)}"
            self._render_live_objects(objects)

            try:
                self.update()
            except Exception:
                # Page may have navigated away / closed; stop the loop quietly.
                break

            sleep_time = frame_interval - (time.perf_counter() - loop_start)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _render_live_objects(self, objects) -> None:
        if not objects:
            self.live_objects_column.controls = [
                ft.Text("No objects currently visible.", size=12, color=ft.colors.ON_SURFACE_VARIANT)
            ]
            return
        best_by_label = {}
        for o in objects:
            if o.label not in best_by_label or o.confidence > best_by_label[o.label]:
                best_by_label[o.label] = o.confidence
        rows = []
        for label, conf in sorted(best_by_label.items(), key=lambda x: -x[1]):
            rows.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[ft.Text(label, size=13), confidence_chip(conf)],
                )
            )
        self.live_objects_column.controls = rows

    def _save_snapshot(self, e) -> None:
        if self._last_frame is None:
            return
        try:
            config.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
            filename = f"live_{int(time.time())}.png"
            out_path = str(config.SCREENSHOTS_DIR / filename)
            cv2.imwrite(out_path, self._last_frame)

            result = DetectionResult(
                source_type="webcam",
                source_name=filename,
                objects=self._last_objects,
                output_path=out_path,
            )
            self.db.save_detection_result(result)
            snack = ft.SnackBar(content=ft.Text("Snapshot saved to history."), open=True)
            self.page.snack_bar = snack
            self.page.update()
        except Exception as err:
            logger.exception("Failed to save live snapshot")
            snack = ft.SnackBar(content=ft.Text(f"Could not save snapshot: {err}"), open=True)
            self.page.snack_bar = snack
            self.page.update()

    def on_view_leave(self) -> None:
        """Called by main.py when the user navigates away, so the camera and
        background thread never keep running unattended."""
        if self._is_running:
            self._stop()
