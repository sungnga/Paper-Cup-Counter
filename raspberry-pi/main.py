#!/usr/bin/python

__author__ = 'Nathan Waddington'
__email__ = 'nathan.waddington@akqa.com'
__copyright__ = 'Copyright 2015 AKQA inc. All Rights Reserved'
__version__ = ''

from time_utilities.timeUtil import TimeUtil
import RPi.GPIO as GPIO
from scale_driver.dymo_usb import *

ds = DymoScale()


def main():
    """main"""
    # main setup

    # time = TimeUtil()

    ds.connect_scales()
    ds.cleanup()

    # main loop
    while True:
        ds.monitor_scales()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("KeyboardInterrupt.")
        ds.cleanup()
        GPIO.cleanup()
