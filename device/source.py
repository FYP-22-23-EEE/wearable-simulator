import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class DeviceType(Enum):
    E4 = 1
    MUSE = 2
    ZEPHYR = 3
    EARBUDS = 4

    @classmethod
    def from_string(cls, s):
        if s.lower() == 'e4':
            return cls.E4
        elif s.lower() == 'muse':
            return cls.MUSE
        elif s.lower() == 'zephyr':
            return cls.ZEPHYR
        elif s.lower() == 'earbuds':
            return cls.EARBUDS

    def __str__(self):
        return self.name.lower()


class Activity(Enum):
    SITTING = 1
    STANDING = 2
    WALKING = 3
    RUNNING = 4

    @classmethod
    def from_string(cls, s):
        if s.lower() == 'sitting':
            return cls.SITTING
        elif s.lower() == 'standing':
            return cls.STANDING
        elif s.lower() == 'walking':
            return cls.WALKING
        elif s.lower() == 'running':
            return cls.RUNNING

    def __str__(self):
        return self.name.lower()


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


distributions_x = {
    Activity.SITTING: Distribution(mean=1.0, std=0.1, min=0.0, max=2.0),
    Activity.STANDING: Distribution(mean=3.0, std=0.1, min=2.1, max=4.0),
    Activity.WALKING: Distribution(mean=5.0, std=0.3, min=4.1, max=7.0),
    Activity.RUNNING: Distribution(mean=9.0, std=0.5, min=7.1, max=12.0)
}
distributions_y = {
    Activity.SITTING: Distribution(mean=1.0, std=0.1, min=12.1, max=14.0),
    Activity.STANDING: Distribution(mean=3.0, std=0.1, min=14.1, max=16.0),
    Activity.WALKING: Distribution(mean=5.0, std=0.3, min=16.1, max=19.0),
    Activity.RUNNING: Distribution(mean=9.0, std=0.5, min=19.1, max=24.0)
}
distributions_z = {
    Activity.SITTING: Distribution(mean=1.0, std=0.1, min=24.1, max=26.0),
    Activity.STANDING: Distribution(mean=3.0, std=0.1, min=26.1, max=28.0),
    Activity.WALKING: Distribution(mean=5.0, std=0.3, min=28.1, max=31.0),
    Activity.RUNNING: Distribution(mean=9.0, std=0.5, min=31.1, max=36.0)
}


class RandomDataSource:

    def __init__(self, device_type, activity: Activity):
        self.device_type = device_type
        self.activity = activity

        # define distributions for each device type and activity
        self.x_dist = distributions_x[activity]
        self.y_dist = distributions_y[activity]
        self.z_dist = distributions_z[activity]

    def get_data(self) -> DataPoint:
        # generate x, y, z datapoints based on the distribution
        x = random.uniform(self.x_dist.min, self.x_dist.max)
        y = random.uniform(self.y_dist.min, self.y_dist.max)
        z = random.uniform(self.z_dist.min, self.z_dist.max)

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
