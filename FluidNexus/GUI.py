#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

# Standard library imports
import hashlib
import logging
import mimetypes
import os
import pickle
import re
import stat
import sys
import time
import urllib2

# External library imports
from PyQt4 import QtCore, QtGui
import simplejson
import oauth2
import textile

# My library imports
from ui.FluidNexusDesktopUI import Ui_FluidNexus
from ui.FluidNexusNewMessageUI import Ui_FluidNexusNewMessage
from ui.FluidNexusAboutUI import Ui_FluidNexusAbout
from ui.FluidNexusPreferencesUI import Ui_FluidNexusPreferences
from Database import FluidNexusDatabase
from Networking import BluetoothServerVer3, BluetoothClientVer3, ZeroconfClient, ZeroconfServer, NexusNetworking
import Log

# TODO
# * Also, on Lucid gnome get a "QThread: Destoryed while thread is still running" error when doing File...Quit
# * Decide whether or not textile is the best way to format our info in these TextBrowsers
# 
DEFAULTS = {
    "database": {
        "type": "pysqlite2",
        "name": "FluidNexus.db"
    },

    "nexus": {
        "ttl": 30,
    },

    "network": {
        "bluetooth": 2,
        "zeroconf": 2,
        "nexus": 2,
    },

    "bluetooth": {
        "scanFrequency": 300
    },

    "zeroconf": {
        "scanFrequency": 300
    }


}

# build our oauth request token request
URL_BASE = "http://localhost:6543/api/01/"
OAUTH_CALLBACK_URL = URL_BASE + "access_token"
REQUEST_TOKEN_URL = URL_BASE + "request_token/desktop"

def build_request_token_request(url, key, secret, method='POST'):
    params = {                                            
        'oauth_version': "1.0",
        'oauth_nonce': oauth2.generate_nonce(),
        'oauth_timestamp': int(time.time()),
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_callback': OAUTH_CALLBACK_URL,
    }
    consumer = oauth2.Consumer(key=key, secret=secret)
    params['oauth_consumer_key'] = consumer.key
    req = oauth2.Request(method=method, url=url, parameters=params)
    signature_method = oauth2.SignatureMethod_HMAC_SHA1()
    req.sign_request(signature_method, consumer, None)
    return req

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

class ServiceThread(QtCore.QThread):
    def __init__(self, databaseDir = None, databaseType = None, attachmentsDir = None, logPath = "FluidNexus.log", parent = None, level = logging.WARN, scanFrequency = 300, threadName = "ServiceThread"):
        QtCore.QThread.__init__(self, parent)

        self.databaseDir = databaseDir
        self.databaseType = databaseType
        self.attachmentsDir = attachmentsDir
        self.parent = parent
        self.threadName = threadName
        self.logPath = logPath
        self.level = level
        self.logger = Log.getLogger(logPath = logPath, level = level)

        self.scanFrequency = scanFrequency

        self.setupService()

        self.connect(self, QtCore.SIGNAL("newMessages"), self.parent.newMessages)
        self.connect(self, QtCore.SIGNAL("started()"), self.handleStarted)
        self.connect(self, QtCore.SIGNAL("finished()"), self.handleFinished)
        self.connect(self, QtCore.SIGNAL("terminated()"), self.handleTerminated)

    def setupService(self):
        """Override in child classes to do the setup for the service as necessary."""

        raise NotImplementedError

    def handleStarted(self):
        self.logger.debug(self.threadName + " started")

    def handleFinished(self):
        self.logger.debug(self.threadName + " finished")
        self.start()

    def handleTerminated(self):
        self.logger.debug(self.threadName + " terminated")

    def handleBluetoothScanFrequencyChanged(self, value):
        self.scanFrequency = value.toInt()[0]

    def cleanup(self):
        """Cleanup after ourselves."""
        self.service.cleanup()

    def addHash(self, message_hash):
        self.service.addHash(message_hash)

    def removeHash(self, hashToRemove):
        self.service.removeHash(hashToRemove)

    def replaceHash(self, hashToReplace, newHash):
        self.service.replaceHash(hashToReplace, newHash)

    def run(self):
        """Override in client classes."""

        raise NotImplementedError

class NexusNetworkingQt(ServiceThread):

    def __init__(self, databaseDir = ".", databaseType = "pysqlite2", attachmentsDir = ".", logPath = "FluidNexus.log", level = logging.WARN, scanFrequency = 300, parent = None, threadName = "NexusNetworkingThread", key = "", secret = "", token = "", token_secret = ""):
        self.key = unicode(key)
        self.secret = unicode(secret)
        self.token = unicode(token)
        self.token_secret = unicode(token_secret)

        super(NexusNetworkingQt, self).__init__(databaseDir = databaseDir, databaseType = databaseType, attachmentsDir = attachmentsDir, logPath = logPath, level = level, parent = parent, scanFrequency = scanFrequency, threadName = threadName)

    def testZeroconf(self):
        enabled = self.service.testZeroconf()

        if (not enabled):
            self.parent.disableZeroconf()
        
        return enabled

    def setupService(self):
        """Setup our nexus service."""

        self.service = NexusNetworking(databaseDir = self.databaseDir, databaseType = self.databaseType, attachmentsDir = self.attachmentsDir, logPath = self.logPath, key = self.key, secret = self.secret, token = self.token, token_secret = self.token_secret)

    def run(self):
        self.service.run()

        # TODO
        # Make this frequency configurable
        self.logger.debug("NexusNetworkingThread sleeping for %d seconds" % self.scanFrequency)
        self.sleep(self.scanFrequency)


class ZeroconfClientQt(ServiceThread):

    def __init__(self, databaseDir = ".", databaseType = "pysqlite2", attachmentsDir = ".", logPath = "FluidNexus.log", level = logging.WARN, scanFrequency = 300, parent = None, threadName = "ZeroconfClientThread", loopType = "qt"):
        self.loopType = loopType
        super(ZeroconfClientQt, self).__init__(databaseDir = databaseDir, databaseType = databaseType, attachmentsDir = attachmentsDir, logPath = logPath, level = level, parent = parent, scanFrequency = scanFrequency, threadName = threadName)

    def setupService(self):
        """Setup our zeroconf service."""

        self.service = ZeroconfClient(databaseDir = self.databaseDir, databaseType = self.databaseType, attachmentsDir = self.attachmentsDir, logPath = self.logPath, loopType = self.loopType)

        self.connect(self.parent, QtCore.SIGNAL("zeroconfScanFrequencyChanged(QVariant)"), self.handleZeroconfScanFrequencyChanged)

    def testZeroconf(self):
        enabled = self.service.testZeroconf()

        if (not enabled):
            self.parent.disableZeroconf()
        
        return enabled

    def handleZeroconfScanFrequencyChanged(self, value):
        self.scanFrequency = value.toInt()[0]

    def run(self):
        newMessages = self.service.run()

        if (newMessages != []):
            self.emit(QtCore.SIGNAL("newMessages"), newMessages)

        self.logger.debug("Sleeping for %d seconds" % self.scanFrequency)
        self.sleep(self.scanFrequency)

class ZeroconfServerQt(ServiceThread):

    def __init__(self, databaseDir = ".", databaseType = "pysqlite2", attachmentsDir = ".", logPath = "FluidNexus.log", level = logging.WARN, parent = None, threadName = "ZeroconfServerThread"):
        super(ZeroconfServerQt, self).__init__(databaseDir = databaseDir, databaseType = databaseType, attachmentsDir = attachmentsDir, logPath = logPath, level = level, parent = parent, threadName = threadName)

    def setupService(self):
        """Setup our zeroconf service."""

        self.service = ZeroconfServer(databaseDir = self.databaseDir, databaseType = self.databaseType, attachmentsDir = self.attachmentsDir, logPath = self.logPath)

    def run(self):
        newMessages = self.service.run()

        if (newMessages != []):
            self.emit(QtCore.SIGNAL("newMessages"), newMessages)


