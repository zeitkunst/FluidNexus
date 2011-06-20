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
from ui.FluidNexusAboutUI import Ui_FluidNexusAbout
from Database import FluidNexusDatabase
from FluidNexusNetworking import FluidNexusClient, FluidNexusServer
import Log

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

class MessageTextBrowser(QtGui.QTextBrowser):
    """Wrapper around the text browser that adds some useful stuff for us."""

    mine_text = """
    <table width='100%'>
        <tr>
        <td width='40' rowspan='3'><img src=':/icons/icons/32x32/menu_enable_outgoing.png' width='32' height='32' /></td>
            <td><h3>%1</h3></td>
        </tr>
        <tr>
            <td>%2</td>
        </tr>
        <tr>
            <td align='right'>%3&nbsp;&nbsp;&nbsp;<img src=':/icons/icons/32x32/menu_delete.png' width='32' height='32'/></td>
        </tr>
    </table>
    """

    other_text = """
    <table width='100%'>
        <tr>
        <td width='40' rowspan='3'><img src=':/icons/icons/fluid_nexus_icon.png' width='32' height='32' /></td>
            <td><h3>%1</h3></td>
        </tr>
        <tr>
            <td>%2</td>
        </tr>
        <tr>
            <td align='right'>%3&nbsp;&nbsp;&nbsp;<img src=':/icons/icons/32x32/menu_delete.png' width='32' height='32'/></td>
        </tr>

    </table>
    """

    def __init__(self, parent = None, mine = False, message_title = "Testing title", message_content = "Testing content", message_type = 0, message_hash = None, message_timestamp = time.time(), logPath = "FluidNexus.log"):
        QtGui.QWidget.__init__(self, parent)
        QtCore.QObject.connect(self, QtCore.SIGNAL("textChanged()"), self.setHeight)
        self.logger = Log.getLogger(logPath = logPath)

        self.setMessageHash(message_hash)

        self.__setupUI()

        if (mine):
            s = QtCore.QString(self.mine_text).arg(message_title, message_content, message_timestamp)
        else:
            s = QtCore.QString(self.other_text).arg(message_title, message_content, message_timestamp)

        self.setHtml(s)

    def __setupUI(self):
        """Setup some UI parameters."""
        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)

    def setMessageHash(self, message_hash):
        self.message_hash = message_hash

    def getMessageHash(self):
        return self.message_hash

    def setHeight(self):
        #print dir(self.document())
        self.document().setTextWidth(self.width() - 2)
        height = self.document().size().toSize().height() + 5
        height = int(height * 0.2)
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

    def mousePressEvent(self, e):
        print self.getMessageHash()

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

class FluidNexusAboutDialog(QtGui.QDialog):
    def __init__(self, parent=None, title = None, message = None):
        QtGui.QDialog.__init__(self, parent)

        self.parent = parent

        self.ui = Ui_FluidNexusAbout()
        self.ui.setupUi(self)

    def closeDialog(self):
        self.close()



