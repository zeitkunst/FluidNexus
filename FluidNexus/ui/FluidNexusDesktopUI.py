# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FluidNexus/ui/FluidNexusDesktop.ui'
#
# Created: Sun Jul 31 23:10:18 2011
#      by: PyQt4 UI code generator 4.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_FluidNexus(object):
    def setupUi(self, FluidNexus):
        FluidNexus.setObjectName(_fromUtf8("FluidNexus"))
        FluidNexus.resize(388, 651)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/fluid_nexus_icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        FluidNexus.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(FluidNexus)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.FluidNexusScrollArea = QtGui.QScrollArea(self.centralwidget)
        self.FluidNexusScrollArea.setGeometry(QtCore.QRect(0, 0, 380, 563))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.FluidNexusScrollArea.sizePolicy().hasHeightForWidth())
        self.FluidNexusScrollArea.setSizePolicy(sizePolicy)
        self.FluidNexusScrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.FluidNexusScrollArea.setWidgetResizable(True)
        self.FluidNexusScrollArea.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.FluidNexusScrollArea.setObjectName(_fromUtf8("FluidNexusScrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget(self.FluidNexusScrollArea)
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 374, 557))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.FluidNexusScrollArea.setWidget(self.scrollAreaWidgetContents)
        FluidNexus.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(FluidNexus)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 388, 24))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        self.menu_View = QtGui.QMenu(self.menubar)
        self.menu_View.setObjectName(_fromUtf8("menu_View"))
        FluidNexus.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(FluidNexus)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        FluidNexus.setStatusBar(self.statusbar)
        self.FluidNexusToolbar = QtGui.QToolBar(FluidNexus)
        self.FluidNexusToolbar.setObjectName(_fromUtf8("FluidNexusToolbar"))
        FluidNexus.addToolBar(QtCore.Qt.TopToolBarArea, self.FluidNexusToolbar)
        self.actionAbout = QtGui.QAction(FluidNexus)
        self.actionAbout.setIcon(icon)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionNewMessage = QtGui.QAction(FluidNexus)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/32x32/menu_add.png")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionNewMessage.setIcon(icon1)
        self.actionNewMessage.setObjectName(_fromUtf8("actionNewMessage"))
        self.actionQuit = QtGui.QAction(FluidNexus)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.actionPreferences = QtGui.QAction(FluidNexus)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/32x32/menu_preferences.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPreferences.setIcon(icon2)
        self.actionPreferences.setObjectName(_fromUtf8("actionPreferences"))
        self.actionViewAll = QtGui.QAction(FluidNexus)
        self.actionViewAll.setCheckable(True)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/32x32/menu_all.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionViewAll.setIcon(icon3)
        self.actionViewAll.setObjectName(_fromUtf8("actionViewAll"))
        self.actionViewOutgoing = QtGui.QAction(FluidNexus)
        self.actionViewOutgoing.setCheckable(True)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/32x32/menu_outgoing.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionViewOutgoing.setIcon(icon4)
        self.actionViewOutgoing.setObjectName(_fromUtf8("actionViewOutgoing"))
        self.actionViewBlacklist = QtGui.QAction(FluidNexus)
        self.actionViewBlacklist.setCheckable(True)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/32x32/menu_blacklist.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionViewBlacklist.setIcon(icon5)
        self.actionViewBlacklist.setObjectName(_fromUtf8("actionViewBlacklist"))
        self.actionViewPublic = QtGui.QAction(FluidNexus)
        self.actionViewPublic.setCheckable(True)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/32x32/menu_public_other.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionViewPublic.setIcon(icon6)
        self.actionViewPublic.setObjectName(_fromUtf8("actionViewPublic"))
        self.actionHelp = QtGui.QAction(FluidNexus)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/32x32/menu_help.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionHelp.setIcon(icon7)
        self.actionHelp.setObjectName(_fromUtf8("actionHelp"))
        self.menuFile.addAction(self.actionNewMessage)
        self.menuFile.addAction(self.actionPreferences)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuHelp.addAction(self.actionHelp)
        self.menuHelp.addAction(self.actionAbout)
        self.menu_View.addAction(self.actionViewAll)
        self.menu_View.addAction(self.actionViewPublic)
        self.menu_View.addAction(self.actionViewOutgoing)
        self.menu_View.addAction(self.actionViewBlacklist)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menu_View.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.FluidNexusToolbar.addAction(self.actionNewMessage)
        self.FluidNexusToolbar.addSeparator()
        self.FluidNexusToolbar.addAction(self.actionViewAll)
        self.FluidNexusToolbar.addAction(self.actionViewPublic)
        self.FluidNexusToolbar.addAction(self.actionViewOutgoing)
        self.FluidNexusToolbar.addAction(self.actionViewBlacklist)

        self.retranslateUi(FluidNexus)
        QtCore.QMetaObject.connectSlotsByName(FluidNexus)

    def retranslateUi(self, FluidNexus):
        FluidNexus.setWindowTitle(QtGui.QApplication.translate("FluidNexus", "Fluid Nexus", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("FluidNexus", "&File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setTitle(QtGui.QApplication.translate("FluidNexus", "&Help", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_View.setTitle(QtGui.QApplication.translate("FluidNexus", "&View", None, QtGui.QApplication.UnicodeUTF8))
        self.FluidNexusToolbar.setWindowTitle(QtGui.QApplication.translate("FluidNexus", "FluidNexusToolbar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setText(QtGui.QApplication.translate("FluidNexus", "&About FluidNexus...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNewMessage.setText(QtGui.QApplication.translate("FluidNexus", "&New Message...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNewMessage.setShortcut(QtGui.QApplication.translate("FluidNexus", "Ctrl+N", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setText(QtGui.QApplication.translate("FluidNexus", "&Quit...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setShortcut(QtGui.QApplication.translate("FluidNexus", "Ctrl+Q", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPreferences.setText(QtGui.QApplication.translate("FluidNexus", "&Preferences...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPreferences.setShortcut(QtGui.QApplication.translate("FluidNexus", "Ctrl+P", None, QtGui.QApplication.UnicodeUTF8))
        self.actionViewAll.setText(QtGui.QApplication.translate("FluidNexus", "View &All", None, QtGui.QApplication.UnicodeUTF8))
        self.actionViewAll.setToolTip(QtGui.QApplication.translate("FluidNexus", "View all messages", None, QtGui.QApplication.UnicodeUTF8))
        self.actionViewOutgoing.setText(QtGui.QApplication.translate("FluidNexus", "View &Outgoing", None, QtGui.QApplication.UnicodeUTF8))
        self.actionViewOutgoing.setToolTip(QtGui.QApplication.translate("FluidNexus", "View outgoing messages", None, QtGui.QApplication.UnicodeUTF8))
        self.actionViewBlacklist.setText(QtGui.QApplication.translate("FluidNexus", "View &Blacklist", None, QtGui.QApplication.UnicodeUTF8))
        self.actionViewBlacklist.setToolTip(QtGui.QApplication.translate("FluidNexus", "View blacklisted messages", None, QtGui.QApplication.UnicodeUTF8))
        self.actionViewPublic.setText(QtGui.QApplication.translate("FluidNexus", "View &Public", None, QtGui.QApplication.UnicodeUTF8))
        self.actionViewPublic.setToolTip(QtGui.QApplication.translate("FluidNexus", "View Public Messages", None, QtGui.QApplication.UnicodeUTF8))
        self.actionHelp.setText(QtGui.QApplication.translate("FluidNexus", "&Help", None, QtGui.QApplication.UnicodeUTF8))
        self.actionHelp.setToolTip(QtGui.QApplication.translate("FluidNexus", "Open the manual for Fluid Nexus", None, QtGui.QApplication.UnicodeUTF8))

import FluidNexus_rc