class FluidNexusServerQt(QtCore.QThread):
    def __init__(self, dataDir = None, databaseType = None, attachmentsDir = None, logPath = "FluidNexus.log", parent = None, level = logging.WARN):
        QtCore.QThread.__init__(self, parent)

        self.databaseDir = dataDir
        self.databaseType = databaseType
        self.attachmentsDir = attachmentsDir
        self.parent = parent
        self.logger = Log.getLogger(logPath = logPath, level = level)


        self.btServer = BluetoothServerVer3(databaseDir = dataDir, databaseType = databaseType, attachmentsDir = attachmentsDir, logPath = logPath)

        self.connect(self, QtCore.SIGNAL("newMessages"), self.parent.newMessages)
        self.connect(self, QtCore.SIGNAL("started()"), self.handleStarted)
        self.connect(self, QtCore.SIGNAL("finished()"), self.handleFinished)
        self.connect(self, QtCore.SIGNAL("terminated()"), self.handleTerminated)

    def testBluetooth(self):
        enabled = self.btServer.testBluetooth()

        if (not enabled):
            self.parent.disableBluetooth()
        
        return enabled

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
    def __init__(self, dataDir = None, databaseType = None, attachmentsDir = None, logPath = "FluidNexus.log", parent = None, level = logging.WARN, scanFrequency = 300):
        QtCore.QThread.__init__(self, parent)

        self.databaseDir = dataDir
        self.databaseType = databaseType
        self.attachmentsDir = attachmentsDir
        self.parent = parent
        self.logger = Log.getLogger(logPath = logPath, level = level)

        self.scanFrequency = scanFrequency

        self.btClient = BluetoothClientVer3(databaseDir = dataDir, databaseType = databaseType, attachmentsDir = attachmentsDir, logPath = logPath)


        self.connect(self, QtCore.SIGNAL("newMessages"), self.parent.newMessages)
        self.connect(self, QtCore.SIGNAL("started()"), self.handleStarted)
        self.connect(self, QtCore.SIGNAL("finished()"), self.handleFinished)
        self.connect(self, QtCore.SIGNAL("terminated()"), self.handleTerminated)
        self.connect(self.parent, QtCore.SIGNAL("bluetoothScanFrequencyChanged(QVariant)"), self.handleBluetoothScanFrequencyChanged)

    def testBluetooth(self):
        enabled = self.btClient.testBluetooth()

        if (not enabled):
            self.parent.disableBluetooth()

        return enabled

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

    # TODO
    # Need to figure out a way to streamline this...
    mine_text = """
    <table width='100%'>
        <tr>
        <td width='40' rowspan='3'><img src=':/icons/icons/32x32/menu_outgoing.png' width='32'/></td>
        <td><h3>%1</h3></td>
        </tr>
        <tr>
            <td>%2</td>
        </tr>
        <tr>
        <td align='right'>%3&nbsp;&nbsp;&nbsp;<a href='fluidnexus://editmessage' title='Edit Message'><img src=':/icons/icons/32x32/menu_edit.png' width='32'/></a>&nbsp;&nbsp;&nbsp;<a href='fluidnexus://deletemessage' title='Delete Message'><img src=':/icons/icons/32x32/menu_delete.png' width='32' /></a></td>
        </tr>
    </table>
    """

    mine_text_public = """
    <table width='100%'>
        <tr>
        <td width='40' rowspan='3'><img src=':/icons/icons/32x32/menu_public.png' width='32'/></td>
        <td><h3>%1</h3></td>
        </tr>
        <tr>
            <td>%2</td>
        </tr>
        <tr>
        <td align='right'>%3&nbsp;&nbsp;&nbsp;<a href='fluidnexus://editmessage' title='Edit Message'><img src=':/icons/icons/32x32/menu_edit.png' width='32'/></a>&nbsp;&nbsp;&nbsp;<a href='fluidnexus://deletemessage' title='Delete Message'><img src=':/icons/icons/32x32/menu_delete.png' width='32' /></a></td>
        </tr>
    </table>
    """


    mine_text_attachment = """
    <table width='100%'>
        <tr>
        <td width='40' rowspan='4'><img src=':/icons/icons/32x32/menu_outgoing.png' width='32' /></td>
        <td><h3>%1</h3></td>
        </tr>
        <tr>
            <td>%2</td>
        </tr>
        <tr>
            <td align='right'><img src=':/icons/icons/32x32/attachment_icon.png'/>&nbsp;&nbsp;<a href='%5'>%4</a></td>
        </tr>
        <tr>
            <td align='right'>%3&nbsp;&nbsp;&nbsp;<a href="fluidnexus://editmessage" title='Edit Message'><img src=':/icons/icons/32x32/menu_edit.png' width='32'/></a>&nbsp;&nbsp;&nbsp;<a href="fluidnexus://deletemessage" title='Delete Message'><img src=':/icons/icons/32x32/menu_delete.png' width='32' /></a></td>
        </tr>
    </table>
    """

    mine_text_attachment_public = """
    <table width='100%'>
        <tr>
        <td width='40' rowspan='4'><img src=':/icons/icons/32x32/menu_public.png' width='32' /></td>
        <td><h3>%1</h3></td>
        </tr>
        <tr>
            <td>%2</td>
        </tr>
        <tr>
            <td align='right'><img src=':/icons/icons/32x32/attachment_icon.png'/>&nbsp;&nbsp;<a href='%5'>%4</a></td>
        </tr>
        <tr>
            <td align='right'>%3&nbsp;&nbsp;&nbsp;<a href="fluidnexus://editmessage" title='Edit Message'><img src=':/icons/icons/32x32/menu_edit.png' width='32'/></a>&nbsp;&nbsp;&nbsp;<a href="fluidnexus://deletemessage" title='Delete Message'><img src=':/icons/icons/32x32/menu_delete.png' width='32' /></a></td>
        </tr>
    </table>
    """


    other_text = """
    <table width='100%'>
        <tr>
        <td width='40' rowspan='3'><img src=':/icons/icons/32x32/menu_all.png' width='32'  /></td>
            <td><h3>%1</h3></td>
        </tr>
        <tr>
            <td>%2</td>
        </tr>
        <tr>
            <td align='right'>%3&nbsp;&nbsp;&nbsp;<a href="fluidnexus://blacklistmessage" title="Blacklist Message"><img src=":/icons/icons/32x32/menu_blacklist.png" width="32"/></a>&nbsp;&nbsp;&nbsp;<a href="fluidnexus://deletemessage" title='Delete Message'><img src=':/icons/icons/32x32/menu_delete.png' width='32' /></a></td>
        </tr>

    </table>
    """

    other_text_public = """
    <table width='100%'>
        <tr>
        <td width='40' rowspan='3'><img src=':/icons/icons/32x32/menu_public_other.png' width='32'  /></td>
            <td><h3>%1</h3></td>
        </tr>
        <tr>
            <td>%2</td>
        </tr>
        <tr>
            <td align='right'>%3&nbsp;&nbsp;&nbsp;<a href="fluidnexus://blacklistmessage" title="Blacklist Message"><img src=":/icons/icons/32x32/menu_blacklist.png" width="32"/></a>&nbsp;&nbsp;&nbsp;<a href="fluidnexus://deletemessage" title='Delete Message'><img src=':/icons/icons/32x32/menu_delete.png' width='32' /></a></td>
        </tr>

    </table>
    """


    other_text_blacklist = """
    <table width='100%'>
        <tr>
        <td width='40' rowspan='3'><img src=':/icons/icons/32x32/menu_all.png' width='32'  /></td>
            <td><h3>%1</h3></td>
        </tr>
        <tr>
            <td>%2</td>
        </tr>
        <tr>
            <td align='right'>%3&nbsp;&nbsp;&nbsp;<a href="fluidnexus://unblacklistmessage" title="Unblacklist Message"><img src=":/icons/icons/32x32/menu_all.png" width="32"/></a>&nbsp;&nbsp;&nbsp;<a href="fluidnexus://deletemessage" title='Delete Message'><img src=':/icons/icons/32x32/menu_delete.png' width='32' /></a></td>
        </tr>

    </table>
    """

    other_text_blacklist_public = """
    <table width='100%'>
        <tr>
        <td width='40' rowspan='3'><img src=':/icons/icons/32x32/menu_public_other.png' width='32'  /></td>
            <td><h3>%1</h3></td>
        </tr>
        <tr>
            <td>%2</td>
        </tr>
        <tr>
            <td align='right'>%3&nbsp;&nbsp;&nbsp;<a href="fluidnexus://unblacklistmessage" title="Unblacklist Message"><img src=":/icons/icons/32x32/menu_all.png" width="32"/></a>&nbsp;&nbsp;&nbsp;<a href="fluidnexus://deletemessage" title='Delete Message'><img src=':/icons/icons/32x32/menu_delete.png' width='32' /></a></td>
        </tr>

    </table>
    """



    other_text_attachment = """
    <table width='100%'>
        <tr>
        <td width='40' rowspan='4'><img src=':/icons/icons/32x32/menu_all.png' width='32' /></td>
            <td><h3>%1</h3></td>
        </tr>
        <tr>
            <td>%2</td>
        </tr>
        <tr>
        <td align='right'><img src=':/icons/icons/32x32/attachment_icon.png'/>&nbsp;&nbsp;<a href='%5'>%4</a></td>
        </tr>
        <tr>
            <td align='right'>%3&nbsp;&nbsp;&nbsp;<a href="fluidnexus://blacklistmessage" title="Blacklist Message"><img src=":/icons/icons/32x32/menu_blacklist.png" width="32"/></a>&nbsp;&nbsp;&nbsp;<a href="fluidnexus://deletemessage" title='Delete Message'><img src=':/icons/icons/32x32/menu_delete.png' width='32' /></a></td>
        </tr>

    </table>
    """

    other_text_attachment_public = """
    <table width='100%'>
        <tr>
        <td width='40' rowspan='4'><img src=':/icons/icons/32x32/menu_public_other.png' width='32' /></td>
            <td><h3>%1</h3></td>
        </tr>
        <tr>
            <td>%2</td>
        </tr>
        <tr>
        <td align='right'><img src=':/icons/icons/32x32/attachment_icon.png'/>&nbsp;&nbsp;<a href='%5'>%4</a></td>
        </tr>
        <tr>
            <td align='right'>%3&nbsp;&nbsp;&nbsp;<a href="fluidnexus://blacklistmessage" title="Blacklist Message"><img src=":/icons/icons/32x32/menu_blacklist.png" width="32"/></a>&nbsp;&nbsp;&nbsp;<a href="fluidnexus://deletemessage" title='Delete Message'><img src=':/icons/icons/32x32/menu_delete.png' width='32' /></a></td>
        </tr>

    </table>
    """


    other_text_attachment_blacklist = """
    <table width='100%'>
        <tr>
        <td width='40' rowspan='4'><img src=':/icons/icons/32x32/menu_all.png' width='32' /></td>
            <td><h3>%1</h3></td>
        </tr>
        <tr>
            <td>%2</td>
        </tr>
        <tr>
            <td align='right'><img src=':/icons/icons/32x32/attachment_icon.png'/>&nbsp;&nbsp;<a href='%5'>%4</a></td>
        </tr>
        <tr>
            <td align='right'>%3&nbsp;&nbsp;&nbsp;<a href="fluidnexus://unblacklistmessage" title="Unblacklist Message"><img src=":/icons/icons/32x32/menu_all.png" width="32"/></a>&nbsp;&nbsp;&nbsp;<a href="fluidnexus://deletemessage" title='Delete Message'><img src=':/icons/icons/32x32/menu_delete.png' width='32' /></a></td>
        </tr>

    </table>
    """

    other_text_attachment_blacklist_public = """
    <table width='100%'>
        <tr>
        <td width='40' rowspan='4'><img src=':/icons/icons/32x32/menu_public_other.png' width='32' /></td>
            <td><h3>%1</h3></td>
        </tr>
        <tr>
            <td>%2</td>
        </tr>
        <tr>
            <td align='right'><img src=':/icons/icons/32x32/attachment_icon.png'/>&nbsp;&nbsp;<a href='%5'>%4</a></td>
        </tr>
        <tr>
            <td align='right'>%3&nbsp;&nbsp;&nbsp;<a href="fluidnexus://unblacklistmessage" title="Unblacklist Message"><img src=":/icons/icons/32x32/menu_all.png" width="32"/></a>&nbsp;&nbsp;&nbsp;<a href="fluidnexus://deletemessage" title='Delete Message'><img src=':/icons/icons/32x32/menu_delete.png' width='32' /></a></td>
        </tr>

    </table>
    """



    def __init__(self, parent = None, mine = False, message_title = "Testing title", message_content = "Testing content", message_type = 0, message_hash = None, message_timestamp = time.time(), message_received_timestamp = time.time(), attachment_path = None, attachment_original_filename = None, message_public = False, logPath = "FluidNexus.log", level = logging.WARN, blacklist = False):
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
        self.setMessageReceivedTimestamp(message_received_timestamp)
        self.setMessageAttachmentPath(attachment_path)
        self.setMessageAttachmentOriginalFilename(attachment_original_filename)
        self.setMessagePublic(message_public)
        self.blacklist = blacklist

        self.connect(self, QtCore.SIGNAL("textChanged()"), self.setHeight)
        self.setTextBrowserHTML()
        self.adjustSize()        
        self.setHeight()

        # TODO
        # This causes recursion errors, even if the size is what we want
        #self.connect(self, QtCore.SIGNAL("resizeEvent(QResizeEvent)"), self.resizeEvent)


    def setTextBrowserHTML(self):
        """Set our HTML content with the instance values."""

        if (self.getMessageAttachmentPath() is None):
            if (self.mine):
                if (self.getMessagePublic()):
                    s = QtCore.QString(self.mine_text_public).arg(self.getMessageTitle(), self.getMessageContent(), time.ctime(self.getMessageTimestamp()))
                else:
                    s = QtCore.QString(self.mine_text).arg(self.getMessageTitle(), self.getMessageContent(), time.ctime(self.getMessageTimestamp()))
            else:
                if (self.getMessagePublic()):
                    if (self.blacklist):
                        s = QtCore.QString(self.other_text_blacklist_public).arg(self.getMessageTitle(), self.getMessageContent(), time.ctime(self.getMessageTimestamp()))
                    else:
                        s = QtCore.QString(self.other_text_public).arg(self.getMessageTitle(), self.getMessageContent(), time.ctime(self.getMessageTimestamp()))
                else:
                    if (self.blacklist):
                        s = QtCore.QString(self.other_text_blacklist).arg(self.getMessageTitle(), self.getMessageContent(), time.ctime(self.getMessageTimestamp()))
                    else:
                        s = QtCore.QString(self.other_text).arg(self.getMessageTitle(), self.getMessageContent(), time.ctime(self.getMessageTimestamp()))
        else:
            if (self.mine):
                if (self.getMessagePublic()):
                    s = QtCore.QString(self.mine_text_attachment_public).arg(self.getMessageTitle(), self.getMessageContent(), time.ctime(self.getMessageTimestamp()), self.getMessageAttachmentOriginalFilename(), "file:///" + self.getMessageAttachmentPath())
                else:
                    s = QtCore.QString(self.mine_text_attachment).arg(self.getMessageTitle(), self.getMessageContent(), time.ctime(self.getMessageTimestamp()), self.getMessageAttachmentOriginalFilename(), "file:///" + self.getMessageAttachmentPath())
            else:
                if (self.getMessagePublic()):
                    if (self.blacklist):
                        s = QtCore.QString(self.other_text_attachment_blacklist_public).arg(self.getMessageTitle(), self.getMessageContent(), time.ctime(self.getMessageTimestamp()), self.getMessageAttachmentOriginalFilename(), "file:///" + self.getMessageAttachmentPath())
                    else:
                        s = QtCore.QString(self.other_text_attachment_public).arg(self.getMessageTitle(), self.getMessageContent(), time.ctime(self.getMessageTimestamp()), self.getMessageAttachmentOriginalFilename(), "file:///" + self.getMessageAttachmentPath())
                else:
                    if (self.blacklist):
                        s = QtCore.QString(self.other_text_attachment_blacklist).arg(self.getMessageTitle(), self.getMessageContent(), time.ctime(self.getMessageTimestamp()), self.getMessageAttachmentOriginalFilename(), "file:///" + self.getMessageAttachmentPath())
                    else:
                        s = QtCore.QString(self.other_text_attachment).arg(self.getMessageTitle(), self.getMessageContent(), time.ctime(self.getMessageTimestamp()), self.getMessageAttachmentOriginalFilename(), "file:///" + self.getMessageAttachmentPath())

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

    def setMessageReceivedTimestamp(self, message_received_timestamp):
        self.message_received_timestamp = message_received_timestamp

    def setMessageAttachmentPath(self, attachment_path):
        self.attachment_path = attachment_path

    def setMessageAttachmentOriginalFilename(self, attachment_original_filename):
        self.attachment_original_filename = attachment_original_filename

    def setMessagePublic(self, message_public):
        self.message_public = message_public

    def getMessageHash(self):
        return self.message_hash

    def getMessageTitle(self):
        return self.message_title

    def getMessageContent(self):
        return self.message_content

    def getMessageTimestamp(self):
        return self.message_timestamp

    def getMessageReceivedTimestamp(self):
        return self.message_received_timestamp

    def getMessageAttachmentPath(self):
        return self.attachment_path

    def getMessageAttachmentOriginalFilename(self):
        return self.attachment_original_filename

    def getMessagePublic(self):
        return self.message_public

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

    def getDatabase(self):
        """Return the database object."""
        return self.parent.database


    def mousePressEvent(self, e):
        pass

    def checkAnchor(self, anchor):
        """Handle anchor links here."""

        if (anchor.scheme() == "fluidnexus"):
            if (anchor.host() == "deletemessage"):
                self.parent.deleteMessage(self.getMessageHash())
            elif (anchor.host() == "blacklistmessage"):
                self.parent.blacklistMessage(self.getMessageHash())
            elif (anchor.host() == "unblacklistmessage"):
                self.parent.unblacklistMessage(self.getMessageHash())
            elif (anchor.host() == "editmessage"):
                # TODO
                # There ought to be a better way of doing this...
                stripped_content = re.sub('<[^<]+?>', '', self.getMessageContent())
                lines = stripped_content.split('\n')
                stripped_content = '\n'.join([line.strip() for line in lines])
                if (self.getMessageAttachmentPath() is None):
                    self.newMessageDialog = FluidNexusNewMessageDialog(parent = self, title = self.getMessageTitle(), content = stripped_content, public = self.getMessagePublic(), windowTitle = self.trUtf8("Edit Message"))
                else:
                    self.newMessageDialog = FluidNexusNewMessageDialog(parent = self, title = self.getMessageTitle(), content = stripped_content, attachment_original_path = os.path.realpath(self.getMessageAttachmentPath()), public = self.getMessagePublic(), windowTitle = self.trUtf8("Edit Message"))
                self.newMessageDialog.exec_()
        elif (anchor.scheme() == "file"):
            QtGui.QDesktopServices.openUrl(anchor)

    def newMessageSaveButtonClicked(self, message_title, message_content, message_filename, public):
        """Respond to the new (edit) message save button."""
        print public
        ttl = self.parent.settings.value("app/ttl", 30).toInt()[0]
        new_message_hash = unicode(hashlib.sha256(unicode(message_title) + unicode(message_content)).hexdigest())
        message_title = unicode(message_title)
        message_content = unicode(message_content)
        if (new_message_hash != self.getMessageHash()):
            if (message_filename is None):
                message_timestamp = time.time()
                self.parent.database.updateByMessageHash(message_hash = self.getMessageHash(), new_message_hash = new_message_hash, new_content = message_content, new_title = message_title, new_timestamp = message_timestamp, new_public = public, new_ttl = ttl)
                self.parent.replaceHash(self.getMessageHash(), new_message_hash)
    
                self.setMessageTitle(message_title)
                self.setMessageContent(textile.textile(message_content))
                self.setMessageHash(new_message_hash)
                self.setMessageTimestamp(message_timestamp)
                self.setMessageReceivedTimestamp(message_timestamp)
                self.setMessagePublic(public)
                self.setTextBrowserHTML()
            else:
                # Get relevant infos about the file
                message_filename = unicode(message_filename)
                fullPath, extension = os.path.splitext(message_filename)
                attachment_original_filename = os.path.basename(message_filename)
                #attachment_path = os.path.join(self.parent.attachmentsDir, new_message_hash) + extension
                attachment_path = message_filename

                message_timestamp = time.time()
                self.parent.database.updateByMessageHash(message_hash = self.getMessageHash(), new_message_hash = new_message_hash, new_content = message_content, new_title = message_title, new_timestamp = message_timestamp, new_attachment_path = attachment_path, new_attachment_original_filename = attachment_original_filename, new_public = public, new_ttl = ttl)
                self.parent.replaceHash(self.getMessageHash(), new_message_hash)

                self.setMessageTitle(message_title)
                self.setMessageContent(textile.textile(message_content))
                self.setMessageHash(new_message_hash)
                self.setMessageTimestamp(message_timestamp)
                self.setMessageReceivedTimestamp(message_timestamp)
                self.setMessageAttachmentPath(attachment_path)
                self.setMessageAttachmentOriginalFilename(attachment_original_filename)
                self.setMessagePublic(public)
                self.setTextBrowserHTML()

    # TODO
    # This does make things the proper size, but then we get recursion errors...and I don't know how to stop the recursion.
    #def resizeEvent(self, event):
    #    self.setHeight()

