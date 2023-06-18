import socketio
import eventlet
import random

# create a Socket.IO server
sio = socketio.Server(
    async_mode='eventlet',
    cors_allowed_origins="*",
    transports=['websocket', 'polling'],
)


# event handler for new connections
@sio.event
def connect(sid, environ):
    print('connect ', sid)


# event handler for a message
@sio.event
def message(sid, data):
    print('message ', data)


# event handler for disconnections
@sio.event
def disconnect(sid):
    print('disconnect ', sid)


def background_task():
    """Example of how to send server generated events to clients."""
    while True:
        number = random.randint(1, 100)  # generate a random number
        sio.emit('message', {'data': number})
        eventlet.sleep(1)  # delay for 1 second


if __name__ == '__main__':
    # wrap with a WSGI application
    app = socketio.WSGIApp(sio)

    # start the background task
    eventlet.spawn(background_task)

    print("Server running on port 5000")
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
