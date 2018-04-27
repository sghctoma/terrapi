import Adafruit_DHT

from .db import SensorType, Sensor
from .device import SensorDevice


class DHT11(SensorDevice):
    """
    DHT 11 temperature and humidity sensor implementation.

    :config gpio_pin: The BCM number of the GPIO pin
    """
    def __init__(self, app, config):
        super().__init__(app, config, [SensorType.temperature, SensorType.humidity])
        self._gpio_pin = config['gpio_pin']

    def _measure(self):
        h, t = Adafruit_DHT.read_retry(11, self._gpio_pin)
        return [(SensorType.humidity, h), (SensorType.temperature, t)]

class DHT22(SensorDevice):
    """
    DHT 22 temperature and humidity sensor implementation.

    :config gpio_pin: The BCM number of the GPIO pin
    """
    def __init__(self, app, config):
        super().__init__(app, config, [SensorType.temperature, SensorType.humidity])
        self._gpio_pin = config['gpio_pin']

    def _measure(self):
        h, t = Adafruit_DHT.read_retry(22, self._gpio_pin)
        return [(SensorType.humidity, h), (SensorType.temperature, t)]

class AMR2302(SensorDevice):
    """
    AMR2302 temperature and humidity sensor implementation.

    :config gpio_pin: The BCM number of the GPIO pin
    """
    def __init__(self, app, config):
        super().__init__(app, config, [SensorType.temperature, SensorType.humidity])
        self._gpio_pin = config['gpio_pin']

    def _measure(self):
        h, t = Adafruit_DHT.read_retry(2302, self._gpio_pin)
        return [(SensorType.humidity, h), (SensorType.temperature, t)]

