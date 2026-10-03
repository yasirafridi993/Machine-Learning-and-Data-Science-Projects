"""
ui/video_detection.py
Pick a video file, run YOLO detection frame-by-frame on a background thread
(so the UI/progress bar stays responsive), write an annotated output video,
show detection statistics, and log the session to the database.
"""
import logging
import threading
from pathlib import Path
from typing import Optional

import flet as ft

import config
from database import DatabaseManager
from detection_service import DetectionService, DetectionServiceError
from models import DetectionResult
from ui.components import empty_state, error_banner, loading_indicator, section_title

logger = logging.getLogger(__name__)


class VideoDetectionView(ft.Column):
    def __init__(self, page: ft.Page, detection_service: Optional[DetectionService], db: DatabaseManager):
        super().__init__(scroll=ft.ScrollMode.AUTO, spacing=16, expand=True)
        self.page = page
        self.detection_service = detection_service
        self.db = db

        self._picked_path: Optional[str] = None
        self._output_path: Optional[str] = None
        self._processing = False

        self.file_picker = ft.FilePicker(on_result=self._on_file_picked)
        page.overlay.append(self.file_picker)

        self.selected_file_text = ft.Text("No video selected.", size=13, color=ft.colors.ON_SURFACE_VARIANT)
        self.progress_bar = ft.ProgressBar(value=0, visible=False, color=config.COLOR_PRIMARY)
        self.progress_label = ft.Text("", size=12, color=ft.colors.ON_SURFACE_VARIANT, visible=False)
        self.run_button = ft.FilledButton(
            "Run detection", icon=ft.icons.PLAY_ARROW_ROUNDED, on_click=self._run_detection, disabled=True,
        )
        self.status_area = ft.Container(
            content=empty_state(
                ft.icons.MOVIE_CREATION_OUTLINED, "No video processed yet",
                "Choose a video file and run detection to see results here.",
            )
        )

        self.controls = [
            section_title("Video Detection", "Run YOLO object detection on a video file"),
            ft.Row(
                wrap=True, spacing=10,
                controls=[
                    ft.FilledTonalButton(
                        "Choose video", icon=ft.icons.UPLOAD_FILE_ROUNDED,
                        on_click=lambda e: self.file_picker.pick_files(
                            allow_multiple=False, file_type=ft.FilePickerFileType.VIDEO,
                        ),
                    ),
                    self.run_button,
                ],
            ),
            self.selected_file_text,
            ft.Column(spacing=6, controls=[self.progress_bar, self.progress_label]),
            self.status_area,
        ]

    # -- Events ---------------------------------------------------------------

    def _on_file_picked(self, e: ft.FilePickerResultEvent) -> None:
        if not e.files:
            return
        self._picked_path = e.files[0].path
        self.selected_file_text.value = f"Selected: {Path(self._picked_path).name}"
        self.run_button.disabled = False
        self.status_area.content = empty_state(
            ft.icons.MOVIE_CREATION_OUTLINED, "Ready to process",
            "Click \"Run detection\" to analyze this video.",
        )
        self.update()

    def _run_detection(self, e) -> None:
        if self._processing:
            return
        if not self._picked_path:
            self._show_error("Choose a video first.")
            return
        if self.detection_service is None or not self.detection_service.is_ready:
            self._show_error("The detection model isn't ready. Check the startup error and restart the app.")
            return

        self._processing = True
        self.run_button.disabled = True
        self.progress_bar.visible = True
        self.progress_bar.value = 0
        self.progress_label.visible = True
        self.progress_label.value = "Starting..."
        self.status_area.content = loading_indicator("Processing video...")
        self.update()

        thread = threading.Thread(target=self._process_video, daemon=True)
        thread.start()

    def _process_video(self) -> None:
        input_path = Path(self._picked_path)
        config.VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
        output_path = str(config.VIDEOS_DIR / f"{input_path.stem}_detected.mp4")

        def on_progress(fraction: float) -> None:
            self.progress_bar.value = fraction
            self.progress_label.value = f"Processing... {fraction * 100:.0f}%"
            try:
                self.update()
            except Exception:
                pass

        try:
            out_path, objects, total_time_ms = self.detection_service.detect_video_file(
                str(input_path), output_path, progress_callback=on_progress
            )
        except DetectionServiceError as err:
            self._finish_with_error(str(err))
            return
        except Exception as err:
            logger.exception("Unexpected error during video detection")
            self._finish_with_error(f"Unexpected error: {err}")
            return

        result = DetectionResult(
            source_type="video",
            source_name=input_path.name,
            objects=objects,
            output_path=out_path,
            processing_time_ms=total_time_ms,
        )
        try:
            self.db.save_detection_result(result)
        except Exception:
            logger.exception("Failed to save video detection result to database")

        self._output_path = out_path
        self._render_success(result)

    def _render_success(self, result: DetectionResult) -> None:
        self._processing = False
        self.progress_bar.visible = False
        self.progress_label.visible = False
        self.run_button.disabled = False

        counts = result.object_counts_by_label
        count_rows = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[ft.Text(label, size=13), ft.Text(str(c), size=13, weight=ft.FontWeight.W_600)],
            )
            for label, c in sorted(counts.items(), key=lambda x: -x[1])
        ] or [ft.Text("No objects were detected in this video.", size=13, color=ft.colors.ON_SURFACE_VARIANT)]

        self.status_area.content = ft.Column(
            spacing=14,
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.icons.CHECK_CIRCLE_ROUNDED, color=config.COLOR_ACCENT),
                        ft.Text("Processing complete", size=15, weight=ft.FontWeight.W_600),
                    ]
                ),
                ft.Row(
                    wrap=True, spacing=24,
                    controls=[
                        _stat_pair("Total objects", str(result.object_count)),
                        _stat_pair("Avg. confidence", f"{result.average_confidence * 100:.0f}%"),
                        _stat_pair("Processing time", f"{result.processing_time_ms / 1000:.1f}s"),
                    ],
                ),
                ft.Divider(height=1),
                section_title("Object counts"),
                ft.Column(spacing=6, controls=count_rows),
                ft.Text(
                    f"Saved output video to: {self._output_path}",
                    size=11, color=ft.colors.ON_SURFACE_VARIANT, selectable=True,
                ),
            ],
        )
        try:
            self.update()
        except Exception:
            pass

    def _finish_with_error(self, message: str) -> None:
        self._processing = False
        self.progress_bar.visible = False
        self.progress_label.visible = False
        self.run_button.disabled = False
        self._show_error(message)

    def _show_error(self, message: str) -> None:
        self.status_area.content = error_banner(message)
        try:
            self.update()
        except Exception:
            pass


def _stat_pair(label: str, value: str) -> ft.Column:
    return ft.Column(
        spacing=0,
        controls=[
            ft.Text(value, size=18, weight=ft.FontWeight.BOLD),
            ft.Text(label, size=11, color=ft.colors.ON_SURFACE_VARIANT),
        ],
    )
