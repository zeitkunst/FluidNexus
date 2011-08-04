#!/usr/bin/env python

# Standard library imports
import base64
import binascii
import cookielib
import hashlib
import logging
import MultipartPostHandlerUnicode
import os
import select
import socket
import struct
import time
import urllib
import urllib2

# External imports
from bluetooth import *
import oauth2
import simplejson as json

# TODO
# Modularize this for different platforms
import pybonjour

# My imports
import FluidNexus_pb2
from Database import FluidNexusDatabase
import Log

class ZeroconfClientCompleteException(Exception): 
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr("ZeroconfClientCompleteException: " + self.value)

FluidNexusUUID = "bd547e68-952b-11e0-a6c7-0023148b3104"

# zeroconf service type
ZEROCONF_SERVICE_TYPE ="_fluidnexus._tcp"

# Command constants
HELO = 0x0010
HASH_LIST = 0x0020
HASH_REQUEST = 0x0030
SWITCH = 0x0040
SWITCH_DONE = 0x0041
DONE_DONE = 0x00F0

# Nexus constants
NEXUS_HOST = "http://dev.fluidnexus.net"
NEXUS_NONCE_ENDPOINT = NEXUS_HOST + "/api/01/nexus/message/nonce.json"
NEXUS_MESSAGE_ENDPOINT = NEXUS_HOST + "/api/01/nexus/message/update.json"
NEXUS_HASH_ENDPOINT = NEXUS_HOST + "/api/01/nexus/hashes/%s.json"

# TODO
# * Deal with settings/config better
# * Better error checking, deal with socket timeouts, socket closing, etc
# * * Basically need to wrap all "recv" with a "read" that takes in socket, amount to read, and captures error of "bluetooth.btcommon.BluetoothError: (104, 'Connection reset by peer')"

class NexusError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr("NexusError: " + self.value)

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

    stateMapping = {0x0000: "STATE_START",
                    0x0001: "STATE_WAITING",
                    0x0010: "STATE_READ_HELO",
                    0x0020: "STATE_WRITE_HELO",
                    0x0030: "STATE_READ_HASHES",
                    0x0040: "STATE_WRITE_MESSAGES",
                    0x0050: "STATE_READ_SWITCH",
                    0x0060: "STATE_WRITE_HASHES",
                    0x0070: "STATE_READ_MESSAGES",
                    0x0080: "STATE_WRITE_SWITCH",
                    0x0090: "STATE_READ_DONE",
                    0x00A0: "STATE_WRITE_DONE",
                    0x00F0: "STATE_QUIT",
                   }

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
        self.logLevel = level

    def openDatabase(self):
        self.database = FluidNexusDatabase(databaseDir = self.databaseDir, databaseType = self.databaseType, level = self.logLevel)

    def closeDatabase(self):
        self.database.close()

    def setState(self, state):
        """Set our state."""
        #tmpNewState = str(state)
        tmpNewState = self.stateMapping[state]
        #tmpOldState = str(self.state)
        tmpOldState = self.stateMapping[self.state]

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
            m.message_received_timestamp = data['received_time']
            m.message_title = data['title']
            m.message_content = data['content']
            m.message_type = FluidNexus_pb2.FluidNexusMessage.TEXT
            m.message_public = data["public"]

            if (data["public"]):
                m.message_ttl = data["ttl"]

            if (data["attachment_path"] != ""):
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

        # Go through the received messages and add any that were received
        fields = messages.ListFields()
        self.newMessages = []
        if (fields != []):
            for message in fields[0][1]: 
                message_hash = hashlib.sha256(message.message_title.encode("utf-8") + message.message_content.encode("utf-8")).hexdigest()

                if (message.message_attachment_original_filename != ""):
                    basename, ext = os.path.splitext(message.message_attachment_original_filename)
                    message_attachment_path = os.path.join(self.attachmentsDir, message_hash + ext)
                    attachmentFP = open(message_attachment_path, "wb")
                    attachmentFP.write(message.message_attachment)
                    attachmentFP.close()
                    
                    # Decrement TTL
                    if (message.message_public and (message.message_ttl != 0)):
                        message.message_ttl = message.message_ttl - 1

                    if (not self.database.checkForMessageByHash(message_hash)):
                        self.database.addReceived(timestamp = message.message_timestamp, received_timestamp = time.time(), title = message.message_title, content = message.message_content, attachment_path = message_attachment_path, attachment_original_filename = message.message_attachment_original_filename, public = message.message_public, ttl = message.message_ttl)
                        newMessage = {"message_hash": message_hash, "message_timestamp": message.message_timestamp, "message_received_timestamp": message.message_received_timestamp, "message_title": message.message_title, "message_content": message.message_content, "message_attachment_path": message_attachment_path, "message_attachment_original_filename": message.message_attachment_original_filename, "message_public": message.message_public, "message_ttl": message.message_ttl}
                        self.newMessages.append(newMessage)
                else:
                    # Decrement TTL
                    if (message.message_public and (message.message_ttl != 0)):
                        message.message_ttl = message.message_ttl - 1

                    if (not self.database.checkForMessageByHash(message_hash)):
                        self.database.addReceived(timestamp = message.message_timestamp, received_timestamp = time.time(), title = message.message_title, content = message.message_content, public = message.message_public, ttl = message.message_ttl)
                        newMessage = {"message_hash": message_hash, "message_timestamp": message.message_timestamp, "message_received_timestamp": message.message_received_timestamp, "message_title": message.message_title, "message_content": message.message_content, "message_attachment_path": "", "message_attachment_original_filename": "", "message_public": message.message_public, "message_ttl": message.message_ttl}
                        self.newMessages.append(newMessage)

        self.getHashesFromDatabase()
        self.setState(self.STATE_WRITE_SWITCH)

