import threading
import time

import eventlet

from device.source import RandomDataSource, DataPoint, DeviceType, Activity


class Device:

    def __init__(self, device_type: DeviceType, frequency=50):
        # immutable attributes
        self.device_type = device_type
        self.lock = threading.Lock()
        self.thread = None
        self.running = False

        # mutable attributes
        self.frequency = frequency

        # computed attributes
        self.source = self.init_source(Activity.IDLE)
        self.buffer = []

    def init_source(self, activity):
        source = RandomDataSource(
            self.device_type,
            activity
        )
        print(f"Device {self.device_type.name} initialized with activity {activity.name}")
        return source

    def consume_data(self) -> list[DataPoint]:
        with self.lock:
            data = self.buffer
            self.buffer = []
        return data

    def loop(self):
        while True:
            # get data
            data = next(self.source)

            # add to buffer
            with self.lock:
                self.buffer.append(data)

            # sleep
            time.sleep(1 / self.frequency)

    def start(self):
        self.thread = eventlet.spawn(self.loop)
        self.running = True
        print(f"Device {self.device_type.name} started")

    def stop(self):
        self.running = False
        self.thread.kill()
        print(f"Device {self.device_type.name} stopped")


class E4(Device):

    def __init__(self):
        super().__init__(
            device_type=DeviceType.E4,
            frequency=10
        )


class Muse(Device):

    def __init__(self):
        super().__init__(
            device_type=DeviceType.MUSE,
            frequency=10
        )


class Zephyr(Device):

    def __init__(self):
        super().__init__(
            device_type=DeviceType.ZEPHYR,
            frequency=10
        )


class Earbuds(Device):

    def __init__(self):
        super().__init__(
            device_type=DeviceType.EARBUDS,
            frequency=10
        )


class DeviceCollection:

    def __init__(self, on_consume=None, consume_frequency=2):
        self.thread = None
        self.on_consume = on_consume
        self.consume_frequency = consume_frequency
        self.activity = Activity.IDLE
        self.devices = {
            DeviceType.E4: E4(),
            DeviceType.MUSE: Muse(),
            DeviceType.ZEPHYR: Zephyr(),
            DeviceType.EARBUDS: Earbuds(),
        }

    def set_activity(self, activity: Activity):
        self.activity = activity
        self.update_device_activity()

    def get_activity(self):
        return self.activity

    def update_device_activity(self):
        for device in self.devices.values():
            device.source = device.init_source(self.activity)

    def start_device(self, device_type: DeviceType):
        self.devices[device_type].start()

    def stop_device(self, device_type: DeviceType):
        self.devices[device_type].stop()

    def is_device_running(self, device_type: DeviceType):
        return self.devices[device_type].running

    def run(self):
        while True:
            all_data = []
            for device in filter(lambda d: d.running, self.devices.values()):
                data = device.consume_data()
                if len(data) > 0:
                    all_data.extend(data)
            if len(all_data) > 0 and self.on_consume is not None:
                self.on_consume(all_data)
            time.sleep(1 / self.consume_frequency)

    def start(self):
        self.thread = eventlet.spawn(self.run)
        print("Device collection started")

    def stop(self):
        self.thread.kill()
        print("Device collection stopped")
