import json

import eventlet
import socketio
import uvicorn
from eventlet import wsgi
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles


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


class Endpoint:
    path: str

    def __init__(self, app: FastAPI):
        self.app = app


class AppServer:
    def __init__(self):
        self.app = FastAPI(title="Energy Expenditure Estimation")
        self.configure()

    def configure(self):
        self.app.mount("/ui/static/", StaticFiles(directory="./ui/dist"), name="ui")

        @self.app.get("/ui")
        def read_root():
            return FileResponse("./ui/dist/index.html")

        @self.app.get("/")
        async def root():
            return JSONResponse(content={"message": "Hello World"})

    def start(self, port=5050):
        uvicorn.run(self.app, host="0.0.0.0", port=port)
