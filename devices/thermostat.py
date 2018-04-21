# DHT22 temperature and humidity sensor device module

import logging
from datetime import datetime

from db.db import SensorType
from devices.device import Device


class Thermostat(Device):
    def __init__(self, app, config):
        super().__init__(app, config)
        self._setup_temp_ranges(config)

        self._controller = Device.create_from_config(self._app,
                config['controller'])

        sensor = [d for d in self._app.sensor_devices if
                d.name==config['sensor']][0]
        sensor.add_callback(self.check_temp, SensorType.temperature)

    def _setup_temp_ranges(self, config):
        self._temp_ranges = {}
        temps = config['temperatures']
        for temp in temps:
            time_min, time_max = temp['time'].split('-')
            time_min = 0 if time_min == '' else int(time_min)
            time_max = 24 if time_max == '' else int(time_max)
            
            temp_min, temp_max = map(int, temp['temperature'].split('-'))
            for i in range(time_min, time_max):
                self._temp_ranges[i] = (temp_min, temp_max)

    def check_temp(self, temperature):
        current_hour = datetime.now().hour
        tmin, tmax = self._temp_ranges[current_hour]
        if temperature < tmin:
            logging.info('Switching on thermostat "%s" at %0.2fC.', self.name,
                    temperature)
            self._controller.switch_on()
        if temperature > tmax:
            logging.info('Switching off thermostat "%s" at %0.2fC.', self.name,
                    temperature)
            self._controller.switch_off()
