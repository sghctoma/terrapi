# Controller devices module

import RPi.GPIO as GPIO

from devices.device import Device


class GPIOSwitch(Device):
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

    def switch_on(self):
        GPIO.output(self._gpio_pin, self._on_state)

    def switch_off(self):
        GPIO.output(self._gpio_pin, self._off_state)

