import flet as ft

import eventlet
from eventlet import wsgi
from eventlet.green import os

from device.source import DeviceType
from utils.singleton import singleton


@singleton
class AppState:

    def __init__(self):
        # states
        self.activity = "IDLE"
        self.frequency = "2 Hz"
        self.devices = {
            DeviceType.E4: False,
            DeviceType.MUSE: False,
            DeviceType.ZEPHYR: False,
            DeviceType.EARBUDS: False,
        }

    def device_state(self, device: DeviceType) -> bool:
        return self.devices[device]

    def set_device_state(self, device: DeviceType, state: bool):
        self.devices[device] = state


class App:
    def __init__(self, port=8080):
        self.state = AppState()
        self.port = port
        self.view = ft.WEB_BROWSER

    def button(self, text, device: DeviceType) -> ft.OutlinedButton:
        ctrl = ft.OutlinedButton(
            text,
            style=ft.ButtonStyle(
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE_700 if self.state.device_state(device) else ft.colors.BLUE_GREY_200,
                overlay_color=ft.colors.BLUE_800,
            ),
            on_click=lambda e: toggle(e),
        )

        def toggle(e):
            self.state.set_device_state(device, not self.state.device_state(device))
            ctrl.style = ft.ButtonStyle(
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE_700 if self.state.device_state(device) else ft.colors.BLUE_GREY_200,
                overlay_color=ft.colors.BLUE_800,
            )
            ctrl.update()

        return ctrl

    def main(self, page: ft.Page):
        page.title = "Flet counter example"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.theme_mode = ft.ThemeMode.LIGHT

        state = AppState()

        page.add(ft.Row(
            [
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Dropdown(
                                    options=[
                                        ft.dropdown.Option("2 Hz"),
                                        ft.dropdown.Option("4 Hz"),
                                        ft.dropdown.Option("8 Hz"),
                                        ft.dropdown.Option("16 Hz"),
                                        ft.dropdown.Option("32 Hz"),
                                    ],
                                    label="Frequency",
                                    hint_text="Select frequency",
                                    expand=True,
                                    value=state.frequency,
                                    on_change=lambda e: setattr(state, "frequency", e.data),
                                ),
                                ft.Dropdown(
                                    options=[
                                        ft.dropdown.Option("IDLE"),
                                        ft.dropdown.Option("WALKING"),
                                        ft.dropdown.Option("RUNNING"),
                                    ],
                                    label="Activity",
                                    hint_text="Select activity",
                                    expand=True,
                                    value=state.activity,
                                    on_change=lambda e: setattr(state, "activity", e.data),
                                ),
                            ]
                        ),
                        ft.GridView(
                            [
                                self.button("E4", DeviceType.E4),
                                self.button("Muse", DeviceType.MUSE),
                                self.button("Zephyr", DeviceType.ZEPHYR),
                                self.button("Earbuds", DeviceType.EARBUDS),
                            ],
                            runs_count=4,
                            run_spacing=10,
                        ),
                        ft.Row(
                            [
                                ft.FilledButton(
                                    "Save",
                                    style=ft.ButtonStyle(
                                        bgcolor=ft.colors.BLUE_700,
                                        overlay_color=ft.colors.BLUE_800,
                                    ),
                                    expand=True,
                                    height=50,
                                ),
                            ]
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    width=500,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ))

        page.update()


def serve_static(env, start_response):
    path = './dist' + env["PATH_INFO"]

    if not os.path.isfile(path):
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b"Not Found\n"]

    if path.endswith(".html"):
        content_type = 'text/html'
    elif path.endswith(".css"):
        content_type = 'text/css'
    elif path.endswith(".js"):
        content_type = 'application/javascript'
    else:
        content_type = 'application/octet-stream'

    start_response('200 OK', [('Content-Type', content_type)])
    return open(path, 'rb')


# wsgi.server(eventlet.listen(('0.0.0.0', 8000)), serve_static)
