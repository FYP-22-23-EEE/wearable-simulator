import os

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
        # print(f"Broadcast {len(data_points)} data points")
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
    def on_state_change(state):
        if devices.activity != state["activity"]:
            devices.set_activity(state["activity"])
        for name in ["e4", "muse", "zephyr", "earbuds"]:
            dt = DeviceType.from_string(name)
            if devices.is_device_running(dt) != state["devices"][name]:
                if state["devices"][name]:
                    devices.start_device(dt)
                else:
                    devices.stop_device(dt)

    app_server = AppServer(
        ui_api_host=os.environ.get("UI_API_HOST", "0.0.0.0"),
        ui_api_port=os.environ.get("UI_API_PORT", 5050),
        on_state_change=on_state_change,
    )
    app_server.start()
