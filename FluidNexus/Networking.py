#!/usr/bin/env python

# Standard library imports
import binascii
import hashlib
import logging
import os
import select
import socket
import struct
import time

# External imports
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
# * Better error checking, deal with socket timeouts, socket closing, etc
# * * Basically need to wrap all "recv" with a "read" that takes in socket, amount to read, and captures error of "bluetooth.btcommon.BluetoothError: (104, 'Connection reset by peer')"

class Networking(object):
    """Base class for all other networking activity.  Other networking modalities need to subclass from this class."""

    # STATES
    STATE_START = 0x0000
    STATE_WAITING = 0x0001
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

    newMessages = []

    def __init__(self, databaseDir = ".", databaseType = "pysqlite2", attachmentsDir = ".", logPath = "FluidNexus.log", level = logging.DEBUG):
        self.logger = Log.getLogger(logPath = logPath, level = level)

        self.databaseDir = databaseDir
        self.databaseType = databaseType
        self.attachmentsDir = attachmentsDir

    def openDatabase(self):
        self.database = FluidNexusDatabase(databaseDir = self.databaseDir, databaseType = self.databaseType)

    def closeDatabase(self):
        self.database.close()

    def setState(self, state):
        """Set our state."""
        tmpNewState = str(state)
        tmpOldState = str(self.state)

        self.logger.debug("Changing state from %s to %s" % (tmpOldState, tmpNewState))
        self.state = state

    def getState(self):
        """Return our current state."""

        return self.state

    def getHashesFromDatabase(self):
        """Get the current list of hashes from the database."""

        self.ourHashes = self.database.hashes()

    def addHash(self, hashToAdd):
        self.ourHashes.append(hashToAdd)

    def removeHash(self, hashToRemove):
        self.ourHashes.remove(hashToRemove)

    def replaceHash(self, hashToReplace, newHash):
        self.ourHashes.remove(hashToReplace)
        self.ourHashes.append(newHash)

    def read(self, cs, size):
        """Read a certain amount from the given socket."""
        data = ""

        try:
            while len(data) < size:
                chunk = cs.recv(size - len(data))
                if chunk == "":
                    self.cleanup(cs)
                data = data + chunk
            return data
        except btcommon.BluetoothError, e:
            self.logger.error("Some sort of bluetooth error: " + str(e))
            self.cleanup(cs)
            return ""


    def readCommand(self, cs):
        """Read a command from the socket.
        
        TODO        
        * Add error handling."""

        # First thing we get should be a command
        self.logger.debug("=> Receive command")
        #command = cs.recv(self.commandStruct.size)
        command = self.read(cs, self.commandStruct.size)
        self.logger.debug("received %s " % binascii.hexlify(command))
        unpackedCommand = self.commandStruct.unpack(command)
        unpackedCommand = unpackedCommand[0]
        self.logger.debug("unpacked: " + str(unpackedCommand))
        
        return unpackedCommand

    def writeCommand(self, cs, command):
        """Write a command to the socket.

        TODO
        * Include return values for error checking."""

        cs.send(self.commandStruct.pack(command))

    def writeSize(self, cs, size):
        """Write a size to the socket.

        TODO
        * do some error handling."""
        cs.send(self.sizeStruct.pack(size))

    def writeSerializedString(self, cs, data):
        """Write a serialized string to the socket.

        TODO
        * do some error handling."""
        cs.send(data)

    def readHashes(self, cs):
        """Read the hashes serialized using protobuffers."""
        
        command = self.readCommand(cs)
        self.logger.debug("Received command: " + str(command))
        if (command != self.HASHES):
            self.cleanup(cs)

        #sizePacked = cs.recv(self.sizeStruct.size)
        sizePacked = self.read(cs, self.sizeStruct.size)
        size = self.sizeStruct.unpack(sizePacked)[0]
        self.logger.debug("Expecting to receive data of size " + str(size))

        #data = cs.recv(size)
        data = self.read(cs, size)
        hashes = FluidNexus_pb2.FluidNexusHashes()
        hashes.ParseFromString(data)

        theirHashesSet = set([givenHash for givenHash in hashes.ListFields()[0][1]])
        ourHashesSet = set(self.ourHashes)
        self.hashesToSend = ourHashesSet.difference(theirHashesSet)
        self.logger.debug("Received hashes: " + str(hashes))
        self.setState(self.STATE_WRITE_MESSAGES)

    def writeMessages(self, cs):
        """Write the messages that the other side doesn't have."""

        # Our output protobuf message
        messages = FluidNexus_pb2.FluidNexusMessages()

        for currentHash in self.hashesToSend:
            m = messages.message.add()
            data = self.database.getMessageByHash(currentHash)
            m.message_timestamp = data['time']
            m.message_title = data['title']
            m.message_content = data['content']
            m.message_type = FluidNexus_pb2.FluidNexusMessage.TEXT
            if (data["attachment_path"] != ""):
                self.logger.debug("ATTACHMENT")
                m.message_attachment_original_filename = data["attachment_original_filename"]

                # TODO
                # Error handling :-)
                attachmentDataFP = open(os.path.realpath(data["attachment_path"]), 'rb')
                attachmentData = attachmentDataFP.read()
                attachmentDataFP.close()
                m.message_attachment = attachmentData

        #self.logger.debug("Sending messages: " + str(messages))
        self.logger.debug("Sending messages...")

        messagesSerialized = messages.SerializeToString()
        messagesSerializedSize = len(messagesSerialized)
        self.writeCommand(cs, self.MESSAGES)
        self.writeSize(cs, messagesSerializedSize)
        self.writeSerializedString(cs, messagesSerialized)
        self.setState(self.STATE_READ_SWITCH)

    def writeHashes(self, cs):
        """Write our current hashes to the client."""
        hashes = FluidNexus_pb2.FluidNexusHashes()

        for currentHash in self.ourHashes:
            hashes.message_hash.append(currentHash)

        hashesSerialized = hashes.SerializeToString()
        hashesSerializedSize = len(hashesSerialized)
        self.writeCommand(cs, self.HASHES)
        self.writeSize(cs, hashesSerializedSize)
        self.writeSerializedString(cs, hashesSerialized)
        self.setState(self.STATE_READ_MESSAGES)

    def readMessages(self, cs):
        """Read the messages from the client."""

        #sizePacked = cs.recv(self.sizeStruct.size)
        sizePacked = self.read(cs, self.sizeStruct.size)
        size = self.sizeStruct.unpack(sizePacked)[0]
        self.logger.debug("Expecting to receive data of size " + str(size))
        
        """
        data = ""
        while len(data) < size:
            chunk = cs.recv(size - len(data))
            if chunk == "":
                self.cleanup(cs)
            data = data + chunk
        """
        data = self.read(cs, size)

        messages = FluidNexus_pb2.FluidNexusMessages()
        messages.ParseFromString(data)

        #self.logger.debug("Received messages: " + str(messages))

        # Go through the received messages and add any that were sent
        fields = messages.ListFields()
        self.newMessages = []
        if (fields != []):
            for message in fields[0][1]: 
                message_hash = hashlib.sha256(message.message_title.encode("utf-8") + message.message_content.encode("utf-8")).hexdigest()

                if (message.message_attachment_original_filename != ""):
                    message_attachment_path = os.path.join(self.attachmentsDir, message_hash)
                    attachmentFP = open(message_attachment_path, "wb")
                    attachmentFP.write(message.message_attachment)
                    attachmentFP.close()
                    self.database.addReceived(timestamp = message.message_timestamp, title = message.message_title, content = message.message_content, attachment_path = message_attachment_path, attachment_original_filename = message.message_attachment_original_filename)
                    newMessage = {"message_hash": message_hash, "message_timestamp": message.message_timestamp, "message_title": message.message_title, "message_content": message.message_content, "message_attachment_path": message_attachment_path, "message_attachment_original_filename": message.message_attachment_original_filename}
                else:
                    self.database.addReceived(timestamp = message.message_timestamp, title = message.message_title, content = message.message_content)
                    newMessage = {"message_hash": message_hash, "message_timestamp": message.message_timestamp, "message_title": message.message_title, "message_content": message.message_content, "message_attachment_path": "", "message_attachment_original_filename": ""}
                self.newMessages.append(newMessage)

        self.getHashesFromDatabase()
        self.setState(self.STATE_WRITE_SWITCH)


