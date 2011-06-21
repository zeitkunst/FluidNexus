#!/usr/bin/env python
import os

from PyQt4 import QtCore

from FluidNexus.Networking import BluetoothClientVer3

settings = QtCore.QSettings("fluidnexus.net", "Fluid Nexus")
dataDir = unicode(settings.value("app/dataDir").toString())
name = unicode(settings.value("database/name").toString())
logPath = os.path.join(dataDir, "FluidNexus.log")
databaseDir = os.path.join(dataDir, name)
databaseType = unicode(settings.value("database/type").toString())

btClient = BluetoothClientVer3(databaseDir = dataDir, databaseType = databaseType, logPath = logPath)
btClient.run()
