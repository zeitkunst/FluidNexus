# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FluidNexus/ui/FluidNexusAbout.ui'
#
# Created: Tue Jul 26 14:41:28 2011
#      by: PyQt4 UI code generator 4.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_FluidNexusAbout(object):
    def setupUi(self, FluidNexusAbout):
        FluidNexusAbout.setObjectName(_fromUtf8("FluidNexusAbout"))
        FluidNexusAbout.resize(372, 533)
        self.buttonBox = QtGui.QDialogButtonBox(FluidNexusAbout)
        self.buttonBox.setGeometry(QtCore.QRect(20, 490, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayoutWidget = QtGui.QWidget(FluidNexusAbout)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 351, 470))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.AboutDialogIcon = QtGui.QLabel(self.verticalLayoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.AboutDialogIcon.sizePolicy().hasHeightForWidth())
        self.AboutDialogIcon.setSizePolicy(sizePolicy)
        self.AboutDialogIcon.setText(_fromUtf8(""))
        self.AboutDialogIcon.setPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/fluid_nexus_icon.png")))
        self.AboutDialogIcon.setObjectName(_fromUtf8("AboutDialogIcon"))
        self.horizontalLayout.addWidget(self.AboutDialogIcon)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.AboutDialogTitle = QtGui.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setWeight(75)
        font.setBold(True)
        self.AboutDialogTitle.setFont(font)
        self.AboutDialogTitle.setObjectName(_fromUtf8("AboutDialogTitle"))
        self.verticalLayout_2.addWidget(self.AboutDialogTitle)
        self.AboutDialogVersion = QtGui.QLabel(self.verticalLayoutWidget)
        self.AboutDialogVersion.setObjectName(_fromUtf8("AboutDialogVersion"))
        self.verticalLayout_2.addWidget(self.AboutDialogVersion)
        self.AboutDialogLink = QtGui.QLabel(self.verticalLayoutWidget)
        self.AboutDialogLink.setOpenExternalLinks(True)
        self.AboutDialogLink.setObjectName(_fromUtf8("AboutDialogLink"))
        self.verticalLayout_2.addWidget(self.AboutDialogLink)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tabWidget = QtGui.QTabWidget(self.verticalLayoutWidget)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.AboutDialogAboutTab = QtGui.QWidget()
        self.AboutDialogAboutTab.setObjectName(_fromUtf8("AboutDialogAboutTab"))
        self.AboutDialogAboutText = QtGui.QTextBrowser(self.AboutDialogAboutTab)
        self.AboutDialogAboutText.setGeometry(QtCore.QRect(10, 10, 311, 281))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.NoRole, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.NoRole, brush)
        brush = QtGui.QBrush(QtGui.QColor(244, 244, 244))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.NoRole, brush)
        self.AboutDialogAboutText.setPalette(palette)
        self.AboutDialogAboutText.setFrameShape(QtGui.QFrame.NoFrame)
        self.AboutDialogAboutText.setOpenExternalLinks(True)
        self.AboutDialogAboutText.setObjectName(_fromUtf8("AboutDialogAboutText"))
        self.tabWidget.addTab(self.AboutDialogAboutTab, _fromUtf8(""))
        self.AboutDialogCreditsTab = QtGui.QWidget()
        self.AboutDialogCreditsTab.setObjectName(_fromUtf8("AboutDialogCreditsTab"))
        self.AboutDialogCreditsText = QtGui.QTextBrowser(self.AboutDialogCreditsTab)
        self.AboutDialogCreditsText.setGeometry(QtCore.QRect(10, 10, 311, 281))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.NoRole, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.NoRole, brush)
        brush = QtGui.QBrush(QtGui.QColor(244, 244, 244))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.NoRole, brush)
        self.AboutDialogCreditsText.setPalette(palette)
        self.AboutDialogCreditsText.setFrameShape(QtGui.QFrame.NoFrame)
        self.AboutDialogCreditsText.setOpenExternalLinks(True)
        self.AboutDialogCreditsText.setObjectName(_fromUtf8("AboutDialogCreditsText"))
        self.tabWidget.addTab(self.AboutDialogCreditsTab, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)

        self.retranslateUi(FluidNexusAbout)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FluidNexusAbout.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FluidNexusAbout.reject)
        QtCore.QMetaObject.connectSlotsByName(FluidNexusAbout)

    def retranslateUi(self, FluidNexusAbout):
        FluidNexusAbout.setWindowTitle(QtGui.QApplication.translate("FluidNexusAbout", "About Fluid Nexus", None, QtGui.QApplication.UnicodeUTF8))
        self.AboutDialogTitle.setText(QtGui.QApplication.translate("FluidNexusAbout", "Fluid Nexus", None, QtGui.QApplication.UnicodeUTF8))
        self.AboutDialogVersion.setText(QtGui.QApplication.translate("FluidNexusAbout", "Version 0.1 Alpha", None, QtGui.QApplication.UnicodeUTF8))
        self.AboutDialogLink.setText(QtGui.QApplication.translate("FluidNexusAbout", "<a href=\"http://fluidnexus.net\">http://fluidnexus.net</a>", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.AboutDialogAboutTab), QtGui.QApplication.translate("FluidNexusAbout", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.AboutDialogCreditsTab), QtGui.QApplication.translate("FluidNexusAbout", "Credits", None, QtGui.QApplication.UnicodeUTF8))

import FluidNexus_rc
import FluidNexus_rc
import FluidNexus_rc