class FluidNexusNewMessageDialog(QtGui.QDialog):
    def __init__(self, parent=None, title = None, content = None, attachment_original_path = None, public = False, windowTitle = "New Message"):
        QtGui.QDialog.__init__(self, parent)

        self.parent = parent

        self.ui = Ui_FluidNexusNewMessage()
        self.ui.setupUi(self)

        self.setWindowTitle(self.trUtf8(windowTitle))

        self.originalTitle = ""
        self.originalContent = ""

        if (title is not None):
            self.ui.newMessageTitle.setText(title)
            self.originalTitle = title
        if (content is not None):
            self.ui.newMessageBody.setPlainText(content)
            self.originalContent = content
        
        self.ui.nexusCheckBox.setChecked(public)

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
        self.originalFilename = attachment_original_path

    def closeDialog(self):
        # TODO
        # Ask for confirmation if the data has changed

        if ((self.originalTitle != unicode(self.ui.newMessageTitle.text()).encode("utf-8")) or (self.originalContent != unicode(self.ui.newMessageBody.document().toPlainText()).encode("utf-8")) or (self.originalFilename != self.filename)):
            response = self.confirmSaveDialog()
            if (response == self.YES):
                self.saveButtonClicked()
            else:
                self.close()
        else:
            self.close()

    def confirmSaveDialog(self):
        """Create a save confirmation dialog."""
        self.YES = self.trUtf8("Yes")
        self.NO = self.trUtf8("No")
        message = QtGui.QMessageBox(self)
        message.setText(self.trUtf8("Message has changed; do you want to save?"))
        message.setWindowTitle('FluidNexus')
        message.setIcon(QtGui.QMessageBox.Warning)
        message.addButton(self.YES, QtGui.QMessageBox.AcceptRole)
        message.addButton(self.NO, QtGui.QMessageBox.RejectRole)
        message.exec_()
        response = message.clickedButton().text()
        return response


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

    def sameDialog(self):
        """Create a delete confirmation dialog."""
        self.YES = self.trUtf8("OK")
        message = QtGui.QMessageBox(self)
        message.setText(self.trUtf8("This message already exists in the database.  Please change the title and/or the content."))
        message.setWindowTitle(self.trUtf8('FluidNexus'))
        message.setIcon(QtGui.QMessageBox.Critical)
        message.addButton(self.YES, QtGui.QMessageBox.AcceptRole)
        message.exec_()
        response = message.clickedButton().text()
        return response

    def saveButtonClicked(self):
        message_hash = hashlib.sha256(unicode(self.ui.newMessageTitle.text()).encode("utf-8") + unicode(self.ui.newMessageBody.document().toPlainText()).encode("utf-8")).hexdigest()
        
        if (self.parent.getDatabase().checkForMessageByHash(message_hash)):
            self.sameDialog()
        else:
            self.emit(QtCore.SIGNAL("saveButtonClicked"), self.ui.newMessageTitle.text(), self.ui.newMessageBody.document().toPlainText(), self.filename, self.ui.nexusCheckBox.isChecked())
            self.close()

