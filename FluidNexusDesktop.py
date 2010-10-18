#!/usr/bin/env python

# Standard library imports
import md5
import os
import pickle
import stat
import sys
import time

# External library imports
from PyQt4 import QtCore, QtGui

# My library imports
from ui.FluidNexusDesktopUI import Ui_FluidNexus
from ui.FluidNexusNewMessageUI import Ui_FluidNexusNewMessage
from database import FluidNexusDatabase
from FluidNexusNetworking import FluidNexusClient, FluidNexusServer

# TODO
# -- need to check if database already exists in home directory; if not, populate it with basic info
# -- need to modularize present code

DEFAULTS = {
    "database": {
        "type": "pysqlite2",
        "name": "FluidNexus.db"
    }
}

# Strangely, the QTreeWidgetItemIterator doesn't provide a python iterable
# So we have to create our own...or base our code on:
# http://www.mail-archive.com/pyqt@riverbankcomputing.com/msg11348.html
class TreeIter(QtGui.QTreeWidgetItemIterator):
    def __init__(self, *args):
        QtGui.QTreeWidgetItemIterator.__init__(self, *args)

    def __iter__(self):
        return self

    def next(self):
        value = self.value()
        if value:
            self.__iadd__(1)
            return value
        else:
            raise StopIteration

# We need to create a separate class to allow threading for the client and the server
class FluidNexusClientQt(QtCore.QThread):
    def __init__(self, databaseDir = None, databaseType = None, parent = None):
        QtCore.QThread.__init__(self, parent)

        self.databaseDir = databaseDir
        self.databaseType = databaseType


    def run(self):
        while True:
            # TODO
            # HACK
            # This works, but it's probably horribly, horribly inefficient.  The problem is is that each time the run method is called it comes from another thread, meaning that we can't reuse the connection anymore.  So we have to use this hack.
            database = FluidNexusDatabase(databaseDir = self.databaseDir, databaseType = self.databaseType)
            self.client = FluidNexusClient(database = database)
            self.client.runLightblue()
            time.sleep(30)

class FluidNexusServerQt(QtCore.QThread):
    def __init__(self, databaseDir = None, databaseType = None, parent = None):
        QtCore.QThread.__init__(self, parent)

        self.databaseDir = databaseDir
        self.databaseType = databaseType

        database = FluidNexusDatabase(databaseDir = self.databaseDir, databaseType = self.databaseType)
        self.server = FluidNexusServer(database = database, library="lightblue")
        self.server.initMessageAdvertisements()
        self.server.database.close()


    def run(self):
        while True:
            self.server.database.openDB()
            self.server.run()


class FluidNexusNewMessageDialog(QtGui.QDialog):
    def __init__(self, parent=None, title = None, message = None):
        QtGui.QDialog.__init__(self, parent)

        self.parent = parent

        self.ui = Ui_FluidNexusNewMessage()
        self.ui.setupUi(self)

        if (title is not None):
            self.ui.newMessageTitle.setText(title)

        if (message is not None):
            self.ui.newMessageBody.setPlainText(message)

        self.connect(self.ui.cancelButton, QtCore.SIGNAL("clicked()"), self.closeDialog)
        self.connect(self, QtCore.SIGNAL("saveButtonClicked"), self.parent.newMessageSaveButtonClicked)

    def closeDialog(self):
        self.close()

    def saveButtonClicked(self):
        print "save button clicked"
        self.emit(QtCore.SIGNAL("saveButtonClicked"), self.ui.newMessageTitle.text(), self.ui.newMessageBody.document().toPlainText())
        self.close()




