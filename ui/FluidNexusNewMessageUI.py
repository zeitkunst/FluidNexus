# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FluidNexusNewMessage.ui'
#
# Created: Sun Oct 17 01:01:43 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_FluidNexusNewMessage(object):
    def setupUi(self, FluidNexusNewMessage):
        FluidNexusNewMessage.setObjectName("FluidNexusNewMessage")
        FluidNexusNewMessage.resize(384, 278)
        self.horizontalLayout = QtGui.QHBoxLayout(FluidNexusNewMessage)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.label = QtGui.QLabel(FluidNexusNewMessage)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.newMessageTitle = QtGui.QLineEdit(FluidNexusNewMessage)
        self.newMessageTitle.setObjectName("newMessageTitle")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.newMessageTitle)
        self.label_2 = QtGui.QLabel(FluidNexusNewMessage)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.newMessageBody = QtGui.QPlainTextEdit(FluidNexusNewMessage)
        self.newMessageBody.setObjectName("newMessageBody")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.newMessageBody)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.cancelButton = QtGui.QPushButton(FluidNexusNewMessage)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout_3.addWidget(self.cancelButton)
        self.saveButton = QtGui.QPushButton(FluidNexusNewMessage)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout_3.addWidget(self.saveButton)
        self.formLayout.setLayout(2, QtGui.QFormLayout.FieldRole, self.horizontalLayout_3)
        self.horizontalLayout.addLayout(self.formLayout)

        self.retranslateUi(FluidNexusNewMessage)
        QtCore.QObject.connect(self.saveButton, QtCore.SIGNAL("clicked()"), FluidNexusNewMessage.saveButtonClicked)
        QtCore.QMetaObject.connectSlotsByName(FluidNexusNewMessage)

    def retranslateUi(self, FluidNexusNewMessage):
        FluidNexusNewMessage.setWindowTitle(QtGui.QApplication.translate("FluidNexusNewMessage", "New Message", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("FluidNexusNewMessage", "Title", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("FluidNexusNewMessage", "Message", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("FluidNexusNewMessage", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.saveButton.setText(QtGui.QApplication.translate("FluidNexusNewMessage", "Save", None, QtGui.QApplication.UnicodeUTF8))

