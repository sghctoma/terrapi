import logging
import RPi.GPIO as GPIO

from .device import ControllerDevice


class GPIOSwitch(ControllerDevice):
    """
    A switch that uses one GPIO pin to control the actual device (
    e.g. a relay).

    :config reversed: True if the device is off when GPIO is high
    """
    def __init__(self, app, config):
        super().__init__(app, config)
        if 'reversed' in config and config['reversed']:
            self._on_state = GPIO.LOW
            self._off_state = GPIO.HIGH
        else:
            self._on_state = GPIO.HIGH
            self._off_state = GPIO.LOW
        GPIO.setmode(GPIO.BCM)

    def init_channel(self, channel):
        GPIO.setup(channel, GPIO.OUT, initial=self._off_state)

    def control(self, channel, value):
        if value == 'on':
            GPIO.output(channel, self._on_state)
        elif value == 'off':
            GPIO.output(channel, self._off_state)
        else:
            logging.warn("{} received invalid control value ({}).".format(
                self.name, value))
