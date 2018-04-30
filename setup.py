#!/usr/bin/env python3

"""setuptools installer script for TerraPi."""

import os
import platform
import shutil
import sys
from subprocess import call

from distutils.cmd import Command
from distutils.util import execute
from setuptools.command.install import install
from setuptools import setup, find_packages


class CustomInstall(install):
    """
    The sole purpose of this class is to make '--without-dashboard' a valid
    installation option.
    """

    user_options =  install.user_options + [
            ('without-dashboard', None, "Install without the dashboard"),
    ]

    def initialize_options(self):
        install.initialize_options(self)
        self.without_dashboard = None

    def finalize_options(self):
        install.finalize_options(self)

    def run(self):
        # XXX:  https://stackoverflow.com/questions/21915469/python-setuptools-install-requires-is-ignored-when-overriding-cmdclass
        #       https://github.com/pypa/setuptools/issues/456
        #install.run(self)
        install.do_egg_install(self)


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
        else:
            print("Not FreeBSD or Linux, nothing to do.")


def read_file(filename):
    """Returns the content of file named filename."""
    with open(filename, 'r') as f:
        return f.read()


def console_scripts():
    s = ['terrapi = TerraPi.terrapi:main']
    if '--without-dashboard' not in sys.argv:
        # see the XXX in install_requires()!
        #s.append('terrapi-dashboard = TerraPi.dashboard:main [dashboard]')
        s.append('terrapi-dashboard = TerraPi.dashboard:main')
    return s


def install_requires():
    """
    XXX: Adding terrapi-dashboard to the entry_points['console_scripts'] list
    does not install the 'dashboard' extra, as I would've expected. Until I
    can't figure out how this is supposed to work, I am merging
    extras_require['dashboard'] with install_requires in this function.
    """

    install_requires = [
        'Adafruit_DHT;(platform_machine=="armv6l" or platform_machine=="armv7l") and platform_system=="Linux"',
        'APScheduler',
        'PyYAML',
        'RPi.bme280',
        'RPi.GPIO;(platform_machine=="armv6l" or platform_machine=="armv7l") and platform_system=="Linux"',
        'SQLAlchemy',
        'pysispm',
        'pyusb'
    ]
    extras_require = {
        'dashboard': [
            'dash==0.21.0',
            'dash-renderer==0.12.1',
            'dash-html-components==0.10.0',
            'dash-core-components==0.22.1',
            'plotly==2.5.1',
            'pytz',
            'tzlocal',
        ]
    }
    if '--without-dashboard' not in sys.argv:
        install_requires = install_requires + extras_require['dashboard']
    return install_requires


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
        'install': CustomInstall,
        'install_rules': InstallRules,
    },
    
    # Need this because pysispm's setup.py imports sispm, which imports usb, so
    # it can't be built without pyusb.
    setup_requires=['pyusb'],
    
    dependency_links=[
        'git+https://github.com/adafruit/Adafruit_Python_DHT.git#egg=Adafruit_DHT',
    ],
    install_requires=install_requires(),
    package_data={
        '': ['conf/config-sample.yaml', 'data/.db_placeholder'],
    },
    entry_points={
        'console_scripts': console_scripts(),
    },
    python_requires='>=3.5',
)
