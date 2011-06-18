#!/usr/bin/env python

import sys

from PyQt4 import QtGui

from FluidNexus.GUI import FluidNexusDesktop

def start():
    app = QtGui.QApplication(sys.argv)
    fluidNexus = FluidNexusDesktop()
    print "here"
    fluidNexus.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    start()