class BluetoothServerVer3(Networking):
    """Class that deals with bluetooth networking using version 3 of the protocol, specifically using protocol buffers.  

TODO

* Write client that can connect to other machines
* Deal with different libraries such as lightblue."""


    def __init__(self, databaseDir = ".", databaseType = "pysqlite2", attachmentsDir = ".", logPath = "FluidNexus.log", level = logging.DEBUG, numConnections = 5):
        super(BluetoothServerVer3, self).__init__(databaseDir = databaseDir, databaseType = databaseType, attachmentsDir = attachmentsDir, logPath = logPath, level = level)

        # Do initial setup
        self.setupServerSockets(numConnections = numConnections)
        self.setupService()


        # Enter into the main loop
        #self.run()


    def setupServerSockets(self, numConnections = 5, blocking = 0):
        """Setup the socket for accepting connections."""
        self.serverSocket = BluetoothSocket(RFCOMM)
        self.serverSocket.bind(("", PORT_ANY))
        self.serverSocket.listen(numConnections)
        #self.serverSocket.setblocking(blocking)
        self.clientSockets = []

    def setupService(self):
        """Setup the service advertisement."""
        advertise_service(self.serverSocket, "FluidNexus", service_id = FluidNexusUUID, service_classes = [FluidNexusUUID, SERIAL_PORT_CLASS], profiles = [SERIAL_PORT_PROFILE])


    def cleanup(self, cs):
        """Do some sort of socket error handling if we ever get a command or data that we don't expect."""
        
        self.hashesToSend = None
        cs.close()
        cs = None
        self.setState(self.STATE_START)


    def handleClientConnection(self, cs):
        """Handle a connection on the client socket.
        
        TODO
        * Decide if we need to dispatch a new thread to deal with this connection."""
        notDone = True
        while (notDone):
            currentState = self.getState()

            if (currentState == self.STATE_READ_HELO):
                command = self.readCommand(cs)
                if (command != self.HELO):
                    self.cleanup(cs)
                else:
                    self.setState(self.STATE_WRITE_HELO)
            elif (currentState == self.STATE_WRITE_HELO):
                # TODO
                # Deal with errors in writing to socket
                self.writeCommand(cs, self.HELO)
                self.setState(self.STATE_READ_HASHES)
            elif (currentState == self.STATE_READ_HASHES):
                self.readHashes(cs)
            elif (currentState == self.STATE_WRITE_MESSAGES):
                self.writeMessages(cs)
            elif (currentState == self.STATE_READ_SWITCH):
                command = self.readCommand(cs)
                if (command != self.SWITCH):
                    self.cleanup(cs)
                else:
                    self.setState(self.STATE_WRITE_HASHES)
            elif (currentState == self.STATE_WRITE_HASHES):
                self.writeHashes(cs)
            elif (currentState == self.STATE_READ_MESSAGES):
                command = self.readCommand(cs)
                if (command != self.MESSAGES):
                    self.cleanup(cs)
                else:
                    self.readMessages(cs)
            elif (currentState == self.STATE_WRITE_SWITCH):
                self.writeCommand(cs, self.SWITCH)
                self.setState(self.STATE_READ_DONE)
            elif (currentState == self.STATE_READ_DONE):
                command = self.readCommand(cs)
                if (command != self.DONE):
                    self.cleanup(cs)
                else:
                    self.setState(self.STATE_WRITE_DONE)
            elif (currentState == self.STATE_WRITE_DONE):
                self.writeCommand(cs, self.DONE)
                self.cleanup(cs)
                notDone = False
            else:
                self.logger.debug("No command matches.")
                self.cleanup(cs)
                notDone = False

    def run(self):
        """Run the main loop."""
        
        self.openDatabase()
        self.getHashesFromDatabase()
        self.hashesToSend = None

        self.notDone = True

        while (self.notDone):

            currentState = self.getState()
            
            if (currentState == self.STATE_START):
                # TODO
                # * This should be dispatched into another thread, probably, and thus we need a separate self.hashesToSend in the other thread, separate states, etc.  Basically we'd need another class that would encapsulate those states.
                try:
                    cs, ci = self.serverSocket.accept()
                    self.clientSockets.append(cs)
                    self.setState(self.STATE_WAITING)
                except btcommon.BluetoothError, e:
                    pass
            elif (currentState == self.STATE_WAITING):
                # See if any sockets are ready to read
                rr, rw, ie = select.select(self.clientSockets, [], [], 60)

                # If a socket is ready to read, then pass off to method that handles the connection
                if (rr != []):
                    for cs in rr:
                        self.setState(self.STATE_READ_HELO)
                        self.handleClientConnection(cs)
                        self.clientSockets.remove(cs)
                        self.notDone = False
                

        self.closeDatabase()
        return self.newMessages

