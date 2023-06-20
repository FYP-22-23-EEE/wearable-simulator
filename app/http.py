from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.models import ReqDeviceState, ReqActivity


class HttpHandler:

    def __init__(self, parent):
        self.parent = parent
        self.app = parent.app

    def configure(self) -> 'HttpHandler':
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
                "url": self.parent.public_url,
            })

        @self.app.get("/api/state")
        async def get_state():
            return JSONResponse(self.parent.state)

        @self.app.post("/api/activity")
        async def set_activity(activity: ReqActivity):
            self.parent.state["activity"] = activity.activity
            self.parent.notify_state_changes()
            return self.parent.state["activity"]

        @self.app.post("/api/device/state")
        async def set_device(device: ReqDeviceState):
            device.device = device.device.lower()
            if device.device in self.parent.state["devices"]:
                self.parent.state["devices"][device.device] = device.state
                self.parent.notify_state_changes()
                return {"message": "Device state updated successfully"}
            else:
                return {"message": "Device not found"}

        return self
