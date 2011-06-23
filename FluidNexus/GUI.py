#!/usr/bin/env python

# Standard library imports
import hashlib
import logging
import os
import pickle
import re
import stat
import sys
import time

# External library imports
from PyQt4 import QtCore, QtGui
import textile

# My library imports
from ui.FluidNexusDesktopUI import Ui_FluidNexus
from ui.FluidNexusNewMessageUI import Ui_FluidNexusNewMessage
from ui.FluidNexusAboutUI import Ui_FluidNexusAbout
from ui.FluidNexusPreferencesUI import Ui_FluidNexusPreferences
from Database import FluidNexusDatabase
from Networking import BluetoothServerVer3, BluetoothClientVer3
import Log

# TODO
# * Interface is not automatically updated in insert of new TextBrowser in gnome on Lucid...why is that?
# * Also, on Lucid gnome get a "QThread: Destoryed while thread is still running" error when doing File...Quit
# * Deal with sqlite thread stuff...why can't I call a thread's method to close the database connection opened in that thread?  And do I even need to close the connection on thread quit?
# * Decide whether or not textile is the best way to format our info in these TextBrowsers
# 
DEFAULTS = {
    "database": {
        "type": "pysqlite2",
        "name": "FluidNexus.db"
    },
    
    "network": {
        "bluetoothEnabled": 2
    },

    "bluetooth": {
        "scanFrequency": 300
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

class FluidNexusServerQt(QtCore.QThread):
    def __init__(self, dataDir = None, databaseType = None, attachmentsPath = None, logPath = "FluidNexus.log", parent = None, level = logging.WARN):
        QtCore.QThread.__init__(self, parent)

        self.databaseDir = dataDir
        self.databaseType = databaseType
        self.attachmentsPath = attachmentsPath
        self.parent = parent
        self.logger = Log.getLogger(logPath = logPath, level = level)


        self.btServer = BluetoothServerVer3(databaseDir = dataDir, databaseType = databaseType, attachmentsPath = attachmentsPath, logPath = logPath)

        self.connect(self, QtCore.SIGNAL("newMessages"), self.parent.newMessages)
        self.connect(self, QtCore.SIGNAL("started()"), self.handleStarted)
        self.connect(self, QtCore.SIGNAL("finished()"), self.handleFinished)
        self.connect(self, QtCore.SIGNAL("terminated()"), self.handleTerminated)

    def handleStarted(self):
        self.logger.debug("BluetoothServerThread started")

    def handleFinished(self):
        self.logger.debug("BluetoothServerThread finished")
        self.start()

    def handleTerminated(self):
        self.logger.debug("BluetoothServerThread terminated")

    def cleanup(self):
        """Cleanup after ourselves."""
        self.btServer.cleanup()

    def addHash(self, message_hash):
        self.btServer.addHash(message_hash)

    def removeHash(self, hashToRemove):
        self.btServer.removeHash(hashToRemove)

    def replaceHash(self, hashToReplace, newHash):
        self.btServer.replaceHash(hashToReplace, newHash)


    def run(self):
        newMessages = self.btServer.run()

        if (newMessages != []):
            self.emit(QtCore.SIGNAL("newMessages"), newMessages)


class FluidNexusClientQt(QtCore.QThread):
    def __init__(self, dataDir = None, databaseType = None, attachmentsPath = None, logPath = "FluidNexus.log", parent = None, level = logging.WARN, scanFrequency = 300):
        QtCore.QThread.__init__(self, parent)

        self.databaseDir = dataDir
        self.databaseType = databaseType
        self.attachmentsPath = attachmentsPath
        self.parent = parent
        self.logger = Log.getLogger(logPath = logPath, level = level)

        self.scanFrequency = scanFrequency

        self.btClient = BluetoothClientVer3(databaseDir = dataDir, databaseType = databaseType, attachmentsPath = attachmentsPath, logPath = logPath)

        self.connect(self, QtCore.SIGNAL("newMessages"), self.parent.newMessages)
        self.connect(self, QtCore.SIGNAL("started()"), self.handleStarted)
        self.connect(self, QtCore.SIGNAL("finished()"), self.handleFinished)
        self.connect(self, QtCore.SIGNAL("terminated()"), self.handleTerminated)
        self.connect(self.parent, QtCore.SIGNAL("bluetoothScanFrequencyChanged(QVariant)"), self.handleBluetoothScanFrequencyChanged)

    def handleStarted(self):
        self.logger.debug("BluetoothClientThread started")

    def handleFinished(self):
        self.logger.debug("BluetoothClientThread finished")
        self.start()

    def handleTerminated(self):
        self.logger.debug("BluetoothClientThread terminated")

    def handleBluetoothScanFrequencyChanged(self, value):
        self.scanFrequency = value.toInt()[0]

    def cleanup(self):
        """Cleanup after ourselves."""
        self.btClient.cleanup()

    def addHash(self, message_hash):
        self.btClient.addHash(message_hash)

    def removeHash(self, hashToRemove):
        self.btClient.removeHash(hashToRemove)

    def replaceHash(self, hashToReplace, newHash):
        self.btClient.replaceHash(hashToReplace, newHash)

    def run(self):
        newMessages = self.btClient.run()

        if (newMessages != []):
            self.emit(QtCore.SIGNAL("newMessages"), newMessages)

        self.logger.debug("Sleeping for %d seconds" % self.scanFrequency)
        self.sleep(self.scanFrequency)

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
            <td align='right'>%3&nbsp;&nbsp;&nbsp;<a href="fluidnexus://editmessage">Edit</a>&nbsp;&nbsp;&nbsp;<a href="fluidnexus://deletemessage"><img src=':/icons/icons/32x32/menu_delete.png' width='32' height='32'/></a></td>
        </tr>
    </table>
    """

    mine_text_attachment = """
    <table width='100%'>
        <tr>
        <td width='40' rowspan='3'><img src=':/icons/icons/32x32/menu_enable_outgoing.png' width='32' height='32' /></td>
        <td><h3>%1</h3></td>
        </tr>
        <tr>
            <td>%2</td>
        </tr>
        <tr>
            <td align='right'>%4&nbsp;&nbsp;&nbsp;%3&nbsp;&nbsp;&nbsp;<a href="fluidnexus://editmessage">Edit</a>&nbsp;&nbsp;&nbsp;<a href="fluidnexus://deletemessage"><img src=':/icons/icons/32x32/menu_delete.png' width='32' height='32'/></a></td>
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
            <td align='right'>%3&nbsp;&nbsp;&nbsp;<a href="fluidnexus://deletemessage"><img src=':/icons/icons/32x32/menu_delete.png' width='32' height='32'/></a></td>
        </tr>

    </table>
    """

    other_text_attachment = """
    <table width='100%'>
        <tr>
        <td width='40' rowspan='3'><img src=':/icons/icons/fluid_nexus_icon.png' width='32' height='32' /></td>
            <td><h3>%1</h3></td>
        </tr>
        <tr>
            <td>%2</td>
        </tr>
        <tr>
            <td align='right'>%4&nbsp;&nbsp;&nbsp;%3&nbsp;&nbsp;&nbsp;<a href="fluidnexus://deletemessage"><img src=':/icons/icons/32x32/menu_delete.png' width='32' height='32'/></a></td>
        </tr>

    </table>
    """


    def __init__(self, parent = None, mine = False, message_title = "Testing title", message_content = "Testing content", message_type = 0, message_hash = None, message_timestamp = time.time(), attachment_path = None, attachment_original_filename = None, logPath = "FluidNexus.log", level = logging.WARN):
        QtGui.QWidget.__init__(self, parent)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.parent = parent

        QtCore.QObject.connect(self, QtCore.SIGNAL("anchorClicked(QUrl)"), self.checkAnchor)
        self.logger = Log.getLogger(logPath = logPath, level = level)

        self.mine = mine
        self.setMessageHash(message_hash)
        self.setMessageTitle(message_title)
        self.setMessageContent(message_content)
        self.setMessageTimestamp(message_timestamp)
        self.setMessageAttachmentPath(attachment_path)
        self.setMessageAttachmentOriginalFilename(attachment_original_filename)

        self.connect(self, QtCore.SIGNAL("textChanged()"), self.setHeight)
        self.setTextBrowserHTML()
        self.adjustSize()        
        self.setHeight()

        #self.connect(self, QtCore.SIGNAL("resizeEvent(QResizeEvent)"), self.resizeEvent)


    def setTextBrowserHTML(self):
        """Set our HTML content with the instance values."""

        if (self.getMessageAttachmentPath() is None):
            if (self.mine):
                s = QtCore.QString(self.mine_text).arg(self.getMessageTitle(), self.getMessageContent(), time.ctime(self.getMessageTimestamp()))
            else:
                s = QtCore.QString(self.other_text).arg(self.getMessageTitle(), self.getMessageContent(), time.ctime(self.getMessageTimestamp()))
        else:
            if (self.mine):
                s = QtCore.QString(self.mine_text_attachment).arg(self.getMessageTitle(), self.getMessageContent(), time.ctime(self.getMessageTimestamp()), self.getMessageAttachmentOriginalFilename())
            else:
                s = QtCore.QString(self.other_text_attachment).arg(self.getMessageTitle(), self.getMessageContent(), time.ctime(self.getMessageTimestamp()), self.getMessageAttachmentOriginalFilename())

        self.setHtml(s)
        # Whether to open links automatically
        self.setOpenLinks(False)

    def setMessageHash(self, message_hash):
        self.message_hash = message_hash

    def setMessageTitle(self, message_title):
        self.message_title = message_title

    def setMessageContent(self, message_content):
        self.message_content = message_content

    def setMessageTimestamp(self, message_timestamp):
        self.message_timestamp = message_timestamp

    def setMessageAttachmentPath(self, attachment_path):
        self.attachment_path = attachment_path

    def setMessageAttachmentOriginalFilename(self, attachment_original_filename):
        self.attachment_original_filename = attachment_original_filename

    def getMessageHash(self):
        return self.message_hash

    def getMessageTitle(self):
        return self.message_title

    def getMessageContent(self):
        return self.message_content

    def getMessageTimestamp(self):
        return self.message_timestamp

    def getMessageAttachmentPath(self):
        return self.attachment_path

    def getMessageAttachmentOriginalFilename(self):
        return self.attachment_original_filename

    def setHeight(self):
        margins = self.contentsMargins()

        width = self.size().width() - margins.left() - margins.right() - self.document().documentMargin() * 2
        #self.document().setPageSize(QtCore.QSizeF(width, -1))
        #self.document().setTextWidth(self.width() - 2)
        self.document().setTextWidth(width)

        height = self.document().size().height() + margins.top() + margins.bottom()
        #height = self.document().size().height() + 2
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

    def mousePressEvent(self, e):
        pass

    def checkAnchor(self, anchor):
        """Handle anchor links here."""

        if (anchor.scheme() == "fluidnexus"):
            if (anchor.host() == "deletemessage"):
                self.parent.deleteMessage(self.getMessageHash())
            elif (anchor.host() == "editmessage"):
                # TODO
                # There ought to be a better way of doing this...
                stripped_content = re.sub('<[^<]+?>', '', self.getMessageContent())
                lines = stripped_content.split('\n')
                stripped_content = '\n'.join([line.strip() for line in lines])
                self.newMessageDialog = FluidNexusNewMessageDialog(parent = self, title = self.getMessageTitle(), content = stripped_content, attachment_original_path = os.path.realpath(self.getMessageAttachmentPath()))
                self.newMessageDialog.exec_()
    
    def newMessageSaveButtonClicked(self, message_title, message_content, message_filename):
        """Respond to the new (edit) message save button."""
        new_message_hash = unicode(hashlib.sha256(unicode(message_title) + unicode(message_content)).hexdigest())
        message_title = unicode(message_title)
        message_content = unicode(message_content)
        if (new_message_hash != self.getMessageHash()):
            if (message_filename is None):
                message_timestamp = time.time()
                self.parent.database.updateByMessageHash(message_hash = self.getMessageHash(), new_message_hash = new_message_hash, new_content = message_content, new_title = message_title, new_timestamp = message_timestamp)
                self.parent.replaceHash(self.getMessageHash(), new_message_hash)
    
                self.setMessageTitle(message_title)
                self.setMessageContent(textile.textile(message_content))
                self.setMessageHash(new_message_hash)
                self.setMessageTimestamp(message_timestamp)
                self.setTextBrowserHTML()
            else:
                # Get relevant infos about the file
                message_filename = unicode(message_filename)
                fullPath, extension = os.path.splitext(message_filename)
                attachment_original_filename = os.path.basename(message_filename)
                attachment_path = os.path.join(self.parent.attachmentsPath, new_message_hash) + extension

                os.unlink(os.path.join(self.parent.attachmentsPath, self.getMessageHash()))

                # TODO
                # This will break on windows and needs to be fixed
                os.symlink(message_filename, attachment_path)

                message_timestamp = time.time()
                self.parent.database.updateByMessageHash(message_hash = self.getMessageHash(), new_message_hash = new_message_hash, new_content = message_content, new_title = message_title, new_timestamp = message_timestamp, new_attachment_path = attachment_path, new_attachment_original_filename = attachment_original_filename)
                self.parent.replaceHash(self.getMessageHash(), new_message_hash)

                self.setMessageTitle(message_title)
                self.setMessageContent(textile.textile(message_content))
                self.setMessageHash(new_message_hash)
                self.setMessageTimestamp(message_timestamp)
                self.setMessageAttachmentPath(attachment_path)
                self.setMessageAttachmentOriginalFilename(attachment_original_filename)
                self.setTextBrowserHTML()

    # TODO
    # This does make things the proper size, but then we get recursion errors...and I don't know how to stop the recursion.
    #def resizeEvent(self, event):
    #    self.setHeight()

class FluidNexusNewMessageDialog(QtGui.QDialog):
    def __init__(self, parent=None, title = None, content = None, attachment_original_path = None):
        QtGui.QDialog.__init__(self, parent)

        self.parent = parent

        self.ui = Ui_FluidNexusNewMessage()
        self.ui.setupUi(self)

        if (title is not None):
            self.ui.newMessageTitle.setText(title)

        if (content is not None):
            self.ui.newMessageBody.setPlainText(content)

        self.connect(self.ui.cancelButton, QtCore.SIGNAL("clicked()"), self.closeDialog)
        self.connect(self, QtCore.SIGNAL("saveButtonClicked"), self.parent.newMessageSaveButtonClicked)
        self.connect(self.ui.fileSelectionButton, QtCore.SIGNAL("clicked()"), self.selectFile)
        self.connect(self.ui.fileRemoveButton, QtCore.SIGNAL("clicked()"), self.removeFile)

        if (attachment_original_path is not None):
            self.filename = attachment_original_path
            self.ui.fileSelectedLabel.setText(QtCore.QString(self.filename))
            self.ui.fileRemoveButton.show()
        else:
            self.filename = None
            self.ui.fileRemoveButton.hide()

    def closeDialog(self):
        # TODO
        # Ask for confirmation if the data has changed
        self.close()

    def selectFile(self):
        """Choose a file to include as an attachment."""
        filename = QtGui.QFileDialog.getOpenFileName(self, self.trUtf8("Choose file for attachment"), os.getcwd());
        if (filename is not None):
            self.ui.fileSelectedLabel.setText(filename)
            self.filename = filename
            self.ui.fileRemoveButton.show()

    def removeFile(self):
        """Remove a file from consideration."""
        # TODO
        # Add dialog for confirmation
        self.filename = None
        self.ui.fileSelectedLabel.setText("")
        self.ui.fileRemoveButton.hide()

    def saveButtonClicked(self):
        self.emit(QtCore.SIGNAL("saveButtonClicked"), self.ui.newMessageTitle.text(), self.ui.newMessageBody.document().toPlainText(), self.filename)
        self.close()

class FluidNexusPreferencesDialog(QtGui.QDialog):
    bluetoothScanFrequencies = [5, 10, 30, 60, 120, 300, 600, 1200, 1800, 3600]
    
    GENERAL_TAB = 0
    NETWORK_TAB = 1
    BLUETOOTH_TAB = 2
    ZEROCONF_TAB = 3
    ADHOC_TAB = 4

    def __init__(self, parent=None, logPath = "FluidNexus.log", level = logging.ERROR, settings = None):
        QtGui.QDialog.__init__(self, parent)
        
        self.logPath = logPath
        self.logLevel = level
        self.logger = Log.getLogger(logPath = self.logPath, level = self.logLevel)
        self.parent = parent
        self.settings = settings
        self.ui = Ui_FluidNexusPreferences()
        self.ui.setupUi(self)

        self.preferencesToChange = {}
        self.__updatePreferencesDialog()


    def __networkPreferencesUpdate(self):
        bluetooth = self.settings.value("network/bluetooth", 2).toInt()[0]

        if (bluetooth == 2):
            self.ui.bluetoothEnabled.setCheckState(QtCore.Qt.Checked)
        else:
            self.ui.bluetoothEnabled.setCheckState(QtCore.Qt.Unchecked)

    def __bluetoothPreferencesUpdate(self):
        bluetoothScanFrequency = self.settings.value("bluetooth/scanFrequency", 300).toInt()[0]
        index = self.bluetoothScanFrequencies.index(bluetoothScanFrequency)
        self.ui.bluetoothScanFrequency.setCurrentIndex(index)

    def __updatePreferencesDialog(self):
        """Update the preferences dialog based on our settings."""
        
        self.ui.FluidNexusPreferencesTabWidget.setTabEnabled(self.ZEROCONF_TAB, False)
        self.ui.FluidNexusPreferencesTabWidget.setTabEnabled(self.ADHOC_TAB, False)
        self.__networkPreferencesUpdate()
        self.__bluetoothPreferencesUpdate()
        self.preferencesToChange = {}

    def reject(self):
        self.logger.debug("Rejecting")
        QtGui.QDialog.reject(self)

    def accept(self):
        self.logger.debug("Accepting")

        for key in self.preferencesToChange.keys():
            self.settings.setValue(key, self.preferencesToChange[key])
        QtGui.QDialog.accept(self)

    def bluetoothChanged(self, value):
        self.preferencesToChange["network/bluetooth"] = value
        if (value == 2):
            self.ui.FluidNexusPreferencesTabWidget.setTabEnabled(self.BLUETOOTH_TAB, True)
        else:
            self.ui.FluidNexusPreferencesTabWidget.setTabEnabled(self.BLUETOOTH_TAB, False)

    def bluetoothScanFrequencyChanged(self, index):
        # TODO
        # It would be nice to get the disambiguation paramter, but that's not likely...
        # Remember that if we change the number of options in the UI, we have to change the number of options here as well
        self.preferencesToChange["bluetooth/scanFrequency"] = self.bluetoothScanFrequencies[index]
        self.parent.emit(QtCore.SIGNAL("bluetoothScanFrequencyChanged(QVariant)"), self.bluetoothScanFrequencies[index])


    def closeDialog(self):
        # TODO
        # Ask for confirmation if the data has changed
        self.close()


class FluidNexusAboutDialog(QtGui.QDialog):

    aboutText = """Copyright 2008-2011 Nicholas A. Knouf
    
Fluid Nexus is an application for mobile   phones that is primarily designed to enable activists or relief workers to send messages and data amongst themselves independent of a centralized cellular      network.  The idea is to provide a means of communication between people when   the centralized network has been shut down, either by the government during a   time of unrest, or by nature due to a massive disaster.  During such times the  use of the centralized network for voice or SMS is not possible.  Yet, if we    can use the fact that people still must move about the world, then we can use   ideas from sneaker-nets to turn people into carriers of data.  Given enough     people, we can create fluid, temporary, ad-hoc networks that pass messages one  person at a time, spreading out as a contagion and eventually reaching members  of the group.  This enables surreptitious communication via daily activity and  relies on a fluid view of reality.  Additionally, Fluid Nexus can be used as a  hyperlocal message board, loosely attached to physical locations.  
    
Fluid Nexus is not designed as a general-purpose piece of software; rather, it is developed with specific types of users in mind.  Thus, while the ideas here could be very useful for social-networking or productivity applications, this is not what I am most interested in.  However, I definitely welcome the extension of these ideas into these other domains.  Indeed, Fluid Nexus is related to work in the following projects: mesh networking in the OLPC ( http://wiki.laptop.org/go/Mesh_Network_Details ), the Haggle project ( http://www.haggleproject.org/ ), and Comm.unity ( http://community.mit.edu/ ), among many  others."""

    creditsText = """Some credits text to go here.  Bruno, Luis, Maria, Claudia, Niranjan, etc."""

    def __init__(self, parent=None, title = None, message = None):
        QtGui.QDialog.__init__(self, parent)

        self.parent = parent

        self.ui = Ui_FluidNexusAbout()
        self.ui.setupUi(self)
        self.ui.AboutDialogAboutText.setText(self.aboutText)

    def closeDialog(self):
        self.close()



class FluidNexusDesktop(QtGui.QMainWindow):
    def __init__(self, parent=None, level = logging.WARN):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_FluidNexus()
        self.ui.setupUi(self)

        self.ourHashes = []

        self.statusBar().showMessage(self.trUtf8("Messages loaded."))
        
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
        self.logger = Log.getLogger(logPath = self.logPath, level = level)
        self.logLevel = level

        self.logger.debug("FluidNexus desktop version has started.")

        # This method of laying out things was cribbed from choqok
        # TODO
        # Still doesn't resize the textbrowsers properly though...
        self.ui.FluidNexusScrollArea.setWidgetResizable(True);
        verticalLayout_2 = QtGui.QVBoxLayout(self.ui.scrollAreaWidgetContents)
        verticalLayout_2.setMargin(1)

        self.ui.FluidNexusVBoxLayout = QtGui.QVBoxLayout()

        self.ui.FluidNexusScrollArea.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        self.ui.FluidNexusVBoxLayout.setSpacing(5)
        self.ui.FluidNexusVBoxLayout.setMargin(1)
        verticalLayout_2.addLayout(self.ui.FluidNexusVBoxLayout)

        # Setup display
        self.setupDisplay()

        # Setup actions
        self.setupActions()

        # Setup signals
        self.__setupSignals()

        self.setupSysTray()

        # Set our enabled/disabled network modalities; we'll refer to these values throughout the course of the program
        bluetooth = self.settings.value("network/bluetooth", 2).toInt()[0]
        if (bluetooth == 2): 
            self.bluetoothEnabled = True
        else:
            self.bluetoothEnabled = False

        # Start the network threads
        self.__startNetworkThreads()


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
        self.database.addDummyData()
        self.settings.setValue("app/firstRun", False)

    def __setupDatabaseConnection(self):
        """Setup our connection to the database."""
        self.logPath = os.path.join(self.dataDir, "FluidNexus.log")
        name = unicode(self.settings.value("database/name").toString())
        self.databaseDir = os.path.join(self.dataDir, name)
        self.databaseType = unicode(self.settings.value("database/type").toString())
        self.database = FluidNexusDatabase(databaseDir = self.dataDir, databaseType = "pysqlite2", logPath = self.logPath)

    def __setupSignals(self):
        """Setup the signals we listen to."""

    def resizeEvent(self, event):
        if (event.oldSize() != self.ui.centralwidget.size()):
            self.ui.FluidNexusScrollArea.resize(self.ui.centralwidget.size())


    def __setupAppData(self):
        """ Setup the application data directory in the home directory."""

        homeDir = os.path.expanduser('~')

        if sys.platform == "win32":
            self.dataDir = os.path.join(homeDir, "FluidNexusData")
        else:
            self.dataDir = os.path.join(homeDir, ".FluidNexus")

        self.attachmentsPath  = os.path.join(self.dataDir, "attachments")
        
        if not os.path.isdir(self.dataDir):
            os.makedirs(self.dataDir)

        if not os.path.isdir(self.attachmentsPath):
            os.makedirs(self.attachmentsPath)

        os.chmod(self.dataDir, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)

    def __startNetworkThreads(self):

        if (self.bluetoothEnabled):
            self.bluetoothServerThread = FluidNexusServerQt(parent = self, dataDir = self.dataDir, databaseType = "pysqlite2", attachmentsPath = self.attachmentsPath, logPath = self.logPath, level = self.logLevel)
            self.bluetoothServerThread.start()
            
            scanFrequency = self.settings.value("bluetooth/scanFrequency", 300).toInt()[0]
            self.bluetoothClientThread = FluidNexusClientQt(parent = self, dataDir = self.dataDir, databaseType = "pysqlite2", attachmentsPath = self.attachmentsPath, logPath = self.logPath, level = self.logLevel, scanFrequency = scanFrequency)
            self.bluetoothClientThread.start()


    def __stopNetworkThreads(self):
        if (self.bluetoothEnabled):
            self.bluetoothServerThread.quit()
            self.bluetoothClientThread.quit()

    def setupDisplay(self):
        """Setup our display with a bunch of text browsers."""

        # TODO
        # Not ideal or quick...probably need to refactor
        items = self.database.all()
        items.reverse()

        for item in items:
            message_timestamp = item['time']
            message_hash = item['message_hash']
            message_title = item['title']
            message_content = item['content']
            message_mine = item['mine']
            attachment_path = item['attachment_path']
            attachment_original_filename = item['attachment_original_filename']

            if (attachment_path == ""):
                tb = MessageTextBrowser(parent = self, mine = message_mine, message_title = message_title, message_content = textile.textile(message_content), message_hash = message_hash, message_timestamp = message_timestamp, logPath = self.logPath)
            else:
                tb = MessageTextBrowser(parent = self, mine = message_mine, message_title = message_title, message_content = textile.textile(message_content), message_hash = message_hash, message_timestamp = message_timestamp, attachment_path = attachment_path, attachment_original_filename = attachment_original_filename, logPath = self.logPath)
            tb.setFocusProxy(self)
            self.ui.FluidNexusVBoxLayout.insertWidget(0, tb)

    def setupActions(self):
        """Setup the actions that we already know about."""
        self.connect(self.ui.actionAbout, QtCore.SIGNAL('triggered()'), self.displayAbout)
        self.connect(self.ui.actionQuit, QtCore.SIGNAL('triggered()'), self.handleQuit)
        self.connect(self.ui.actionNewMessage, QtCore.SIGNAL('triggered()'), self.handleNewMessage)
        self.connect(self.ui.actionPreferences, QtCore.SIGNAL('triggered()'), self.handlePreferences)

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
        self.newMessageDialog = FluidNexusNewMessageDialog(parent = self)
        self.newMessageDialog.exec_()

    def handlePreferences(self):
        self.preferencesDialog = FluidNexusPreferencesDialog(parent = self, logPath = self.logPath, level = self.logLevel,  settings = self.settings)
        self.preferencesDialog.exec_()


    def handleQuit(self):
        self.logger.debug("Quiting...")
        self.emit(QtCore.SIGNAL("handleQuit"))
        self.__stopNetworkThreads()
        self.sysTray.hide()
        self.database.close()
        self.close()

    def displayAbout(self):
        """Display our about box."""
        self.aboutDialog = FluidNexusAboutDialog(parent = self)
        self.aboutDialog.exec_()

    def newMessages(self, newMessages):
        """Slot for when an incoming message was added by the server thread."""
        self.logger.debug("New messages received: " + str(newMessages))
        for message in newMessages:
            tb = MessageTextBrowser(parent = self, mine = 0, message_title = message["message_title"], message_content = textile.textile(message["message_content"]), message_hash = message["message_hash"], message_timestamp = message["message_timestamp"], logPath = self.logPath)
            self.ourHashes.append(message["message_hash"])
            tb.setFocusProxy(self)
            self.ui.FluidNexusVBoxLayout.insertWidget(0, tb)

        self.statusBar().showMessage(self.trUtf8("New messages received."))

    def replaceHash(self, hashToReplace, newHash):
        """Replace a hash in our threads."""

        if (self.bluetoothEnabled):
            self.bluetoothServerThread.replaceHash(hashToReplace, newHash)
            self.bluetoothClientThread.replaceHash(hashToReplace, newHash)
    
    def removeHash(self, hashToRemove):
        """Remove a hash from our threads."""

        if (self.bluetoothEnabled):
            self.bluetoothServerThread.removeHash(hashToRemove)
            self.bluetoothClientThread.removeHash(hashToRemove)

    def deleteMessage(self, hashToDelete):
        """Delete the selected hash and remove from display."""

        numItems = self.ui.FluidNexusVBoxLayout.count()
        
        #Find a particular widget with the given hash.  This is a pain to do, and the searching algorithm can probably better, but here it goes.
        for index in xrange(0, numItems):
            currentWidget = self.ui.FluidNexusVBoxLayout.itemAt(index).widget()
            if (currentWidget.getMessageHash() == hashToDelete):
                self.logger.debug("Got message to delete hash: " + hashToDelete)
                response = self.confirmDialogDelete()
                if (response == self.YES):
                    self.ui.FluidNexusVBoxLayout.removeWidget(currentWidget)
                    if (currentWidget.getMessageAttachmentPath() is not None):
                        os.unlink(currentWidget.getMessageAttachmentPath())
                    currentWidget.close()
                    self.database.removeByMessageHash(hashToDelete)
                break

    def confirmDialogDelete(self):
        """Create a delete confirmation dialog."""
        self.YES = "Yes"
        self.NO = "No"
        message = QtGui.QMessageBox(self)
        message.setText(self.trUtf8("Do you really want to delete this message?"))
        message.setWindowTitle('FluidNexus')
        message.setIcon(QtGui.QMessageBox.Question)
        message.addButton(self.YES, QtGui.QMessageBox.AcceptRole)
        message.addButton(self.NO, QtGui.QMessageBox.RejectRole)
        message.exec_()
        response = message.clickedButton().text()
        return response

    def newMessageSaveButtonClicked(self, message_title, message_content, message_filename):
        message_hash = unicode(hashlib.sha256(unicode(message_title) + unicode(message_content)).hexdigest())

        if (message_filename is None):
            self.database.addMine(title = unicode(message_title), content = unicode(message_content))
            self.addHash(message_hash)
            
            message_content = unicode(message_content)
            tb = MessageTextBrowser(parent = self, mine = 1, message_title = message_title, message_content = textile.textile(message_content), message_hash = message_hash, message_timestamp = time.time(), logPath = self.logPath)
            tb.setFocusProxy(self)

            self.ui.FluidNexusVBoxLayout.insertWidget(0, tb)
        else:
            # Get relevant infos about the file
            message_filename = unicode(message_filename)
            fullPath, extension = os.path.splitext(message_filename)
            attachment_original_filename = os.path.basename(message_filename)
            attachment_path = os.path.join(self.attachmentsPath, message_hash) + extension
            # TODO
            # This will break on windows and needs to be fixed
            os.symlink(message_filename, attachment_path)

            # Add the hash
            self.addHash(message_hash)

            # Convert QString to unicode
            message_content = unicode(message_content)

            # Add to database
            self.database.addMine(title = unicode(message_title), content = unicode(message_content), attachment_path = attachment_path, attachment_original_filename = attachment_original_filename + extension)

            # Update display
            tb = MessageTextBrowser(parent = self, mine = 1, message_title = message_title, message_content = textile.textile(message_content), message_hash = message_hash, message_timestamp = time.time(), attachment_path = attachment_path, attachment_original_filename = attachment_original_filename + extension, logPath = self.logPath)
            tb.setFocusProxy(self)

            self.ui.FluidNexusVBoxLayout.insertWidget(0, tb)

    def addHash(self, message_hash):
        """Add a hash to our threads."""

        if (self.bluetoothEnabled):
            self.bluetoothServerThread.addHash(message_hash)
            self.bluetoothClientThread.addHash(message_hash)

def start():
    app = QtGui.QApplication(sys.argv)
    fluidNexus = FluidNexusDesktop()
    fluidNexus.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    start()
