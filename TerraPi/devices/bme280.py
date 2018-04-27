from ..db import SensorType, Sensor
from .device import SensorDevice
from ..lib.bme280 import readBME280All


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
            raise AttributeError("BME280 I2C address can only be 0x76 or 0x77!")

    def _measure(self):
        t,p,h = readBME280All(addr=self._address)
        return [
            (SensorType.temperature, t),
	    (SensorType.humidity, h),
	    (SensorType.pressure, p)
	]
