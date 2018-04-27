#!/usr/bin/env python3

import logging
import pkg_resources
import sys
import yaml
from logging.config import dictConfig
from os.path import expanduser, isfile

import RPi.GPIO as GPIO
from apscheduler.schedulers.blocking import BlockingScheduler

from .db import Measurement, create_sessionmaker
from .devices.device import Device, SensorDevice


class TerrapiApp():
    def __init__(self, config):
        connection_string = config.get('connection_string')
        if not connection_string:
            logging.info("Database configuration not found, using SQLite.")
            database = pkg_resources.resource_filename('TerraPi',
                    'data/terrapi.db')
            connection_string = 'sqlite:///%s' % database
        self.sessionmaker = create_sessionmaker(connection_string)

        self.scheduler = BlockingScheduler(
                daemon=False,
                job_defaults={'misfire_grace_time':10})

        confs = config.get('sensor_devices', [])
        self.sensor_devices = [
                SensorDevice.create_from_config(self, c) for c in confs]
        self.sensor_devices = list(filter(None, self.sensor_devices))

        confs = config.get('controlled_devices', [])
        self.controlled_devices = [
                Device.create_from_config(self, c) for c in confs]
        self.controlled_devices = list(filter(None, self.controlled_devices))

        if not self.sensor_devices and not self.controlled_devices:
            logging.warn("There are no devices in the configuration file!")
    
    def main(self):
        self.scheduler.start()
        GPIO.cleanup()


def main():
    config_paths = []
    if len(sys.argv) > 1:
        config_paths.append(sys.argv[1])
    config_paths.append(expanduser('~') + '/.terrapi.yaml')
    config_paths.append(expanduser('~') + '/.config/terrapi/config.yaml')
    config_paths.append(pkg_resources.resource_filename('TerraPi',
        'conf/config-sample.yaml'))
    for path in config_paths:
        if isfile(path):
            configfile = path
            break
    if not configfile:
        logging.error("No config file found! Exiting..")
        sys.exit(1)
    with open(configfile, 'r') as stream:
        config = yaml.load(stream)
    if not config:
        logging.error("Empty configuration! Exiting...")
        sys.exit(1)

    if config['logging']:
        dictConfig(config['logging'])

    app = TerrapiApp(config)
    app.main()


if __name__ == "__main__":
    main()
