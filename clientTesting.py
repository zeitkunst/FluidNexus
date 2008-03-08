# Standard library imports
import sys
import os
import socket
import select
import md5
import time

# other imports
import lightblue

# @HACK@
# Adding paths to find the modules
sys.path.append('.')
sys.path.append(os.getcwd())
sys.path.append('C:\\System\\Apps\\Python\\my\\')
sys.path.append('E:\\System\\Apps\\Python\\my\\')
sys.path.append('C:\\Python')
sys.path.append('E:\\Python')

from logger import Logger
import database
from database import FluidNexusDatabase

# Series 60 specific imports
try:
    # On phone?
    import e32
    import e32db

    # @SEMI-HACK@
    # At the moment, set global variable that determines where our data is      going to live
    try:
        os.listdir('E:')
        dataPath = u'E:\\System\\Data\\FluidNexusData'
    except OSError:
        dataPath = u'C:\\System\\Data\\FluidNexusData'

    # Setup our data path
    if not os.path.isdir(dataPath):
        os.makedirs(dataPath)

    # Setup logging and redirect standard input and output
    log = Logger(dataPath + u'\\FluidNexus.log', prefix = 'FluidNexus Networking: ')
    #sys.stderr = sys.stdout = log

    onPhone = True
except ImportError:
    #from s60Compat import e32
    dataPath = '.'
    log = Logger(dataPath + u'\\FluidNexus.log', prefix = 'FluidNexusServer: ')
    #sys.stderr = sys.stdout = log

    onPhone = False


class FluidNexusClient(object):
    def __init__(self, database = None):
        self.db = database
   
    def splitclass(self, deviceClass):
        """Taken from lightblue library."""

        if not isinstance(deviceClass, int):
            try:
                deviceClass = int(deviceClass)
            except (TypeError, ValueError):
                raise TypeError("Given device class '%s' cannot be split" % \
                                str(deviceClass))

        data = deviceClass >> 2   # skip over the 2 "format" bits
        service = data >> 11
        major = (data >> 6) & 0x1F
        minor = data & 0x3F
        return (service, major, minor)


    def runLightblue(self):
        print "looking for devices"
        #allDevices = socket.bt_discover()
        allDevices = lightblue.finddevices()
        phones = []

        for device in allDevices:
            foo, isPhone, bar = lightblue.splitclass(device[2])
            if isPhone == 2:
                phones.append(device)

        for phone in phones:
            print "Looking at phone", phone
            services = lightblue.findservices(phone[0])
            print services
            for service in services:
                if service[2] is not None and service[2] == 'FluidNexus':
                    port = service[1]
                    break
                else:
                    port = None
            print port
            print "at end of service search"

            if port is not None:
                print "sending data!"
                self.db.outgoing()
                listItems = []

                for item in database:
                    listItems.append(item)

                print listItems

                messageTime = listItems[0][2]
                title = listItems[0][4]
                message = listItems[0][5]

                clientSocket = socket.socket(socket.AF_BT, socket.SOCK_STREAM)
                clientSocket.connect((phone[0], port))
                clientSocket.send('01')
                time.sleep(1)
                clientSocket.send("%03d" % len(title))
                time.sleep(1)
                clientSocket.send("%06d" % len(message))
                time.sleep(1)
                clientSocket.send(str(messageTime))
                time.sleep(1)
                clientSocket.send(md5.md5(title + message).hexdigest())
                time.sleep(1)
                clientSocket.send(title)
                time.sleep(1)
                clientSocket.send(message)
                time.sleep(1)
                clientSocket.close()

    def run(self):
        allDevices = socket.bt_discover()
        phones = []

        for device in allDevices:
            foo, isPhone, bar = self.splitclass(device[2])
            if isPhone == 2:
                phones.append(device)

        for phone in phones:
            print "Looking at phone", phone
            services = socket.bt_discover(phone[0])
            print services
            for service in services:
                if service[2] is not None and 'FluidNexus' in service[2]:
                    port = service[1]
                    break
                else:
                    port = None
            print port
            print "at end of service search"

            if port is not None:
                print "sending data!"
                clientSocket = socket.socket(socket.AF_BT, socket.SOCK_STREAM)
                clientSocket.connect((phone[0], port))
                clientSocket.send('01')
                time.sleep(1)
                clientSocket.send('010')
                time.sleep(1)
                clientSocket.send('000010')
                time.sleep(1)
                clientSocket.send(str(time.time()))
                time.sleep(1)
                clientSocket.send(md5.md5('foo').hexdigest())
                time.sleep(1)
                clientSocket.send('aaaaaaaaaa')
                time.sleep(1)
                clientSocket.send('aaaaaaaaaa')
                time.sleep(1)
                clientSocket.close()

if __name__ == "__main__":
    database = FluidNexusDatabase()
    client = FluidNexusClient(database = database)
    client.runLightblue()
