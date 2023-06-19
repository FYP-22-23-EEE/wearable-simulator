import json

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

    def run(self, port=5000):
        print(f"Server running on port {port}")
        wsgi.server(eventlet.listen(('0.0.0.0', port)), self.app)

    def start(self, port=5000):
        eventlet.spawn(self.run, port)
        print(f"Socket server started on port {port}")


class ReqActivity(BaseModel):
    activity: str


class ReqDeviceState(BaseModel):
    device: str
    state: bool


class AppServer:
    def __init__(self, ui_api_host, ui_api_port, on_state_change=None):
        self.ui_api_host = ui_api_host
        self.ui_api_port = ui_api_port
        self.on_state_change = on_state_change

        self.app = FastAPI(title="Energy Expenditure Estimation")
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.configure()
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

    def configure(self):
        self.app.mount("/ui/static/", StaticFiles(directory="./ui/dist"), name="ui")

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
            self.state["activity"] = activity.activity
            if self.on_state_change is not None:
                self.on_state_change(self.state)
            return self.state["activity"]

        @self.app.post("/api/device/state")
        async def set_device(device: ReqDeviceState):
            device.device = device.device.lower()
            if device.device in self.state["devices"]:
                self.state["devices"][device.device] = device.state
                if self.on_state_change is not None:
                    self.on_state_change(self.state)
                return {"message": "Device state updated successfully"}
            else:
                return {"message": "Device not found"}

    def start(self, port=5050):
        uvicorn.run(self.app, host="0.0.0.0", port=port)
