#!/usr/bin/env python

# Standard library imports
import binascii
import hashlib
import logging
import os
import struct
import time

# External imports
from PyQt4 import QtCore
from bluetooth import *

# My imports
from Database import FluidNexusDatabase
import Log

FluidNexusUUID = "bd547e68-952b-11e0-a6c7-0023148b3104"

# Command constants
HELO = 0x0010
HASH_LIST = 0x0020
HASH_REQUEST = 0x0030
SWITCH = 0x0040
SWITCH_DONE = 0x0041
DONE_DONE = 0x00F0

# Length constants
TIMESTAMP_LENGTH = 13
OWNER_HASH_LENGTH= 32

"""
settings = QtCore.QSettings("fluidnexus.net", "Fluid Nexus")
dataDir = unicode(settings.value("app/dataDir").toString())
name = unicode(settings.value("database/name").toString())
databaseDir = os.path.join(dataDir, name)
databaseType = unicode(settings.value("database/type").toString())
"""

#database = FluidNexusDatabase(databaseDir = databaseDir, databaseType = databaseType)

testTitle = 'This is a test from ver2'
testMessage = 'Nothing but a test.\n\nTesting here.\n\nHope this gets through.\n\nShould eventually try unicode.'
testData = {hashlib.md5(testTitle + testMessage).hexdigest():
    (str(int(float(time.time()))), testTitle, testMessage)
}


# TODO
# Deal with settings/config better
class Networking(object):
    """Base class for all other networking activity.  Other networking modalities need to subclass from this class."""

    def __init__(self, logPath = "FluidNexus.log", level = logging.DEBUG):
        self.logger = Log.getLogger(logPath = logPath)

