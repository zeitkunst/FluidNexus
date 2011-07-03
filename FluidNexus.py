#!/usr/bin/env python

import logging
from optparse import OptionParser
import os
import sys




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

        import dbus
        from dbus.mainloop.qt import DBusQtMainLoop
        import avahi
        ZEROCONF_SERVICE_TYPE = "_fluidnexus._tcp"

        def serviceResolved(*args):
            """Handle the resolution of the service."""
            print("Received args: " + str(args))

        def serviceResolvedError(*args):
            """Handle the resolution of the service."""
            print("Error: " + str(args))

        def serviceHandler(interface, protocol, name, stype, domain, flags):
            """Setup the handler for connecting to services."""
            print("Found service '%s' type '%s' domain '%s'" % (name, stype, domain))
        
            if flags & avahi.LOOKUP_RESULT_LOCAL:
                pass
        
            server.ResolveService(interface, protocol, name, stype, domain, avahi.PROTO_UNSPEC, dbus.UInt32(0), reply_handler=serviceResolved, error_handler = serviceResolvedError)


        loop = DBusQtMainLoop(set_as_default = True)

        bus = dbus.SystemBus()
        server = dbus.Interface(bus.get_object(avahi.DBUS_NAME, "/"), "org.freedesktop.Avahi.Server")
        sbrowser = dbus.Interface(bus.get_object(avahi.DBUS_NAME, server.ServiceBrowserNew(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, ZEROCONF_SERVICE_TYPE, 'local', dbus.UInt32(0))), avahi.DBUS_INTERFACE_SERVICE_BROWSER)
        dbus.set_default_main_loop(loop)
        sbrowser.connect_to_signal("ItemNew", serviceHandler)
        dbus.set_default_main_loop(loop)

        app = QtGui.QApplication(sys.argv)
        fluidNexus = FluidNexusDesktop(level = level)
        fluidNexus.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-v", "--verbose", dest = "verbosity", action = "count",  help = "How verbose to be.  Use up to 3 v's for full debug.")
    # TODO
    # Better short option...
    parser.add_option("-e", "--headless", dest = "headless", action = "store_true",  help = "Whether to run the network services without the GUI")
    (options, args) = parser.parse_args()
    start(verbosity = options.verbosity, headless = options.headless)
