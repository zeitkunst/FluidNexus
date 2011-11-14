# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FluidNexus/ui/FluidNexusHelp.ui'
#
# Created: Sun Nov 13 17:16:28 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_FluidNexusHelp(object):
    def setupUi(self, FluidNexusHelp):
        FluidNexusHelp.setObjectName(_fromUtf8("FluidNexusHelp"))
        FluidNexusHelp.resize(400, 573)
        self.buttonBox = QtGui.QDialogButtonBox(FluidNexusHelp)
        self.buttonBox.setGeometry(QtCore.QRect(40, 530, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.fluidNexusHelpBrowser = QtGui.QTextBrowser(FluidNexusHelp)
        self.fluidNexusHelpBrowser.setGeometry(QtCore.QRect(0, 0, 391, 521))
        self.fluidNexusHelpBrowser.setObjectName(_fromUtf8("fluidNexusHelpBrowser"))

        self.retranslateUi(FluidNexusHelp)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FluidNexusHelp.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FluidNexusHelp.reject)
        QtCore.QMetaObject.connectSlotsByName(FluidNexusHelp)

    def retranslateUi(self, FluidNexusHelp):
        FluidNexusHelp.setWindowTitle(QtGui.QApplication.translate("FluidNexusHelp", "Dialog", None, QtGui.QApplication.UnicodeUTF8))

