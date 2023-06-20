import threading
import time

from device.source import RandomDataSource, DataPoint, DeviceType, Activity


class Device:

    def __init__(self, device_type: DeviceType, frequency=50):
        # immutable attributes
        self.device_type = device_type

        self.thread = None
        self.running = False

        # mutable attributes
        self.frequency = frequency

        # computed attributes
        self.buffer_lock = threading.Lock()
        self.source_lock = threading.Lock()
        self.source = None
        self.init_source(Activity.IDLE)
        self.buffer = []

    def init_source(self, activity):
        with self.source_lock:
            self.source = RandomDataSource(
                self.device_type,
                activity
            )
        print(f"Device {self.device_type.name} initialized with activity {activity.name}")

    def consume_data(self) -> list[DataPoint]:
        with self.buffer_lock:
            data = self.buffer
            self.buffer = []
        return data

    def loop(self):
        while self.running:
            # get data
            with self.source_lock:
                data = next(self.source)

            # add to buffer
            with self.buffer_lock:
                self.buffer.append(data)

            # sleep
            time.sleep(1 / self.frequency)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.loop)
        self.thread.start()
        print(f"Device {self.device_type.name} started")

    def stop(self):
        self.running = False
        self.thread.join()
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

    def __init__(self, activity: Activity):
        self.activity = activity
        self.devices = {
            DeviceType.E4: E4(),
            DeviceType.MUSE: Muse(),
            DeviceType.ZEPHYR: Zephyr(),
            DeviceType.EARBUDS: Earbuds(),
        }
        self.running = False

    def set_activity(self, activity: Activity):
        self.activity = activity
        self.update_device_activity()

    def get_activity(self):
        return self.activity

    def update_device_activity(self):
        for device in self.devices.values():
            device.init_source(self.activity)

    def start_device(self, device_type: DeviceType):
        self.devices[device_type].start()

    def stop_device(self, device_type: DeviceType):
        self.devices[device_type].stop()

    def is_device_running(self, device_type: DeviceType):
        return self.devices[device_type].running

    def consume_all_data(self):
        all_data = []
        for device in filter(lambda d: d.running, self.devices.values()):
            data = device.consume_data()
            if len(data) > 0:
                all_data.extend(data)
        return all_data
