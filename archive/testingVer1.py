#!/usr/bin/env python

import os

from PyQt4 import QtCore
from bluetooth import *

from database import FluidNexusDatabase

settings = QtCore.QSettings("fluidnexus.net", "Fluid Nexus")
dataDir = unicode(settings.value("app/dataDir").toString())
name = unicode(settings.value("database/name").toString())
databaseDir = os.path.join(dataDir, name)
databaseType = unicode(settings.value("database/type").toString())

database = FluidNexusDatabase(databaseDir = databaseDir, databaseType = databaseType)

uuid = "bd547e68-952b-11e0-a6c7-0023148b3104"
s = BluetoothSocket(RFCOMM)
s.bind(("", PORT_ANY))
s.listen(1)
advertise_service(s, "FluidNexus", service_id = uuid, service_classes = [uuid, SERIAL_PORT_CLASS], profiles = [SERIAL_PORT_PROFILE])

timestampLength = 13
ownerHashLength = 32

cs, ci = s.accept()
while True:
    print "Starting accept..."
    version = cs.recv(2)
    print version
    titleLength = cs.recv(3)
    print titleLength
    messageLength = cs.recv(6)
    print messageLength
    timestamp = cs.recv(timestampLength)
    print timestamp
    messageHash = cs.recv(ownerHashLength)
    print messageHash
    title = cs.recv(int(titleLength))
    print title
    message = cs.recv(int(messageLength))
    print message
