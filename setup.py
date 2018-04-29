#!/usr/bin/env python3

"""setuptools installer script for TerraPi."""

import os
import platform
import shutil
from subprocess import call

from distutils.cmd import Command
from distutils.util import execute
from setuptools.command.install import install
from setuptools import setup, find_packages


class InstallRules(Command):
    """
    A custom command to install udev (for Linux) or devd (for FreeBSD) rules
    that allow access to Energenie USB devices to the group 'sispmctl'.
    """

    description = "install udev or devd rules (requires root privileges)"
    user_options = []

    udev_reload = ['udevadm', 'control', '--reload-rules']
    udev_trigger = ['udevadm', 'trigger', '--subsystem-match=usb',
          '--attr-match=idVendor=04b4', '--action=add']
    devd_restart = ['service', 'devd', 'restart']
    linux_create_group = ['groupadd', 'sispmctl']
    fbsd_create_group = ['pw', 'groupadd', 'sispmctl']

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        system = platform.system()
        if os.getuid() != 0 and system in ['Linux', 'FreeBSD']:
            raise OSError(
                    'You must have root privileges to install udev/devd rules!')
        if system == 'Linux':
            shutil.copy('resources/60-sispmctl.rules', '/etc/udev/rules.d/')
            execute(lambda: call(self.linux_create_group), [],
                    "Creating sispmctl group")
            execute(lambda: call(self.udev_reload), [], "Reloading udev rules")
            execute(lambda: call(self.udev_trigger), [], "Triggering udev rules")
        elif system == 'FreeBSD':
            shutil.copy('resources/sispmctl.conf', '/usr/local/etc/devd/')
            execute(lambda: call(self.fbsd_create_group), [],
                    "Creating sispmctl group")
            execute(lambda: call(self.devd_restart), [], "Restarting devd")


class TerraPiInstall(install):
    def run(self):
        install.run(self)
        if platform.system() == 'Linux':
            self.run_command('udev_rules')
        elif platform.system() == 'FreeBSD':
            self.run_command('devd_rules')


def read_file(filename):
    """Returns the content of file named filename."""
    with open(filename, 'r') as f:
        return f.read()


setup(
    name="TerraPi",
    version="0.1.0",
    description='TberraPi is a terrarium control software for the Raspberry Pi',
    long_description=read_file('README.md'),
    url='https://github.com/sghctoma/terrapi',
    author='sghctoma',
    author_email='sghctoma@gmail.com',
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: BSD',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Home Automation',
    ],
    keywords='terrarium automation thermostat sensor',
    packages=find_packages(),
    cmdclass={
        'rules': InstallRules,
        'install': TerraPiInstall,
    },
    
    # Need this because pysispm's setup.py imports sispm, which imports usb, so
    # it can't be built without pyusb.
    setup_requires=['pyusb'],
    
    dependency_links=[
        'git+https://github.com/adafruit/Adafruit_Python_DHT.git#egg=Adafruit_DHT',
    ],
    install_requires=[
        'Adafruit_DHT;(platform_machine=="armv6l" or platform_machine=="armv7l") and platform_system=="Linux"',
        'APScheduler',
        'PyYAML',
        'RPi.bme280',
        'RPi.GPIO',
        'SQLAlchemy',
        'pysispm',
        'pyusb'
    ],
    extras_require={
        'dashboard': [
            'dash==0.21.0',
            'dash-renderer==0.12.1',
            'dash-html-components==0.10.0',
            'dash-core-components==0.22.1',
            'plotly',
            'pytz',
            'tzlocal',
        ]
    },
    package_data={
        '': ['conf/config-sample.yaml', 'data/.db_placeholder'],
    },
    entry_points={
        'console_scripts': [
            'terrapi = TerraPi.terrapi:main',
            'terrapi-dashboard = TerraPi.dashboard:main [dashboard]',
        ]
    },
    python_requires='>=3.5',
)
