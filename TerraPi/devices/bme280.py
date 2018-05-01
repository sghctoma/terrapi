import smbus2
import bme280

from ..db import SensorType, Sensor
from .device import SensorDevice


class BME280(SensorDevice):
    """
    BME280 temperature, humidity and barometric pressure sensor implementation.

    :config address: I2C address (0x76 or 0x77, the former is the default)
    """
    def __init__(self, app, config):
        super().__init__(app, config, [
            SensorType.temperature, 
            SensorType.humidity,
            SensorType.pressure])
        self._address = config.get('address', 0x76)
        if self._address not in [0x76, 0x77]:
            raise ValueError("BME280 I2C address can only be 0x76 or 0x77!")

        self._bus = smbus2.SMBus(1)
        self._calibration_params = bme280.load_calibration_params(
                self._bus, self._address)

    def _measure(self):
        data = bme280.sample(self._bus, self._address, self._calibration_params)
        return [
            (SensorType.temperature, data.temperature),
            (SensorType.humidity, data.humidity),
            (SensorType.pressure, data.pressure)
        ]
