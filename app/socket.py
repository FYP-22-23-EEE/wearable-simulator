import json

import socketio


class SocketHandler:

    def __init__(self, parent, mount_path='/stream'):
        self.parent = parent
        self.app = parent.app
        self.mount_path = mount_path
        self.sio = socketio.AsyncServer(async_mode='asgi')

    def configure(self) -> 'SocketHandler':
        self.app.mount(self.mount_path, socketio.ASGIApp(self.sio))

        @self.sio.event
        def connect(sid, environ):
            print('connect ', sid)

        @self.sio.event
        def disconnect(sid):
            print('disconnect ', sid)

        return self

    async def broadcast(self, data):
        try:
            json_data = json.dumps(data, default=lambda x: x.to_dict())
            await self.sio.emit('message', json_data)
        except Exception as e:
            print(f"Error broadcasting data: {e}")