class BluetoothClientVer3(Networking):
    """Class that deals with bluetooth networking using version 3 of the protocol, specifically using protocol buffers.  

TODO

* Write client that can connect to other machines
* Deal with different libraries such as lightblue."""


    def __init__(self, databaseDir = ".", databaseType = "pysqlite2", attachmentsDir = ".", logPath = "FluidNexus.log", level = logging.DEBUG, numConnections = 5):
        super(BluetoothClientVer3, self).__init__(databaseDir = databaseDir, databaseType = databaseType, attachmentsDir = attachmentsDir, logPath = logPath, level = level)
        self.setState(self.STATE_START)

    def doDeviceDiscovery(self):
        """Do our device discovery."""

        self.logger.debug("Starting device discovery")
        self.devices = []

        nearbyDevices = discover_devices(lookup_names = True)
        self.devices = [list(device) for device in nearbyDevices]

        self.logger.debug("Device discovery completed")

    def doServiceDiscovery(self):
        """Do service discovery, adding devices to the list that run Fluid Nexus."""

        self.devicesFN = []

        for device in self.devices:
            services = find_service(uuid = FluidNexusUUID, address = device[0])
            
            if (len(services) > 0):
                device.append(services[0]["port"])
                self.devicesFN.append(device)

    def cleanup(self, cs):
        """Do some sort of socket error handling if we ever get a command or data that we don't expect."""
        
        self.hashesToSend = None
        cs.close()
        cs = None
        self.setState(self.STATE_START)

    def handleServerConnection(self, cs):
        """HELO            Write           Read
        HELO            Read            Write
        HASHES          Write           Read
        MESSAGES        Read            Write
        SWITCH          Write           Read
        HASHES          Read            Write
        MESSAGES        Write           Read
        SWITCH          Read            Write
        DONE            Write           Read
        DONE            Read            Write"""
        
        notDone = True
        while (notDone):
            currentState = self.getState()
            
            if (currentState == self.STATE_WRITE_HELO):
                # TODO
                # Deal with errors in writing to socket
                self.writeCommand(cs, self.HELO)
                self.setState(self.STATE_READ_HELO)
            elif (currentState == self.STATE_READ_HELO):
                command = self.readCommand(cs)
                if (command != self.HELO):
                    self.cleanup(cs)
                else:
                    self.setState(self.STATE_WRITE_HASHES)
            elif (currentState == self.STATE_WRITE_HASHES):
                self.writeHashes(cs)
                self.setState(self.STATE_READ_MESSAGES)
            elif (currentState == self.STATE_READ_MESSAGES):
                command = self.readCommand(cs)
                if (command != self.MESSAGES):
                    self.cleanup(cs)
                else:
                    self.readMessages(cs)
                    self.setState(self.STATE_WRITE_SWITCH)
            elif (currentState == self.STATE_WRITE_SWITCH):
                self.writeCommand(cs, self.SWITCH)
                self.setState(self.STATE_READ_HASHES)
            elif (currentState == self.STATE_READ_HASHES):
                self.readHashes(cs)
            elif (currentState == self.STATE_WRITE_MESSAGES):
                self.writeMessages(cs)
            elif (currentState == self.STATE_READ_SWITCH):
                command = self.readCommand(cs)
                if (command != self.SWITCH):
                    self.cleanup(cs)
                else:
                    self.setState(self.STATE_WRITE_DONE)
            elif (currentState == self.STATE_WRITE_DONE):
                self.writeCommand(cs, self.DONE)
                self.setState(self.STATE_READ_DONE)
            elif (currentState == self.STATE_READ_DONE):
                command = self.readCommand(cs)
                if (command != self.DONE):
                    self.cleanup(cs)
                else:
                    self.setState(self.STATE_START)
                    self.cleanup(cs)
                    notDone = False
            else:
                self.logger.debug("No command matches.")
                self.cleanup(cs)
                notDone = False

    def run(self):
        """Our run method."""
        self.notDone = True
        self.openDatabase()
        self.getHashesFromDatabase()
        self.hashesToSend = None
        self.newMessages = []

        while (self.notDone):

            currentState = self.getState()
           
            if (currentState == self.STATE_START):
                self.doDeviceDiscovery()
                self.doServiceDiscovery()
                cs = BluetoothSocket(RFCOMM)

                for device in self.devicesFN:
                    self.logger.debug("Connecting to '%s' (%s)" % (device[1], device[0]))
                    cs.connect((device[0], device[2]))
                    self.setState(self.STATE_WRITE_HELO)
                    self.handleServerConnection(cs)
                    cs.close()
                self.notDone = False

        self.closeDatabase()
        return self.newMessages

