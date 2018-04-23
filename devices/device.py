# Device factory module

import importlib
import logging
from abc import ABC, abstractmethod

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

from db.db import Sensor, Measurement


class Device():
    """
    Generic device class that provides a factory interface to create device
    instances from configuration.

    :config type: The device type in the format `module.class` relative to the
        `devices` package
    :config name: An arbitrary, but unique name
    :config description: A short description that is stored in the database
    """
    def __init__(self, app, config):
        """
        Constructs a new 'Device' object.

        :param app: The TerrapiApp instance
        :param config: The config that describes the device
        """
        self.name = config['name'] if 'name' in config else None
        self._app = app

    def _parse_trigger(self, schedule):
        """
        Creates an APScheduler trigger from a schedule specification.
        
        :param schedule: Schedule specification (minutes or cron-style)
        :return: An APScheduler trigger
        """
        if type(schedule) is int:
            trigger = IntervalTrigger(minutes=schedule)
        elif type(schedule) is str:
            trigger = CronTrigger.from_crontab(schedule)
        return trigger

    @staticmethod
    def create_from_config(app, config):
        """
        Creates a Device instant from configuration.
        
        :param config: The config that describes the device
        """
        typ = config['type'].split('.')
        clazz = getattr(importlib.import_module('devices.'+typ[0]), typ[1])
        return clazz(app, config)

class SensorDevice(Device, ABC):
    """
    Abstract class that represents a sensor device.

    :config schedule: Period in minutes or cron-style schedule for measurements.
    """
    def __init__(self, app, config, sensor_types):
        """
        Constructs a new 'SensorDevice' object.

        :param app: The TerrapiApp instance
        :param config: The config that describes the device
        :param sensor_types: A list of SensorType values that specify what kind
            of measurements it can do
        """
        super().__init__(app, config)

        self._callbacks = {}
        self._sensors = {}
        self._setup_sensors(config, sensor_types)
        self._setup_schedule(config)

    def _setup_schedule(self, config):
        """
        Adds a job to the scheduler based on config.
        
        :param config: The config that describes the device
        """
        sched = config['schedule']
        self._app.scheduler.add_job(self._refresh,
                trigger=self._parse_trigger(sched))

    def _setup_sensors(self, config, sensor_types):
        """
        Retrieves the Device's sensors from database, or create them if they
        do not exist yet.

        :param config: The config that describes the device
        :param sensor_types: A list of SensorType values that specify what kind
            of measurements it can do
        """
        session = self._app.sessionmaker()
        for sensor_type in sensor_types:
            try:
                sensor = session.query(Sensor).filter(
                        Sensor.name==config['name']).filter(
                        Sensor.type==sensor_type).one()
            except NoResultFound:
                sensor = Sensor(
                        name=config['name'],
                        type=sensor_type,
                        description=config['description'])
                session.add(sensor)
                session.commit()
            self._sensors[sensor_type] = sensor.id
        session.close()

    def add_callback(self, callback, sensor_type):
        """
        Registers a callback function with one of the device's sensors.

        :param callback: The callback function with the signature
            callback(measurement)
        :param sensor_type: Specifies hich sensor the callback should be
            registered to.
        """
        if sensor_type in self._callbacks:
            self._callbacks[sensor_type].append(callback)
        else:
            self._callbacks[sensor_type] = [callback]

    def _refresh(self):
        """Handles database insertion and calls callbacks."""
        session = self._app.sessionmaker()
        for sensor_type, value in self._measure():
            if not value:
                logging.warn('Null value received as measurement!')
                continue

            session.add(Measurement(
                sensor_id=self._sensors[sensor_type],
                value=value))
            if sensor_type in self._callbacks:
                for callback in self._callbacks[sensor_type]:
                    callback(value)
        try:
            session.commit()
        except SQLAlchemyError:
            logging.exception('Could not store measurement in database!')
            session.rollback()
        finally:
            session.close()

    @abstractmethod
    def _measure():
        """
        Returns measurements from device. Should be overriden in subclasses.

        :return: A list of Measurement objects
        """
        pass

