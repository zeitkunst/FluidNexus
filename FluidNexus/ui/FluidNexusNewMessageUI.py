# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FluidNexus/ui/FluidNexusNewMessage.ui'
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

class Ui_FluidNexusNewMessage(object):
    def setupUi(self, FluidNexusNewMessage):
        FluidNexusNewMessage.setObjectName(_fromUtf8("FluidNexusNewMessage"))
        FluidNexusNewMessage.resize(384, 418)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/fluid_nexus_icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        FluidNexusNewMessage.setWindowIcon(icon)
        self.horizontalLayout = QtGui.QHBoxLayout(FluidNexusNewMessage)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.titleLabel = QtGui.QLabel(FluidNexusNewMessage)
        self.titleLabel.setMargin(0)
        self.titleLabel.setObjectName(_fromUtf8("titleLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.titleLabel)
        self.newMessageTitle = QtGui.QLineEdit(FluidNexusNewMessage)
        self.newMessageTitle.setObjectName(_fromUtf8("newMessageTitle"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.newMessageTitle)
        self.messageLabel = QtGui.QLabel(FluidNexusNewMessage)
        self.messageLabel.setMargin(0)
        self.messageLabel.setObjectName(_fromUtf8("messageLabel"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.messageLabel)
        self.newMessageBody = QtGui.QPlainTextEdit(FluidNexusNewMessage)
        self.newMessageBody.setObjectName(_fromUtf8("newMessageBody"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.newMessageBody)
        self.attachmentLabel = QtGui.QLabel(FluidNexusNewMessage)
        self.attachmentLabel.setObjectName(_fromUtf8("attachmentLabel"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.attachmentLabel)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.fileSelectionButton = QtGui.QPushButton(FluidNexusNewMessage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileSelectionButton.sizePolicy().hasHeightForWidth())
        self.fileSelectionButton.setSizePolicy(sizePolicy)
        self.fileSelectionButton.setObjectName(_fromUtf8("fileSelectionButton"))
        self.verticalLayout_3.addWidget(self.fileSelectionButton)
        self.fileRemoveButton = QtGui.QPushButton(FluidNexusNewMessage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileRemoveButton.sizePolicy().hasHeightForWidth())
        self.fileRemoveButton.setSizePolicy(sizePolicy)
        self.fileRemoveButton.setObjectName(_fromUtf8("fileRemoveButton"))
        self.verticalLayout_3.addWidget(self.fileRemoveButton)
        self.fileSelectedLabel = QtGui.QLabel(FluidNexusNewMessage)
        self.fileSelectedLabel.setMaximumSize(QtCore.QSize(300, 16777215))
        self.fileSelectedLabel.setText(_fromUtf8(""))
        self.fileSelectedLabel.setObjectName(_fromUtf8("fileSelectedLabel"))
        self.verticalLayout_3.addWidget(self.fileSelectedLabel)
        self.formLayout.setLayout(2, QtGui.QFormLayout.FieldRole, self.verticalLayout_3)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.formLayout.setItem(5, QtGui.QFormLayout.LabelRole, spacerItem)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.cancelButton = QtGui.QPushButton(FluidNexusNewMessage)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.horizontalLayout_3.addWidget(self.cancelButton)
        self.saveButton = QtGui.QPushButton(FluidNexusNewMessage)
        self.saveButton.setObjectName(_fromUtf8("saveButton"))
        self.horizontalLayout_3.addWidget(self.saveButton)
        self.formLayout.setLayout(5, QtGui.QFormLayout.FieldRole, self.horizontalLayout_3)
        self.nexusCheckBox = QtGui.QCheckBox(FluidNexusNewMessage)
        self.nexusCheckBox.setObjectName(_fromUtf8("nexusCheckBox"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.nexusCheckBox)
        self.priorityComboBox = QtGui.QComboBox(FluidNexusNewMessage)
        self.priorityComboBox.setObjectName(_fromUtf8("priorityComboBox"))
        self.priorityComboBox.addItem(_fromUtf8(""))
        self.priorityComboBox.addItem(_fromUtf8(""))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.priorityComboBox)
        self.priorityLabel = QtGui.QLabel(FluidNexusNewMessage)
        self.priorityLabel.setObjectName(_fromUtf8("priorityLabel"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.priorityLabel)
        self.horizontalLayout.addLayout(self.formLayout)
        self.titleLabel.setBuddy(self.newMessageTitle)
        self.messageLabel.setBuddy(self.newMessageBody)

        self.retranslateUi(FluidNexusNewMessage)
        QtCore.QObject.connect(self.saveButton, QtCore.SIGNAL(_fromUtf8("clicked()")), FluidNexusNewMessage.saveButtonClicked)
        QtCore.QObject.connect(self.priorityComboBox, QtCore.SIGNAL(_fromUtf8("activated(int)")), FluidNexusNewMessage.priorityChanged)
        QtCore.QMetaObject.connectSlotsByName(FluidNexusNewMessage)

    def retranslateUi(self, FluidNexusNewMessage):
        FluidNexusNewMessage.setWindowTitle(QtGui.QApplication.translate("FluidNexusNewMessage", "New Message", None, QtGui.QApplication.UnicodeUTF8))
        self.titleLabel.setText(QtGui.QApplication.translate("FluidNexusNewMessage", "&Title:", None, QtGui.QApplication.UnicodeUTF8))
        self.messageLabel.setText(QtGui.QApplication.translate("FluidNexusNewMessage", "&Message:", None, QtGui.QApplication.UnicodeUTF8))
        self.attachmentLabel.setText(QtGui.QApplication.translate("FluidNexusNewMessage", "Attachment:", None, QtGui.QApplication.UnicodeUTF8))
        self.fileSelectionButton.setText(QtGui.QApplication.translate("FluidNexusNewMessage", "Choose File...", None, QtGui.QApplication.UnicodeUTF8))
        self.fileRemoveButton.setText(QtGui.QApplication.translate("FluidNexusNewMessage", "Remove File", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("FluidNexusNewMessage", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.saveButton.setText(QtGui.QApplication.translate("FluidNexusNewMessage", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.nexusCheckBox.setText(QtGui.QApplication.translate("FluidNexusNewMessage", "Public (pust to Nexus?)", None, QtGui.QApplication.UnicodeUTF8))
        self.priorityComboBox.setItemText(0, QtGui.QApplication.translate("FluidNexusNewMessage", "Normal", "0", QtGui.QApplication.UnicodeUTF8))
        self.priorityComboBox.setItemText(1, QtGui.QApplication.translate("FluidNexusNewMessage", "High", "1", QtGui.QApplication.UnicodeUTF8))
        self.priorityLabel.setText(QtGui.QApplication.translate("FluidNexusNewMessage", "Priority:", None, QtGui.QApplication.UnicodeUTF8))

import FluidNexus_rc
