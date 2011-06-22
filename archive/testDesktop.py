#!/usr/bin/env python

import sys
from PyQt4 import QtCore, QtGui
from FluidNexus.ui.FluidNexusDesktopUI import Ui_FluidNexus

class MessageTextBrowser(QtGui.QTextBrowser):
    mine_text = """
    <table width='100%'>
        <tr>
        <td width='40' rowspan='2'><img src=':/icons/icons/32x32/menu_enable_outgoing.png' width='32' height='32' /></td>
            <td><h3>%1</h3></td>
        </tr>
        <tr>
            <td>%2</td>
        </tr>
    </table>
    """

    other_text = """
    <table width='100%'>
        <tr>
        <td width='40' rowspan='2'><img src=':/icons/icons/32x32/menu_enable_outgoing.png' width='32' height='32' /></td>
            <td><h3>%1</h3></td>
        </tr>
        <tr>
            <td>%2</td>
        </tr>
    </table>
    """

    def __init__(self, parent = None, mine = False, message_title = "Testing title", message_content = "Testing content", message_type = 0):
        QtGui.QWidget.__init__(self, parent)
        if (mine):
            s = QtCore.QString(self.mine_text).arg(message_title, message_content)
        else:
            s = QtCore.QString(self.other_text).arg(message_title, message_content)
        self.setText(s)
        QtCore.QObject.connect(self, QtCore.SIGNAL("textChanged()"), self.setHeight)

    def setHeight(self):
        #print dir(self.document())
        #self.setTextWidth(self.width() - 2)
        print self.size()
        height = self.size().height() + 5
        print height
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

class ScrollArea(QtGui.QMainWindow):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        print dir(self)
        self.ui = Ui_FluidNexus()
        self.ui.setupUi(self)

        # TODO
        # * Subclass from QTextBrowser so that we can add instance variables to hold the hash, etc, for later deleting/updating
        # * Also figure out how to have the scrollarea, well, scroll
        # * add appropriate slots for clicking, changing of style on click, etc
        tb = MessageTextBrowser(parent = self, message_title = "foo", message_content = "bar")
        tb.messageHash = "asdfasfdasdf"
        self.ui.FluidNexusVBoxLayout.insertWidget(0, tb)

        tb = MessageTextBrowser(parent = self)
        tb.setText("<h1>Hello world!</h1>")
        tb.messageHash = "asdfasfdasdf"
        self.ui.FluidNexusVBoxLayout.insertWidget(0, tb)

        tb = MessageTextBrowser(parent = self)
        tb.setText("<h1>Hello world!</h1>")
        tb.messageHash = "asdfasfdasdf"
        self.ui.FluidNexusVBoxLayout.insertWidget(0, tb)

        tb = QtGui.QTextBrowser(parent = self)
        tb.setText("<h1>Hello world2!</h1>")
        self.ui.FluidNexusVBoxLayout.insertWidget(0, tb)

        tb = QtGui.QTextBrowser(parent = self)
        tb.setText("<h1>Hello world3!</h1>")
        self.ui.FluidNexusVBoxLayout.insertWidget(0, tb)

        tb = QtGui.QTextBrowser(parent = self)
        tb.setText("<h1>Hello world4!</h1>")
        self.ui.FluidNexusVBoxLayout.insertWidget(0, tb)

        tb = QtGui.QTextBrowser(parent = self)
        tb.setText("<h1>Hello world5!</h1>")
        self.ui.FluidNexusVBoxLayout.insertWidget(0, tb)

        tb = QtGui.QTextBrowser(parent = self)
        tb.setText("<h1>Hello world6!</h1>")
        self.ui.FluidNexusVBoxLayout.insertWidget(0, tb)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = ScrollArea()
    #print dir(myapp.ui)
    myapp.show()
    sys.exit(app.exec_())
