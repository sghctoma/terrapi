import logging

from .device import ControlledDevice


class Lightswitch(ControlledDevice):
    """
    Light on-off switch implementation.

    :config off_schedule: Lights off schedule.
    :config on_schedule: Lights on schedule.
    """
    def __init__(self, app, config):
        super().__init__(app, config)
        self._setup_schedule(config)

    def _setup_schedule(self, config):
        sched_on = config['on_schedule']
        sched_off = config['off_schedule']
        job_on = self._app.scheduler.add_job(self._switch_on,
                trigger=self._parse_trigger(sched_on))
        job_off = self._app.scheduler.add_job(self._switch_off,
                trigger=self._parse_trigger(sched_off))

    def _switch_off(self):
        logging.info("Switching off light {}.".format(self.name))
        self._controller.control(self._channel, 'off')

    def _switch_on(self):
        logging.info("Switching on light {}.".format(self.name))
        self._controller.control(self._channel, 'on')
