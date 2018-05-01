import logging
import RPi.GPIO as GPIO
import sispm

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

class EnergenieUSBSwitch(ControllerDevice):
    """
    A switch that uses the Energenie EG-PMS and EG-PM2 USB-controllable power
    switches. You can have as many of these power switches as free USB ports you
    have. The individual devices are identified by an index or an ID, and the
    sockets are identified by the port number.

    :config device: Device index (0 for first power switch), or device ID (e.g. 
        '01:01:55:34:8e').
    :config port: Port number (1-4 for EG-PM2)
    """
    def __init__(self, app, config):
        super().__init__(app, config)
        self._port = config['port']
        
        dev = config.get('device', 0)
        devices = sispm.connect()
        if not devices:
            raise ConnectionError("No Energenie USB devices found!")
        if type(dev) is int:
            if dev < 0 or dev >= len(devices):
                raise IndexError("Invalid device index!")
            self._device = devices[dev]
        elif type(dev) is str:
            d = [d for d in devices if sispm.getid(d)==dev]
            if not d:
                raise ValueError("Invalid device ID!")
            self._device = d[0]

        minport = sispm.getminport(self._device)
        maxport = sispm.getmaxport(self._device)
        if self._port < minport or self._port > maxport:
            raise IndexError("There is no port {} on device {}".format(
                self._port, self._device))

    def control(self, value):
	if value == 'on':
	    sispm.switchon(self._device, self._port)
	elif value == 'off':
	    sispm.switchoff(self._device, self._port)
	else:
	    logging.warn("{} received invalid control value ({}).".format(
		self.name, value))
