#!/usr/bin/env python3

"""setuptools installer script for TerraPi."""

from setuptools import setup, find_packages


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
    install_requires=[
        'Adafruit_DHT',
        'APScheduler',
        'PyYAML',
        'RPi.bme280',
        'RPi.GPIO',
        'SQLAlchemy',
        'pysispm',
        'pytz',
        'pyusb'
        'tzlocal',
    ],
    package_data={
        '': ['conf/config-sample.yaml', 'data/.db_placeholder'],
    },
    entry_points={
        'console_scripts': [
            'terrapi = TerraPi.terrapi:main',
            'terrapi-dashboard = TerraPi.dashboard:main',
        ]
    },
    python_requires='>=3.5',
)
