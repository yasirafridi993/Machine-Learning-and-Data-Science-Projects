import asyncio

import flet as ft

from src.predict import get_locations, predict_house_price


INK = "#173B35"
MINT = "#D8EAE2"
ACCENT = "#B78B4A"
BACKGROUND = "#F2F5F2"
MUTED = "#71817B"


def main(page: ft.Page):
    page.title = "House Price Predictor"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = BACKGROUND
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    page.theme = ft.Theme(color_scheme_seed=INK)

    locations = get_locations()
    location_search = ft.TextField(
        label="Search Lahore locations",
        hint_text="Start typing a neighborhood",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=10,
        filled=True,
        bgcolor="#F8FAF8",
        text_size=14,
    )
    location_dropdown = ft.Dropdown(
        label="Location",
        hint_text="Choose a location",
        options=[ft.dropdown.Option(key=value, text=value.title()) for value in locations],
        border_radius=10,
        filled=True,
        bgcolor="#F8FAF8",
        text_size=14,
    )
    area_field = ft.TextField(
        label="Area (sq ft)",
        hint_text="e.g. 5,000",
        prefix_icon=ft.Icons.SQUARE_FOOT_OUTLINED,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=10,
        filled=True,
        bgcolor="#F8FAF8",
        text_size=14,
    )
    bedrooms_field = ft.TextField(
        label="Bedrooms",
        hint_text="e.g. 3",
        prefix_icon=ft.Icons.BEDROOM_PARENT_OUTLINED,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=10,
        filled=True,
        bgcolor="#F8FAF8",
        text_size=14,
    )
    bathrooms_field = ft.TextField(
        label="Bathrooms",
        hint_text="e.g. 3",
        prefix_icon=ft.Icons.BATHTUB_OUTLINED,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=10,
        filled=True,
        bgcolor="#F8FAF8",
        text_size=14,
    )
    status_text = ft.Text(size=13, color=MUTED)
    price_text = ft.Text(
        "PKR --",
        size=30,
        weight=ft.FontWeight.BOLD,
        color="white",
        selectable=True,
    )
    result_caption = ft.Text(
        "Complete the property details to see an estimate.",
        size=13,
        color="#D0DDD8",
    )
    reset_button = ft.TextButton(
        "Clear and start again",
        icon=ft.Icons.REFRESH,
        icon_color="white",
        style=ft.ButtonStyle(color="white"),
        visible=False,
    )
    predict_button = ft.FilledButton(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.AUTO_AWESOME, size=18),
                ft.Text("Predict price", weight=ft.FontWeight.W_600),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=9,
        ),
        height=50,
        style=ft.ButtonStyle(
            bgcolor=INK,
            color="white",
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
    )

    def set_error(field: ft.TextField | ft.Dropdown, message: str | None):
        field.error_text = message

    def filter_locations(event):
        query = (event.control.value or "").strip().casefold()
        matches = [value for value in locations if query in value.casefold()]
        location_dropdown.options = [
            ft.dropdown.Option(key=value, text=value.title()) for value in matches
        ]
        if location_dropdown.value not in matches:
            location_dropdown.value = None
        set_error(location_dropdown, None)
        page.update()

    def clear_form(event=None):
        location_search.value = ""
        location_search.error_text = None
        location_dropdown.value = None
        location_dropdown.options = [
            ft.dropdown.Option(key=value, text=value.title()) for value in locations
        ]
        area_field.value = ""
        bedrooms_field.value = ""
        bathrooms_field.value = ""
        for field in (area_field, bedrooms_field, bathrooms_field):
            field.error_text = None
        status_text.value = ""
        price_text.value = "PKR --"
        result_caption.value = "Complete the property details to see an estimate."
        reset_button.visible = False
        page.update()

    def parse_inputs():
        valid = True
        location = location_dropdown.value
        if not location:
            set_error(location_dropdown, "Choose a location from the list.")
            valid = False
        else:
            set_error(location_dropdown, None)

        try:
            area = float((area_field.value or "").replace(",", "").strip())
            if area <= 0:
                raise ValueError
            set_error(area_field, None)
        except ValueError:
            set_error(area_field, "Enter an area greater than 0 sq ft.")
            area = 0
            valid = False

        numeric_values = []
        for field, label in (
            (bedrooms_field, "bedrooms"),
            (bathrooms_field, "bathrooms"),
        ):
            try:
                value = int((field.value or "").strip())
                if value < 0:
                    raise ValueError
                set_error(field, None)
                numeric_values.append(value)
            except ValueError:
                set_error(field, f"Enter a whole number of {label} (0 or more).")
                numeric_values.append(0)
                valid = False
        return (location, area, *numeric_values) if valid else None

    async def predict(event):
        if predict_button.disabled:
            return
        values = parse_inputs()
        if values is None:
            status_text.value = "Please check the highlighted property details."
            page.update()
            return

        location, area, bedrooms, bathrooms = values
        predict_button.disabled = True
        predict_button.content = ft.Row(
            [
                ft.ProgressRing(width=17, height=17, stroke_width=2, color="white"),
                ft.Text("Estimating...", weight=ft.FontWeight.W_600),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )
        status_text.value = "Calculating your estimate..."
        page.update()

        try:
            price = await asyncio.to_thread(
                predict_house_price,
                area_sqft=area,
                location=location,
                bedrooms=bedrooms,
                baths=bathrooms,
            )
            price_text.value = f"PKR {price:,.0f}"
            result_caption.value = "Estimated value based on the property details provided."
            reset_button.visible = True
            status_text.value = "Estimate ready."
        except ValueError as error:
            status_text.value = str(error)
        except Exception:
            status_text.value = "We couldn't calculate this estimate. Please try again."
        finally:
            predict_button.disabled = False
            predict_button.content = ft.Row(
                [
                    ft.Icon(ft.Icons.AUTO_AWESOME, size=18),
                    ft.Text("Predict price", weight=ft.FontWeight.W_600),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=9,
            )
            page.update()

    location_search.on_change = filter_locations
    predict_button.on_click = predict
    reset_button.on_click = clear_form

    details_card = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.HOME_WORK_OUTLINED, color=INK, size=21),
                            width=42,
                            height=42,
                            alignment=ft.alignment.center,
                            bgcolor=MINT,
                            border_radius=12,
                        ),
                        ft.Column(
                            [
                                ft.Text("Property details", size=19, weight=ft.FontWeight.BOLD, color=INK),
                                ft.Text("A few details help us estimate the value.", size=13, color=MUTED),
                            ],
                            spacing=3,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                ),
                ft.ResponsiveRow(
                    [
                        ft.Column([location_search, location_dropdown], spacing=4, col={"sm": 12, "md": 6}),
                        ft.Column([area_field], col={"sm": 12, "md": 6}),
                        ft.Column([bedrooms_field], col={"sm": 12, "md": 6}),
                        ft.Column([bathrooms_field], col={"sm": 12, "md": 6}),
                    ],
                    run_spacing=8,
                    spacing=14,
                ),
                ft.Row(
                    [
                        predict_button,
                        ft.TextButton("Reset", icon=ft.Icons.RESTART_ALT, on_click=clear_form),
                    ],
                    spacing=10,
                    wrap=True,
                ),
                status_text,
            ],
            spacing=20,
        ),
        padding=24,
        bgcolor="white",
        border=ft.border.all(1, "#E1E9E4"),
        border_radius=16,
    )

    result_card = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.QUERY_STATS, color="#D5B982", size=21),
                        ft.Text("PRICE ESTIMATE", size=12, weight=ft.FontWeight.BOLD, color="#D5B982"),
                    ],
                    spacing=9,
                ),
                ft.Container(height=18),
                ft.Text("Your estimated\nproperty value", size=22, weight=ft.FontWeight.W_600, color="white"),
                ft.Container(height=8),
                price_text,
                ft.Container(height=6),
                result_caption,
                ft.Divider(color="#49635D", height=26),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.INFO_OUTLINE, color="#D0DDD8", size=16),
                        ft.Text("An estimate, not a formal valuation.", size=12, color="#D0DDD8", expand=True),
                    ],
                    spacing=8,
                ),
                reset_button,
            ],
            spacing=3,
        ),
        padding=24,
        bgcolor=INK,
        border_radius=16,
        border=ft.border.all(1, "#31564F"),
    )

    page.add(
        ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.HOME_WORK, color="white", size=23),
                                width=44,
                                height=44,
                                alignment=ft.alignment.center,
                                bgcolor="#2A5C51",
                                border_radius=12,
                            ),
                            ft.Column(
                                [
                                    ft.Text("House Price Predictor", size=21, weight=ft.FontWeight.BOLD, color="white"),
                                    ft.Text("AI-Powered Property Price Estimation", size=13, color="#D0DDD8"),
                                ],
                                spacing=3,
                            ),
                        ],
                        spacing=12,
                    ),
                    padding=ft.padding.symmetric(horizontal=28, vertical=20),
                    bgcolor=INK,
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text("Lahore property estimator", size=12, color=ACCENT, weight=ft.FontWeight.BOLD),
                                            ft.Text("Find your property's\nestimated value", size=29, color=INK, weight=ft.FontWeight.BOLD),
                                            ft.Text("Enter the key details and get an instant estimate in PKR.", size=14, color=MUTED),
                                        ],
                                        spacing=8,
                                        expand=True,
                                    ),
                                    ft.Container(
                                        content=ft.Icon(ft.Icons.DOMAIN, size=42, color="#8CA99D"),
                                        width=92,
                                        height=92,
                                        alignment=ft.Alignment(0, 0),
                                        bgcolor="#E5EEE8",
                                        border_radius=24,
                                    ),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=20,
                            ),
                            ft.ResponsiveRow(
                                [
                                    ft.Column([details_card], col={"sm": 12, "md": 8}),
                                    ft.Column([result_card], col={"sm": 12, "md": 4}),
                                ],
                                spacing=18,
                                run_spacing=18,
                            ),
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.SHIELD_OUTLINED, size=15, color=MUTED),
                                    ft.Text("Your property details stay on this device.", size=12, color=MUTED),
                                ],
                                spacing=7,
                            ),
                        ],
                        spacing=24,
                    ),
                    padding=ft.padding.symmetric(horizontal=28, vertical=30),
                    width=1100,
                ),
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)