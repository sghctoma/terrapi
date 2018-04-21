# BME280 temperature, humidity and barometric pressure sensor device module

from db.db import SensorType, Sensor
from devices.device import SensorDevice
from devices.lib import bme280


class BME280(SensorDevice):
    def __init__(self, app, config):
        super().__init__(app, config, [
            SensorType.temperature, 
            SensorType.humidity,
            SensorType.pressure])
        self._address = config['address']

    def _measure(self):
        t,p,h = bme280.readBME280All(addr=self._address)
        return [
            (SensorType.temperature, t),
	    (SensorType.humidity, h),
	    (SensorType.pressure, p)
	]
