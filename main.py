import os
import time

from device.devices import DeviceCollection
from device.source import DeviceType
from app import AppServer
import asyncio


def main():
    # events
    def on_consume_data(data_points):
        print("Consuming data points:", len(data_points))
        while app_server.event_loop is None or app_server.event_loop.is_closed():
            time.sleep(0.1)
        asyncio.run_coroutine_threadsafe(app_server.socket.broadcast(data_points), app_server.event_loop)

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

    # init
    app_server = AppServer(
        ui_api_host=os.environ.get("UI_API_HOST", "localhost"),
        ui_api_port=os.environ.get("UI_API_PORT", 5050),
        on_state_change=on_state_change,
    )
    devices = DeviceCollection(
        consume_frequency=1,
        on_consume_data=on_consume_data,
    )

    # start
    devices.start()
    devices.start_device(DeviceType.E4)
    app_server.start()


if __name__ == '__main__':
    main()
