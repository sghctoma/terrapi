import random

from ..db import SensorType, Sensor
from .device import SensorDevice


class RandomTemperatureHumidity(SensorDevice):
    """
    Sensor device that returns random temperature and humidity measurements.
    For testing purposes only!.
    """
    def __init__(self, app, config):
        super().__init__(app, config, [
            SensorType.temperature, 
            SensorType.humidity])

    def _measure(self):
        return [
            (SensorType.temperature, random.randint(18, 50)),
	    (SensorType.humidity, random.randint(30, 90)),
	]
