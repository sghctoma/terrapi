import logging
from datetime import datetime

from ..db import SensorType
from .device import ControlledDevice


class Thermostat(ControlledDevice):
    def __init__(self, app, config):
        super().__init__(app, config)
        self._setup_temp_ranges(config)
        s = config['sensor']
        sensors = [d for d in self._app.sensor_devices if d.name==s]
        if not sensors:
            raise AttributeError(
                    "{} tried to set a callback for non-existing sensor {}.".
                    format((self.name, s)))

        sensors[0].add_callback(self.check_temp, SensorType.temperature)

    def _setup_temp_ranges(self, config):
        self._temp_ranges = {i:'x' for i in range(24)}
        temps = config['temperatures']
        for temp in temps:
            time_min, time_max = temp['time'].split('-')
            time_min = 0 if time_min == '' else int(time_min)
            time_max = 24 if time_max == '' else int(time_max)
            
            temp_min, temp_max = map(int, temp['temperature'].split('-'))
            for i in range(time_min, time_max):
                self._temp_ranges[i] = (temp_min, temp_max)

        if 'x' in self._temp_ranges.values():
            raise ValueError("Temperature ranges for {} should cover an \
                    entire day (24 hours).".format(self.name))

    def check_temp(self, temperature):
        current_hour = datetime.now().hour
        tmin, tmax = self._temp_ranges[current_hour]
        if temperature < tmin:
            logging.info('Switching on thermostat {} at {:.2f}C.'.format(
                self.name, temperature))
            self._controller.control(self._channel, 'on')
        if temperature > tmax:
            logging.info('Switching off thermostat {} at {:.2f}C.'.format(
                self.name, temperature))
            self._controller.control(self._channel, 'off')