class NexusNetworking(Networking):
    """Class for dealing with uploading public messages to the nexus."""

    def __init__(self, databaseDir = ".", databaseType = "pysqlite2", attachmentsDir = ".", logPath = "FluidNexus.log", level = logging.DEBUG, key = "", secret = "", token = "", token_secret = ""):

        super(NexusNetworking, self).__init__(databaseDir = databaseDir, databaseType = databaseType, attachmentsDir = attachmentsDir, logPath = logPath, level = level)

        self.key = key
        self.secret = secret
        self.token = token
        self.token_secret = token_secret

    def build_request(self, url, method="POST"):
        # TODO
        # do we need to add in oauth_callback to be in compliance?
        consumer = oauth2.Consumer(key = self.key, secret = self.secret)
        #params = {}
        #params.update(message)
        token = oauth2.Token(self.token, self.token_secret)
        #req = oauth2.Request.from_consumer_and_token(consumer, token = token, http_method=method, http_url=url, parameters=params)
        req = oauth2.Request.from_consumer_and_token(consumer, token = token, http_method=method, http_url=url)
        signature_method = oauth2.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, consumer, token)
        return req

    def run(self):
        self.openDatabase()
        self.getHashesFromDatabase()
        publicMessages = self.database.public()

        # TODO
        # Check that we can access internet
        for message in publicMessages:
            if (not message["uploaded"]):
                try:
                    u = urllib2.urlopen(NEXUS_HASH_ENDPOINT % message["message_hash"])
                except urllib2.URLError, e:
                    self.logger.error("Some sort of urllib2 error: " + str(e))
                    return False

                result = u.read()
                u.close()
                result = json.loads(result)
                
                # If the result is true, then the message has already been uploaded by someone else and we should save this result
                if (result["result"]):
                    self.database.setUploaded(message["message_hash"])
                else:
                    self.logger.debug("NO MESSAGE WITH HASH %s FOUND" % message["message_hash"])

                    # Check that the token is not ""
                    if (self.token == ""):
                        self.logger.warn("Cannot upload to the nexus without an access token; please enter a valid token in the preferences.")
                        return False
                    
                    uploadData = {}
                    if (message["attachment_original_filename"] == ""):
                        messageJSON = {"message_title": message["title"], "message_content": message["content"], "message_hash": message["message_hash"], "message_time": message["time"], "message_type": message["message_type"]}
                    else:
                        # TODO
                        # Error handling :-)
                        attachmentDataFP = open(os.path.realpath(message["attachment_path"]), 'rb')
                        #attachmentData = attachmentDataFP.read()
                        #attachmentDataFP.close()
                        #attachmentDataBase64 = base64.b64encode(attachmentData)
                        messageJSON = {"message_title": message["title"], "message_content": message["content"], "message_hash": message["message_hash"], "message_time": message["time"], "message_type": message["message_type"], "message_attachment_original_filename": message["attachment_original_filename"]}
                        uploadData["message_attachment"] = attachmentDataFP

                    request = self.build_request(NEXUS_NONCE_ENDPOINT)
                    try:
                        # get our nonce
                        u = urllib2.urlopen(NEXUS_NONCE_ENDPOINT, data = request.to_postdata())
                        result = u.read()
                        u.close()
    
                        result = json.loads(result)
                        
                        if (not result.has_key("nonce")):
                            break

                        nonce = result["nonce"]

                        # Now take our nonce and add it to the message
                        messageJSON["message_nonce"] = nonce
                        messageJSON["message_key"] = self.key
                        uploadData["message"] = json.dumps(messageJSON)

                        cookies = cookielib.CookieJar()
                        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies), MultipartPostHandlerUnicode.MultipartPostHandler)
                        response = opener.open(NEXUS_MESSAGE_ENDPOINT, uploadData)
                        result = response.read()
                        response.close()

                        #u = urllib2.urlopen(NEXUS_MESSAGE_ENDPOINT, data = urllib.urlencode(data))
                        #result = u.read()
                        #u.close()
                        result = json.loads(result)
                        if (result["result"]):
                            self.database.setUploaded(message["message_hash"])
                            return True
                        else:
                            raise NexusError(result["result"])

                    except urllib2.URLError, e:
                        self.logger.error("Some sort of urllib2 error: " + str(e))
                        return False
                    except NexusError, e:
                        self.logger.error("Error pushing message to the nexus: " + str(e))
                        return False




