import logging
import RPi.GPIO as GPIO

from .device import ControllerDevice


class GPIOSwitch(ControllerDevice):
    """
    A switch that uses one GPIO pin to control the actual device (
    e.g. a relay).

    :config gpio_pin: The BCM number of the controlling GPIO pin
    :config reversed: True if the device is off when GPIO is high
    """
    def __init__(self, app, config):
        super().__init__(app, config)
        self._gpio_pin = config['gpio_pin']
        if 'reversed' in config and config['reversed']:
            self._on_state = GPIO.LOW
            self._off_state = GPIO.HIGH
        else:
            self._on_state = GPIO.HIGH
            self._off_state = GPIO.LOW
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._gpio_pin, GPIO.OUT, initial=self._off_state)

    def control(self, value):
        if value == 'on':
            GPIO.output(self._gpio_pin, self._on_state)
        elif value == 'off':
            GPIO.output(self._gpio_pin, self._off_state)
        else:
            logging.warn("{} received invalid control value ({}).".format(
                self.name, value))