class FluidNexusPreferencesDialog(QtGui.QDialog):
    bluetoothScanFrequencies = [5, 10, 30, 60, 120, 300, 600, 1200, 1800, 3600]
    zeroconfScanFrequencies = bluetoothScanFrequencies
    
    GENERAL_TAB = 0
    NETWORK_TAB = 1
    BLUETOOTH_TAB = 2
    ZEROCONF_TAB = 3
    ADHOC_TAB = 4
    NEXUS_TAB = 5

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
        zeroconf = self.settings.value("network/zeroconf", 2).toInt()[0]
        nexus = self.settings.value("network/nexus", 2).toInt()[0]

        if (bluetooth == 2):
            self.ui.bluetoothEnabled.setCheckState(QtCore.Qt.Checked)
            self.ui.FluidNexusPreferencesTabWidget.setTabEnabled(self.BLUETOOTH_TAB, True)
        else:
            self.ui.bluetoothEnabled.setCheckState(QtCore.Qt.Unchecked)
            self.ui.FluidNexusPreferencesTabWidget.setTabEnabled(self.BLUETOOTH_TAB, False)

        if (zeroconf == 2):
            self.ui.zeroconfEnabled.setCheckState(QtCore.Qt.Checked)
            self.ui.FluidNexusPreferencesTabWidget.setTabEnabled(self.ZEROCONF_TAB, True)
        else:
            self.ui.zeroconfEnabled.setCheckState(QtCore.Qt.Unchecked)
            self.ui.FluidNexusPreferencesTabWidget.setTabEnabled(self.ZEROCONF_TAB, False)

        if (nexus == 2):
            self.ui.nexusEnabled.setCheckState(QtCore.Qt.Checked)
            self.ui.FluidNexusPreferencesTabWidget.setTabEnabled(self.NEXUS_TAB, True)
        else:
            self.ui.nexusEnabled.setCheckState(QtCore.Qt.Unchecked)
            self.ui.FluidNexusPreferencesTabWidget.setTabEnabled(self.NEXUS_TAB, False)



    def __bluetoothPreferencesUpdate(self):
        bluetoothScanFrequency = self.settings.value("bluetooth/scanFrequency", 300).toInt()[0]
        index = self.bluetoothScanFrequencies.index(bluetoothScanFrequency)
        self.ui.bluetoothScanFrequency.setCurrentIndex(index)

    def __zeroconfPreferencesUpdate(self):
        zeroconfScanFrequency = self.settings.value("zeroconf/scanFrequency", 300).toInt()[0]
        index = self.zeroconfScanFrequencies.index(zeroconfScanFrequency)
        self.ui.zeroconfScanFrequency.setCurrentIndex(index)

    def __nexusPreferencesUpdate(self):
        self.ui.keyInput.setText(self.settings.value("nexus/key", "").toString())
        self.ui.secretInput.setText(self.settings.value("nexus/secret", "").toString())
        self.ui.tokenInput.setText(self.settings.value("nexus/token", "").toString())
        self.ui.tokenSecretInput.setText(self.settings.value("nexus/tokenSecret", "").toString())
        self.ui.ttlSpinBox.setValue(self.settings.value("nexus/ttl", 30).toInt()[0])


    def __updatePreferencesDialog(self):
        """Update the preferences dialog based on our settings."""
        
        self.ui.FluidNexusPreferencesTabWidget.setTabEnabled(self.ADHOC_TAB, False)
        self.__networkPreferencesUpdate()
        self.__bluetoothPreferencesUpdate()
        self.__zeroconfPreferencesUpdate()
        self.__nexusPreferencesUpdate()
        self.preferencesToChange = {}

    def reject(self):
        QtGui.QDialog.reject(self)

    def accept(self):

        for key in self.preferencesToChange.keys():
            self.settings.setValue(key, self.preferencesToChange[key])
        QtGui.QDialog.accept(self)

    def bluetoothChanged(self, value):
        self.preferencesToChange["network/bluetooth"] = value
        if (value == 2):
            self.ui.FluidNexusPreferencesTabWidget.setTabEnabled(self.BLUETOOTH_TAB, True)
        else:
            self.ui.FluidNexusPreferencesTabWidget.setTabEnabled(self.BLUETOOTH_TAB, False)

    def zeroconfChanged(self, value):
        self.preferencesToChange["network/zeroconf"] = value
        if (value == 2):
            self.ui.FluidNexusPreferencesTabWidget.setTabEnabled(self.ZEROCONF_TAB, True)
        else:
            self.ui.FluidNexusPreferencesTabWidget.setTabEnabled(self.ZEROCONF_TAB, False)

    def nexusChanged(self, value):
        self.preferencesToChange["network/nexus"] = value
        if (value == 2):
            self.ui.FluidNexusPreferencesTabWidget.setTabEnabled(self.NEXUS_TAB, True)
        else:
            self.ui.FluidNexusPreferencesTabWidget.setTabEnabled(self.NEXUS_TAB, False)


    def bluetoothScanFrequencyChanged(self, index):
        # TODO
        # It would be nice to get the disambiguation paramter, but that's not likely...
        # Remember that if we change the number of options in the UI, we have to change the number of options here as well
        self.preferencesToChange["bluetooth/scanFrequency"] = self.bluetoothScanFrequencies[index]
        self.parent.emit(QtCore.SIGNAL("bluetoothScanFrequencyChanged(QVariant)"), self.bluetoothScanFrequencies[index])

    def zeroconfScanFrequencyChanged(self, index):
        # TODO
        # It would be nice to get the disambiguation paramter, but that's not likely...
        # Remember that if we change the number of options in the UI, we have to change the number of options here as well
        self.preferencesToChange["zeroconf/scanFrequency"] = self.zeroconfScanFrequencies[index]
        self.parent.emit(QtCore.SIGNAL("zeroconfScanFrequencyChanged(QVariant)"), self.zeroconfScanFrequencies[index])

    def ttlFinished(self):
        self.preferencesToChange["nexus/ttl"] = self.ui.ttlSpinBox.value()

    def nexusKeyFinished(self):
        self.preferencesToChange["nexus/key"] = self.ui.keyInput.text()

    def nexusSecretFinished(self):
        self.preferencesToChange["nexus/secret"] = self.ui.secretInput.text()

    def tokenFinished(self):
        self.preferencesToChange["nexus/token"] = self.ui.tokenInput.text()

    def tokenSecretFinished(self):
        self.preferencesToChange["nexus/tokenSecret"] = self.ui.tokenSecretInput.text()


    def onRequestAuthorization(self):
        request = build_request_token_request(REQUEST_TOKEN_URL, unicode(self.ui.keyInput.text()), unicode(self.ui.secretInput.text()))
        u = urllib2.urlopen(REQUEST_TOKEN_URL, data = request.to_postdata())
        result = u.read()
        u.close()
        url = simplejson.loads(unicode(result))

        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url["result"]))

    def closeDialog(self):
        # TODO
        # Ask for confirmation if the data has changed
        self.close()


