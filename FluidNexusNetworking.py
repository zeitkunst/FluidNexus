# Copyright (C) 2008, Nick Knouf, Bruno Vianna, and Luis Ayuso
# 
# This file is part of Fluid Nexus
#
# Fluid Nexus is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# Standard library imports
import sys
import os
import socket
import select
import md5
import time
import thread

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
from database import FluidNexusDatabase

FLUID_NEXUS_PROTOCOL_VERSION = '01'

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


########################################################################
#  acceptCallback
########################################################################
ownerHashLength = 32
timestampLength = 13
cellIDLength = None

########################################################################
#  FluidNexusServer
########################################################################
class FluidNexusServer(object):
    numberConnections = 2
    connections = []
    currentlyAccepting = False

    def __init__(self, serviceName = u'FluidNexus', database = None):
        """Initialize the server be setting up the server socket and advertising the FluidNexus service."""

        log.write("Starting Fluid Nexus Server")
        # Save our database object 
        self.database = database

        # Save our service name
        self.serviceName = serviceName

        self.mutex = thread.allocate_lock()

        # Setup our server socket
        self.serverSocket = socket.socket(socket.AF_BT, socket.SOCK_STREAM)
        self.serverPort = socket.bt_rfcomm_get_available_server_channel(self.serverSocket)
        self.serverSocket.bind(("", self.serverPort))
        self.serverSocket.listen(self.numberConnections)
        socket.bt_advertise_service(self.serviceName, self.serverSocket, True, socket.RFCOMM)

        # Remove security protections
        # @TODO@ Make sure this actually does what we want it to do!
        socket.set_security(self.serverSocket, 0)

    def __exit__(self):
        """This method can probably be removed."""
        if running:
            running = 0
        app_lock.signal()
        log.write("goodbye!")

    def initMessageAdvertisements(self):
        """Initialize the advertisement of hashes that have been sent to us."""

        # @TODO@ Use the correct database here :-)
        #self.database.query('select * from FluidNexusStigmergy')
        self.database.services()

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

    def advertiseNewHash(self, hash):
        """Advertise a new hash that we have just received."""
        
        log.write(str(hash))
        newSocket = socket.socket(socket.AF_BT, socket.SOCK_STREAM)
        self.advertisingSockets[hash] = newSocket
        tempPort = socket.bt_rfcomm_get_available_server_channel(newSocket)
        newSocket.bind(("", tempPort))
        newSocket.listen(1)
        socket.bt_advertise_service(unicode(':' + hash), newSocket, True, socket.RFCOMM)

    def acceptCallback(self, clientData):
        """CANDIDATE FOR REMOVAL: We do everything in the run method right now, since we choose to block (as we're running in a separate process)."""
        log.write(str(clientData))
   
        self.mutex.acquire()
        # Get client info
        clientSocket = clientData[0]
        clientAddress = clientData[1]

        #####################################################
        #  Read header information
        #  ASSUME BIG ENDIAN BYTE ORDER!
        #####################################################
        
        # VERSION: 1 byte
        version = clientSocket.recv(2)
        log.write(str(version))
        
        # @TODO@
        # In the future, split here based on different versions
        
        # TITLE LENGTH: 2 bytes
        titleLength = clientSocket.recv(3)
        log.write(str(titleLength))
    
        # MESSAGE LENGTH: 4 bytes
        # Note: this is to eventually support unicode text
        messageLength = clientSocket.recv(6)
        log.write(str(messageLength))
    
        #####################################################
        #  Start reading data!
        #  ASSUME BIG ENDIAN BYTE ORDER!
        #####################################################
        timestamp = clientSocket.recv(timestampLength)
        log.write(str(timestamp))
        # Skip cellID for now
        #cellID = clientSocket.recv(cellIDLength)
        ownerHash = clientSocket.recv(ownerHashLength)
        log.write(str(ownerHash))
        title = clientSocket.recv(int(titleLength))
        log.write(str(title))
        message = clientSocket.recv(int(messageLength))
        log.write(str(message))

        self.mutex.release()

        # Finish up
        # @TODO@
        # Add the correct owner bluetooth ID hash
        self.database.add_received(ownerHash, timestamp, 0, title, message, md5.md5(title + message).hexdigest(), '0')
        self.advertiseNewHash(md5.md5(title + message).hexdigest())
        try:
            self.currentlyAccepting = False
            self.serverSocket.accept(self.acceptCallback)
            log.write("after starting new accept thread")
            #clientSocket.close()
        except Exception, e:
            log.write(str(e))

        #import audio
        #f = 'Z:\\Nokia\\Sounds\\Digital\\Message.mid'
        #s = audio.Sound.open(f); s.play()
        #s.close()
        self.database.setSignal()

    def run(self):
        """Main loop with blocking accept."""

        clientData = self.serverSocket.accept()

        log.write(str(clientData))
   
        # Get client info
        clientSocket = clientData[0]
        clientAddress = clientData[1]
        
        #####################################################
        #  Read header information
        #  ASSUME BIG ENDIAN BYTE ORDER!
        #####################################################
        
        # VERSION: 1 byte
        version = clientSocket.recv(2)
        log.write(str(version))
        
        # @TODO@
        # In the future, split here based on different versions
        
        # TITLE LENGTH: 2 bytes
        titleLength = clientSocket.recv(3)
        log.write(str(titleLength))
    
        # MESSAGE LENGTH: 4 bytes
        # Note: this is to eventually support unicode text
        messageLength = clientSocket.recv(6)
        log.write(str(messageLength))
    
        #####################################################
        #  Start reading data!
        #  ASSUME BIG ENDIAN BYTE ORDER!
        #####################################################
        timestamp = clientSocket.recv(timestampLength)
        log.write(str(timestamp))
        # Skip cellID for now
        #cellID = clientSocket.recv(cellIDLength)
        ownerHash = clientSocket.recv(ownerHashLength)
        log.write(str(ownerHash))
        title = clientSocket.recv(int(titleLength))
        log.write(str(title))
        message = clientSocket.recv(int(messageLength))
        log.write(str(message))


        # Finish up
        # @TODO@
        # Add the correct owner bluetooth ID hash
        self.database.add_received(ownerHash, timestamp, 0, title, message, md5.md5(title + message).hexdigest(), '0')
        self.advertiseNewHash(md5.md5(title + message).hexdigest())
        try:
            self.currentlyAccepting = False
            self.serverSocket.accept(self.acceptCallback)
            log.write("after starting new accept thread")
            #clientSocket.close()
        except Exception, e:
            log.write(str(e))

    def runOld(self):
        """Main loop for the server."""
        # @TODO@
        # Figure out how to accept connections continuously
        self.running = True
        self.serverSocket.accept(self.acceptCallback)