class ZeroconfServer(Networking):
    """Class that deals with zeroconf networking using version 3 of the protocol, specifically using protocol buffers."""

    def __init__(self, databaseDir = ".", databaseType = "pysqlite2", attachmentsDir = ".", logPath = "FluidNexus.log", level = logging.DEBUG, numConnections = 5):
        super(ZeroconfServer, self).__init__(databaseDir = databaseDir, databaseType = databaseType, attachmentsDir = attachmentsDir, logPath = logPath, level = level)

        # Do initial setup
        self.setupServerSockets(numConnections = numConnections)
        # TODO
        # conver to avahi zeroconf
        #self.setupService()

    def setupServerSockets(self, numConnections = 5, blocking = 0):
        """Setup the socket for accepting connections."""
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind(("", 17894))
        self.serverSocket.listen(numConnections)
        #self.serverSocket.setblocking(blocking)
        self.clientSockets = []

    def setupService(self):
        """Setup the service advertisement."""
        advertise_service(self.serverSocket, "FluidNexus", service_id = FluidNexusUUID, service_classes = [FluidNexusUUID, SERIAL_PORT_CLASS], profiles = [SERIAL_PORT_PROFILE])


    def cleanup(self, cs):
        """Do some sort of socket error handling if we ever get a command or data that we don't expect."""
        
        self.hashesToSend = None
        cs.close()
        cs = None
        self.setState(self.STATE_START)


    def handleClientConnection(self, cs):
        """Handle a connection on the client socket.
        
        TODO
        * Decide if we need to dispatch a new thread to deal with this connection."""
        notDone = True
        while (notDone):
            currentState = self.getState()

            if (currentState == self.STATE_READ_HELO):
                command = self.readCommand(cs)
                if (command != self.HELO):
                    self.cleanup(cs)
                else:
                    self.setState(self.STATE_WRITE_HELO)
            elif (currentState == self.STATE_WRITE_HELO):
                # TODO
                # Deal with errors in writing to socket
                self.writeCommand(cs, self.HELO)
                self.setState(self.STATE_READ_HASHES)
            elif (currentState == self.STATE_READ_HASHES):
                self.readHashes(cs)
            elif (currentState == self.STATE_WRITE_MESSAGES):
                self.writeMessages(cs)
            elif (currentState == self.STATE_READ_SWITCH):
                command = self.readCommand(cs)
                if (command != self.SWITCH):
                    self.cleanup(cs)
                else:
                    self.setState(self.STATE_WRITE_HASHES)
            elif (currentState == self.STATE_WRITE_HASHES):
                self.writeHashes(cs)
            elif (currentState == self.STATE_READ_MESSAGES):
                command = self.readCommand(cs)
                if (command != self.MESSAGES):
                    self.cleanup(cs)
                else:
                    self.readMessages(cs)
            elif (currentState == self.STATE_WRITE_SWITCH):
                self.writeCommand(cs, self.SWITCH)
                self.setState(self.STATE_READ_DONE)
            elif (currentState == self.STATE_READ_DONE):
                command = self.readCommand(cs)
                if (command != self.DONE):
                    self.cleanup(cs)
                else:
                    self.setState(self.STATE_WRITE_DONE)
            elif (currentState == self.STATE_WRITE_DONE):
                self.writeCommand(cs, self.DONE)
                self.cleanup(cs)
                notDone = False
            else:
                self.logger.debug("No command matches.")
                self.cleanup(cs)
                notDone = False

    def run(self):
        """Run the main loop."""
        
        self.openDatabase()
        self.getHashesFromDatabase()
        self.hashesToSend = None

        self.notDone = True

        while (self.notDone):

            currentState = self.getState()
            
            if (currentState == self.STATE_START):
                # TODO
                # * This should be dispatched into another thread, probably, and thus we need a separate self.hashesToSend in the other thread, separate states, etc.  Basically we'd need another class that would encapsulate those states.
                try:
                    cs, ci = self.serverSocket.accept()
                    self.clientSockets.append(cs)
                    self.setState(self.STATE_WAITING)
                except btcommon.BluetoothError, e:
                    pass
            elif (currentState == self.STATE_WAITING):
                # See if any sockets are ready to read
                rr, rw, ie = select.select(self.clientSockets, [], [], 60)

                # If a socket is ready to read, then pass off to method that handles the connection
                if (rr != []):
                    for cs in rr:
                        self.setState(self.STATE_READ_HELO)
                        self.handleClientConnection(cs)
                        self.clientSockets.remove(cs)
                        self.notDone = False
                

        self.closeDatabase()
        return self.newMessages