class FluidNexusAboutDialog(QtGui.QDialog):

    aboutText = u"""<p>Copyright 2008-2011 Nicholas A. Knouf</p>
    
<p>Fluid Nexus is an application for mobile   phones that is primarily designed to enable activists or relief workers to send messages and data amongst themselves independent of a centralized cellular      network.  The idea is to provide a means of communication between people when   the centralized network has been shut down, either by the government during a   time of unrest, or by nature due to a massive disaster.  During such times the  use of the centralized network for voice or SMS is not possible.  Yet, if we    can use the fact that people still must move about the world, then we can use   ideas from sneaker-nets to turn people into carriers of data.  Given enough     people, we can create fluid, temporary, ad-hoc networks that pass messages one  person at a time, spreading out as a contagion and eventually reaching members  of the group.  This enables surreptitious communication via daily activity and  relies on a fluid view of reality.  Additionally, Fluid Nexus can be used as a  hyperlocal message board, loosely attached to physical locations.  </p>
    
<p>Fluid Nexus is not designed as a general-purpose piece of software; rather, it is developed with specific types of users in mind.  Thus, while the ideas here could be very useful for social-networking or productivity applications, this is not what I am most interested in.  However, I definitely welcome the extension of these ideas into these other domains.  Indeed, Fluid Nexus is related to work in the following projects: mesh networking in the OLPC ( http://wiki.laptop.org/go/Mesh_Network_Details ), the Haggle project ( http://www.haggleproject.org/ ), and Comm.unity ( http://community.mit.edu/ ), among many  others.</p>"""

    creditsText = u"""<h2>Initial Version Credits</h2>
    <p>The initial version of Fluid Nexus for Series 60 Nokia phones running Python was written in conjunction with Bruno Vianna, Luis Ayuso; design help by Mónica Sánchez; and the support of <a href="http://medialab-prado.es">Medialab Prado</a> during the 2° Encuentro Inclusiva-net: redes digitales y espacio fisico.</p>"""

    def __init__(self, parent=None, title = None, message = None):
        QtGui.QDialog.__init__(self, parent)

        self.parent = parent
    
        self.ui = Ui_FluidNexusAbout()
        self.ui.setupUi(self)
        self.ui.AboutDialogAboutText.setText(self.aboutText)
        self.ui.AboutDialogCreditsText.setText(self.creditsText)

    def closeDialog(self):
        self.close()



