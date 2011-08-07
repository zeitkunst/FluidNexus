#!/usr/bin/env python
# vim: set fileencoding=utf-8
# Copyright (C) 2011, Nicholas Knouf
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

import logging
from optparse import OptionParser
import multiprocessing
import os
import sys

import FluidNexus
from FluidNexus.Cmdline import get_optparser

def start(verbosity = 0, headless = False):
    if (verbosity >= 3):
        level = logging.DEBUG
    elif (verbosity == 2):
        level = logging.INFO
    elif (verbosity == 1):
        level = logging.WARNING
    else:
        level = logging.ERROR

    if (headless):
        from PyQt4 import QtCore
        from FluidNexus.Networking import BluetoothServerVer3
        
        settings = QtCore.QSettings("fluidnexus.net", "Fluid Nexus")
        dataDir = unicode(settings.value("app/dataDir").toString())
        name = unicode(settings.value("database/name").toString())
        logPath = os.path.join(dataDir, "FluidNexus.log")
        databaseDir = os.path.join(dataDir, name)
        databaseType = unicode(settings.value("database/type").toString())
        
        btServer = BluetoothServerVer3(databaseDir = dataDir, databaseType = databaseType, logPath = logPath, level = level)
        btServer.run()
    else:
        from PyQt4 import QtGui
        from FluidNexus.GUI import FluidNexusDesktop
        
        app = QtGui.QApplication(sys.argv)
        fluidNexus = FluidNexusDesktop(level = level)
        fluidNexus.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    multiprocessing.freeze_support()

    # TODO
    # Better short option...
    # Disabling headless until we're able to figure out how to handle all of the threads, the sleeping, etc.
    #parser.add_option("-e", "--headless", dest = "headless", action = "store_true",  help = "Whether to run the network services without the GUI")
    parser = get_optparser()
    (options, args) = parser.parse_args()

    #start(verbosity = options.verbosity, headless = options.headless)
    start(verbosity = options.verbosity)
