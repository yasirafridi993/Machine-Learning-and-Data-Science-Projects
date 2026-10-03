"""
ui/components.py
Small, reusable Flet widgets shared across screens: stat cards, empty/error
states, section headers, and a confirmation dialog helper. Keeping these in
one place is what gives the app a consistent, professional look.
"""
import flet as ft

import config


def stat_card(icon: str, label: str, value: str, color: str, expand: int = 1) -> ft.Container:
    """A rounded dashboard stat card with an icon, big value, and caption."""
    return ft.Container(
        expand=expand,
        padding=18,
        border_radius=16,
        bgcolor=ft.colors.SURFACE_VARIANT,
        content=ft.Column(
            spacing=6,
            controls=[
                ft.Container(
                    width=40,
                    height=40,
                    border_radius=12,
                    bgcolor=ft.colors.with_opacity(0.15, color),
                    alignment=ft.alignment.center,
                    content=ft.Icon(icon, color=color, size=22),
                ),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
                ft.Text(label, size=12, color=ft.colors.ON_SURFACE_VARIANT),
            ],
        ),
        shadow=ft.BoxShadow(
            blur_radius=14,
            color=ft.colors.with_opacity(0.08, ft.colors.BLACK),
            offset=ft.Offset(0, 4),
        ),
    )


def section_title(text: str, subtitle: str = "") -> ft.Column:
    controls = [ft.Text(text, size=18, weight=ft.FontWeight.W_600)]
    if subtitle:
        controls.append(ft.Text(subtitle, size=12, color=ft.colors.ON_SURFACE_VARIANT))
    return ft.Column(spacing=2, controls=controls)


def empty_state(icon: str, title: str, message: str) -> ft.Container:
    return ft.Container(
        padding=40,
        alignment=ft.alignment.center,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Icon(icon, size=48, color=ft.colors.ON_SURFACE_VARIANT),
                ft.Text(title, size=16, weight=ft.FontWeight.W_600),
                ft.Text(
                    message, size=12, color=ft.colors.ON_SURFACE_VARIANT,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
    )


def error_banner(message: str, on_dismiss=None) -> ft.Container:
    return ft.Container(
        padding=14,
        border_radius=12,
        bgcolor=ft.colors.with_opacity(0.12, config.COLOR_DANGER),
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.icons.ERROR_OUTLINE_ROUNDED, color=config.COLOR_DANGER, size=20),
                ft.Text(message, color=config.COLOR_DANGER, size=13, expand=True),
                ft.IconButton(
                    icon=ft.icons.CLOSE_ROUNDED,
                    icon_size=16,
                    icon_color=config.COLOR_DANGER,
                    on_click=on_dismiss,
                    visible=on_dismiss is not None,
                ),
            ],
        ),
    )


def loading_indicator(message: str = "Working...") -> ft.Column:
    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12,
        controls=[
            ft.ProgressRing(width=36, height=36, stroke_width=3, color=config.COLOR_PRIMARY),
            ft.Text(message, size=13, color=ft.colors.ON_SURFACE_VARIANT),
        ],
    )


def confidence_chip(confidence: float) -> ft.Container:
    if confidence >= 0.75:
        color = config.COLOR_ACCENT
    elif confidence >= 0.5:
        color = config.COLOR_WARNING
    else:
        color = config.COLOR_DANGER
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=8, vertical=3),
        border_radius=20,
        bgcolor=ft.colors.with_opacity(0.15, color),
        content=ft.Text(f"{confidence * 100:.0f}%", size=11, color=color, weight=ft.FontWeight.W_600),
    )


def confirm_dialog(page: ft.Page, title: str, message: str, on_confirm, confirm_label: str = "Delete"):
    """Show a confirmation dialog; on_confirm is called with no args if the
    user confirms."""

    def _close(e=None):
        dialog.open = False
        page.update()

    def _confirm(e):
        _close()
        on_confirm()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title),
        content=ft.Text(message),
        actions=[
            ft.TextButton("Cancel", on_click=_close),
            ft.FilledButton(
                confirm_label, on_click=_confirm,
                style=ft.ButtonStyle(bgcolor=config.COLOR_DANGER, color=ft.colors.WHITE),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialog)
    dialog.open = True
    page.update()
