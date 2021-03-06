from __future__ import division

__author__ = 'Nathan Waddington'
__email__ = 'nathan.waddington@akqa.com'
__copyright__ = 'Copyright 2015 AKQA inc. All Rights Reserved'

# original scale code samples by andyseubert at:
__version__ = 'https://github.com/andyseubert/CoffeeScale'

import usb.core
import usb.util
import sys
import time
from time import localtime, strftime
import logging
from firebase_connector import firebase_paper_cup_counter
import datetime


class DymoScale(object):
    def __init__(self):
        self.VENDOR_ID = 0x0922  # dymo vendor
        self.PRODUCT_ID = 0x8004  # 25lb scale -- other dymo scales have different product_ids # Todo: find 10lb prod id
        self.DATA_MODE_GRAMS = 2
        self.DATA_MODE_OUNCES = 11

        self.debug = 0

        self.serialno = ''
        self.manufacturer = ''
        self.description = ''
        self.scales = []

        self.devices = usb.core.find(find_all=True, idVendor=self.VENDOR_ID)
        self.lastreading = []
        self.readmillis = 0

        self.CUP_WEIGHT_IN_G = 10.0  # We think that a cup weighs between 10g and 10.8g
        self.last_estimated_number_of_cups = 0
        self.differential = 0

        logging.basicConfig(filename='/home/pi/Paper-Cup-Counter/logs/current.log', filemode='a',
                            format='%(asctime)s.%(msecs)d,%(levelname)s,%(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.INFO)

        logging.info(
            "Paper Cup Counter Data Format: Date time, level, scale serial no, raw data reading, raw data units, " +
            "rounded reading in g, estimated current number of cups, differential")

        self.logger = logging.getLogger('PaperCupCounter')

    def connect_scales(self):
        # find the USB Dymo scale devices
        sys.stdout.write('There are ' + str(len(self.devices)) + ' scales connected!\n')

        i = 1
        for device in self.devices:
            scalename = "ChangeMyName " + str(i)
            print "scale #" + str(i)
            devbus = str(device.bus)
            devaddr = str(device.address)
            productid = str(device.idProduct)

            # help found here
            # http://stackoverflow.com/questions/5943847/get-string-descriptor-using-pyusb-usb-util-get-string
            self.serialno = str(usb.util.get_string(device, 256, 3))
            self.manufacturer = str(usb.util.get_string(device, 256, 1))
            self.description = str(usb.util.get_string(device, 256, 2))
            if self.debug:
                print self.serialno
                print self.manufacturer
                print self.description

        for i in range(0, len(self.devices)):
            self.lastreading.append(0)

    def monitor_scales(self):
        for i in range(0, len(self.devices)):

            time.sleep(.5)  # please only one reading per second

            id = str(i)

            for device in self.devices:
                if device.is_kernel_driver_active(0) is True:
                    device.detach_kernel_driver(0)
                devbus = str(device.bus)
                devaddr = str(device.address)
                productid = str(device.idProduct)
                try:
                    if str(usb.util.get_string(device, 256, 3)) == self.serialno:

                        # set USB device endpoint here
                        endpoint = device[0][(0, 0)][0]
                        # read a data packet
                        attempts = 10
                        data = None
                        while data is None:  # and attempts > 0:
                            try:
                                data = device.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)
                                if self.debug: print "data: " + str(data)
                            except usb.core.USBError as e:
                                data = None
                                if e.args == ('Operation timed out',):
                                    attempts -= 1
                                    print e
                                    continue

                        # The raw scale array data
                        raw_weight = data[4] + (256 * data[5])

                        if data[2] == self.DATA_MODE_OUNCES:
                            ounces = raw_weight * 0.1
                            reading = "%s,oz" % ounces
                        elif data[2] == self.DATA_MODE_GRAMS:
                            grams = raw_weight
                            reading = "%s,g" % grams

                        if self.debug: print "raw reading '" + reading + "'"

                        readval = float(reading.split(",")[0])
                        readunit = reading.split(",")[1]

                        # if the units are ounces ("oz") then convert to "g"
                        if readunit == "oz" and readval != 0:
                            readval = readval * 28.3495
                            readunit = "g"
                            if self.debug: print "converted oz to g"

                        if self.debug: print "current weight : '" + str(readval) + "' " + readunit
                        if self.debug: print "current time   : " + strftime("%Y-%m-%d %H:%M:%S", localtime())


                        # print '********'
                        # print str(readval) + ', ' + str(self.CUP_WEIGHT_IN_G) + ', ' + str(readval / self.CUP_WEIGHT_IN_G)

                        estnoofcups = readval / float(self.CUP_WEIGHT_IN_G)
                        # readval = round(readval)

                        # if self.debug: print "rounded read value is: " + str(readval)
                        if self.debug: print "est. no. of cups: " + str(estnoofcups)

                        # compare the cached value with the current value
                        if (readval != float(self.lastreading[i])) or (int(round(time.time() * 1000)) - self.readmillis) > 5:
                            # if different then update the database and update the cache

                            # determine the magnitude of the change here
                            delta = abs(readval - float(self.lastreading[i]))

                            # a small change of a few grams should not be noted
                            if 7 < int(delta) < 6000:
                                if readval != float(self.lastreading[i]):
                                    if self.debug:
                                        print "delta: " + str(delta) + " not ignoring"
                                        print "scale " + id + " reading changed from " + str(
                                            self.lastreading[i]) + " to " + str(readval)

                                    self.differential = round(estnoofcups) - self.last_estimated_number_of_cups

                                    # Log our data!
                                    logging.warning(self.serialno + "," + reading + "," + str(readval) + "," + str(
                                        round(estnoofcups)) + ',' + str(self.differential))

                                    timestamp = str(datetime.datetime.now())
                                    print timestamp + " " + self.serialno + "," + reading + "," + str(
                                        readval) + "," + str(round(estnoofcups)) + "," + str(self.differential)

                                    # send the data out to firebase.io
                                    paperCupCountJson = {'timestamp': timestamp, 'serialno': self.serialno,
                                                         'raw_data_reading': reading,
                                                         'rounded_data_reading': readval,
                                                         'estimated_no_cups': round(estnoofcups),
                                                         'differential': self.differential}

                                    firebase_paper_cup_counter.firebase_post(paperCupCountJson)

                                    # update last count
                                    self.last_estimated_number_of_cups = round(estnoofcups)

                                self.readmillis = int(round(time.time() * 1000))
                        else:
                            if self.debug: print "reading unchanged"
                        # set the last read value to the current read value
                        self.lastreading[i] = readval
                except usb.core.USBError as e:
                    print "usb core error:"
                    print e

    def cleanup(self):
        for device in self.devices:
            try:
                device.detach_kernel_driver(0)
            except Exception, e:
                pass
