#!/usr/bin/env python
import os

from PyQt4 import QtCore

from FluidNexus.Networking import BluetoothServerVer3

settings = QtCore.QSettings("fluidnexus.net", "Fluid Nexus")
dataDir = unicode(settings.value("app/dataDir").toString())
name = unicode(settings.value("database/name").toString())
logPath = os.path.join(dataDir, "FluidNexus.log")
databaseDir = os.path.join(dataDir, name)
databaseType = unicode(settings.value("database/type").toString())

btServer = BluetoothServerVer3(databaseDir = dataDir, databaseType = databaseType, logPath = logPath)
btServer.run()
