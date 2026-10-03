"""
ui/results.py
Detection history: a searchable/filterable list of past sessions, with a
detail dialog per session (per-object breakdown) and the ability to delete
individual sessions or clear all history.
"""
import logging
from typing import Optional

import flet as ft

import config
from database import DatabaseManager
from ui.components import confidence_chip, confirm_dialog, empty_state, section_title

logger = logging.getLogger(__name__)

_SOURCE_ICON = {
    "webcam": ft.icons.VIDEOCAM_ROUNDED,
    "image": ft.icons.IMAGE_ROUNDED,
    "video": ft.icons.MOVIE_ROUNDED,
}


class ResultsView(ft.Column):
    def __init__(self, page: ft.Page, db: DatabaseManager):
        super().__init__(scroll=ft.ScrollMode.AUTO, spacing=16, expand=True)
        self.page = page
        self.db = db
        self._filter: Optional[str] = None

        self.filter_tabs = ft.Tabs(
            selected_index=0,
            on_change=self._on_filter_change,
            tabs=[ft.Tab(text="All"), ft.Tab(text="Webcam"), ft.Tab(text="Image"), ft.Tab(text="Video")],
        )
        self.list_column = ft.Column(spacing=10)

        self.controls = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    section_title("Detection History", "All saved detection sessions"),
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.IconButton(icon=ft.icons.REFRESH_ROUNDED, tooltip="Refresh", on_click=lambda e: self.refresh()),
                            ft.IconButton(
                                icon=ft.icons.DELETE_SWEEP_ROUNDED, tooltip="Clear all history",
                                icon_color=config.COLOR_DANGER, on_click=self._confirm_clear_all,
                            ),
                        ],
                    ),
                ],
            ),
            self.filter_tabs,
            self.list_column,
        ]
        self.refresh()

    # -- Data ---------------------------------------------------------------

    def refresh(self) -> None:
        try:
            sessions = self.db.get_history(limit=100, source_type=self._filter)
            error = None
        except Exception as e:
            sessions, error = [], str(e)

        if error:
            from ui.components import error_banner
            self.list_column.controls = [error_banner(f"Could not load history: {error}")]
        elif not sessions:
            self.list_column.controls = [
                empty_state(
                    ft.icons.HISTORY_TOGGLE_OFF_ROUNDED, "No detections yet",
                    "Run detection on your webcam, an image, or a video, and results will appear here.",
                )
            ]
        else:
            self.list_column.controls = [self._session_tile(s) for s in sessions]

        if self.page and self.uid is not None:
            self.update()

    def _on_filter_change(self, e) -> None:
        index = self.filter_tabs.selected_index
        self._filter = None if index == 0 else ["webcam", "image", "video"][index - 1]
        self.refresh()

    # -- Rendering ---------------------------------------------------------------

    def _session_tile(self, session: dict) -> ft.Container:
        icon = _SOURCE_ICON.get(session["source_type"], ft.icons.DEVICES_ROUNDED)
        return ft.Container(
            padding=14, border_radius=14, bgcolor=ft.colors.SURFACE_VARIANT,
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=42, height=42, border_radius=12,
                        bgcolor=ft.colors.with_opacity(0.15, config.COLOR_PRIMARY),
                        alignment=ft.alignment.center,
                        content=ft.Icon(icon, color=config.COLOR_PRIMARY, size=20),
                    ),
                    ft.Column(
                        expand=True, spacing=2,
                        controls=[
                            ft.Text(session["source_name"], size=13, weight=ft.FontWeight.W_600, no_wrap=True),
                            ft.Text(
                                f'{session["timestamp"]} · {session["object_count"]} objects',
                                size=11, color=ft.colors.ON_SURFACE_VARIANT,
                            ),
                        ],
                    ),
                    confidence_chip(session["avg_confidence"] or 0.0),
                    ft.IconButton(
                        icon=ft.icons.VISIBILITY_ROUNDED, tooltip="View details",
                        on_click=lambda e, s=session: self._show_details(s),
                    ),
                    ft.IconButton(
                        icon=ft.icons.DELETE_OUTLINE_ROUNDED, tooltip="Delete", icon_color=config.COLOR_DANGER,
                        on_click=lambda e, s=session: self._confirm_delete(s),
                    ),
                ],
            ),
        )

    def _show_details(self, session: dict) -> None:
        try:
            objects = self.db.get_session_objects(session["id"])
        except Exception:
            objects = []
            logger.exception("Failed to load session objects")

        if objects:
            rows = [
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[ft.Text(o["label"], size=13), confidence_chip(o["confidence"])],
                )
                for o in objects
            ]
        else:
            rows = [ft.Text("No per-object detail was recorded for this session.", size=12,
                             color=ft.colors.ON_SURFACE_VARIANT)]

        content_controls = [
            ft.Text(f'Source: {session["source_type"].capitalize()} — {session["source_name"]}', size=12),
            ft.Text(f'Timestamp: {session["timestamp"]}', size=12),
            ft.Text(f'Processing time: {session["processing_time_ms"]:.0f} ms', size=12),
            ft.Divider(height=1),
        ] + rows

        if session.get("output_path"):
            content_controls.append(ft.Divider(height=1))
            content_controls.append(
                ft.Text(f'Saved to: {session["output_path"]}', size=11, color=ft.colors.ON_SURFACE_VARIANT, selectable=True)
            )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Session details"),
            content=ft.Container(
                width=380,
                content=ft.Column(controls=content_controls, spacing=8, scroll=ft.ScrollMode.AUTO, tight=True),
            ),
            actions=[ft.TextButton("Close", on_click=lambda e: self._close_dialog(dialog))],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _close_dialog(self, dialog: ft.AlertDialog) -> None:
        dialog.open = False
        self.page.update()

    def _confirm_delete(self, session: dict) -> None:
        confirm_dialog(
            self.page, "Delete this session?",
            f'This will permanently remove "{session["source_name"]}" from your history.',
            on_confirm=lambda: self._delete(session["id"]),
        )

    def _delete(self, session_id: int) -> None:
        try:
            self.db.delete_session(session_id)
        except Exception:
            logger.exception("Failed to delete session")
        self.refresh()

    def _confirm_clear_all(self, e) -> None:
        confirm_dialog(
            self.page, "Clear all history?",
            "This will permanently remove every saved detection session. This cannot be undone.",
            on_confirm=self._clear_all, confirm_label="Clear all",
        )

    def _clear_all(self) -> None:
        try:
            self.db.clear_all()
        except Exception:
            logger.exception("Failed to clear history")
        self.refresh()
