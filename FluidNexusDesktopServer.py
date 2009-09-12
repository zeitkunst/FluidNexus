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

from logger import Logger
from database import FluidNexusDatabase
from FluidNexusNetworking import FluidNexusServer

dataPath = '.'

# TODO
# Make this platform-agnostic using os module
log = Logger(os.path.join(dataPath,  u'FluidNexus.log'), prefix = 'FluidNexusServer: ')
sys.stderr = sys.stdout = log


if __name__ == "__main__":
    #database.setupDatabase()
    #database.all()
    #for item in database:
    #    print item
    try:
        database = FluidNexusDatabase(databaseType = "pysqlite2")
        database.setupDatabase()
        title = u'Client testing'
        data = u'This is nothing but a test of the client'
        hash = unicode(md5.md5(title + data).hexdigest())
        database.add_new("00", 0, title, data, hash, 0)
        database.all()
        for item in database:
            print item
        server = FluidNexusServer(database = database, library="lightblue")
        server.initMessageAdvertisements()
        server.run()
    except:
        log.print_exception_trace()
