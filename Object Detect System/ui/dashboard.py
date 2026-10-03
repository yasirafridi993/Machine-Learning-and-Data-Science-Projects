"""
ui/dashboard.py
Landing screen: overview stat cards, a top-objects bar chart, a detections-
by-source breakdown, and a quick-access row of actions plus a preview of the
most recent detections.
"""
from typing import Callable, Optional

import flet as ft

import config
from analytics_service import AnalyticsService
from ui.components import empty_state, section_title, stat_card


class DashboardView(ft.Column):
    def __init__(self, analytics: AnalyticsService, on_navigate: Callable[[str], None]):
        super().__init__(scroll=ft.ScrollMode.AUTO, spacing=20, expand=True)
        self.analytics = analytics
        self.on_navigate = on_navigate
        self.refresh()

    # -- Public ---------------------------------------------------------------

    def refresh(self) -> None:
        """Rebuild the dashboard content from the latest stats. Safe to call
        again whenever the tab is revisited."""
        try:
            summary = self.analytics.summary()
            top = self.analytics.top_objects(limit=6)
            by_source = self.analytics.counts_by_source()
            recent = self.analytics.recent_sessions(limit=5)
            error = None
        except Exception as e:
            summary, top, by_source, recent = {}, [], {}, []
            error = str(e)

        self.controls = [
            self._header(),
            self._error_or_stats(summary, error),
            self._quick_actions(),
            self._charts_row(top, by_source),
            self._recent_section(recent),
        ]
        if self.page:
            self.update()

    # -- Sections ---------------------------------------------------------------

    def _header(self) -> ft.Row:
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            "Overview of all detection activity",
                            size=13, color=ft.colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                ),
                ft.IconButton(
                    icon=ft.icons.REFRESH_ROUNDED,
                    tooltip="Refresh",
                    on_click=lambda e: self.refresh(),
                ),
            ],
        )

    def _error_or_stats(self, summary: dict, error: Optional[str]) -> ft.Control:
        if error:
            from ui.components import error_banner
            return error_banner(f"Could not load statistics: {error}")

        total_sessions = summary.get("total_sessions", 0)
        total_objects = summary.get("total_objects", 0)
        avg_conf = summary.get("avg_confidence", 0.0)

        return ft.ResponsiveRow(
            spacing=14, run_spacing=14,
            controls=[
                ft.Container(
                    col={"xs": 6, "md": 3},
                    content=stat_card(
                        ft.icons.CAMERA_ALT_ROUNDED, "Detection sessions",
                        str(total_sessions), config.COLOR_PRIMARY,
                    ),
                ),
                ft.Container(
                    col={"xs": 6, "md": 3},
                    content=stat_card(
                        ft.icons.CATEGORY_ROUNDED, "Objects detected",
                        str(total_objects), config.COLOR_ACCENT,
                    ),
                ),
                ft.Container(
                    col={"xs": 6, "md": 3},
                    content=stat_card(
                        ft.icons.SPEED_ROUNDED, "Avg. confidence",
                        f"{avg_conf * 100:.0f}%", config.COLOR_WARNING,
                    ),
                ),
                ft.Container(
                    col={"xs": 6, "md": 3},
                    content=stat_card(
                        ft.icons.MEMORY_ROUNDED, "Unique labels",
                        str(len(summary.get("label_counts", {}))), config.COLOR_PRIMARY_DARK,
                    ),
                ),
            ],
        )

    def _quick_actions(self) -> ft.Container:
        def action_button(icon, label, route):
            return ft.OutlinedButton(
                content=ft.Row(
                    spacing=8,
                    controls=[ft.Icon(icon, size=18), ft.Text(label)],
                ),
                on_click=lambda e: self.on_navigate(route),
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
            )

        return ft.Container(
            content=ft.Row(
                wrap=True, spacing=10, run_spacing=10,
                controls=[
                    action_button(ft.icons.VIDEOCAM_ROUNDED, "Start live detection", "live"),
                    action_button(ft.icons.IMAGE_ROUNDED, "Detect on image", "image"),
                    action_button(ft.icons.MOVIE_ROUNDED, "Detect on video", "video"),
                    action_button(ft.icons.HISTORY_ROUNDED, "View history", "results"),
                ],
            )
        )

    def _charts_row(self, top: list, by_source: dict) -> ft.ResponsiveRow:
        return ft.ResponsiveRow(
            spacing=14, run_spacing=14,
            controls=[
                ft.Container(col={"xs": 12, "md": 7}, content=self._top_objects_chart(top)),
                ft.Container(col={"xs": 12, "md": 5}, content=self._source_breakdown(by_source)),
            ],
        )

    def _top_objects_chart(self, top: list) -> ft.Container:
        body: ft.Control
        if not top:
            body = empty_state(
                ft.icons.BAR_CHART_ROUNDED, "No data yet",
                "Run a detection to see your most common objects here.",
            )
        else:
            max_count = max(c for _, c in top) or 1
            groups = []
            for i, (label, count) in enumerate(top):
                groups.append(
                    ft.BarChartGroup(
                        x=i,
                        bar_rods=[
                            ft.BarChartRod(
                                from_y=0, to_y=count, width=26,
                                color=config.COLOR_PRIMARY,
                                border_radius=6,
                                tooltip=f"{label}: {count}",
                            )
                        ],
                    )
                )
            body = ft.BarChart(
                bar_groups=groups,
                border=ft.border.all(0, ft.colors.TRANSPARENT),
                left_axis=ft.ChartAxis(labels_size=30),
                bottom_axis=ft.ChartAxis(
                    labels=[
                        ft.ChartAxisLabel(
                            value=i,
                            label=ft.Text(label[:8], size=10),
                        )
                        for i, (label, _) in enumerate(top)
                    ],
                    labels_size=32,
                ),
                horizontal_grid_lines=ft.ChartGridLines(
                    color=ft.colors.with_opacity(0.08, ft.colors.ON_SURFACE), width=1
                ),
                max_y=max_count * 1.2,
                interactive=True,
                expand=True,
            )

        return ft.Container(
            padding=18, border_radius=16, bgcolor=ft.colors.SURFACE_VARIANT,
            height=280,
            content=ft.Column(
                spacing=12,
                controls=[section_title("Most detected objects"), ft.Container(content=body, expand=True)],
            ),
        )

    def _source_breakdown(self, by_source: dict) -> ft.Container:
        body: ft.Control
        if not by_source:
            body = empty_state(
                ft.icons.PIE_CHART_ROUNDED, "No data yet", "Detections by source will appear here.",
            )
        else:
            palette = [config.COLOR_PRIMARY, config.COLOR_ACCENT, config.COLOR_WARNING]
            total = sum(by_source.values()) or 1
            sections = []
            legend_rows = []
            for i, (source, count) in enumerate(by_source.items()):
                color = palette[i % len(palette)]
                pct = count / total * 100
                sections.append(
                    ft.PieChartSection(
                        value=count, color=color, radius=45,
                        title=f"{pct:.0f}%", title_style=ft.TextStyle(size=11, color=ft.colors.WHITE),
                    )
                )
                legend_rows.append(
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Container(width=10, height=10, border_radius=5, bgcolor=color),
                            ft.Text(source.capitalize(), size=12, expand=True),
                            ft.Text(str(count), size=12, weight=ft.FontWeight.W_600),
                        ],
                    )
                )
            body = ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.PieChart(sections=sections, sections_space=2, center_space_radius=30, expand=True),
                    ft.Column(spacing=8, controls=legend_rows, expand=True),
                ],
                expand=True,
            )

        return ft.Container(
            padding=18, border_radius=16, bgcolor=ft.colors.SURFACE_VARIANT,
            height=280,
            content=ft.Column(
                spacing=12,
                controls=[section_title("Detections by source"), ft.Container(content=body, expand=True)],
            ),
        )

    def _recent_section(self, recent: list) -> ft.Container:
        if not recent:
            body = empty_state(
                ft.icons.INBOX_ROUNDED, "No detections yet",
                "Your recent detection sessions will show up here.",
            )
        else:
            rows = []
            icon_map = {"webcam": ft.icons.VIDEOCAM_ROUNDED, "image": ft.icons.IMAGE_ROUNDED, "video": ft.icons.MOVIE_ROUNDED}
            for row in recent:
                rows.append(
                    ft.Container(
                        padding=12, border_radius=12, bgcolor=ft.colors.SURFACE,
                        content=ft.Row(
                            controls=[
                                ft.Icon(icon_map.get(row["source_type"], ft.icons.DEVICES_ROUNDED), color=config.COLOR_PRIMARY),
                                ft.Column(
                                    spacing=0, expand=True,
                                    controls=[
                                        ft.Text(row["source_name"], size=13, weight=ft.FontWeight.W_600, no_wrap=True),
                                        ft.Text(row["timestamp"], size=11, color=ft.colors.ON_SURFACE_VARIANT),
                                    ],
                                ),
                                ft.Text(f'{row["object_count"]} objects', size=12),
                            ],
                        ),
                    )
                )
            body = ft.Column(spacing=8, controls=rows)

        return ft.Container(
            padding=18, border_radius=16, bgcolor=ft.colors.SURFACE_VARIANT,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            section_title("Recent activity"),
                            ft.TextButton("View all", on_click=lambda e: self.on_navigate("results")),
                        ],
                    ),
                    body,
                ],
            ),
        )