class FluidNexusDesktop(QtGui.QMainWindow):
    """Main class for interacting with the desktop version of the software."""

    # Global values for the view modes
    VIEW_ALL = 0
    VIEW_PUBLIC = 1
    VIEW_OUTGOING = 2
    VIEW_BLACKLIST = 3

    viewMode = VIEW_ALL

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
            self.saveGeometrySettings()
        else:
            self.restoreGeometrySettings()
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

        # Setup actions
        self.setupActions()

        # Setup display
        self.handleViewAll()

        # Setup signals
        self.__setupSignals()

        self.setupSysTray()

        # Set our enabled/disabled network modalities; we'll refer to these values throughout the course of the program
        bluetooth = self.settings.value("network/bluetooth", 2).toInt()[0]
        if (bluetooth == 2): 
            self.bluetoothEnabled = True
        else:
            self.bluetoothEnabled = False

        zeroconf = self.settings.value("network/zeroconf", 2).toInt()[0]
        if (zeroconf == 2): 
            self.zeroconfEnabled = True
        else:
            self.zeroconfEnabled = False

        nexus = self.settings.value("network/nexus", 2).toInt()[0]
        if (nexus == 2): 
            self.nexusEnabled = True
        else:
            self.nexusEnabled = False


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
        pass

    def saveGeometrySettings(self):
        self.settings.setValue("app/pos", self.pos())
        self.settings.setValue("app/size", self.size())

    def restoreGeometrySettings(self):
        pos = self.settings.value("app/pos", QtCore.QPoint(200, 200)).toPoint()
        size = self.settings.value("app/size", QtCore.QSize(200, 400)).toSize()
        self.resize(size)
        self.move(pos)

    def resizeEvent(self, event):
        if (event.oldSize() != self.ui.centralwidget.size()):
            self.ui.FluidNexusScrollArea.resize(self.ui.centralwidget.size())

    def findAppDirWin(self):
        if hasattr(sys, "frozen"):
            return os.path.dirname(sys.executable)

        return os.path.dirname(sys.argv[0])

    def __setupAppData(self):
        """ Setup the application data directory in the home directory."""

        homeDir = os.path.expanduser('~')

        if sys.platform == "win32":
            # We don't want a centralized location for app data, especially on multi-user systems
            #homeDir = self.findAppDirWin()
            self.dataDir = os.path.join(homeDir, "FluidNexusData")
        else:
            self.dataDir = os.path.join(homeDir, ".FluidNexus")

        self.attachmentsDir  = os.path.join(self.dataDir, "attachments")
        
        if not os.path.isdir(self.dataDir):
            os.makedirs(self.dataDir)

        if not os.path.isdir(self.attachmentsDir):
            os.makedirs(self.attachmentsDir)

        os.chmod(self.dataDir, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)

    def __startNetworkThreads(self):

        if (self.bluetoothEnabled):
            self.bluetoothServerThread = FluidNexusServerQt(parent = self, dataDir = self.dataDir, databaseType = "pysqlite2", attachmentsDir = self.attachmentsDir, logPath = self.logPath, level = self.logLevel)

            # TODO
            # Any faster way to determine whether or not it's enabled?
            enabled = self.bluetoothServerThread.testBluetooth()

            if (enabled):
                self.bluetoothServerThread.start()
            
                scanFrequency = self.settings.value("bluetooth/scanFrequency", 300).toInt()[0]
                self.bluetoothClientThread = FluidNexusClientQt(parent = self, dataDir = self.dataDir, databaseType = "pysqlite2", attachmentsDir = self.attachmentsDir, logPath = self.logPath, level = self.logLevel, scanFrequency = scanFrequency)
    
                self.bluetoothClientThread.start()

        if (self.zeroconfEnabled):
            scanFrequency = self.settings.value("zeroconf/scanFrequency", 300).toInt()[0]
            self.zeroconfClientThread = ZeroconfClientQt(parent = self, databaseDir = self.dataDir, databaseType = "pysqlite2", attachmentsDir = self.attachmentsDir, logPath = self.logPath, level = self.logLevel, scanFrequency = scanFrequency, loopType = "qt")
            enabled = self.zeroconfClientThread.testZeroconf()

            if (enabled):
                self.zeroconfClientThread.start()
    
                self.zeroconfServerThread = ZeroconfServerQt(parent = self, databaseDir = self.dataDir, databaseType = "pysqlite2", attachmentsDir = self.attachmentsDir, logPath = self.logPath, level = self.logLevel)
                self.zeroconfServerThread.start()
            
        # TODO
        # enable configuration of nexus sending
        if (self.nexusEnabled):
            key = self.settings.value("nexus/key", "").toString()
            secret = self.settings.value("nexus/secret", "").toString()
            token = self.settings.value("nexus/token", "").toString()
            token_secret = self.settings.value("nexus/tokenSecret", "").toString()
            self.nexusThread = NexusNetworkingQt(parent = self, databaseDir = self.dataDir, databaseType = "pysqlite2", attachmentsDir = self.attachmentsDir, logPath = self.logPath, level = self.logLevel, key = key, secret = secret, token = token, token_secret = token_secret)
            self.nexusThread.start()

    def __stopNetworkThreads(self):
        if (self.bluetoothEnabled):
            self.bluetoothServerThread.quit()
            self.bluetoothClientThread.quit()

        if (self.zeroconfEnabled):
            self.zeroconfServerThread.quit()
            self.zeroconfClientThread.quit()

        if (self.nexusEnabled):
            self.nexusThread.quit()

    def setupDisplay(self):
        """Setup our display with a bunch of text browsers."""

        # TODO
        # Not ideal or quick...probably need to refactor
        if (self.viewMode == self.VIEW_ALL):
            items = self.database.all()
            self.setWindowTitle(self.trUtf8("Fluid Nexus: View All Messages"))
        elif (self.viewMode == self.VIEW_PUBLIC):
            items = self.database.public()
            self.setWindowTitle(self.trUtf8("Fluid Nexus: View Public Messages"))
        elif (self.viewMode == self.VIEW_OUTGOING):
            items = self.database.outgoing()
            self.setWindowTitle(self.trUtf8("Fluid Nexus: View Outgoing Messages"))
        elif (self.viewMode == self.VIEW_BLACKLIST):
            items = self.database.blacklist()
            self.setWindowTitle(self.trUtf8("Fluid Nexus: View Blacklisted Messages"))
        items.reverse()

        for item in items:
            message_timestamp = item['time']
            message_hash = item['message_hash']
            message_title = item['title']
            message_content = item['content']
            message_mine = item['mine']
            attachment_path = item['attachment_path']
            attachment_original_filename = item['attachment_original_filename']
            message_public = item['public']

            if (attachment_path == ""):
                if (self.viewMode != self.VIEW_BLACKLIST):
                    tb = MessageTextBrowser(parent = self, mine = message_mine, message_title = message_title, message_content = textile.textile(message_content), message_hash = message_hash, message_timestamp = message_timestamp, message_public = message_public, logPath = self.logPath)
                else:
                    tb = MessageTextBrowser(parent = self, mine = message_mine, message_title = message_title, message_content = textile.textile(message_content), message_hash = message_hash, message_timestamp = message_timestamp, message_public = message_public, logPath = self.logPath, blacklist = True)
            else:
                if (self.viewMode != self.VIEW_BLACKLIST):
                    tb = MessageTextBrowser(parent = self, mine = message_mine, message_title = message_title, message_content = textile.textile(message_content), message_hash = message_hash, message_timestamp = message_timestamp, attachment_path = attachment_path, attachment_original_filename = attachment_original_filename, message_public = message_public, logPath = self.logPath)
                else:
                    tb = MessageTextBrowser(parent = self, mine = message_mine, message_title = message_title, message_content = textile.textile(message_content), message_hash = message_hash, message_timestamp = message_timestamp, attachment_path = attachment_path, attachment_original_filename = attachment_original_filename, message_public = message_public, logPath = self.logPath, blacklist = True)
            tb.setFocusProxy(self)
            self.ui.FluidNexusVBoxLayout.insertWidget(0, tb)

    def setupActions(self):
        """Setup the actions that we already know about."""
        self.connect(self.ui.actionAbout, QtCore.SIGNAL('triggered()'), self.displayAbout)
        self.connect(self.ui.actionQuit, QtCore.SIGNAL('triggered()'), self.handleQuit)
        self.connect(self.ui.actionNewMessage, QtCore.SIGNAL('triggered()'), self.handleNewMessage)
        self.connect(self.ui.actionPreferences, QtCore.SIGNAL('triggered()'), self.handlePreferences)

        self.connect(self.ui.actionViewAll, QtCore.SIGNAL('triggered()'), self.handleViewAll)
        self.connect(self.ui.actionViewPublic, QtCore.SIGNAL('triggered()'), self.handleViewPublic)
        self.connect(self.ui.actionViewOutgoing, QtCore.SIGNAL('triggered()'), self.handleViewOutgoing)
        self.connect(self.ui.actionViewBlacklist, QtCore.SIGNAL('triggered()'), self.handleViewBlacklist)

    def setupSysTray(self):
        """Setup the systray."""
        self.showing = True
        self.sysTray = QtGui.QSystemTrayIcon(self)
        self.sysTray.setIcon( QtGui.QIcon(':icons/icons/fluid_nexus_icon.png') )
        self.sysTray.setVisible(True)
        self.connect(self.sysTray, QtCore.SIGNAL("activated(QSystemTrayIcon::ActivationReason)"), self.onSysTrayActivated)

        self.sysTrayMenu = QtGui.QMenu(self)
        newMessageAction = self.sysTrayMenu.addAction(self.ui.actionNewMessage)
        self.sysTray.setContextMenu(self.sysTrayMenu)

    def onSysTrayActivated(self, reason):
        """Handle systray actions."""

        if ((reason == 3) and (self.showing)):
            if (self.isActiveWindow() == False):
                self.raise_()
                self.activateWindow()
            else:
                self.hide()
                self.showing = False
        elif ((reason == 3) and (not (self.showing))):
            self.show()
            self.showing = True

    def getDatabase(self):
        """Return the database object."""
        return self.database

    def deleteTextBrowserWidgets(self):
        """Delete all of the text browser widgets in preparation for repopulating.

        TODO:
        * this is probably _really_ inefficient..."""

        numItems = self.ui.FluidNexusVBoxLayout.count()
        
        for index in xrange(0, numItems):
            currentWidget = self.ui.FluidNexusVBoxLayout.itemAt(index).widget()
            currentWidget.close()

    def handleNewMessage(self):
        self.newMessageDialog = FluidNexusNewMessageDialog(parent = self)
        self.newMessageDialog.exec_()

    def handlePreferences(self):
        self.preferencesDialog = FluidNexusPreferencesDialog(parent = self, logPath = self.logPath, level = self.logLevel,  settings = self.settings)
        self.preferencesDialog.exec_()

    def handleViewAll(self):
        self.changeToolbarCheckedState(self.viewMode, self.VIEW_ALL)
        self.viewMode = self.VIEW_ALL
        self.deleteTextBrowserWidgets()
        self.setupDisplay()

    def handleViewPublic(self):
        self.changeToolbarCheckedState(self.viewMode, self.VIEW_PUBLIC)
        self.viewMode = self.VIEW_PUBLIC
        self.deleteTextBrowserWidgets()
        self.setupDisplay()

    def handleViewOutgoing(self):
        self.changeToolbarCheckedState(self.viewMode, self.VIEW_OUTGOING)
        self.viewMode = self.VIEW_OUTGOING
        self.deleteTextBrowserWidgets()
        self.setupDisplay()

    def handleViewBlacklist(self):
        self.changeToolbarCheckedState(self.viewMode, self.VIEW_BLACKLIST)
        self.viewMode = self.VIEW_BLACKLIST
        self.deleteTextBrowserWidgets()
        self.setupDisplay()

    def closeEvent(self, event):
        """Handle the close event from the WM."""
        self.handleQuit()

    def handleQuit(self):
        self.logger.debug("Quiting...")
        self.saveGeometrySettings()
        self.emit(QtCore.SIGNAL("handleQuit"))
        self.__stopNetworkThreads()
        self.sysTray.hide()
        self.database.close()
        self.close()

    def changeToolbarCheckedState(self, old, new):
        """Change the checked state of the toolbar buttons from the old to the new."""
        # TODO
        # Perhaps a better way of doing this rather than hard-coding it?
        actions = ["actionViewAll", "actionViewPublic", "actionViewOutgoing", "actionViewBlacklist"]
        oldAction = getattr(self.ui, actions[old])
        newAction = getattr(self.ui, actions[new])
        oldAction.setChecked(False)
        newAction.setChecked(True)

    def displayAbout(self):
        """Display our about box."""
        self.aboutDialog = FluidNexusAboutDialog(parent = self)
        self.aboutDialog.exec_()

    def newMessages(self, newMessages):
        """Slot for when an incoming message was added by the server thread."""
        self.logger.debug("New messages received: " + str(newMessages))
        for message in newMessages:
            if (message["message_attachment_path"] == ""):
                tb = MessageTextBrowser(parent = self, mine = 0, message_title = message["message_title"], message_content = textile.textile(message["message_content"]), message_hash = message["message_hash"], message_timestamp = message["message_timestamp"], message_public = message["message_public"], logPath = self.logPath)
            else:
                tb = MessageTextBrowser(parent = self, mine = 0, message_title = message["message_title"], message_content = textile.textile(message["message_content"]), message_hash = message["message_hash"], message_timestamp = message["message_timestamp"], attachment_path = message["message_attachment_path"], attachment_original_filename = message["message_attachment_original_filename"], message_public = message["message_public"], logPath = self.logPath)

            self.ourHashes.append(message["message_hash"])
            tb.setFocusProxy(self)
            self.ui.FluidNexusVBoxLayout.insertWidget(0, tb)

        self.statusBar().showMessage(self.trUtf8("New messages received."))

    def disableBluetooth(self):
        self.bluetoothEnabled = False
        self.settings.setValue("network/bluetooth", 0)
        # TODO
        # add dialog that bluetooth was not enabled
        self.logger.error("Bluetooth not enabled; shutting off bluetooth service")
        self.statusBar().showMessage(self.trUtf8("Bluetooth not enabled; shutting off bluetooth service."))

    def disableZeroconf(self):
        self.zeroconfEnabled = False
        self.settings.setValue("network/zeroconf", 0)
        #TODO
        # add dialog that zeroconf was not enabled
        self.logger.error("Zeroconf not enabled; shutting off zeroconf service")
        self.statusBar().showMessage(self.trUtf8("Zeroconf not enabled; shutting off zeroconf service."))

    def replaceHash(self, hashToReplace, newHash):
        """Replace a hash in our threads."""

        if (self.bluetoothEnabled):
            self.bluetoothServerThread.replaceHash(hashToReplace, newHash)
            self.bluetoothClientThread.replaceHash(hashToReplace, newHash)

        if (self.zeroconfEnabled):
            self.zeroconfServerThread.replaceHash(hashToReplace, newHash)
            self.zeroconfClientThread.replaceHash(hashToReplace, newHash)

        if (self.nexusEnabled):
            self.nexusThread.replaceHash(hashToReplace, newHash)
  
    def removeHash(self, hashToRemove):
        """Remove a hash from our threads."""

        if (self.bluetoothEnabled):
            self.bluetoothServerThread.removeHash(hashToRemove)
            self.bluetoothClientThread.removeHash(hashToRemove)

        if (self.zeroconfEnabled):
            self.zeroconfServerThread.removeHash(hashToRemove)
            self.zeroconfClientThread.removeHash(hashToRemove)

        if (self.nexusEnabled):
            self.nexusThread.removeHash(hashToRemove)


    def getTextBrowserWidgetForHash(self, message_hash):
        """Get a particular text browser widget with the given hash."""
        numItems = self.ui.FluidNexusVBoxLayout.count()

        foundWidget = None
        
        #Find a particular widget with the given hash.  This is a pain to do, and the searching algorithm can probably better, but here it goes.
        for index in xrange(0, numItems):
            currentWidget = self.ui.FluidNexusVBoxLayout.itemAt(index).widget()
            if (currentWidget.getMessageHash() == message_hash):
                foundWidget = currentWidget
                break

        return foundWidget


    def deleteMessage(self, hashToDelete):
        """Delete the selected hash and remove from display."""

        numItems = self.ui.FluidNexusVBoxLayout.count()
        
        #Find a particular widget with the given hash.  This is a pain to do, and the searching algorithm can probably better, but here it goes.
        for index in xrange(0, numItems):
            currentWidget = self.ui.FluidNexusVBoxLayout.itemAt(index).widget()
            if (currentWidget.getMessageHash() == hashToDelete):
                self.logger.debug("Got message to delete hash: " + hashToDelete)
                response = self.confirmDeleteDialog()
                if (response == self.YES):
                    self.ui.FluidNexusVBoxLayout.removeWidget(currentWidget)
                    if (currentWidget.getMessageAttachmentPath() is not None):
                        # Only delete non-mine attachments
                        if (not currentWidget.mine):
                            os.unlink(currentWidget.getMessageAttachmentPath())
                    currentWidget.close()
                    self.database.removeByMessageHash(hashToDelete)
                    self.removeHash(hashToDelete)
                break

    def confirmDeleteDialog(self):
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

    def blacklistMessage(self, message_hash):
        """Blacklist the given message with message_hash."""

        foundWidget = self.getTextBrowserWidgetForHash(message_hash)

        if (foundWidget is not None):
            response = self.confirmBlacklistDialog()
            if (response == self.YES):
                self.ui.FluidNexusVBoxLayout.removeWidget(foundWidget)
                foundWidget.close()
                self.database.toggleBlacklist(message_hash, 1)

    def confirmBlacklistDialog(self, un = False):
        """Create a blacklist confirmation dialog."""
        self.YES = "Yes"
        self.NO = "No"
        message = QtGui.QMessageBox(self)
        if (un):
            message.setText(self.trUtf8("Do you really want to unblacklist this message?"))
        else:
            message.setText(self.trUtf8("Do you really want to blacklist this message?"))

        message.setWindowTitle('FluidNexus')
        message.setIcon(QtGui.QMessageBox.Question)
        message.addButton(self.YES, QtGui.QMessageBox.AcceptRole)
        message.addButton(self.NO, QtGui.QMessageBox.RejectRole)
        message.exec_()
        response = message.clickedButton().text()
        return response

    def unblacklistMessage(self, message_hash):
        """Unblacklist the given message with message_hash."""

        foundWidget = self.getTextBrowserWidgetForHash(message_hash)

        if (foundWidget is not None):
            response = self.confirmBlacklistDialog(un = True)
            if (response == self.YES):
                self.ui.FluidNexusVBoxLayout.removeWidget(foundWidget)
                foundWidget.close()
                self.database.toggleBlacklist(message_hash, 0)


    def newMessageSaveButtonClicked(self, message_title, message_content, message_filename, public):

        message_hash = unicode(hashlib.sha256(unicode(message_title).encode("utf-8") + unicode(message_content).encode("utf-8")).hexdigest())

        ttl = self.settings.value("app/ttl", 30).toInt()[0]

        if (message_filename is None):
            self.database.addMine(title = unicode(message_title), content = unicode(message_content), public = public, ttl = ttl)
            self.addHash(message_hash)
            
            message_content = unicode(message_content)
            tb = MessageTextBrowser(parent = self, mine = 1, message_title = message_title, message_content = textile.textile(message_content), message_hash = message_hash, message_timestamp = time.time(), message_public = public, logPath = self.logPath)
            tb.setFocusProxy(self)

            self.ui.FluidNexusVBoxLayout.insertWidget(0, tb)
        else:
            # Get relevant infos about the file
            message_filename = unicode(message_filename)
            fullPath, extension = os.path.splitext(message_filename)
            attachment_original_filename = os.path.basename(message_filename)
            attachment_path = message_filename

            # Add the hash
            self.addHash(message_hash)

            # Convert QString to unicode
            message_content = unicode(message_content)

            # Guess type
            mimeType = mimetypes.guess_type(attachment_original_filename)
            
            print mimeType
            if ("image" in mimeType[0]):
                message_type = 2
            elif ("audio" in mimeType[0]):
                message_type = 1
            elif ("video" in mimeType[0]):
                message_type = 3
            else:
                message_type = 0

            # Add to database
            self.database.addMine(message_type = message_type, title = unicode(message_title), content = unicode(message_content), attachment_path = attachment_path, attachment_original_filename = attachment_original_filename, public = public, ttl = ttl)

            # Update display
            tb = MessageTextBrowser(parent = self, mine = 1, message_title = message_title, message_content = textile.textile(message_content), message_hash = message_hash, message_timestamp = time.time(), attachment_path = attachment_path, attachment_original_filename = attachment_original_filename, message_public = public, logPath = self.logPath)
            tb.setFocusProxy(self)

            self.ui.FluidNexusVBoxLayout.insertWidget(0, tb)

    def addHash(self, message_hash):
        """Add a hash to our threads."""

        if (self.bluetoothEnabled):
            self.bluetoothServerThread.addHash(message_hash)
            self.bluetoothClientThread.addHash(message_hash)

        if (self.zeroconfEnabled):
            self.zeroconfServerThread.addHash(message_hash)
            self.zeroconfClientThread.addHash(message_hash)

        if (self.nexusEnabled):
            self.nexusThread.addHash(message_hash)
