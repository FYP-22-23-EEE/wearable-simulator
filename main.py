import os

import asyncio

from app import AppServer
from device.devices import DeviceCollection
from device.source import DeviceType


def main():
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

    async def consume_all_data():
        while True:
            data = devices.consume_all_data()
            if len(data) > 0:
                await app_server.socket.broadcast(data)
            await asyncio.sleep(1 / 2)  # Sleep for 5 seconds before the next iteration

    async def on_started():
        loop = asyncio.get_running_loop()
        loop.create_task(consume_all_data())
        print(f"Data Consumer Started")

    # init
    app_server = AppServer(
        host=os.environ.get("APP_HOST", "localhost"),
        port=os.environ.get("APP_PORT", 5050),
        public_url=os.environ.get("APP_PUBLIC_URL", "http://localhost:5050"),
        on_state_change=on_state_change,
        on_started=on_started,
    )
    devices = DeviceCollection(app_server.get_state()["activity"])

    # start
    devices.start_device(DeviceType.E4)
    app_server.start()


if __name__ == '__main__':
    main()