class BluetoothServer(Networking):
    """Class that deals with bluetooth networking.  

TODO

* Write client that can connect to other machines
* Deal with different libraries such as lightblue."""

    commandStruct = struct.Struct('>H')
    hashStruct = struct.Struct('>32s')

    def __init__(self, databaseDir = ".", databaseType = "pysqlite2", logPath = "FluidNexus.log", level = logging.DEBUG, numConnections = 5):
        super(BluetoothServer, self).__init__(logPath = logPath, level = level)

        self.database = FluidNexusDatabase(databaseDir = databaseDir, databaseType = databaseType)

        # Do initial setup
        self.setupServerSocket(numConnections = numConnections)
        self.setupService()

        self.getHashesFromDatabase()

        # Enter into the main loop
        self.run()

    def setupServerSocket(self, numConnections = 5):
        """Setup the socket for accepting connections."""
        self.serverSocket = BluetoothSocket(RFCOMM)
        self.serverSocket.bind(("", PORT_ANY))
        self.serverSocket.listen(numConnections)

    def setupService(self):
        """Setup the service advertisement."""
        advertise_service(self.serverSocket, "FluidNexus", service_id = FluidNexusUUID, service_classes = [FluidNexusUUID, SERIAL_PORT_CLASS], profiles = [SERIAL_PORT_PROFILE])

    def getHashesFromDatabase(self):
        """Get the current list of hashes from the database."""

        self.database.services()

        self.messageHashes = []

        for item in self.database:
            # @TODO@ This can break if we change the database schema

            # Get the last item (the hash)
            self.messageHashes.append('%s' % str(item[-1]))

    def respondHELO(self):
        """Respond to HELO with a HELO."""

        self.cs.send(self.commandStruct.pack(HELO))

    def respondWithHashes(self):
        """Respond with the hashes that we have."""

        self.logger.debug("=> Send hashes")
        # Send hashes
        # TODO
        # Deal with having more hashes than we can send
        numHashes = len(self.messageHashes)
        numHashesPacked = self.commandStruct.pack(numHashes)
        
        self.cs.send(numHashesPacked)
        for currentHash in self.messageHashes:
            self.cs.send(self.hashStruct.pack(currentHash))

    def respondWithDataForHash(self):
        """Respond with data for a particular hash."""
        # Receiving hash request
        self.logger.debug("=> Receiving hash request")
        # TODO
        # should figure out how to deal with this using the struct
        tmpHash = self.cs.recv(32)
        self.logger.debug(tmpHash)

        data = self.database.returnItemBasedOnHash(tmpHash)
        timestamp = str(data[2])
        title = str(data[4])
        message = str(data[5])

        # Send data corresponding to hash
        self.logger.debug("=> Send data corresponding to hash %s" % tmpHash)
        versionPack = struct.Struct(">B")
        self.cs.send(versionPack.pack(0x02))
        
        titleLengthPack = struct.Struct(">I")
        self.cs.send(titleLengthPack.pack(int(len(title))))

        messageLengthPack = struct.Struct(">I")
        self.cs.send(messageLengthPack.pack(int(len(message))))

        timestampPacker = struct.Struct(">10s")
        self.cs.send(timestampPacker.pack(timestamp))

        titlePacker = struct.Struct(">%ds" % int(len(title)) )
        self.cs.send(titlePacker.pack(title))

        messagePacker = struct.Struct(">%ds" % int(len(message)) )
        self.cs.send(messagePacker.pack(message))

    def respondSWITCH(self):
        """Respond to SWITCH with a SWITCH."""

        self.cs.send(self.commandStruct.pack(SWITCH))

        self.doRequestLoop()

    def sendHashListRequest(self):
        """Send a request for a list of hashes from the client."""

        # Send command for hash list
        self.cs.send(self.commandStruct.pack(HASH_LIST))
        numHashesCommand = self.cs.recv(self.commandStruct.size)
        numHashes = self.commandStruct.unpack(numHashesCommand)
        numHashes = numHashes[0]
        self.logger.debug("Expect to receive %d hashes" % numHashes)

        self.hashesToReceive = []

        for index in xrange(0, numHashes):
            hashPacked = self.cs.recv(self.hashStruct.size)
            hashUnpacked = self.hashStruct.unpack(hashPacked)
            self.logger.debug("Received hash: " + hashUnpacked[0])
            self.hashesToReceive.append(hashUnpacked[0])

        self.currentSendingState = HASH_REQUEST
    
    def __requestHash(self, currentHash):
        """Private method to request data for a particular hash."""

        # Send command for hash request
        self.cs.send(self.commandStruct.pack(HASH_REQUEST))
        self.logger.debug("=> Requesting data for hash %s" % currentHash)

        # Send hash that we want to receive
        self.cs.send(self.hashStruct.pack(currentHash))

        # Receive data corresponding to hash
        versionPacker = struct.Struct(">B")
        versionPacked = self.cs.recv(versionPacker.size)
        self.logger.debug("received %s " % binascii.hexlify(versionPacked))
        version = versionPacker.unpack(versionPacked)[0]
        self.logger.debug("Version: %d" % version)
        
        titleLengthPacker = struct.Struct(">I")
        titleLengthPacked = self.cs.recv(titleLengthPacker.size)
        titleLength = titleLengthPacker.unpack(titleLengthPacked)[0]
        self.logger.debug("Title length: %d" % titleLength)

        messageLengthPacker = struct.Struct(">I")
        messageLengthPacked = self.cs.recv(messageLengthPacker.size)
        messageLength = messageLengthPacker.unpack(messageLengthPacked)[0]
        self.logger.debug("Message length: %d" % messageLength)

        timestampPacker = struct.Struct(">10s")
        timestampPacked = self.cs.recv(timestampPacker.size)
        timestamp = timestampPacker.unpack(timestampPacked)[0]
        self.logger.debug("Timestamp: %s" % timestamp)

        titlePacker = struct.Struct(">%ds" % int(titleLength) )
        titlePacked = self.cs.recv(titlePacker.size)
        title = titlePacker.unpack(titlePacked)[0]
        self.logger.debug("Title: %s" % title)

        messagePacker = struct.Struct(">%ds" % int(messageLength) )
        messagePacked = self.cs.recv(messagePacker.size)
        message = messagePacker.unpack(messagePacked)[0]
        self.logger.debug("Message: %s" % message)
    
    def sendHashRequest(self):
        """Send a request for a given hash."""

        # TODO
        # Only request hashes we don't already have
        # Receiving hash request
        for currentHash in self.hashesToReceive:
            self.__requestHash(currentHash)

    def doRequestLoop(self):
        """Enter into a loop to send requests to our client."""
        done = False
        self.currentSendingState = HASH_LIST
        while (not done):
            if (self.currentSendingState == HASH_LIST):
                self.sendHashListRequest()
            elif (self.currentSendingState == HASH_REQUEST):
                self.sendHashRequest()
                # Send command for hash list
                self.cs.send(self.commandStruct.pack(SWITCH_DONE))
                done = True
            else:
                done = True

    def respondDoneDone(self):
        """Respond that we're really done."""
        self.logger.debug("=> Sending back command")
        self.cs.send(self.commandStruct.pack(DONE_DONE))
        self.cs.close()
        self.cs = None
        self.ci = None

    def run(self):
        """Run the main loop."""

        self.cs = None
        self.ci = None

        while (True):
            self.logger.debug("starting accept sequence")

            # TODO
            # At some point, make this threaded
            if (self.cs is None):
                self.cs, self.ci = self.serverSocket.accept()

            # First thing we get should be a command
            self.logger.debug("=> Receive command")
            command = self.cs.recv(self.commandStruct.size)
            self.logger.debug("received %s " % binascii.hexlify(command))
            unpacked_command = self.commandStruct.unpack(command)
            unpacked_command = unpacked_command[0]
            self.logger.debug("unpacked: " + str(unpacked_command))

            # Go through our command tree
            if (unpacked_command == HELO):
                self.logger.debug("=> Received HELO")
                self.respondHELO()
            elif (unpacked_command == HASH_LIST):
                self.logger.debug("=> Received command for hash list")
                self.respondWithHashes()
            elif (unpacked_command == HASH_REQUEST):
                self.logger.debug("=> Received command for particular hash request")
                self.respondWithDataForHash()
            elif (unpacked_command == SWITCH):
                self.logger.debug("=> Received command to switch direction")
                self.respondSWITCH()
            elif (unpacked_command == DONE_DONE):
                self.logger.debug("=> Received command that we're done")
                self.respondDoneDone()
            else:
                self.logger.debug("No command matches.")
                self.cs.send(self.commandStruct.pack(0x00F0))
                self.cs.close()
                self.cs = None
                self.ci = None
