import logging
import sispm

from .device import ControllerDevice


class EnergenieUSBSwitch(ControllerDevice):
    """
    A switch that uses the Energenie EG-PMS and EG-PM2 USB-controllable power
    switches. You can have as many of these power switches as free USB ports you
    have. The individual devices are identified by an index or an ID, and the
    sockets are identified by the port number.

    :config device: Device index (0 for first power switch), or device ID (e.g. 
        '01:01:55:34:8e').
    """
    def __init__(self, app, config):
        super().__init__(app, config)
        
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

    def init_channel(self, channel):
        minport = sispm.getminport(self._device)
        maxport = sispm.getmaxport(self._device)
        if channel < minport or channel > maxport:
            raise IndexError("There is no port {} on device {}".format(
                channel, self._device)

    def control(self, channel, value):
        if value == 'on':
            sispm.switchon(self._device, channel)
        elif value == 'off':
            sispm.switchoff(self._device, channel)
        else:
            logging.warn("{} received invalid control value ({}).".format(
                self.name, value))
