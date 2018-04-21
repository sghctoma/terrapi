#!/usr/bin/env python3

import logging
import sys
import yaml

import RPi.GPIO as GPIO
from apscheduler.schedulers.blocking import BlockingScheduler

from db.db import Measurement, create_sessionmaker
from devices.device import Device, SensorDevice


class TerrapiApp():
    def __init__(self, configfile):
        with open(configfile, 'r') as stream:
            config = yaml.load(stream)
        self.sessionmaker = create_sessionmaker(config['connection_string'])
        self.scheduler = BlockingScheduler(
                daemon=False,
                job_defaults={'misfire_grace_time':10})

        self.sensor_devices = []
        for device_conf in config['sensor_devices']:
            d = SensorDevice.create_from_config(self, device_conf)
            self.sensor_devices.append(d)

        self.controlled_devices = []
        for device_conf in config['controlled_devices']:
            d = Device.create_from_config(self, device_conf)
            self.controlled_devices.append(d)
    
    def main(self):
        logging.basicConfig()
        self.scheduler.start()
        GPIO.cleanup()
    
if __name__ == "__main__":
    logging.basicConfig(filename='terrapi.log', level=logging.INFO)
    app = TerrapiApp(sys.argv[1] if len(sys.argv) > 1 else 'config.yaml')
    app.main()
