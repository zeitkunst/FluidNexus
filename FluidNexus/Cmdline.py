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

from optparse import OptionParser
import version

def get_optparser():
    parser = OptionParser(
        version="Fluid Nexus v%s" % version.__version__, 
        description = """Fluid Nexus is an application for Android phones and desktop computers that exchanges messages without the need for centralized mobile networks. Messages hop from one device to another, being transferred by short-range networking technologies like bluetooth, as well as via the movement of people from one location to another.  For more information see http://fluidnexus.net.""")
    parser.add_option("-v", "--verbose", dest = "verbosity", action = "count",  help = "How verbose to be.  Use up to 3 v's for full debug.")
    return parser
