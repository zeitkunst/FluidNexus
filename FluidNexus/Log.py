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

import sys

_loggerSetup = False
def getLogger(logPath = "FluidNexus.log", level = logging.WARN, console = True):
    global _loggerSetup

    if (_loggerSetup == False):
        logger = logging.getLogger('FluidNexus')
        logFormatter = logging.Formatter('%(asctime)s (%(process)d) %(levelname)s: %(message)s')
        fileHandler = logging.FileHandler(logPath)
        fileHandler.setFormatter(logFormatter)
        #level = getattr(logging, config.get("Station", "defaultLogLevel").upper())
        logger.addHandler(fileHandler)

        if (console and (sys.platform != "win32")):
            logger.addHandler(ConsoleHandler())
        logger.setLevel(level)
        _loggerSetup = True
        return logger
    else:
        return logging.getLogger("FluidNexus")


## {{{ http://code.activestate.com/recipes/576819/ (r3)
class ConsoleHandler(logging.StreamHandler):
    """A handler that logs to console in the sensible way.
    StreamHandler can log to *one of* sys.stdout or sys.stderr.
    It is more sensible to log to sys.stdout by default with only error
    (logging.ERROR and above) messages going to sys.stderr. This is how
    ConsoleHandler behaves.
    """

    def __init__(self):
        logging.StreamHandler.__init__(self)
        self.stream = None # reset it; we are not going to use it anyway

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self.__emit(record, sys.stderr)
        else:
            self.__emit(record, sys.stdout)

    def __emit(self, record, strm):
        self.stream = strm
        logging.StreamHandler.emit(self, record)

    def flush(self):
        # Workaround a bug in logging module
        # See:
        #   http://bugs.python.org/issue6333
        if self.stream and hasattr(self.stream, 'flush') and not self.stream.closed:
            logging.StreamHandler.flush(self)

