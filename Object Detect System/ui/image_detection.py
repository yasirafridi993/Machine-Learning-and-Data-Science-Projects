"""
ui/image_detection.py
Pick an image from the device, run YOLO detection on it, show the
annotated result plus a breakdown of detected objects, and optionally save
the result (annotated image is stored in outputs/screenshots and the
session is logged to the database).
"""
import base64
import logging
from pathlib import Path
from typing import Optional

import cv2
import flet as ft

import config
from database import DatabaseManager
from detection_service import DetectionService, DetectionServiceError
from models import DetectionResult
from ui.components import confidence_chip, empty_state, error_banner, loading_indicator, section_title

logger = logging.getLogger(__name__)


class ImageDetectionView(ft.Column):
    def __init__(self, page: ft.Page, detection_service: Optional[DetectionService], db: DatabaseManager):
        super().__init__(scroll=ft.ScrollMode.AUTO, spacing=16, expand=True)
        self.page = page
        self.detection_service = detection_service
        self.db = db

        self._picked_path: Optional[str] = None
        self._last_annotated = None
        self._last_objects = []
        self._last_elapsed_ms = 0.0
        self._already_saved = False

        self.file_picker = ft.FilePicker(on_result=self._on_file_picked)
        page.overlay.append(self.file_picker)

        self.preview_image = ft.Image(
            fit=ft.ImageFit.CONTAIN, border_radius=12, visible=False,
        )
        self.status_area = ft.Container(content=empty_state(
            ft.icons.IMAGE_SEARCH_ROUNDED, "No image selected",
            "Choose a photo to run object detection on it.",
        ))
        self.results_column = ft.Column(spacing=8)
        self.save_button = ft.FilledButton(
            "Save result", icon=ft.icons.SAVE_ROUNDED,
            on_click=self._save_result, disabled=True,
        )

        self.controls = [self._header(), self._picker_row(), self._preview_card(), self._results_card()]

    # -- Layout ---------------------------------------------------------------

    def _header(self) -> ft.Column:
        return section_title("Image Detection", "Run YOLO object detection on a photo")

    def _picker_row(self) -> ft.Row:
        return ft.Row(
            wrap=True, spacing=10,
            controls=[
                ft.FilledButton(
                    "Choose image", icon=ft.icons.UPLOAD_FILE_ROUNDED,
                    on_click=lambda e: self.file_picker.pick_files(
                        allow_multiple=False,
                        file_type=ft.FilePickerFileType.IMAGE,
                    ),
                ),
                ft.OutlinedButton(
                    "Run detection", icon=ft.icons.PLAY_ARROW_ROUNDED,
                    on_click=self._run_detection,
                ),
                self.save_button,
            ],
        )

    def _preview_card(self) -> ft.Container:
        return ft.Container(
            padding=16, border_radius=16, bgcolor=ft.colors.SURFACE_VARIANT,
            height=420,
            content=ft.Stack(
                expand=True,
                controls=[
                    ft.Container(content=self.status_area, alignment=ft.alignment.center, expand=True),
                    self.preview_image,
                ],
            ),
        )

    def _results_card(self) -> ft.Container:
        return ft.Container(
            padding=16, border_radius=16, bgcolor=ft.colors.SURFACE_VARIANT,
            content=ft.Column(
                spacing=10,
                controls=[section_title("Detected objects"), self.results_column],
            ),
        )

    # -- Events ---------------------------------------------------------------

    def _on_file_picked(self, e: ft.FilePickerResultEvent) -> None:
        if not e.files:
            return
        self._picked_path = e.files[0].path
        self._already_saved = False
        self.save_button.disabled = True
        self.preview_image.src = self._picked_path
        self.preview_image.visible = True
        self.status_area.visible = False
        self.results_column.controls = [
            ft.Text("Image loaded. Click \"Run detection\" to analyze it.", size=12,
                    color=ft.colors.ON_SURFACE_VARIANT)
        ]
        self.update()

    def _run_detection(self, e) -> None:
        if not self._picked_path:
            self._show_status(error_banner("Choose an image first."))
            return
        if self.detection_service is None or not self.detection_service.is_ready:
            self._show_status(error_banner(
                "The detection model isn't ready. Check the startup error and restart the app."
            ))
            return

        self.status_area.visible = True
        self.status_area.content = loading_indicator("Running detection...")
        self.preview_image.visible = False
        self.results_column.controls = []
        self.update()

        try:
            annotated, objects, elapsed_ms = self.detection_service.detect_image_file(self._picked_path)
        except DetectionServiceError as err:
            self._show_status(error_banner(str(err)))
            return
        except Exception as err:
            logger.exception("Unexpected error during image detection")
            self._show_status(error_banner(f"Unexpected error: {err}"))
            return

        self._last_annotated = annotated
        self._last_objects = objects
        self._last_elapsed_ms = elapsed_ms
        self._already_saved = False

        ok, buf = cv2.imencode(".png", annotated)
        if ok:
            b64 = base64.b64encode(buf.tobytes()).decode("ascii")
            self.preview_image.src = None
            self.preview_image.src_base64 = b64
            self.preview_image.visible = True
        self.status_area.visible = False

        self._render_results(objects, elapsed_ms)
        self.save_button.disabled = False
        self.update()

    def _render_results(self, objects, elapsed_ms) -> None:
        if not objects:
            self.results_column.controls = [
                empty_state(
                    ft.icons.SEARCH_OFF_ROUNDED, "No objects detected",
                    "Try a different image or a lower-confidence model.",
                )
            ]
            return

        counts: dict = {}
        for o in objects:
            counts[o.label] = counts.get(o.label, 0) + 1

        rows = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(f"{len(objects)} objects · {elapsed_ms:.0f} ms", size=12,
                            color=ft.colors.ON_SURFACE_VARIANT),
                ],
            )
        ]
        for label, count in sorted(counts.items(), key=lambda x: -x[1]):
            best_conf = max(o.confidence for o in objects if o.label == label)
            rows.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(spacing=8, controls=[
                            ft.Icon(ft.icons.LABEL_ROUNDED, size=16, color=config.COLOR_PRIMARY),
                            ft.Text(f"{label} × {count}", size=13),
                        ]),
                        confidence_chip(best_conf),
                    ],
                )
            )
        self.results_column.controls = rows

    def _show_status(self, control: ft.Control) -> None:
        self.status_area.visible = True
        self.status_area.content = control
        self.preview_image.visible = False
        self.update()

    def _save_result(self, e) -> None:
        if self._already_saved or self._last_annotated is None:
            return
        try:
            config.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
            filename = Path(self._picked_path).stem + "_detected.png"
            out_path = str(config.SCREENSHOTS_DIR / filename)
            cv2.imwrite(out_path, self._last_annotated)

            result = DetectionResult(
                source_type="image",
                source_name=Path(self._picked_path).name,
                objects=self._last_objects,
                output_path=out_path,
                processing_time_ms=self._last_elapsed_ms,
            )
            self.db.save_detection_result(result)
            self._already_saved = True
            self.save_button.disabled = True
            self._notify("Result saved to history.")
        except Exception as err:
            logger.exception("Failed to save image detection result")
            self._notify(f"Could not save result: {err}")
        self.update()

    def _notify(self, message: str) -> None:
        snack = ft.SnackBar(content=ft.Text(message), open=True)
        self.page.snack_bar = snack
        self.page.update()