class FluidNexusDesktop(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_FluidNexus()
        self.ui.setupUi(self)

        self.statusBar().showMessage("Messages loaded.")
        
        self.settings = QtCore.QSettings("zeitkunst", "Fluid Nexus")
       
        # Setup the defaults
        #self._setupDefaultSettings()

        # Setup location of the app-specific data
        self._setupAppData()

        # Setup a hash for enabled outgoing messages
        enabledHash = self.settings.value("outgoing/enabled", "none").toString() 

        if (enabledHash == "none"):
            self.enabledHash = {}
        else:
            self.enabledHash = pickle.loads(str(enabledHash))

        # Setup the database and the views
        self.database = FluidNexusDatabase(databaseDir = self.dataDir, databaseType = "pysqlite2")
        #self.database.setupDatabase()
        self.setupTreeViews()

        # Save the currently edited hash
        self.currentEditingHash = None

        # Ensure files are readable only by user
        # @HACK@
        # Need to make this less brittle
        os.chmod(os.path.join(self.dataDir, "FluidNexus.db"), stat.S_IREAD | stat.S_IWRITE)
        try:
            os.chmod(os.path.join(self.dataDir, "FluidNexus.log"), stat.S_IREAD | stat.S_IWRITE)
        except OSError:
            pass

        # Setup clients and servers
        self.clientThread = FluidNexusClientQt(parent = self, databaseDir = self.dataDir, databaseType = "pysqlite2")
        self.clientThread.start()

        self.serverThread = FluidNexusServerQt(parent = self, databaseDir = self.dataDir, databaseType = "pysqlite2")
        self.serverThread.start()

        # Setup signals
        self.connect(self, QtCore.SIGNAL("incomingMessageDeleted"), self.incomingMessageDeleted)

    def _setupDefaultSettings(self):
        self.settings.clear()

        for section in DEFAULTS.keys():
            for key in DEFAULTS[section].keys():
                name = section + "/" + key
                self.settings.setValue(name, DEFAULTS[section][key])

    def _setupAppData(self):
        """ Setup the application data directory in the home directory."""

        homeDir = os.path.expanduser('~')

        if sys.platform == "win32":
            self.dataDir = os.path.join(homeDir, "FluidNexusData")
        else:
            self.dataDir = os.path.join(homeDir, ".FluidNexus")
        
        if not os.path.isdir(self.dataDir):
            os.makedirs(self.dataDir)

        os.chmod(self.dataDir, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)

    def setupTreeViews(self):
        # Setup incoming
        self.database.non_outgoing()
        for item in self.database:
            a = QtGui.QTreeWidgetItem(self.ui.incomingMessagesList)
            # Hash
            a.setText(0, item[6])
            # Title
            a.setText(1, item[4])
            # Data
            a.setText(2, item[5][0:20] + "...")

        self.ui.incomingMessagesList.hideColumn(0)

        # Setup outgoing
        self.database.outgoing()
        for item in self.database:
            a = QtGui.QTreeWidgetItem(self.ui.outgoingMessagesList)

            hash = item[6]

            if (self.enabledHash.has_key(hash)):
                if (self.enabledHash[hash]):
                    enabledIcon = QtGui.QIcon()
                    enabledIcon.addPixmap(QtGui.QPixmap(":/icon32x32/icons/32x32/menu_enable_outgoing.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    a.setIcon(1, enabledIcon)
                else:
                    enabledIcon = QtGui.QIcon()
                    a.setIcon(1, enabledIcon)
            else:
                enabledIcon = QtGui.QIcon()
                a.setIcon(1, enabledIcon)

            # Hash
            a.setText(0, item[6])
            # Title
            a.setText(2, item[4])
            # Data
            a.setText(3, item[5][0:20] + "...")
            # TODO
            # Not working for some reason
            a.font(2).setWeight(75)
            a.font(3).setWeight(75)

        self.ui.outgoingMessagesList.hideColumn(0)
        self.ui.outgoingMessagesList.resizeColumnToContents(1)

    def mainWindowDestroyed(self):
        #self.settings.setValue(name, DEFAULTS[section][key])
        items = TreeIter(self.ui.outgoingMessagesList)
        for item in items:
            currentItemIcon = item.icon(1)
            hash
            if (currentItemIcon.isNull()):
                self.enabledHash[str(item.data(0, 0).toString())] = False
            else:
                self.enabledHash[str(item.data(0, 0).toString())] = True

        self.settings.setValue("outgoing/enabled", pickle.dumps(self.enabledHash))
        self.settings.sync()

        print "Stopping client thread..."
        self.clientThread.exit()
        self.serverThread.exit()

        self.database.close()
        self.close()

    def incomingMessageDeleted(self, messageHash):
        self.serverThread.server.stopAdvertise(str(messageHash))

    def incomingMessageClicked(self):
        currentItem = self.ui.incomingMessagesList.currentItem()
        item = self.database.returnItemBasedOnHash(currentItem.data(0, 0).toString())
        te = self.ui.incomingMessageText
        te.clear()
        te.setPlainText(item[5])

    def outgoingMessageClicked(self):
        currentItem = self.ui.outgoingMessagesList.currentItem()
        currentItemIcon = currentItem.icon(1)
        if (currentItemIcon.isNull()):
            pass

        item = self.database.returnItemBasedOnHash(unicode(currentItem.data(0, 0).toString()))
        te = self.ui.outgoingMessageText
        te.clear()
        te.setPlainText(item[5])

    def outgoingMessageDoubleClicked(self):
        currentItem = self.ui.outgoingMessagesList.currentItem()

        item = self.database.returnItemBasedOnHash(currentItem.data(0, 0).toString())

        self.currentEditingHash = str(currentItem.data(0, 0).toString())

        self.newMessageDialog = FluidNexusNewMessageDialog(parent = self, title = str(currentItem.data(2, 0).toString()), message = item[5])
        self.newMessageDialog.exec_()

    def outgoingMessageItemActivated(self):
        if (not self.ui.deleteOutgoingButton.isEnabled()):
            self.ui.deleteOutgoingButton.setEnabled(True)

        if (not self.ui.toggleOutgoingButton.isEnabled()):
            self.ui.toggleOutgoingButton.setEnabled(True)

    def toggleOutgoingMessage(self):
        currentItem = self.ui.outgoingMessagesList.currentItem()
        currentItemIcon = currentItem.icon(1)

        if (currentItemIcon.isNull()):
            enabledIcon = QtGui.QIcon()
            enabledIcon.addPixmap(QtGui.QPixmap(":/icon32x32/icons/32x32/menu_enable_outgoing.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            currentItem.setIcon(1, enabledIcon)
            self.enabledHash[str(currentItem.data(0, 0).toString())] = True
        else:
            enabledIcon = QtGui.QIcon()
            currentItem.setIcon(1, enabledIcon)
            self.enabledHash[str(currentItem.data(0, 0).toString())] = False

        self.settings.setValue("outgoing/enabled", pickle.dumps(self.enabledHash))
        self.settings.sync()

    def deleteOutgoingMessage(self):
        # TODO
        # Disable the delete button if nothing else is selected

        # Get current item, delete from database
        currentItem = self.ui.outgoingMessagesList.currentItem()
        self.database.remove_by_hash(currentItem.data(0, 0).toString())

        # Remove the selected items from the list
        for twi in self.ui.outgoingMessagesList.selectedItems():
            self.ui.outgoingMessagesList.removeItemWidget(twi, 0)
        del twi # remove last reference

        # Clear message text area
        te = self.ui.outgoingMessageText
        te.clear()

        # Remove from hash and sync
        # TODO
        # Make this into a method, or raise a signal, or something of the sort
        try:
            del self.enabledHash[unicode(currentItem.data(0, 0).toString())]
        except KeyError:
            # not sure why I get a key error here...
            pass
        self.settings.setValue("outgoing/enabled", pickle.dumps(self.enabledHash))
        self.settings.sync()

        # Update status bar
        self.statusBar().showMessage("'%s' deleted." % currentItem.data(2, 0).toString())

    def deleteIncomingMessage(self):
        # TODO
        # Remove the advertised hash once we've deleted it
        # Disable the delete button if nothing else is selected

        # Get current item, delete from database
        currentItem = self.ui.incomingMessagesList.currentItem()
        self.database.remove_by_hash(currentItem.data(0, 0).toString())

        # Remove the selected items from the list
        for twi in self.ui.incomingMessagesList.selectedItems():
            self.ui.incomingMessagesList.removeItemWidget(twi, 0)
        del twi # remove last reference

        # Clear message text area
        te = self.ui.incomingMessageText
        te.clear()

        # Update status bar
        self.statusBar().showMessage("'%s' deleted." % currentItem.data(1, 0).toString())

        self.emit(QtCore.SIGNAL("incomingMessageDeleted"), currentItem.data(0, 0).toString())


    def showNewMessageWindow(self):
        self.newMessageDialog = FluidNexusNewMessageDialog(parent = self)
        self.newMessageDialog.exec_()

    def newMessageSaveButtonClicked(self, title, body):
        hash = unicode(md5.md5(unicode(title) + unicode(body)).hexdigest())

        if (self.currentEditingHash is not None):
            self.database.remove_by_hash(self.currentEditingHash)

            # Find the right item to update
            treeItems = TreeIter(self.ui.outgoingMessagesList)
            for treeItem in treeItems:
                currentItemHash = unicode(treeItem.data(0, 0).toString())
                if (currentItemHash == unicode(self.currentEditingHash)):
                    treeItem.setText(0, unicode(md5.md5(unicode(title) + unicode(body)).hexdigest()))
                    treeItem.setText(2, title)
                    treeItem.setText(3, body[0:20] + "...")
            self.database.add_new(u"00:00", 0, unicode(title), unicode(body), hash, u"00:00")

            try:
                del self.enabledHash[self.currentEditingHash]
            except KeyError:
                # If we haven't toggled anything yet, the item won't be there yet
                pass
            self.currentEditingHash = None
        else:
            self.database.add_new(u"00:00", 0, unicode(title), unicode(body), hash, u"00:00")
            outgoing = QtGui.QTreeWidgetItem(self.ui.outgoingMessagesList)
            outgoing.setText(0, hash)
            outgoing.setText(2, title)
            outgoing.setText(3, body[0:20] + "...")
            outgoing.font(2).setBold(True)
            outgoing.font(3).setBold(True)
            enabledIcon = QtGui.QIcon()
            enabledIcon.addPixmap(QtGui.QPixmap(":/icon32x32/icons/32x32/menu_enable_outgoing.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            outgoing.setIcon(1, enabledIcon)


if __name__ == "__main__":
    print "here"
    app = QtGui.QApplication(sys.argv)
    fluidNexus = FluidNexusDesktop()
    fluidNexus.show()
    sys.exit(app.exec_())

