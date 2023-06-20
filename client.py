import socketio

sio = socketio.Client(
    reconnection=True,
    reconnection_attempts=5,
    reconnection_delay=1
)


@sio.event
def connect():
    print('Connection established')


@sio.event
def disconnect():
    print('Disconnected from server')


@sio.event
def message(data):
    print('MSG:', data)


if __name__ == '__main__':
    sio.connect('ws://localhost:5050', socketio_path='/stream/socket.io')