#        while 1:
#            if not self.currentlyAccepting:
#                self.currentlyAccepting = True
#                print "trying to call the accept."
#                self.serverSocket.accept(self.acceptCallback)
            #clientSocket, clientAddress = self.serverSocket.accept()
            #print clientSocket

class FluidNexusClient(object):
    def __init__(self, database = None):
        """Initialize the client."""
        log.write("Starting Fluid Nexus Client")
        self.mutex = thread.allocate_lock()
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

    def sendData(self, data, phone, port):
        """Send our data to the other phone!"""
        clientTimer = e32.Ao_timer()

        messageTime = data[2]
        title = data[4]
        message = data[5]
        log.write("trying to open a client socket")
        clientSocket = socket.socket(socket.AF_BT, socket.SOCK_STREAM)
        log.write("writing to socket %s" % str(clientSocket)) 

        # Connect to the other phone; perhaps we should consider grabbing some sort of lock to ensure that the connection happens
        try:
            log.write("trying to use client socket to connect")
            clientSocket.connect((phone[0], port))
        except Exception, e:
            log.write("unable to open client socket")
            log.write(str(e))
            clientSocket.close()
            return
        try:
            log.write("going through send process")
            clientSocket.send(FLUID_NEXUS_PROTOCOL_VERSION)
            clientTimer.after(1)
            clientSocket.send("%03d" % len(title))
            clientTimer.after(1)
            clientSocket.send("%06d" % len(message))
            clientTimer.after(1)
            clientSocket.send(str(messageTime))
            clientTimer.after(1)
            clientSocket.send(md5.md5(title + message).hexdigest())
            clientTimer.after(1)
            clientSocket.send(title)
            clientTimer.after(1)
            clientSocket.send(message)
            clientTimer.after(1)
            clientSocket.close()
        except:
            log.write("unable to send to server")

    def getOurMessageHashes(self):
        """Return a list of the messages marked as 'mine'."""
        ourMessageHashes = []

        self.db.outgoing()

        for item in self.db:
            ourMessageHashes.append(item[6])

        return ourMessageHashes

    def getNotOurMessageHashes(self):
        """Return a list of the messages marked as 'mine'."""
        notOurMessageHashes = []

        self.db.non_outgoing()

        for item in self.db:
            notOurMessageHashes.append(item[6])

        return notOurMessageHashes


    def getServerMessageHashes(self, services):
        """Loop through the services that we've gotten and return a list of hashes that we've seen."""
        serverMessageHashes = []
        
        for service in services:
            if service[2][0] == ':':
                serverMessageHashes.append(service[2][1:])

        return serverMessageHashes

    def runLightblue(self):
        """Version of the run method that uses lightblue to find devices and services."""

        log.write("looking for devices")
        #allDevices = socket.bt_discover()
        allDevices = lightblue.finddevices()
        phones = []

        for device in allDevices:
            foo, isPhone, bar = self.splitclass(device[2])
            # TODO
            # This needs to be changed back to "2" after my Android testing
            # is done
            if isPhone == 1:
                phones.append(device)

        for phone in phones:
            log.write("Looking at phone %s" % str(phone))
            services = lightblue.findservices(phone[0])
            port = None
            for service in services:
                if service[2] is not None and service[2] == 'FluidNexus':
                    port = service[1]
                    break
                else:
                    port = None
            log.write("at end of service search")
            
            log.write(str(port))
            if port is not None:
                serverMessageHashes = self.getServerMessageHashes(services)
                ourMessageHashes = self.getOurMessageHashes()
                notOurMessageHashes = self.getNotOurMessageHashes()
                hashesToSend = []

                # First, check if any of our outgoing messages are already on
                # the server
                for hash in serverMessageHashes:
                    if hash in ourMessageHashes:
                        ourMessageHashes.remove(hash)
                hashesToSend.extend(ourMessageHashes)

                # Then, check if any of our other messages are on the server
                for hash in serverMessageHashes:
                    if hash in notOurMessageHashes:
                        notOurMessageHashes.remove(hash)
                hashesToSend.extend(notOurMessageHashes)

                # Thus we have a precedence where the ones that we have created will appear first in the list

                if hashesToSend != []:
                    log.write("sending data!")
                    for hash in hashesToSend:
                        data = self.db.returnItemBasedOnHash(hash)
                        log.write(str(data))
                        self.sendData(data, phone, port)
                else:
                    log.write("no data to send")

    def run(self):
        """Version of the run method that does not use the lightblue library; does not work because "bt_discover" opens up a window, but doesn't return a list."""

        allDevices = socket.bt_discover()
        phones = []

        for device in allDevices:
            foo, isPhone, bar = self.splitclass(device[2])
            if isPhone == 2:
                phones.append(device)

        for phone in phones:
            log.write("Looking at phone %s" % str(phone))
            services = socket.bt_discover(phone[0])
            log.write(str(services))
            for service in services:
                if service[2] is not None and 'FluidNexus' in service[2]:
                    port = service[1]
                    break
                else:
                    port = None
            log.write(str(port))
            log.write("at end of service search")

            if port is not None:
                log.write("sending data!")
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


if __name__ == """__main__""":
    pass
    try:
        database = FluidNexusDatabase()

        server = FluidNexusServer(database = database)
        server.initMessageAdvertisements()
        server.run()
    except:
        log.print_exception_trace()
