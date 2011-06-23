# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FluidNexus/ui/FluidNexusDesktop.ui'
#
# Created: Thu Jun 23 01:17:04 2011
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
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.FluidNexusScrollArea = QtGui.QScrollArea(self.centralwidget)
        self.FluidNexusScrollArea.setGeometry(QtCore.QRect(0, 0, 380, 563))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.FluidNexusScrollArea.sizePolicy().hasHeightForWidth())
        self.FluidNexusScrollArea.setSizePolicy(sizePolicy)
        self.FluidNexusScrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.FluidNexusScrollArea.setWidgetResizable(False)
        self.FluidNexusScrollArea.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.FluidNexusScrollArea.setObjectName(_fromUtf8("FluidNexusScrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget(self.FluidNexusScrollArea)
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 374, 557))
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
        self.actionPreferences.setObjectName(_fromUtf8("actionPreferences"))
        self.menuFile.addAction(self.actionNewMessage)
        self.menuFile.addAction(self.actionPreferences)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.FluidNexusToolbar.addAction(self.actionNewMessage)

        self.retranslateUi(FluidNexus)
        QtCore.QMetaObject.connectSlotsByName(FluidNexus)

    def retranslateUi(self, FluidNexus):
        FluidNexus.setWindowTitle(QtGui.QApplication.translate("FluidNexus", "Fluid Nexus", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("FluidNexus", "&File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setTitle(QtGui.QApplication.translate("FluidNexus", "&Help", None, QtGui.QApplication.UnicodeUTF8))
        self.FluidNexusToolbar.setWindowTitle(QtGui.QApplication.translate("FluidNexus", "FluidNexusToolbar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setText(QtGui.QApplication.translate("FluidNexus", "&About FluidNexus...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNewMessage.setText(QtGui.QApplication.translate("FluidNexus", "&New Message...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNewMessage.setShortcut(QtGui.QApplication.translate("FluidNexus", "Ctrl+N", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setText(QtGui.QApplication.translate("FluidNexus", "&Quit...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setShortcut(QtGui.QApplication.translate("FluidNexus", "Ctrl+Q", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPreferences.setText(QtGui.QApplication.translate("FluidNexus", "&Preferences...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPreferences.setShortcut(QtGui.QApplication.translate("FluidNexus", "Ctrl+P", None, QtGui.QApplication.UnicodeUTF8))

import FluidNexus_rc
