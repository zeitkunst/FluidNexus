# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FluidNexus/ui/FluidNexusDesktop.ui'
#
# Created: Mon Jun 20 15:14:25 2011
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
        FluidNexus.resize(388, 645)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/fluid_nexus_icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        FluidNexus.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(FluidNexus)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.FluidNexusTabWidget = QtGui.QTabWidget(self.centralwidget)
        self.FluidNexusTabWidget.setGeometry(QtCore.QRect(0, 0, 381, 591))
        self.FluidNexusTabWidget.setObjectName(_fromUtf8("FluidNexusTabWidget"))
        self.MessagesTab = QtGui.QWidget()
        self.MessagesTab.setObjectName(_fromUtf8("MessagesTab"))
        self.FluidNexusScrollArea = QtGui.QScrollArea(self.MessagesTab)
        self.FluidNexusScrollArea.setGeometry(QtCore.QRect(-1, -1, 371, 551))
        self.FluidNexusScrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.FluidNexusScrollArea.setWidgetResizable(True)
        self.FluidNexusScrollArea.setObjectName(_fromUtf8("FluidNexusScrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget(self.FluidNexusScrollArea)
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.FluidNexusScrollArea.setWidget(self.scrollAreaWidgetContents)
        self.FluidNexusTabWidget.addTab(self.MessagesTab, _fromUtf8(""))
        self.CreateMessageTab = QtGui.QWidget()
        self.CreateMessageTab.setObjectName(_fromUtf8("CreateMessageTab"))
        self.FluidNexusTabWidget.addTab(self.CreateMessageTab, _fromUtf8(""))
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
        self.actionAbout = QtGui.QAction(FluidNexus)
        self.actionAbout.setIcon(icon)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(FluidNexus)
        self.FluidNexusTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(FluidNexus)

    def retranslateUi(self, FluidNexus):
        FluidNexus.setWindowTitle(QtGui.QApplication.translate("FluidNexus", "Fluid Nexus", None, QtGui.QApplication.UnicodeUTF8))
        self.FluidNexusTabWidget.setTabText(self.FluidNexusTabWidget.indexOf(self.MessagesTab), QtGui.QApplication.translate("FluidNexus", "Messages", None, QtGui.QApplication.UnicodeUTF8))
        self.FluidNexusTabWidget.setTabText(self.FluidNexusTabWidget.indexOf(self.CreateMessageTab), QtGui.QApplication.translate("FluidNexus", "Create Message", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("FluidNexus", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setTitle(QtGui.QApplication.translate("FluidNexus", "Help", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setText(QtGui.QApplication.translate("FluidNexus", "About FluidNexus...", None, QtGui.QApplication.UnicodeUTF8))

import FluidNexus_rc
