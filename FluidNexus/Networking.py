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
import FluidNexus_pb2
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

# TODO
# * Deal with settings/config better
# * Refactor to allow for reuse of methods between client, server classes
# * Better error checking, deal with socket timeouts, socket closing, etc

class Networking(object):
    """Base class for all other networking activity.  Other networking modalities need to subclass from this class."""

    def __init__(self, databaseDir = ".", databaseType = "pysqlite2", logPath = "FluidNexus.log", level = logging.DEBUG):
        self.logger = Log.getLogger(logPath = logPath)

        self.database = FluidNexusDatabase(databaseDir = databaseDir, databaseType = databaseType)

    def getHashesFromDatabase(self):
        """Get the current list of hashes from the database."""

        self.database.services()

        self.ourHashes = []

        for item in self.database:
            # @TODO@ This can break if we change the database schema

            # Get the last item (the hash)
            self.ourHashes.append('%s' % str(item[-1]))

class BluetoothServerVer2(Networking):
    """Class that deals with bluetooth networking.  

TODO

* Write client that can connect to other machines
* Deal with different libraries such as lightblue."""

    commandStruct = struct.Struct('>H')
    hashStruct = struct.Struct('>32s')

    def __init__(self, databaseDir = ".", databaseType = "pysqlite2", logPath = "FluidNexus.log", level = logging.DEBUG, numConnections = 5):
        super(BluetoothServer, self).__init__(databaseDir = databaseDir, databaseType = databaseType, logPath = logPath, level = level)

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
            hashUnpacked = self.hashStruct.unpack(hashPacked)[0]
            self.logger.debug("Received hash: " + hashUnpacked)
            
            hashUnpacked = hashUnpacked.lower()
            if (not (self.database.look_for_hash(hashUnpacked))):
                self.logger.debug("Don't currently have hash: " + hashUnpacked)
                self.hashesToReceive.append(hashUnpacked)

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


