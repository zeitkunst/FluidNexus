# Standard library imports
import sys
import os
import socket
import select
import md5

# @HACK@
# Adding paths to find the modules
sys.path.append('.')
sys.path.append(os.getcwd())
sys.path.append('C:\\System\\Apps\\Python\\my\\')
sys.path.append('E:\\System\\Apps\\Python\\my\\')
sys.path.append('C:\\Python')
sys.path.append('E:\\Python')

from logger import Logger
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
    from s60Compat import e32
    dataPath = '.'
    log = Logger(dataPath + u'\\FluidNexus.log', prefix = 'FluidNexusServer: ')
    #sys.stderr = sys.stdout = log

    onPhone = False


class FluidNexusServer(object):
    numberConnections = 1
    connections = []
    ownerHashLength = 32
    timestampLength = 4
    cellIDLength = None

    def __init__(self, serviceName = u'FluidNexus', database = None):
        # Save our database object 
        self.database = database

        # Save our service name
        self.serviceName = serviceName

        # Setup our server socket
        self.serverSocket = socket.socket(socket.AF_BT, socket.SOCK_STREAM)
        self.serverPort = socket.bt_rfcomm_get_available_server_channel(self.serverSocket)
        self.serverSocket.bind(("", self.serverPort))
        self.serverSocket.listen(self.numberConnections)
        socket.bt_advertise_service(self.serviceName, self.serverSocket, True, socket.RFCOMM)

        # Remove security protections
        # @TODO@ Make sure this actually does what we want it to do!
        socket.set_security(self.serverSocket, 0)

    def initMessageAdvertisements(self):
        """Initialize the advertisement of hashes."""

        # @TODO@ Use the correct database here :-)
        self.database.query('select * from FluidNexusStigmergy')

        self.messageHashes = []

        for item in self.database:
            # @TODO@ This can break if we change the database schema

            # Get the last item (the hash)
            self.messageHashes.append('%s' % item[-1])

        # If there is nothing in the FluidNexusStigmergy database, return now
        if len(self.messageHashes) == 0:
            return

        # @HACK@
        # For some reason we have to do this convoluted process below, otherwise sockets get reused or don't advertise properly.  
        # Meaning, we have to create the sockets beforehand, and then loop through them to advertise with the desired hashes.
        # This seems strange, because we create the sockets anew before we advertise them, so it seems like some kind of race condition.

        # Get the number of hashes to advertise
        numAdvertise = len(self.messageHashes)

        # Create all of our advertisingSockets
        self.advertisingSockets = {}
        for counter in range(0, len(self.messageHashes)):
            self.advertisingSockets[self.messageHashes[counter]] = socket.socket(socket.AF_BT, socket.SOCK_STREAM)

        # Now, do what we need to with the sockets
        for item in self.advertisingSockets.items():
            hash = item[0]
            s = item[1]
            
            tempPort = socket.bt_rfcomm_get_available_server_channel(s)

            s.bind(("", tempPort))
            s.listen(1)
            socket.bt_advertise_service(unicode(':' + hash), s, True, socket.RFCOMM)

    def acceptCallback(self, connectionTuple):
        """This is called when the server socket receives a connection."""
        self.connections.append(connectionTuple)

        print "here"

        # Get client info
        clientSocket = connectionTuple[0]
        clientAddress = connectionTuple[1]

        #####################################################
        #  Read header information
        #  ASSUME BIG ENDIAN BYTE ORDER!
        #####################################################

        # VERSION: 1 byte
        version = clientSocket.recv(1)
        print version

        # @TODO@
        # In the future, split here based on different versions

        # TITLE LENGTH: 2 bytes
        titleLength = clientSocket.recv(2)

        # MESSAGE LENGTH: 4 bytes
        # Note: this is to eventually support unicode text
        messageLength = clientSocket.recv(4)

        #####################################################
        #  Start reading data!
        #  ASSUME BIG ENDIAN BYTE ORDER!
        #####################################################
        timestamp = clientSocket.recv(self.timestampLength)
        # Skip cellID for now
        #cellID = clientSocket.recv(self.cellIDLength)
        ownerHash = clientSocket.recv(self.ownerHashLength)
        title = clientSocket.recv(titleLength)
        message = clientSocket.recv(messageLength)

        # Finish up
        clientSocket.close()

    def run(self):
        """Main loop for the server."""

        while 1:
            self.serverSocket.accept(self.acceptCallback)