class BluetoothServerVer3(Networking):
    """Class that deals with bluetooth networking using version 3 of the protocol, specifically using protocol buffers.  

TODO

* Write client that can connect to other machines
* Deal with different libraries such as lightblue."""


    def __init__(self, databaseDir = ".", databaseType = "pysqlite2", attachmentsDir = ".", logPath = "FluidNexus.log", level = logging.DEBUG, numConnections = 5, setup = False):
        super(BluetoothServerVer3, self).__init__(databaseDir = databaseDir, databaseType = databaseType, attachmentsDir = attachmentsDir, logPath = logPath, level = level)
    
        self.numConnections = numConnections

        if setup:
            # Do initial setup
            self.setupServerSockets(numConnections = self.numConnections)
            self.setupService()


    def testBluetooth(self):
        """Test the bluetooth connection."""
        try:
            # Do initial setup
            self.setupServerSockets(numConnections = self.numConnections)
            self.setupService()

            nearbyDevices = discover_devices(duration = 1)
            return True
        except BluetoothError, e:
            self.logger.error("Unable to setup bluetooth, BluetoothError: " + str(e))
            return False
        except IOError, e:
            self.logger.error("Unable to setup bluetooth, IOError: " + str(e))
            return False

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

    def testBluetooth(self):
        """Test the bluetooth connection."""
        try:
            nearbyDevices = discover_devices(duration = 1)
            return True
        except BluetoothError, e:
            return False

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

    def __init__(self, databaseDir = ".", databaseType = "pysqlite2", attachmentsDir = ".", logPath = "FluidNexus.log", level = logging.DEBUG, numConnections = 5, host = "", port = 17897):
        super(ZeroconfServer, self).__init__(databaseDir = databaseDir, databaseType = databaseType, attachmentsDir = attachmentsDir, logPath = logPath, level = level)
        self.host = host
        self.port = port
        self.name = hashlib.md5(str(time.time())).hexdigest()
        self.domain = ""
        self.text = ""
        self.numConnections = numConnections

        # Do initial setup
        #self.setupServerSockets(numConnections = numConnections)
        # TODO
        # conver to avahi zeroconf
        #self.setupService()

    def setupServerSockets(self, numConnections = 5, blocking = 0):
        """Setup the socket for accepting connections."""
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((self.host, self.port))
        self.serverSocket.listen(numConnections)
        self.clientSockets = []

    def serviceCallback(self, sdRef, falgs, errorCode, name, regtype, domain):
        """Callback for when we have setup a service."""
        if (errorCode == pybonjour.kDNSServiceErr_NoError):
            self.logger.debug("Registered service:\nname: " + name + "\nregtype: " + regtype + "\ndomain: " + domain)

    def setupService(self):
        """Setup the service for zeroconf."""
        self.sdRef = pybonjour.DNSServiceRegister(name = self.name, regtype = ZEROCONF_SERVICE_TYPE, port = self.port, callBack = self.serviceCallback)

        """
        bus = dbus.SystemBus()
        server = dbus.Interface(
                         bus.get_object(
                                 avahi.DBUS_NAME,
                                 avahi.DBUS_PATH_SERVER),
                        avahi.DBUS_INTERFACE_SERVER)

        g = dbus.Interface(
                    bus.get_object(avahi.DBUS_NAME,
                                   server.EntryGroupNew()),
                    avahi.DBUS_INTERFACE_ENTRY_GROUP)

        g.AddService(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC,dbus.UInt32(0),
                     self.name, ZEROCONF_SERVICE_TYPE, self.domain, self.host,
                     dbus.UInt16(self.port), self.text)

        g.Commit()
        self.group = g
        """

    def takedownService(self):
        """Stop the zeroconf service"""
        #self.group.Reset()
        self.sdRef.close()
        self.serverSocket.shutdown(1)
        self.serverSocket.close()

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

                self.setupServerSockets(numConnections = self.numConnections)
                self.setupService()
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
        self.takedownService()
        return self.newMessages


