import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class DeviceType(Enum):
    E4 = 1
    MUSE = 2
    ZEPHYR = 3
    EARBUDS = 4


class Activity(Enum):
    IDLE = 1
    WALKING = 2
    RUNNING = 3


@dataclass
class DataPoint:
    timestamp: datetime
    device: DeviceType
    x: float
    y: float
    z: float

    def to_dict(self):
        return {
            'timestamp': self.timestamp.isoformat(),
            'device': self.device.name,
            'x': self.x,
            'y': self.y,
            'z': self.z
        }

    def __str__(self):
        return str(self.to_dict())


@dataclass
class Distribution:
    mean: float
    std: float
    min: float
    max: float


class RandomDataSource:

    def __init__(self, device_type, activity):
        self.device_type = device_type
        self.activity = activity

        # define distributions for each device type and activity
        self.x_dist = Distribution(0, 1, -1, 1)
        self.y_dist = Distribution(0, 1, -1, 1)
        self.z_dist = Distribution(0, 1, -1, 1)

    def get_data(self) -> DataPoint:
        # generate x, y, z datapoints based on the distribution
        x = random.gauss(self.x_dist.mean, self.x_dist.std)
        y = random.gauss(self.y_dist.mean, self.y_dist.std)
        z = random.gauss(self.z_dist.mean, self.z_dist.std)

        # create a datapoint
        data_point = DataPoint(
            timestamp=datetime.now(),
            device=self.device_type,
            x=x,
            y=y,
            z=z
        )

        return data_point

    def __next__(self):
        return self.get_data()
