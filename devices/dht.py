# DHT22 temperature and humidity sensor device module

import Adafruit_DHT

from db.db import SensorType, Sensor
from devices.device import SensorDevice


class DHT11(SensorDevice):
    def __init__(self, app, config):
        super().__init__(app, config, [SensorType.temperature, SensorType.humidity])
        self._gpio_pin = config['gpio_pin']

    def _measure(self):
        h, t = Adafruit_DHT.read_retry(11, self._gpio_pin)
        return [(SensorType.humidity, h), (SensorType.temperature, t)]

class DHT22(SensorDevice):
    def __init__(self, app, config):
        super().__init__(app, config, [SensorType.temperature, SensorType.humidity])
        self._gpio_pin = config['gpio_pin']

    def _measure(self):
        h, t = Adafruit_DHT.read_retry(22, self._gpio_pin)
        return [(SensorType.humidity, h), (SensorType.temperature, t)]

class AMR2302(SensorDevice):
    def __init__(self, app, config):
        super().__init__(app, config, [SensorType.temperature, SensorType.humidity])
        self._gpio_pin = config['gpio_pin']

    def _measure(self):
        h, t = Adafruit_DHT.read_retry(2302, self._gpio_pin)
        return [(SensorType.humidity, h), (SensorType.temperature, t)]

