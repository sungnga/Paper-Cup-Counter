__author__ = 'nathan.waddington'
__version__ = 'https://www.raspberrypi.org/forums/viewtopic.php?f=44&t=53437'

debug = True

VENDOR_ID = 0x0922
devices = usb.core.find(find_all=True, idVendor=VENDOR_ID)

for device in devices:
    if device.is_kernel_driver_active(0) is True:
        device.detach_kernel_driver(0)
    devbus = str(device.bus)
    devaddr = str(device.address)
    productid = str(device.idProduct)
    try:
        if str(usb.util.get_string(device, 256, 3)) == serialno:
            if debug: print "scale id:" + id + " serial: " + serialno
            if debug: print ("device serial:    <" + str(usb.util.get_string(device, 256, 3))) + ">"
            ## set USB device endpoint here
            endpoint = device[0][(0, 0)][0]
            # read a data packet
            attempts = 10
            data = None
            while data is None:  # and attempts > 0:
                try:
                    data = device.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)
                    if debug: print "data: " + str(data)
                except usb.core.USBError as e:
                    data = None
                    if e.args == ('Operation timed out',):
                        attempts -= 1
                        print e
                        continue

            # The raw scale array data
            # print data
            raw_weight = data[4] + (256 * data[5])

            if data[2] == DATA_MODE_OUNCES:
                ounces = raw_weight * 0.1
                weight = "%s oz" % ounces
            elif data[2] == DATA_MODE_GRAMS:
                grams = raw_weight
                weight = "%s g" % grams

            reading = weight
            if debug: print "raw reading '" + reading + "'"
            readval = float(reading.split(" ")[0])
            readunit = reading.split(" ")[1]
            ## if the units are ounces ("oz") then convert to "g"
            if readunit == "oz" and readval != 0:
                readval = readval * 28.3495
                if debug: print "converted oz to g"
            if debug: print "current weight : '" + str(readval) + "' " + readunit
            if debug: print "current time   : " + strftime("%Y-%m-%d %H:%M:%S", localtime())
