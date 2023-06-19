import time
import threading

import eventlet

from device.source import RandomDataSource, DataPoint, DeviceType, Activity


class Device:

    def __init__(self, device_type: DeviceType, frequency=50):
        # immutable attributes
        self.device_type = device_type
        self.lock = threading.Lock()

        # mutable attributes
        self.frequency = frequency
        self.activity = Activity.IDLE

        # computed attributes
        self.source = self.init_source()
        self.buffer = []

    def init_source(self):
        source = RandomDataSource(
            self.device_type,
            self.activity
        )
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
        eventlet.spawn(self.loop)
        print(f"Device {self.device_type.name} started")


class EmpaticaE4(Device):

    def __init__(self):
        super().__init__(
            device_type=DeviceType.E4,
            frequency=50
        )
