import json
import time

import eventlet
import socketio

from device.devices import EmpaticaE4

eventlet.monkey_patch()


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

    def start(self, port=5000):
        print(f"Server running on port {port}")
        eventlet.wsgi.server(eventlet.listen(('0.0.0.0', port)), self.app)


if __name__ == '__main__':
    # initialize instances
    server = SocketServer()
    e4 = EmpaticaE4()

    # start devices
    e4.start()


    def consume_data():
        print("Start consuming data")
        while True:
            data = e4.consume_data()
            if len(data) > 0:
                server.broadcast(data)
            print(f"Broadcast {len(data)} data points")
            time.sleep(0.5)


    eventlet.spawn(consume_data)

    # start server
    server.start()
