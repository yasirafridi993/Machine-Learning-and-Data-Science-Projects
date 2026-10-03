"""
main.py
Application entry point: window/theme setup, service initialization, and the
responsive navigation shell (sidebar on desktop, bottom nav on mobile) that
switches between the Dashboard, Live Detection, Image Detection, Video
Detection, and History screens.

Run with:  python main.py
"""
import logging

import flet as ft

import config
from analytics_service import AnalyticsService
from database import DatabaseManager, DatabaseError
from detection_service import DetectionService, DetectionServiceError
from ui.dashboard import DashboardView
from ui.image_detection import ImageDetectionView
from ui.live_detection import LiveDetectionView
from ui.results import ResultsView
from ui.video_detection import VideoDetectionView

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app")

_DESTINATIONS = [
    ("dashboard", "Dashboard", ft.icons.DASHBOARD_OUTLINED, ft.icons.DASHBOARD_ROUNDED),
    ("live", "Live", ft.icons.VIDEOCAM_OUTLINED, ft.icons.VIDEOCAM_ROUNDED),
    ("image", "Image", ft.icons.IMAGE_OUTLINED, ft.icons.IMAGE_ROUNDED),
    ("video", "Video", ft.icons.MOVIE_OUTLINED, ft.icons.MOVIE_ROUNDED),
    ("results", "History", ft.icons.HISTORY_OUTLINED, ft.icons.HISTORY_ROUNDED),
]


def main(page: ft.Page) -> None:
    page.title = config.APP_NAME
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.spacing = 0
    page.theme = ft.Theme(color_scheme_seed=config.COLOR_PRIMARY, use_material3=True)
    page.dark_theme = ft.Theme(color_scheme_seed=config.COLOR_PRIMARY, use_material3=True)
    page.fonts = {}

    try:
        page.window.width = config.WINDOW_WIDTH
        page.window.height = config.WINDOW_HEIGHT
        page.window.min_width = config.WINDOW_MIN_WIDTH
        page.window.min_height = config.WINDOW_MIN_HEIGHT
    except Exception:
        pass  # Not fatal on platforms/versions without a window object (e.g. web/mobile).

    # -- Services (Model/DB failures must not crash the whole app) ---------------

    startup_error = None
    try:
        db = DatabaseManager()
    except DatabaseError as e:
        logger.exception("Database initialization failed")
        db = None
        startup_error = f"Database error: {e}"

    detection_service = None
    if db is not None:
        try:
            detection_service = DetectionService()
        except DetectionServiceError as e:
            logger.exception("Detection model failed to load")
            startup_error = str(e)

    analytics = AnalyticsService(db) if db is not None else None

    # -- Fatal failure screen (no DB at all) ---------------------------------------

    if db is None:
        page.add(
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                padding=30,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                    controls=[
                        ft.Icon(ft.icons.ERROR_OUTLINE_ROUNDED, size=48, color=config.COLOR_DANGER),
                        ft.Text("Could not start the application", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(startup_error or "Unknown error", size=13, color=ft.colors.ON_SURFACE_VARIANT,
                                text_align=ft.TextAlign.CENTER),
                    ],
                ),
            )
        )
        return

    # -- Build views ---------------------------------------------------------------

    views = {
        "dashboard": DashboardView(analytics, on_navigate=lambda route: navigate(route)),
        "live": LiveDetectionView(page, detection_service, db),
        "image": ImageDetectionView(page, detection_service, db),
        "video": VideoDetectionView(page, detection_service, db),
        "results": ResultsView(page, db),
    }
    current_route = {"value": "dashboard"}

    content_container = ft.Container(expand=True, padding=24, content=views["dashboard"])

    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=90,
        min_extended_width=180,
        bgcolor=ft.colors.SURFACE,
        destinations=[
            ft.NavigationRailDestination(icon=outlined, selected_icon=filled, label=label)
            for _, label, outlined, filled in _DESTINATIONS
        ],
        on_change=lambda e: navigate(_DESTINATIONS[e.control.selected_index][0]),
    )

    nav_bar = ft.NavigationBar(
        selected_index=0,
        bgcolor=ft.colors.SURFACE,
        destinations=[
            ft.NavigationDestination(icon=outlined, selected_icon=filled, label=label)
            for _, label, outlined, filled in _DESTINATIONS
        ],
        on_change=lambda e: navigate(_DESTINATIONS[e.control.selected_index][0]),
    )

    def theme_toggle_icon() -> str:
        return ft.icons.LIGHT_MODE_ROUNDED if page.theme_mode == ft.ThemeMode.DARK else ft.icons.DARK_MODE_ROUNDED

    theme_button = ft.IconButton(icon=theme_toggle_icon(), tooltip="Toggle theme")

    def toggle_theme(e) -> None:
        page.theme_mode = (
            ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        )
        theme_button.icon = theme_toggle_icon()
        page.update()

    theme_button.on_click = toggle_theme

    app_bar = ft.Container(
        padding=ft.padding.symmetric(horizontal=20, vertical=14),
        bgcolor=ft.colors.SURFACE,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Icon(ft.icons.VISIBILITY_ROUNDED, color=config.COLOR_PRIMARY, size=26),
                        ft.Text(config.APP_NAME, size=18, weight=ft.FontWeight.BOLD),
                    ],
                ),
                ft.Row(
                    spacing=4,
                    controls=[
                        ft.Text(
                            f"YOLO · {detection_service.device_label}" if detection_service and detection_service.is_ready
                            else "Model unavailable",
                            size=12, color=ft.colors.ON_SURFACE_VARIANT,
                        ),
                        theme_button,
                    ],
                ),
            ],
        ),
    )

    root_body = ft.Container(expand=True)

    def build_layout() -> None:
        """Choose sidebar-rail (desktop) vs bottom-nav (mobile) based on width."""
        is_mobile = page.width is not None and page.width < config.MOBILE_BREAKPOINT
        if is_mobile:
            root_body.content = ft.Column(
                expand=True, spacing=0,
                controls=[
                    ft.Container(expand=True, content=content_container),
                    nav_bar,
                ],
            )
        else:
            root_body.content = ft.Row(
                expand=True, spacing=0,
                controls=[
                    nav_rail,
                    ft.VerticalDivider(width=1),
                    content_container,
                ],
            )
        if page.controls:
            page.update()

    def navigate(route: str) -> None:
        previous = views.get(current_route["value"])
        if previous is not None and hasattr(previous, "on_view_leave") and route != current_route["value"]:
            previous.on_view_leave()

        current_route["value"] = route
        content_container.content = views[route]
        if route == "dashboard":
            views["dashboard"].refresh()
        if route == "results":
            views["results"].refresh()

        index = [d[0] for d in _DESTINATIONS].index(route)
        nav_rail.selected_index = index
        nav_bar.selected_index = index
        page.update()

    if startup_error:
        banner_text = ft.Text(startup_error, color=config.COLOR_DANGER, size=12, expand=True)
        startup_banner = ft.Container(
            padding=10, bgcolor=ft.colors.with_opacity(0.12, config.COLOR_DANGER),
            content=ft.Row(controls=[
                ft.Icon(ft.icons.WARNING_AMBER_ROUNDED, color=config.COLOR_DANGER, size=18),
                banner_text,
            ]),
        )
    else:
        startup_banner = ft.Container(height=0)

    page.on_resized = lambda e: build_layout()
    build_layout()

    page.add(
        ft.Column(
            expand=True, spacing=0,
            controls=[app_bar, startup_banner, root_body],
        )
    )


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
