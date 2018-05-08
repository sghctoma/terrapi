import logging
import random

from ..db import SensorType, Sensor
from .device import SensorDevice, ControllerDevice


class RandomTemperatureHumidity(SensorDevice):
    """
    Sensor device that returns random temperature and humidity measurements.
    For testing purposes only!
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

class DummySwitch(ControllerDevice):
    """
    A switch that switches nothing, only logs status changes.
    For testing purposes only!
    """
    def __init__(self, app, config):
        super().__init__(app, config)

    def control(self, channel, value):
        if value == 'on':
            logging.info("Switching {} channel {} on.".format(
                self.name, channel))
        elif value == 'off':
            logging.info("Switching {} channel {} off.".format(
                self.name, channel))
        else:
            logging.warn("{} received invalid control value ({}).".format(
                self.name, value))

