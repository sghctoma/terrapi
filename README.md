TerraPi
====

Introduction
----

TerraPi is a simple program that collects data from various sensors, and is able
to control devices based on measurements. I wrote it to monitor and control
heat, light and humidity in my pancake tortoises enclosure with a Raspberry Pi
Zero.

My initial goal was to to create something that is

* a simple daemon without a hardwired GUI or web interface.
* configurable from a text file. 
* easily extendable with new sensors, etc.

**WARNING**: *Please note that this is by no means "production ready"! I am using it to
control my enclosure, but it's still experimental.*

Architecture
----

The core of the program is a scheduler that fires up each *Sensor Device* at
configurable periods. Measurements from these devices are stored in a database.
This is all handled by the `SensorDevice` abtract class, so *Sensor Device*
implementations only need to subclass it, and override the `_measure` abstract
method.

It is important that one *Sensor Device* can have multiple sensors. For
example, the BME280 is a temperature, humidity and barometric pressure sensor in
one chip. These sensors are handled individually in the database (e.g. for each
configured BME280 device there will be 3 sensors in the database).

*Sensor Devices* have a list of callbacks, so *Controlled Devices* can
register themselves to get notified of measurements. For example, a thermostat
device can register itself to a temperature sensor, and receive the temperature
in its callback function every time the sensor is read.

Installation
----

TerraPi is a Python program so you are going to need Python, obviously. I wrote
it for Python 3, and it was not tested with Python 2.

To install the program you need to get the repo, and run setup.py:

```
pi@raspberrypi:~ $ git clone https://github.com/sghctoma/terrapi
pi@raspberrypi:~ $ cd terrapi
pi@raspberrypi:~ $ python3 setup.py install
```

This will install all dependencies, and create two scripts:

* `terrapi`: the main program
* `terrapi-dashboard`: a web dashboard to show interactive measurement diagrams.
  This script is completely decoupled from the TerraPi daemon, it just uses the
  same database. The databse connection string is read from the TerraPi
  configuration.

You can opt-out of installing the latter by using the `--without-dashboard`
switch:

```
pi@raspberrypi:~ $ python3 setup.py install --without-dashboard
```

