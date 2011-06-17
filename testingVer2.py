#!/usr/bin/env python

import binascii
import hashlib
import os
import struct
import time

from PyQt4 import QtCore
from bluetooth import *

from database import FluidNexusDatabase

settings = QtCore.QSettings("fluidnexus.net", "Fluid Nexus")
dataDir = unicode(settings.value("app/dataDir").toString())
name = unicode(settings.value("database/name").toString())
databaseDir = os.path.join(dataDir, name)
databaseType = unicode(settings.value("database/type").toString())

#database = FluidNexusDatabase(databaseDir = databaseDir, databaseType = databaseType)

uuid = "bd547e68-952b-11e0-a6c7-0023148b3104"
s = BluetoothSocket(RFCOMM)
s.bind(("", PORT_ANY))
s.listen(1)
advertise_service(s, "FluidNexus", service_id = uuid, service_classes = [uuid, SERIAL_PORT_CLASS], profiles = [SERIAL_PORT_PROFILE])

timestampLength = 13
ownerHashLength = 32

unpacker = struct.Struct('>H')
packer = struct.Struct('>H')
hashPacker = struct.Struct('>32s')

HELO = 0x0010
HASH_LIST = 0x0020
HASH_REQUEST = 0x0030
DONE_DONE = 0x00F0

# TODO
# Need to figure out the time thing...
testTitle = 'This is a test from ver2'
testMessage = 'Nothing but a test.\n\nTesting here.\n\nHope this gets through.\n\nShould eventually try unicode.'
testData = {hashlib.md5(testTitle + testMessage).hexdigest():
            (str(int(float(time.time()))), testTitle, testMessage)
}
print testData

while True:
    print "starting accept sequence"
    cs, ci = s.accept()

    # Receive and send HELO
    print "=> Receive and send HELO"
    tmp = cs.recv(unpacker.size)
    print "received %s " % binascii.hexlify(tmp)
    unpacked_data = unpacker.unpack(tmp)
    print "unpacked: ", unpacked_data
    if (unpacked_data[0] == HELO):
        cs.send(packer.pack(HELO))
    else:
        print "non equals"
        cs.send(packer.pack(0xF0))

    # Receive command for hash list
    print "=> Receive command for hash list"
    tmp = cs.recv(unpacker.size)
    print "received %s " % binascii.hexlify(tmp)
    unpacked_data = unpacker.unpack(tmp)
    if (unpacked_data[0] == HASH_LIST):
        print "=> Send hashes"
        # Send hashes
        # TODO
        # Deal with having more hashes than we can send
        numHashes = len(testData.keys())
        numHashesPacked = packer.pack(numHashes)

        cs.send(numHashesPacked)
        for currentHash in testData.keys():
            cs.send(hashPacker.pack(currentHash))
    else:
        print "non equals"
        cs.send(packer.pack(0xF0))

    # Receive command for particular hash request
    print "=> Receive command for particular hash request"
    tmp = cs.recv(unpacker.size)
    print "received %s " % binascii.hexlify(tmp)
    unpacked_data = unpacker.unpack(tmp)
    if (unpacked_data[0] == HASH_REQUEST):
        # Receiving hash request
        print "=> Receiving hash request"
        # TODO
        # should figure out how to deal with this using the struct
        tmpHash = cs.recv(32)
        print tmpHash

        # Send data corresponding to hash
        print "=> Send data corresponding to hash %s" % tmpHash
        dataToSend = testData[tmpHash]
        versionPack = struct.Struct(">B")
        cs.send(versionPack.pack(0x02))
        
        titleLengthPack = struct.Struct(">I")
        cs.send(titleLengthPack.pack(int(len(dataToSend[1]))))

        messageLengthPack = struct.Struct(">I")
        cs.send(messageLengthPack.pack(int(len(dataToSend[2]))))

        print "Length of timestamp: " + str(len(dataToSend[0]))
        timestampPacker = struct.Struct(">10s")
        cs.send(timestampPacker.pack(dataToSend[0]))

        titlePacker = struct.Struct(">%ds" % int(len(dataToSend[1])) )
        cs.send(titlePacker.pack(dataToSend[1]))
        #cs.send(dataToSend[1])

        messagePacker = struct.Struct(">%ds" % int(len(dataToSend[2])) )
        cs.send(messagePacker.pack(dataToSend[2]))
        #cs.send(dataToSend[2])

    else:
        print "non equals"
        cs.send(packer.pack(0xF0))

    # Receive command for done done
    print "=> Receive command for done done"
    tmp = cs.recv(unpacker.size)
    print "received %s " % binascii.hexlify(tmp)
    unpacked_data = unpacker.unpack(tmp)
    if (unpacked_data[0] == DONE_DONE):
        print "=> Sending back command"
        cs.send(packer.pack(DONE_DONE))
    else:
        print "non equals"
        cs.send(packer.pack(0xF0))

