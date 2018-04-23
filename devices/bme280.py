# BME280 temperature, humidity and barometric pressure sensor device module

from db.db import SensorType, Sensor
from devices.device import SensorDevice
from devices.lib import bme280


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
        if 'address' in config:
            self._address = config['address']
        else
            self._address = 0x76

    def _measure(self):
        t,p,h = bme280.readBME280All(addr=self._address)
        return [
            (SensorType.temperature, t),
	    (SensorType.humidity, h),
	    (SensorType.pressure, p)
	]
