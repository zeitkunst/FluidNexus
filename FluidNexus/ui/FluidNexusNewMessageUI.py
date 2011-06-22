# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FluidNexus/ui/FluidNexusNewMessage.ui'
#
# Created: Tue Jun 21 23:25:28 2011
#      by: PyQt4 UI code generator 4.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_FluidNexusNewMessage(object):
    def setupUi(self, FluidNexusNewMessage):
        FluidNexusNewMessage.setObjectName(_fromUtf8("FluidNexusNewMessage"))
        FluidNexusNewMessage.resize(384, 278)
        self.horizontalLayout = QtGui.QHBoxLayout(FluidNexusNewMessage)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(FluidNexusNewMessage)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.newMessageTitle = QtGui.QLineEdit(FluidNexusNewMessage)
        self.newMessageTitle.setObjectName(_fromUtf8("newMessageTitle"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.newMessageTitle)
        self.label_2 = QtGui.QLabel(FluidNexusNewMessage)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.newMessageBody = QtGui.QPlainTextEdit(FluidNexusNewMessage)
        self.newMessageBody.setObjectName(_fromUtf8("newMessageBody"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.newMessageBody)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.cancelButton = QtGui.QPushButton(FluidNexusNewMessage)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.horizontalLayout_3.addWidget(self.cancelButton)
        self.saveButton = QtGui.QPushButton(FluidNexusNewMessage)
        self.saveButton.setObjectName(_fromUtf8("saveButton"))
        self.horizontalLayout_3.addWidget(self.saveButton)
        self.formLayout.setLayout(2, QtGui.QFormLayout.FieldRole, self.horizontalLayout_3)
        self.horizontalLayout.addLayout(self.formLayout)
        self.label.setBuddy(self.newMessageTitle)
        self.label_2.setBuddy(self.newMessageBody)

        self.retranslateUi(FluidNexusNewMessage)
        QtCore.QObject.connect(self.saveButton, QtCore.SIGNAL(_fromUtf8("clicked()")), FluidNexusNewMessage.saveButtonClicked)
        QtCore.QMetaObject.connectSlotsByName(FluidNexusNewMessage)

    def retranslateUi(self, FluidNexusNewMessage):
        FluidNexusNewMessage.setWindowTitle(QtGui.QApplication.translate("FluidNexusNewMessage", "New Message", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("FluidNexusNewMessage", "&Title", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("FluidNexusNewMessage", "&Message", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("FluidNexusNewMessage", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.saveButton.setText(QtGui.QApplication.translate("FluidNexusNewMessage", "Save", None, QtGui.QApplication.UnicodeUTF8))