class ZeroconfClient(Networking):
    """Class that deals with zeroconf networking using version 3 of the protocol, specifically using protocol buffers.  """

    def __init__(self, databaseDir = ".", databaseType = "pysqlite2", attachmentsDir = ".", logPath = "FluidNexus.log", level = logging.DEBUG, host = "", port = 17894):
        super(ZeroconfClient, self).__init__(databaseDir = databaseDir, databaseType = databaseType, attachmentsDir = attachmentsDir, logPath = logPath, level = level)
        self.host = host
        self.port = port
        self.setState(self.STATE_START)


    def cleanup(self, cs):
        """Do some sort of socket error handling if we ever get a command or data that we don't expect."""
        
        self.hashesToSend = None
        cs.close()
        cs = None
        self.setState(self.STATE_START)

    def handleServerConnection(self, cs):
        """HELO            Write           Read
        HELO            Read            Write
        HASHES          Write           Read
        MESSAGES        Read            Write
        SWITCH          Write           Read
        HASHES          Read            Write
        MESSAGES        Write           Read
        SWITCH          Read            Write
        DONE            Write           Read
        DONE            Read            Write"""
        
        notDone = True
        while (notDone):
            currentState = self.getState()
            
            if (currentState == self.STATE_WRITE_HELO):
                # TODO
                # Deal with errors in writing to socket
                self.writeCommand(cs, self.HELO)
                self.setState(self.STATE_READ_HELO)
            elif (currentState == self.STATE_READ_HELO):
                command = self.readCommand(cs)
                if (command != self.HELO):
                    self.cleanup(cs)
                else:
                    self.setState(self.STATE_WRITE_HASHES)
            elif (currentState == self.STATE_WRITE_HASHES):
                self.writeHashes(cs)
                self.setState(self.STATE_READ_MESSAGES)
            elif (currentState == self.STATE_READ_MESSAGES):
                command = self.readCommand(cs)
                if (command != self.MESSAGES):
                    self.cleanup(cs)
                else:
                    self.readMessages(cs)
                    self.setState(self.STATE_WRITE_SWITCH)
            elif (currentState == self.STATE_WRITE_SWITCH):
                self.writeCommand(cs, self.SWITCH)
                self.setState(self.STATE_READ_HASHES)
            elif (currentState == self.STATE_READ_HASHES):
                self.readHashes(cs)
            elif (currentState == self.STATE_WRITE_MESSAGES):
                self.writeMessages(cs)
            elif (currentState == self.STATE_READ_SWITCH):
                command = self.readCommand(cs)
                if (command != self.SWITCH):
                    self.cleanup(cs)
                else:
                    self.setState(self.STATE_WRITE_DONE)
            elif (currentState == self.STATE_WRITE_DONE):
                self.writeCommand(cs, self.DONE)
                self.setState(self.STATE_READ_DONE)
            elif (currentState == self.STATE_READ_DONE):
                command = self.readCommand(cs)
                if (command != self.DONE):
                    self.cleanup(cs)
                else:
                    self.setState(self.STATE_START)
                    self.cleanup(cs)
                    notDone = False
            else:
                self.logger.debug("No command matches.")
                self.cleanup(cs)
                notDone = False

    def run(self):
        """Our run method."""
        self.notDone = True
        self.openDatabase()
        self.getHashesFromDatabase()
        self.hashesToSend = None
        self.newMessages = []

        while (self.notDone):

            currentState = self.getState()
           
            if (currentState == self.STATE_START):
                cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.logger.debug("Connecting to '%s' (%d)" % (self.host, self.port))
                cs.connect((self.host, self.port))

                self.setState(self.STATE_WRITE_HELO)
                self.handleServerConnection(cs)
                cs.close()
                self.notDone = False

        self.closeDatabase()
        return self.newMessages