class ZeroconfClient(Networking):
    """Class that deals with zeroconf networking using version 3 of the protocol, specifically using protocol buffers.  """

    timeout = 5
    resolved = []

    def __init__(self, databaseDir = ".", databaseType = "pysqlite2", attachmentsDir = ".", logPath = "FluidNexus.log", level = logging.DEBUG, host = "", port = 9999, loopType = "glib"):
        super(ZeroconfClient, self).__init__(databaseDir = databaseDir, databaseType = databaseType, attachmentsDir = attachmentsDir, logPath = logPath, level = level)
        self.host = host
        self.port = port
        self.loopType = loopType
        self.setState(self.STATE_START)

        self.openDatabase()
        self.getHashesFromDatabase()
        self.closeDatabase()

    def resolveCallback(self, sdRef, flags, interfaceIndex, errorCode, fullname, hosttarget, port, txtRecord):
        """Our callback for resolved hosts."""

        if (errorCode == pybonjour.kDNSServiceErr_NoError):
            #self.logger.debug("Resolved service: " + "\nfullname: " + fullname + "\nhosttarget: " + hosttarget + "\nport: " + str(port))
            
            # Filter out our own zeroconf service
            # TODO
            # Will this work in all cases?
            if (hosttarget.find(socket.gethostname() + ".local.") == -1):
                self.resolved.append(True)
    
                self.openDatabase()
                self.getHashesFromDatabase()
                self.hashesToSend = None
    
                cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.logger.debug("Connecting to '%s' (%d)" % (hosttarget, port))
                cs.connect((hosttarget, port))
        
                self.setState(self.STATE_WRITE_HELO)
                self.handleServerConnection(cs)
                cs.close()
                self.closeDatabase()
                self.clientNotComplete = False


    def browseCallback(self, sdRef, flags, interfaceIndex, errorCode, serviceName, regtype, replyDomain):
        """Our callback for browsing services."""
        if (errorCode != pybonjour.kDNSServiceErr_NoError):
            return

        if (not (flags & pybonjour.kDNSServiceFlagsAdd)):
            self.logger.debug("Service removed")
            return

        #self.logger.debug("Service added; resolving")

        self.resolveSDRef = pybonjour.DNSServiceResolve(0, interfaceIndex, serviceName, regtype, replyDomain, self.resolveCallback)

        try:
            while not self.resolved:
                ready = select.select([self.resolveSDRef], [], [], self.timeout)
                if self.resolveSDRef not in ready[0]:
                    #self.logger.error("Resolve timed out")
                    break
                pybonjour.DNSServiceProcessResult(self.resolveSDRef)
            else:
                self.resolved.pop()
        finally:
            self.resolveSDRef.close()
       
    def testZeroconf(self):
        try:
            browse = pybonjour.DNSServiceBrowse(regtype = ZEROCONF_SERVICE_TYPE)
            browse.close()
            return True
        except pybonjour.BonjourError, e:
            if (e[0] == -65537):
                return False


    def setupBrowse(self):
        """Setup our service browsing."""
        self.browseSDRef = pybonjour.DNSServiceBrowse(regtype = ZEROCONF_SERVICE_TYPE, callBack = self.browseCallback)

        self.clientNotComplete = True
        try:
            try:
                while self.clientNotComplete:
                    ready = select.select([self.browseSDRef], [], [])
                    if self.browseSDRef in ready[0]:
                        pybonjour.DNSServiceProcessResult(self.browseSDRef)
            except KeyboardInterrupt:
                pass
        finally:
            self.browseSDRef.close()
            return self.newMessages

    def serviceResolvedError(self, *args):
        self.logger.debug("Service resolution error: " + args[0])

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

        # Our method for doing all of the browsing and service resolving
        self.setupBrowse()
        return self.newMessages

