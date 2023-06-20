import os

import eventlet

from app import SocketServer, AppServer
from device.devices import DeviceCollection
from device.source import DeviceType

if __name__ == '__main__':
    eventlet.monkey_patch()

    # app server
    app_server = AppServer(
        ui_api_host=os.environ.get("UI_API_HOST", "localhost"),
        ui_api_port=os.environ.get("UI_API_PORT", 5050),
        # on_state_change=on_state_change,
    )
    app_server.start()



    # stream
    socket_server = SocketServer()
    socket_server.start()

    # devices
    def on_consume_data(data_points):
        socket_server.broadcast(data_points)


    devices = DeviceCollection(
        on_consume=on_consume_data,
        consume_frequency=1,
    )
    devices.start()


    # app
    def on_state_change(state):
        if devices.activity != state["activity"]:
            devices.set_activity(state["activity"])
        for name in ["e4", "muse", "zephyr", "earbuds"]:
            dt = DeviceType.from_string(name)
            if devices.is_device_running(dt) != state["devices"][dt]:
                if state["devices"][dt]:
                    devices.start_device(dt)
                else:
                    devices.stop_device(dt)


    app_server.on_state_change = on_state_change