class FluidNexusServerOld:
    """This thread accepts connections and appropriate data.

    @TODO@ Need better description, name."""


    def __init__(self, serviceName = u'FluidNexus', database = None):
        # Save our database object
        self.database = database

        self.counter = 0

        self.serviceName = serviceName
        #self.serverSocket = socket.socket(socket.AF_BT, socket.SOCK_STREAM)
        self.serverSocket = lightblue.socket()
        #self.serverPort = socket.bt_rfcomm_get_available_server_channel(self.   serverSocket)
        self.serverSocket.bind(("", 0))

        #socket.set_security(self.serverSocket,
        #   socket.AUTH)

        # Only listen for one connection
        self.serverSocket.listen(1)

        # Advertise my service
        #socket.bt_advertise_service(serviceName,
        #                            self.serverSocket,
        #                            True,
        #                            socket.RFCOMM)
        lightblue.advertise(serviceName, self.serverSocket, lightblue.RFCOMM)
        #self.serverSocket.setblocking(False)
        
        self.initMessageAdvertisements()

    def initMessageAdvertisements(self):
        # @TODO@ Use the correct database here :-)
        self.database.query('select * from FluidNexusStigmergy')

        hashes = []

        for item in database:
            # @TODO@ This can break if we change the database schema

            # Get the last item (the hash)
            hashes.append('%s' % item[-1])

        # If there is nothing in the FluidNexusStigmergy database, return now
        if len(hashes) == 0:
            return

        # @HACK@
        # For some reason we have to do this convoluted process below, otherwise sockets get reused or don't advertise properly.  This is true even though the new socket objects are different objects when they get made in the integrated loop.  Should probably figure out why this is at some point...

        # Get the number of hashes to advertise
        numAdvertise = len(hashes)

        # Create all of our advertisingSockets
        self.advertisingSockets = {}
        for counter in range(0, len(hashes)):
            self.advertisingSockets[hashes[counter]] = lightblue.socket()

        # Now, do what we need to with the sockets
        for item in self.advertisingSockets.items():
            hash = item[0]
            s = item[1]

            s.bind(("", 0))
            s.listen(1)
            lightblue.advertise(unicode(':' + hash), s, lightblue.RFCOMM)

            # Old Socket code
            #s = socket.socket(socket.AF_BT, socket.SOCK_STREAM)
            #port = socket.bt_rfcomm_get_available_server_channel(s)
            #s.bind(("", port))
            #s.listen(1)
            #socket.bt_advertise_service(unicode(hash), 
            #                            s, 
            #                            True, 
            #                            socket.RFCOMM)
            #s = lightblue.socket()
            #s.bind(("", 0))
            #s.listen(1)
            #log.write(unicode(hash))
            #lightblue.advertise(unicode(hash), s, lightblue.RFCOMM)

    def acceptCallback(self, clientSocket, clientAddress):
        print "in accept callback"
        print clientAddress
        clientSocket.close()

    def run(self):
        log.write('Starting the FluidNexus Server')
        # Dummy run program for right now
        while 1:
            clientSocket, clientAddress = self.serverSocket.accept()
            receivedData = ""

            foundStop = False
            while not foundStop:
                receivedData += clientSocket.recv(1024)

                if receivedData.find('\x00') != -1:
                    foundStop = True

            receivedData = receivedData.replace('\x00', '')
            receivedDataList = receivedData.split('\xFF')

            print receivedDataList
            title = receivedDataList[0]
            data = receivedDataList[1]
            hash = unicode(md5.md5(title + data).hexdigest())
            self.database.query("insert into FluidNexusData (source, type, title, data, hash) values ('%s', 0, '%s', '%s',   '%s')" % (clientAddress[0], title, data, hash))
            self.database.query("insert into FluidNexusStigmergy (dataHash) values ('%s')" % (hash))

            clientSocket.close()

if __name__ == """__main__""":
    try:
        database = FluidNexusDatabase()

        server = FluidNexusServer(database = database)
        server.initMessageAdvertisements()
        server.run()
    except:
        log.print_exception_trace()