You can run TerraPi right after installing, but the provided sample
configuration only spits random values into the database, and switches a GPIO on
and off. You will learn how to set up your sensors and other devices in the
[Configuration](#configuration) section.

### Additional steps for databases other than SQLite

TerraPi uses a local SQLite database by default, but you can use any database
servers supported by SQLAlchemy. In order to do so, you have to set up a
database for TerraPi. Here is how you can do it with PostgreSQL:

```
pi@raspberrypi:~ $ su - postgres
postgres@raspberrypi:~$ createdb terrapidb
postgres@raspberrypi:~$ createuser terrapiusr
postgres@raspberrypi:~$ psql
psql (9.6.7)
Type "help" for help.

postgres=# alter user terrapiusr with encrypted password 'terrapi';
ALTER ROLE
postgres=# grant all privileges on database terrapidb to terrapiusr;
GRANT
postgres=#
```

### Additional steps for Energenie USB power switches

If you want to use the Energenie USB power switches, and don't want to run
TerraPi as root (which I strongly suggest), you are going to need to install the
udev (for Linux) or devd (for FreeBSD) rules, and create the `sispmctl` group.
The `install_rules` setup command does this for you:

```
pi@raspberrypi:~ $ sudo python3 setup.py install_rules
```

After this you will still need to add the user you plan to run TerraPi with to
the `sispmctl` group:

```
pi@raspberrypi:~ $ sudo usermod -a -G sispmctl terrapi
```


Configuration
----

Configuration is done in a YAML file that has four main sections:

* global: Settings used by multiple devices go here. Currently only the database
  connection string is in the global scope.
* `sensor_devices`: A list of *Sensor Device* configurations
* `controlled_devices`: A list of *Controlled Device* configurations
* `logging`: Logging configuration. Please refer to the [Configuration dictionary schema](https://docs.python.org/3/library/logging.config.html#logging-config-dictschema) in the Python documentation for a complete reference.

TerraPi tries to find the configuration in the following places and order:

1. The first command line argument.
2. A file named .terrapi.yaml under the current user's home directory.
3. A file named .config/terrapi/config.yaml under the current user's home
   directory.
4. The file named conf/config-sample.yaml under the package directory of
   TerraPi.

These files are not used in an incremental fashion, the first one found is the
configuration. The provided `config-sample.conf` file gives an example of how
the configuration file should look like, but it does nothing meaningful.

The following tables describe the settings for all available devices. Settings
in **`bold`** are required, the `others` are optional.

### Global settings

Setting | Description
--- | ---
`connection_string` | Database connection string. The program uses SQLAlchemy, so in theory it is compatible with a wide range of databases. It has been tested only with PostgreSQL and SQLite though.<br />By default an SQLite database (data/terrapi.db under the TerraPi package directory) is used.

### Device common settings

Setting | Description
--- | ---
**`type`** | The device type in the format `module.class` relative to the `devices` package. E.g. `dht.DHT22` for the DHT22 sensor device.
`name` | An arbitrary, but unique name.<br />Default is <module.class>_<type4 UUID>.
`description` | A short description that is stored in the database along with the name and type of the sensor.

### Sensor device common settings

Setting | Description
--- | ---
`schedule` | It's either a number, or a cron-style schedule specification. In case it's a number, it is interpreted as a period in minutes, and in case of a cron-style schedule specification, please refer to `man 5 crontab`. Jobs are automatically added to the scheduler, device module writers do not need to bother with it (they just need to subclass `SensorDevice`).<br />Default is a 5 minute period.

### Controlled device common settings

Setting | Description
--- | ---
**`controller`** | What kind of *Controller Device* to use. Currently only the `controller.GPIOSwitch` is implemented, which simply uses a GPIO to control a device (probably through a relay).

### Sensor devices

#### bme280.BME280

[BME280](https://www.bosch-sensortec.com/bst/products/all_products/bme280) is a
temperature, humidity and barometric pressure sensor. It supports both SPI and
I2C interfaces, but TerraPi currently supports only I2C (SPI is used for the
MPC3008 ADC).

Setting | Description
--- | ---
`address` | The I2C address of the BME280 sensor. The chip can be configured to use 0x77 instead of the default 0x76. This means that only two of these devices can be used on one I2C bus!<br />The default is 0x76.

#### dht.DHT11, dht.DHT22, dht.AMR2302

[DHT11, DHT22, and AMR2302](https://cdn-learn.adafruit.com/downloads/pdf/dht.pdf)
are temperature and humidity sensors. These devices use one GPIO to communicate.

Setting | Description
--- | ---
**`gpio_pin`** | The BCM number of the GPIO pin used to communicate with the device.

### Controller devices

#### controller.GPIOSwitch

This device uses one GPIO to control some other devices probably via a relay board.

Setting | Description
--- | ---
**`gpio_pin`** | The BCM number of the GPIO pin used to communicate with the device.
`reversed` | `True` if the device is off when GPIO is high, `False` otherwise.<br />The default is `True`.

#### controller.EnergenieUSBSwitch

This device uses an Energenie EG-PMS or EG-PM2 USB programmable power switch to
control some other devices (e.g. lamps, heaters, etc.). You can have as many of
these power switches as free USB ports you have. The individual devices are
identified by an index or an ID, and the sockets are identified by the port
number.

Setting | Description
--- | ---
`device` | Either an integer (device index), or a string (device ID, e.g. '01:01:55:34:8e') that identifies the particular power switch to use.<br />Default value: 0 (the first power switch connected to the system).
**`port`** | The number of the socket to control. Sockets are labeled with these numbers on the actual device.

### Controlled devices

#### light.Lightswitch

This *Controlled Device* is used to switch lights on and off, but can be used
for anything that needs an on and off schedule. I control a modified ZooMed
UVB/LED Terrarium Hood with this.

Setting | Description
--- | ---
**`off_schedule`** | Typically this will be a cron-style schedule specification for when the lights turn off. You can also give an integer, which will be interpreted as a period in minutes.
**`on_schedule`** | Typically this will be a cron-style schedule specification for when the lights turn on. You can also give an integer, which will be interpreted as a period in minutes.

#### thermostat.Thermostat

This *Controlled Device* acts as a thermostat (switches things on and off based
on temperature.

Setting | Description
--- | ---
**`sensor`** | The `name` of the temperature sensor you want to use.
**`temperatures`** | A list of `time` and `temperature` pairs, so you can specify acceptable temperature ranges for time ranges. Time ranges can be open-ended, so for example the following means temperature should be between 28 and 30 Celsius from 12:00 to 20:00, and between 20 and 25 Celsius in the remaining time:<br />`temperatures:`<br />&nbsp;`-time: "-12"`<br />&nbsp;&nbsp;`temperature: 28-30`<br />&nbsp;`-time: "20-"`<br />&nbsp;&nbsp;`temperature: "20-25"`. The time ranges should cover a whole day (24 hours)!

Todo
----

There are a lot of things I want to do with this tool. Just to name a few:

* I would like to store device state switches, so that I know when a controlled
  device is on and off. This could be useful for e.g. a thermostat.
* *Controller Devices* probably should get their own main section in the future,
  so that multiple *Controlled Devices* can use the same controller.
