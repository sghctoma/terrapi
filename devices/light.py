# Light on-off timer module

import logging

from devices.device import Device


class Lightswitch(Device):
    def __init__(self, app, config):
        super().__init__(app, config)
        self._setup_schedule(config)
        self._controller = Device.create_from_config(self._app,
                config['controller'])

    def _setup_schedule(self, config):
        sched_on = config['on_schedule']
        sched_off = config['off_schedule']
        self._app.scheduler.add_job(self._switch_on,
                trigger=self._parse_trigger(sched_on))
        self._app.scheduler.add_job(self._switch_off,
                trigger=self._parse_trigger(sched_off))

    def _switch_off(self):
        logging.info('Switching off light "%s".', self.name)
        self._controller.switch_off()

    def _switch_on(self):
        logging.info('Switching on light "%s".', self.name)
        self._controller.switch_on()
