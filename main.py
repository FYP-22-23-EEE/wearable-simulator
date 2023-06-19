import time

import eventlet

from app import SocketServer, AppServer
from device.devices import E4, DeviceCollection
from device.source import DeviceType

eventlet.monkey_patch()

if __name__ == '__main__':
    # stream
    socket_server = SocketServer()
    socket_server.start()

    # devices
    def on_consume_data(data_points):
        socket_server.broadcast(data_points)
        print(f"Broadcast {len(data_points)} data points")
    devices = DeviceCollection(
        on_consume=on_consume_data,
        consume_frequency=1,
    )
    devices.start_device(DeviceType.E4)
    devices.start_device(DeviceType.MUSE)
    devices.start_device(DeviceType.ZEPHYR)
    devices.start_device(DeviceType.EARBUDS)
    devices.start()

    # app
    app_server = AppServer()
    app_server.start()
