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
        self.parent = parent

        database = FluidNexusDatabase(databaseDir = self.databaseDir, databaseType = self.databaseType)
        self.server = FluidNexusServer(database = database, library="lightblue")
        self.server.initMessageAdvertisements()
        self.server.database.close()

        self.connect(self, QtCore.SIGNAL("incomingMessageAdded"), self.parent.incomingMessageAdded)


    def run(self):
        while True:
            self.server.database.openDB()
            newHash = self.server.run()
            self.emit(QtCore.SIGNAL("incomingMessageAdded"), newHash)


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

        # Setup models
        self.setupModels()

        # Save the currently edited hash
        self.currentEditingHash = None
        self.currentEditingRow = None

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

    def setupModels(self):
        # Incoming model
        self.incomingMessagesModel = QtGui.QStandardItemModel(parent = self)
        self.incomingMessagesModel.setHorizontalHeaderLabels(["Hash", "Title", "Message"])
        self.database.non_outgoing()
        for item in self.database:
            itemHash = QtGui.QStandardItem(item[6])
            itemTitle = QtGui.QStandardItem(item[4])
            itemMessageFragment = QtGui.QStandardItem(item[5][0:20])
            self.incomingMessagesModel.appendRow([itemHash, itemTitle, itemMessageFragment])

        self.ui.incomingMessagesList.setModel(self.incomingMessagesModel)
        self.ui.incomingMessagesList.hideColumn(0)

        # Outgoing model
        iconOutgoing = QtGui.QIcon()
        iconOutgoing.addPixmap(QtGui.QPixmap(":/icon32x32/icons/32x32/menu_enable_outgoing.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.outgoingMessagesModel = QtGui.QStandardItemModel(parent = self)
        self.outgoingMessagesModel.setHorizontalHeaderItem(0, QtGui.QStandardItem("Hash"))
        self.outgoingMessagesModel.setHorizontalHeaderItem(1, QtGui.QStandardItem(iconOutgoing, ""))
        self.outgoingMessagesModel.setHorizontalHeaderItem(2, QtGui.QStandardItem("Title"))
        self.outgoingMessagesModel.setHorizontalHeaderItem(3, QtGui.QStandardItem("Message"))

        self.database.outgoing()
        for item in self.database:
            itemHash = QtGui.QStandardItem(item[6])
            itemTitle = QtGui.QStandardItem(item[4])
            itemMessageFragment = QtGui.QStandardItem(item[5][0:20])

            if (self.enabledHash.has_key(item[6])):
                if (self.enabledHash[item[6]]):
                    enabledIcon = QtGui.QIcon()
                    enabledIcon.addPixmap(QtGui.QPixmap(":/icon32x32/icons/32x32/menu_enable_outgoing.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                else:
                    enabledIcon = QtGui.QIcon()
            else:
                enabledIcon = QtGui.QIcon()

            self.outgoingMessagesModel.appendRow([itemHash, QtGui.QStandardItem(enabledIcon, ""), itemTitle, itemMessageFragment])

        self.ui.outgoingMessagesList.setModel(self.outgoingMessagesModel)
        self.ui.outgoingMessagesList.hideColumn(0)

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
        print "Stopping client thread..."
        #self.clientThread.quit()
        #self.clientThread.wait()
        print "Stopping server thread..."
        #self.serverThread.quit()
        #self.serverThread.wait()

        #self.database.close()
        #self.close()

    def incomingMessageDeleted(self, messageHash):
        self.serverThread.server.stopAdvertise(str(messageHash))

    def incomingMessageAdded(self, newHash):
        """Slot for when an incoming message was added by the server thread."""
        item = self.database.returnItemBasedOnHash(newHash)

        itemHash = QtGui.QStandardItem(item[6])
        itemTitle = QtGui.QStandardItem(item[4])
        itemMessageFragment = QtGui.QStandardItem(item[5][0:20])
        self.incomingMessagesModel.insertRow(0, [itemHash, itemTitle, itemMessageFragment])

    def incomingMessageClicked(self, index):
        currentItem = self.incomingMessagesModel.itemFromIndex(index)
        row = currentItem.row()
        messageHash = str(self.incomingMessagesModel.item(row, column = 0).text())
        item = self.database.returnItemBasedOnHash(messageHash)
        te = self.ui.incomingMessageText
        te.clear()
        te.setPlainText(item[5])

    def editOutgoingMessage(self):
        indices = self.ui.outgoingMessagesList.selectedIndexes()
        currentItem = self.outgoingMessagesModel.itemFromIndex(indices[0])
        row = currentItem.row()
        messageHash = str(self.outgoingMessagesModel.item(row, column = 0).text())
        item = self.database.returnItemBasedOnHash(messageHash)
        messageTitle = str(self.outgoingMessagesModel.item(row, column = 2).text())

        self.currentEditingHash = messageHash
        self.currentEditingRow = row

        self.newMessageDialog = FluidNexusNewMessageDialog(parent = self, title = messageTitle, message = item[5])
        self.newMessageDialog.exec_()

    def outgoingMessageClicked(self, index):
        if (not self.ui.deleteOutgoingButton.isEnabled()):
            self.ui.deleteOutgoingButton.setEnabled(True)

        if (not self.ui.toggleOutgoingButton.isEnabled()):
            self.ui.toggleOutgoingButton.setEnabled(True)

        if (not self.ui.editMessageButton.isEnabled()):
            self.ui.editMessageButton.setEnabled(True)


        currentItem = self.outgoingMessagesModel.itemFromIndex(index)
        row = currentItem.row()
        messageHash = str(self.outgoingMessagesModel.item(row, column = 0).text())
        item = self.database.returnItemBasedOnHash(messageHash)
        te = self.ui.outgoingMessageText
        te.clear()
        te.setPlainText(item[5])

    def outgoingMessageDoubleClicked(self, index):
        print "double clicked"
        currentItem = self.outgoingMessagesModel.itemFromIndex(index)
        row = currentItem.row()
        messageHash = str(self.outgoingMessagesModel.item(row, column = 0).text())
        item = self.database.returnItemBasedOnHash(messageHash)
        
        self.currentEditingHash = messageHash
        self.newMessageDialog = FluidNexusNewMessageDialog(parent = self, title = item[4], message = item[5])
        self.newMessageDialog.exec_()

    def outgoingMessageItemActivated(self, index):
        print "here"
        if (not self.ui.deleteOutgoingButton.isEnabled()):
            self.ui.deleteOutgoingButton.setEnabled(True)

        if (not self.ui.toggleOutgoingButton.isEnabled()):
            self.ui.toggleOutgoingButton.setEnabled(True)

    def toggleOutgoingMessage(self):
        indices = self.ui.outgoingMessagesList.selectedIndexes()
        currentItem = self.outgoingMessagesModel.itemFromIndex(indices[0])
        row = currentItem.row()
        messageHash = str(self.outgoingMessagesModel.item(row, column = 0).text())
        currentItemIcon = self.outgoingMessagesModel.item(row, column = 1).icon()

        if (currentItemIcon.isNull()):
            enabledIcon = QtGui.QIcon()
            enabledIcon.addPixmap(QtGui.QPixmap(":/icon32x32/icons/32x32/menu_enable_outgoing.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.outgoingMessagesModel.setItem(row, 1, QtGui.QStandardItem(enabledIcon, ""))
            self.enabledHash[messageHash] = True
        else:
            enabledIcon = QtGui.QIcon()
            self.outgoingMessagesModel.setItem(row, 1, QtGui.QStandardItem(enabledIcon, ""))
            self.enabledHash[messageHash] = False

        self.settings.setValue("outgoing/enabled", pickle.dumps(self.enabledHash))
        self.settings.sync()

    def deleteOutgoingMessage(self):
        # TODO
        # Disable the delete button if nothing else is selected
        indices = self.ui.outgoingMessagesList.selectedIndexes()
        currentItem = self.outgoingMessagesModel.itemFromIndex(indices[0])
        row = currentItem.row()
        messageHash = str(self.outgoingMessagesModel.item(row, column = 0).text())
        title = str(self.outgoingMessagesModel.item(row, column = 1).text())
        self.outgoingMessagesModel.removeRow(row)

        self.database.remove_by_hash(messageHash)

        # Clear message text area
        te = self.ui.outgoingMessageText
        te.clear()

        # Update status bar
        self.statusBar().showMessage("'%s' deleted." % title)

        # Remove from hash and sync
        # TODO
        # Make this into a method, or raise a signal, or something of the sort
        try:
            del self.enabledHash[unicode(messageHash)]
        except KeyError:
            # not sure why I get a key error here...
            pass
        self.settings.setValue("outgoing/enabled", pickle.dumps(self.enabledHash))
        self.settings.sync()

    def deleteIncomingMessage(self):
        # TODO
        # Disable the delete button if nothing else is selected

        # Get current item, delete from database
        indices = self.ui.incomingMessagesList.selectedIndexes()
        currentItem = self.incomingMessagesModel.itemFromIndex(indices[0])
        row = currentItem.row()
        hash = str(self.incomingMessagesModel.item(row, column = 0).text())
        title = str(self.incomingMessagesModel.item(row, column = 1).text())
        self.incomingMessagesModel.removeRow(row)

        self.database.remove_by_hash(hash)

        # Clear message text area
        te = self.ui.incomingMessageText
        te.clear()

        # Update status bar
        self.statusBar().showMessage("'%s' deleted." % title)

        # Emit signal to deadvertise hash
        self.emit(QtCore.SIGNAL("incomingMessageDeleted"), hash)


    def showNewMessageWindow(self):
        self.newMessageDialog = FluidNexusNewMessageDialog(parent = self)
        self.newMessageDialog.exec_()

    def newMessageSaveButtonClicked(self, title, body):
        messageHash = unicode(md5.md5(unicode(title) + unicode(body)).hexdigest())

        if (self.currentEditingHash is not None):
            self.database.remove_by_hash(self.currentEditingHash)

            # Find the right item to update
            self.database.add_new(u"00:00", 0, unicode(title), unicode(body), messageHash, u"00:00")
            self.outgoingMessagesModel.setItem(self.currentEditingRow, 0, QtGui.QStandardItem(messageHash))
            self.outgoingMessagesModel.setItem(self.currentEditingRow, 2, QtGui.QStandardItem(title))
            self.outgoingMessagesModel.setItem(self.currentEditingRow, 3, QtGui.QStandardItem(body[0:20] + " ..."))

            try:
                del self.enabledHash[self.currentEditingHash]
            except KeyError:
                # If we haven't toggled anything yet, the item won't be there yet
                pass
            self.currentEditingHash = None
            self.currentEditingRow = None
        else:
            self.database.add_new(u"00:00", 0, unicode(title), unicode(body), messageHash, u"00:00")

            itemHash = QtGui.QStandardItem(messageHash)
            itemTitle = QtGui.QStandardItem(title)
            itemMessageFragment = QtGui.QStandardItem(body[0:20] + " ...")
            enabledIcon = QtGui.QIcon()
            enabledIcon.addPixmap(QtGui.QPixmap(":/icon32x32/icons/32x32/menu_enable_outgoing.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.outgoingMessagesModel.insertRow(0, [itemHash, QtGui.QStandardItem(enabledIcon, ""), itemTitle, itemMessageFragment])

def start():
    app = QtGui.QApplication(sys.argv)
    fluidNexus = FluidNexusDesktop()
    fluidNexus.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    start()