class BluetoothServerVer3(Networking):
    """Class that deals with bluetooth networking using version 3 of the protocol, specifically using protocol buffers.  

TODO

* Write client that can connect to other machines
* Deal with different libraries such as lightblue."""

    # STATES
    STATE_START = 0x0000
    STATE_READ_HELO = 0x0010
    STATE_WRITE_HELO = 0x0020
    STATE_READ_HASHES = 0x0030
    STATE_WRITE_MESSAGES = 0x0040
    STATE_READ_SWITCH = 0x0050
    STATE_WRITE_HASHES = 0x0060
    STATE_READ_MESSAGES = 0x0070
    STATE_WRITE_SWITCH = 0x0080
    STATE_READ_DONE = 0x0090
    STATE_WRITE_DONE = 0x00A0
    STATE_QUIT = 0x00F0

    # Commands
    HELO = 0x0010
    HASHES = 0x0020
    MESSAGES = 0x0030
    SWITCH = 0x0080
    DONE = 0x00F0

    commandStruct = struct.Struct('>H')
    sizeStruct = struct.Struct('>I')
    hashStruct = struct.Struct('>32s')
    state = STATE_START

    def __init__(self, databaseDir = ".", databaseType = "pysqlite2", logPath = "FluidNexus.log", level = logging.DEBUG, numConnections = 5):
        super(BluetoothServerVer3, self).__init__(databaseDir = databaseDir, databaseType = databaseType, logPath = logPath, level = level)

        # Do initial setup
        self.setupServerSocket(numConnections = numConnections)
        self.setupService()

        self.getHashesFromDatabase()
        self.hashesToSend = None

        # Enter into the main loop
        self.run()

    def setState(self, state):
        """Set our state."""
        tmpNewState = str(state)
        tmpOldState = str(self.state)

        self.logger.debug("Changing state from %s to %s" % (tmpOldState, tmpNewState))
        self.state = state

    def getState(self):
        """Return our current state."""

        return self.state

    def setupServerSocket(self, numConnections = 5):
        """Setup the socket for accepting connections."""
        self.serverSocket = BluetoothSocket(RFCOMM)
        self.serverSocket.bind(("", PORT_ANY))
        self.serverSocket.listen(numConnections)

    def setupService(self):
        """Setup the service advertisement."""
        advertise_service(self.serverSocket, "FluidNexus", service_id = FluidNexusUUID, service_classes = [FluidNexusUUID, SERIAL_PORT_CLASS], profiles = [SERIAL_PORT_PROFILE])

    def respondHELO(self):
        """Respond to HELO with a HELO."""

        self.cs.send(self.commandStruct.pack(self.HELO))

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
            hashUnpacked = self.hashStruct.unpack(hashPacked)[0]
            self.logger.debug("Received hash: " + hashUnpacked)
            
            hashUnpacked = hashUnpacked.lower()
            if (not (self.database.look_for_hash(hashUnpacked))):
                self.logger.debug("Don't currently have hash: " + hashUnpacked)
                self.hashesToReceive.append(hashUnpacked)

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

    def readCommand(self):
        """Read a command from the socket.
        
        TODO        
        * Add error handling."""

        # First thing we get should be a command
        self.logger.debug("=> Receive command")
        command = self.cs.recv(self.commandStruct.size)
        self.logger.debug("received %s " % binascii.hexlify(command))
        unpackedCommand = self.commandStruct.unpack(command)
        unpackedCommand = unpackedCommand[0]
        self.logger.debug("unpacked: " + str(unpackedCommand))
        
        return unpackedCommand

    def writeCommand(self, command):
        """Write a command to the socket.

        TODO
        * Include return values for error checking."""

        self.cs.send(self.commandStruct.pack(command))

    def writeSize(self, size):
        """Write a size to the socket.

        TODO
        * do some error handling."""
        self.cs.send(self.sizeStruct.pack(size))

    def writeSerializedString(self, data):
        """Write a serialized string to the socket.

        TODO
        * do some error handling."""
        self.cs.send(data)

    def readHashes(self):
        """Read the hashes serialized using protobuffers."""
        
        command = self.readCommand()
        self.logger.debug("Received command: " + str(command))
        if (command != self.HASHES):
            self.handleError()

        sizePacked = self.cs.recv(self.sizeStruct.size)
        size = self.sizeStruct.unpack(sizePacked)[0]
        self.logger.debug("Expecting to receive data of size " + str(size))

        data = self.cs.recv(size)
        hashes = FluidNexus_pb2.FluidNexusHashes()
        hashes.ParseFromString(data)

        theirHashesSet = set([givenHash for givenHash in hashes.ListFields()[0][1]])
        print theirHashesSet
        ourHashesSet = set(self.ourHashes)
        print ourHashesSet
        self.hashesToSend = ourHashesSet.difference(theirHashesSet)
        print self.hashesToSend
        self.logger.debug("Received message: " + str(hashes))
        self.setState(self.STATE_WRITE_MESSAGES)

    def writeMessages(self):
        """Write the messages that the other side doesn't have."""

        # Our output protobuf message
        messages = FluidNexus_pb2.FluidNexusMessages()

        for currentHash in self.hashesToSend:
            m = messages.message.add()
            data = self.database.returnItemBasedOnHash(currentHash)
            m.message_timestamp = data[2]
            m.message_title = data[4]
            m.message_content = data[5]
            m.message_type = FluidNexus_pb2.FluidNexusMessage.TEXT

        print str(messages)

        messagesSerialized = messages.SerializeToString()
        messagesSerializedSize = len(messagesSerialized)
        self.writeCommand(self.MESSAGES)
        self.writeSize(messagesSerializedSize)
        self.writeSerializedString(messagesSerialized)
        self.setState(self.STATE_READ_SWITCH)

    def writeHashes(self):
        """Write our current hashes to the client."""
        hashes = FluidNexus_pb2.FluidNexusHashes()

        for currentHash in self.ourHashes:
            hashes.message_hash.append(currentHash)

        hashesSerialized = hashes.SerializeToString()
        hashesSerializedSize = len(hashesSerialized)
        self.writeCommand(self.HASHES)
        self.writeSize(hashesSerializedSize)
        self.writeSerializedString(hashesSerialized)
        self.setState(self.STATE_READ_MESSAGES)

    def readMessages(self):
        """Read the messages from the client."""

        sizePacked = self.cs.recv(self.sizeStruct.size)
        size = self.sizeStruct.unpack(sizePacked)[0]
        self.logger.debug("Expecting to receive data of size " + str(size))

        data = ""
        while len(data) < size:
            chunk = self.cs.recv(size - len(data))
            if chunk == "":
                self.handleError()
            data = data + chunk

        messages = FluidNexus_pb2.FluidNexusMessages()
        messages.ParseFromString(data)

        self.logger.debug("Received messages: " + str(messages))

        # Go through the received messages and add any that were sent
        fields = messages.ListFields()
        if (fields != []):
            for message in fields[0][1]: 
                message_hash = hashlib.md5(unicode(message.message_title) + unicode(message.message_content)).hexdigest()
                self.database.add_received("foo", message.message_timestamp, 0, message.message_title, message.message_content, message_hash, "(123, 123, 123, 123)")

        self.getHashesFromDatabase()
        self.setState(self.STATE_WRITE_SWITCH)

    def handleError(self):
        """Do some sort of socket error handling if we ever get a command or data that we don't expect."""
        
        self.hashesToSend = None
        self.cs.close()
        self.cs = None
        self.ci = None
        self.setState(self.STATE_START)

    def cleanup(self):
        """Cleanup our connections for starting over.

        TODO
        * do we just need to change handleError to this?"""
        self.hashesToSend = None
        self.cs.close()
        self.cs = None
        self.ci = None
        self.setState(self.STATE_START)


    def run(self):
        """Run the main loop."""

        self.cs = None
        self.ci = None

        while (True):

            currentState = self.getState()
            self.logger.debug("Current state is: " + str(currentState))

            # Go through our command tree
            if (currentState == self.STATE_START):
                self.logger.debug("starting accept sequence")
                # TODO
                # At some point, make this threaded
                if (self.cs is None):
                    self.cs, self.ci = self.serverSocket.accept()
                    self.setState(self.STATE_READ_HELO)
            elif (currentState == self.STATE_READ_HELO):
                command = self.readCommand()
                if (command != self.HELO):
                    self.handleError()
                else:
                    self.setState(self.STATE_WRITE_HELO)
            elif (currentState == self.STATE_WRITE_HELO):
                # TODO
                # Deal with errors in writing to socket
                self.writeCommand(self.HELO)
                self.setState(self.STATE_READ_HASHES)
            elif (currentState == self.STATE_READ_HASHES):
                self.readHashes()
            elif (currentState == self.STATE_WRITE_MESSAGES):
                self.writeMessages()
            elif (currentState == self.STATE_READ_SWITCH):
                command = self.readCommand()
                if (command != self.SWITCH):
                    self.handleError()
                else:
                    self.setState(self.STATE_WRITE_HASHES)
            elif (currentState == self.STATE_WRITE_HASHES):
                self.writeHashes()
            elif (currentState == self.STATE_READ_MESSAGES):
                command = self.readCommand()
                if (command != self.MESSAGES):
                    self.handleError()
                else:
                    self.readMessages()
            elif (currentState == self.STATE_WRITE_SWITCH):
                self.writeCommand(self.SWITCH)
                self.setState(self.STATE_READ_DONE)
            elif (currentState == self.STATE_READ_DONE):
                command = self.readCommand()
                if (command != self.DONE):
                    self.handleError()
                else:
                    self.setState(self.STATE_WRITE_DONE)
            elif (currentState == self.STATE_WRITE_DONE):
                self.writeCommand(self.DONE)
                self.cleanup()
            else:
                self.logger.debug("No command matches.")
                self.handleError()

