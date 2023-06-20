import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.http import HttpHandler
from app.models import ReqActivity, ReqDeviceState
from app.socket import SocketHandler
from device.source import Activity, DeviceType


class AppServer:
    def __init__(self, host, port, public_url, on_state_change=None, on_started=None):
        self.host = host
        self.port = port
        self.public_url = public_url
        self.on_state_change = on_state_change
        self.on_started = on_started

        self.app = FastAPI(title="Energy Expenditure Estimation")

        self.http = HttpHandler(self).configure()
        self.socket = SocketHandler(self).configure()

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @self.app.on_event("startup")
        async def startup_event():
            if self.on_started:
                await self.on_started()

        self.state = {
            "activity": "idle",
            "devices": {
                "e4": False,
                "muse": False,
                "zephyr": False,
                "earbuds": False,
            }
        }

    def get_state(self):
        return {
            "activity": Activity.from_string(self.state["activity"]),
            "devices": {
                DeviceType.E4: self.state["devices"]["e4"],
                DeviceType.MUSE: self.state["devices"]["muse"],
                DeviceType.ZEPHYR: self.state["devices"]["zephyr"],
                DeviceType.EARBUDS: self.state["devices"]["earbuds"],
            }
        }

    def notify_state_changes(self):
        if self.on_state_change:
            self.on_state_change(self.get_state())

    def run(self, port):
        uvicorn.run(
            self.app,
            host=os.environ.get("APP_HOST", "localhost"),
            port=os.environ.get("APP_PORT", port),
        )

    def start(self, port=5050):
        self.run(port)