class FluidNexusDesktop(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_FluidNexus()
        self.ui.setupUi(self)

        self.statusBar().showMessage("Messages loaded.")
        
        self.settings = QtCore.QSettings("fluidnexus.net", "Fluid Nexus")
       
        # Setup location of the app-specific data
        self.__setupAppData()
        
        # Check to see if this is the first time we're being run
        firstRun = self.settings.value("app/firstRun", True).toBool()

        if firstRun:
            self.__setupDefaultSettings()
            firstRun = False
        else:
            self.__setupDatabaseConnection()

        # Setup logging
        self.logger = Log.getLogger(logPath = self.logPath)

        self.logger.debug("FluidNexus desktop version has started.")

        # This method of laying out things was cribbed from choqok
        # TODO
        # Still doesn't resize the textbrowsers properly though...
        verticalLayout_2 = QtGui.QVBoxLayout(self.ui.scrollAreaWidgetContents)
        verticalLayout_2.setMargin(1)

        self.ui.FluidNexusVBoxLayout = QtGui.QVBoxLayout()

        self.ui.FluidNexusVBoxLayout.setSpacing(5)
        self.ui.FluidNexusVBoxLayout.setMargin(1)
        verticalLayout_2.addLayout(self.ui.FluidNexusVBoxLayout)

        # Setup display
        self.setupDisplay()

        # Setup actions
        self.setupActions()

        self.setupSysTray()

    def __setupDefaultSettings(self):
        self.settings.clear()

        for section in DEFAULTS.keys():
            for key in DEFAULTS[section].keys():
                name = section + "/" + key
                self.settings.setValue(name, DEFAULTS[section][key])

        self.settings.setValue("app/dataDir", self.dataDir)
        self.logPath = os.path.join(self.dataDir, "FluidNexus.log")
        name = unicode(self.settings.value("database/name").toString())
        self.databaseDir = os.path.join(self.dataDir, name)
        self.databaseType = unicode(self.settings.value("database/type").toString())
        self.database = FluidNexusDatabase(databaseDir = self.dataDir, databaseType = "pysqlite2", logPath = self.logPath)
        self.database.setupDatabase()
        self.settings.setValue("app/firstRun", False)

    def __setupDatabaseConnection(self):
        """Setup our connection to the database."""
        self.logPath = os.path.join(self.dataDir, "FluidNexus.log")
        name = unicode(self.settings.value("database/name").toString())
        self.databaseDir = os.path.join(self.dataDir, name)
        self.databaseType = unicode(self.settings.value("database/type").toString())
        self.database = FluidNexusDatabase(databaseDir = self.dataDir, databaseType = "pysqlite2", logPath = self.logPath)



    def __setupAppData(self):
        """ Setup the application data directory in the home directory."""

        homeDir = os.path.expanduser('~')

        if sys.platform == "win32":
            self.dataDir = os.path.join(homeDir, "FluidNexusData")
        else:
            self.dataDir = os.path.join(homeDir, ".FluidNexus")
        
        if not os.path.isdir(self.dataDir):
            os.makedirs(self.dataDir)

        os.chmod(self.dataDir, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)

    def setupDisplay(self):
        """Setup our display with a bunch of text browsers."""

        self.database.all()
        for item in self.database:
            message_timestamp = item[2]
            message_hash = item[6]
            message_title = item[4]
            message_content = item[5]
            message_mine = item[8]

            tb = MessageTextBrowser(parent = self, mine = message_mine, message_title = message_title, message_content = message_content, message_hash = message_hash, message_timestamp = time.ctime(message_timestamp), logPath = self.logPath)
            self.ui.FluidNexusVBoxLayout.insertWidget(0, tb)

    def setupActions(self):
        """Setup the actions that we already know about."""
        self.connect(self.ui.actionAbout, QtCore.SIGNAL('triggered()'), self.displayAbout)
        self.connect(self.ui.actionQuit, QtCore.SIGNAL('triggered()'), self.handleQuit)
        self.connect(self.ui.actionNewMessage, QtCore.SIGNAL('triggered()'), self.handleNewMessage)

    def setupSysTray(self):
        """Setup the systray."""
        self.showing = True
        self.sysTray = QtGui.QSystemTrayIcon(self)
        self.sysTray.setIcon( QtGui.QIcon(':icons/icons/fluid_nexus_icon.png') )
        self.sysTray.setVisible(True)
        self.connect(self.sysTray, QtCore.SIGNAL("activated(QSystemTrayIcon::ActivationReason)"), self.onSysTrayActivated)

        self.sysTrayMenu = QtGui.QMenu(self)
        act = self.sysTrayMenu.addAction("FOO")

    def onSysTrayActivated(self, reason):
        """Handle systray actions."""

        self.logger.debug("Handing actions: " + str(reason))
        if ((reason == 3) and (self.showing)):
            self.hide()
            self.showing = False
        elif ((reason == 3) and (not (self.showing))):
            self.show()
            self.showing = True

    def handleNewMessage(self):
        print "new message"
        self.newMessageDialog = FluidNexusNewMessageDialog(parent = self)
        self.newMessageDialog.exec_()


    def handleQuit(self):
        self.logger.debug("Quiting...")
        self.sysTray.hide()
        self.database.close()
        self.close()

    def displayAbout(self):
        """Display our about box."""
        self.aboutDialog = FluidNexusAboutDialog(parent = self)
        self.aboutDialog.exec_()

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


class FluidNexusDesktopOld(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_FluidNexus()
        self.ui.setupUi(self)

        self.statusBar().showMessage("Messages loaded.")
        
        self.settings = QtCore.QSettings("fluidnexus.net", "Fluid Nexus")
       
        # Setup location of the app-specific data
        self.__setupAppData()
        
        # Check to see if this is the first time we're being run
        firstRun = self.settings.value("app/firstRun", True).toBool()

        if firstRun:
            self.__setupDefaultSettings()
            firstRun = False
        else:
            self.__setupDatabaseConnection()

        # Setup logging
        self.logger = Log.getLogger(logPath = self.logPath)

        # Setup a hash for enabled outgoing messages
        enabledHash = self.settings.value("outgoing/enabled", "none").toString() 

        if (enabledHash == "none"):
            self.enabledHash = {}
        else:
            self.enabledHash = pickle.loads(str(enabledHash))


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
        """
        self.clientThread = FluidNexusClientQt(parent = self, databaseDir = self.dataDir, databaseType = "pysqlite2")
        self.clientThread.start()

        self.serverThread = FluidNexusServerQt(parent = self, databaseDir = self.dataDir, databaseType = "pysqlite2")
        self.serverThread.start()
        """

        # Setup signals
        self.connect(self, QtCore.SIGNAL("incomingMessageDeleted"), self.incomingMessageDeleted)

        self.logger.debug("FluidNexus desktop version has started.")

    def __setupDefaultSettings(self):
        self.settings.clear()

        for section in DEFAULTS.keys():
            for key in DEFAULTS[section].keys():
                name = section + "/" + key
                self.settings.setValue(name, DEFAULTS[section][key])

        self.settings.setValue("app/dataDir", self.dataDir)
        self.logPath = os.path.join(self.dataDir, "FluidNexus.log")
        name = unicode(self.settings.value("database/name").toString())
        self.databaseDir = os.path.join(self.dataDir, name)
        self.databaseType = unicode(self.settings.value("database/type").toString())
        self.database = FluidNexusDatabase(databaseDir = self.dataDir, databaseType = "pysqlite2", logPath = self.logPath)
        self.database.setupDatabase()
        self.settings.setValue("app/firstRun", False)

    def __setupDatabaseConnection(self):
        """Setup our connection to the database."""
        self.logPath = os.path.join(self.dataDir, "FluidNexus.log")
        name = unicode(self.settings.value("database/name").toString())
        self.databaseDir = os.path.join(self.dataDir, name)
        self.databaseType = unicode(self.settings.value("database/type").toString())
        self.database = FluidNexusDatabase(databaseDir = self.dataDir, databaseType = "pysqlite2", logPath = self.logPath)



    def __setupAppData(self):
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
    print "here"
    fluidNexus.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    start()
