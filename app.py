import json
import os

import eventlet
import socketio
import uvicorn
from eventlet import wsgi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from device.source import Activity, DeviceType


class SocketServer:

    def __init__(self):
        self.sio = socketio.Server(
            async_mode='eventlet',
            cors_allowed_origins="*",
            transports=['websocket', 'polling'],
        )
        self.app = socketio.WSGIApp(self.sio)

        @self.sio.event
        def connect(sid, environ):
            print('connect ', sid)

    def broadcast(self, data):
        json_data = json.dumps(data, default=lambda x: x.to_dict())
        self.sio.emit('message', json_data)

    def run(self, port):
        print(f"Server running on port {port}")
        wsgi.server(eventlet.listen((
            os.environ.get("SOCKET_SERVER_HOST", "localhost"),
            os.environ.get("SOCKET_SERVER_PORT", port),
        )), self.app)

    def start(self, port=5000):
        eventlet.spawn(self.run, port)


class ReqActivity(BaseModel):
    activity: str


class ReqDeviceState(BaseModel):
    device: str
    state: bool


class AppServer:
    def __init__(self, ui_api_host, ui_api_port, on_state_change=None):
        self.ui_api_host = ui_api_host
        self.ui_api_port = ui_api_port
        self._on_state_change = on_state_change

        self.app = FastAPI(title="Energy Expenditure Estimation")
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.state = {
            "activity": "idle",
            "devices": {
                "e4": False,
                "muse": False,
                "zephyr": False,
                "earbuds": False,
            }
        }
        self.configure()

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
        if self._on_state_change:
            self._on_state_change(self.get_state())

    def configure(self):
        self.app.mount("/ui/static/", StaticFiles(directory="./ui/dist"), name="ui_static_files")

        @self.app.get("/ui")
        def ui_root():
            return FileResponse("./ui/dist/index.html")

        @self.app.get("/")
        async def root():
            return RedirectResponse(url="/ui")

        @self.app.get("/config")
        async def config():
            return JSONResponse({
                "host": self.ui_api_host,
                "port": self.ui_api_port,
            })

        @self.app.get("/api/state")
        async def get_state():
            return JSONResponse(self.state)

        @self.app.post("/api/activity")
        async def set_activity(activity: ReqActivity):
            print(activity.activity)
            self.state["activity"] = activity.activity
            self.notify_state_changes()
            return self.state["activity"]

        @self.app.post("/api/device/state")
        async def set_device(device: ReqDeviceState):
            device.device = device.device.lower()
            if device.device in self.state["devices"]:
                self.state["devices"][device.device] = device.state
                self.notify_state_changes()
                return {"message": "Device state updated successfully"}
            else:
                return {"message": "Device not found"}

    def run(self, port):
        uvicorn.run(
            self.app,
            host=os.environ.get("UI_HOST", "localhost"),
            port=os.environ.get("UI_PORT", port),
        )

    def start(self, port=5050):
        # eventlet.spawn(self.run, port)
        self.run(port)
