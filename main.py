#!/usr/bin/python

__author__ = 'Nathan Waddington'
__email__ = 'nathan.waddington@akqa.com'
__copyright__ = 'Copyright 2015 AKQA inc. All Rights Reserved'
__version__ = ''

from time_utilities.timeUtil import TimeUtil

def main():
    """main"""
    # main setup
    time = TimeUtil()

    # main loop
    while True:
        pass
        # coffeeMachine1.count()
        # coffeeMachine2.count()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("KeyboardInterrupt.")
        GPIO.cleanup()
