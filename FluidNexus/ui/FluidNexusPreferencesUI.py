# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FluidNexus/ui/FluidNexusPreferences.ui'
#
# Created: Sun Jul 24 12:31:05 2011
#      by: PyQt4 UI code generator 4.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_FluidNexusPreferences(object):
    def setupUi(self, FluidNexusPreferences):
        FluidNexusPreferences.setObjectName(_fromUtf8("FluidNexusPreferences"))
        FluidNexusPreferences.resize(501, 350)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/fluid_nexus_icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        FluidNexusPreferences.setWindowIcon(icon)
        self.buttonBox = QtGui.QDialogButtonBox(FluidNexusPreferences)
        self.buttonBox.setGeometry(QtCore.QRect(150, 310, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.FluidNexusPreferencesTabWidget = QtGui.QTabWidget(FluidNexusPreferences)
        self.FluidNexusPreferencesTabWidget.setEnabled(True)
        self.FluidNexusPreferencesTabWidget.setGeometry(QtCore.QRect(10, 10, 481, 291))
        self.FluidNexusPreferencesTabWidget.setObjectName(_fromUtf8("FluidNexusPreferencesTabWidget"))
        self.generalTab = QtGui.QWidget()
        self.generalTab.setObjectName(_fromUtf8("generalTab"))
        self.sendBlacklistedMessagesCheckbox = QtGui.QCheckBox(self.generalTab)
        self.sendBlacklistedMessagesCheckbox.setEnabled(False)
        self.sendBlacklistedMessagesCheckbox.setGeometry(QtCore.QRect(10, 10, 221, 21))
        self.sendBlacklistedMessagesCheckbox.setObjectName(_fromUtf8("sendBlacklistedMessagesCheckbox"))
        self.ttlSpinBox = QtGui.QSpinBox(self.generalTab)
        self.ttlSpinBox.setGeometry(QtCore.QRect(10, 40, 56, 26))
        self.ttlSpinBox.setProperty(_fromUtf8("value"), 30)
        self.ttlSpinBox.setObjectName(_fromUtf8("ttlSpinBox"))
        self.ttlLabel = QtGui.QLabel(self.generalTab)
        self.ttlLabel.setGeometry(QtCore.QRect(70, 40, 81, 31))
        self.ttlLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.ttlLabel.setObjectName(_fromUtf8("ttlLabel"))
        self.FluidNexusPreferencesTabWidget.addTab(self.generalTab, _fromUtf8(""))
        self.networkTab = QtGui.QWidget()
        self.networkTab.setObjectName(_fromUtf8("networkTab"))
        self.formLayoutWidget = QtGui.QWidget(self.networkTab)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 10, 393, 231))
        self.formLayoutWidget.setObjectName(_fromUtf8("formLayoutWidget"))
        self.networkFormLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.networkFormLayout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.networkFormLayout.setObjectName(_fromUtf8("networkFormLayout"))
        self.bluetoothEnabled = QtGui.QCheckBox(self.formLayoutWidget)
        self.bluetoothEnabled.setObjectName(_fromUtf8("bluetoothEnabled"))
        self.networkFormLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.bluetoothEnabled)
        self.zeroconfEnabled = QtGui.QCheckBox(self.formLayoutWidget)
        self.zeroconfEnabled.setEnabled(True)
        self.zeroconfEnabled.setObjectName(_fromUtf8("zeroconfEnabled"))
        self.networkFormLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.zeroconfEnabled)
        self.adhocEnabled = QtGui.QCheckBox(self.formLayoutWidget)
        self.adhocEnabled.setEnabled(False)
        self.adhocEnabled.setObjectName(_fromUtf8("adhocEnabled"))
        self.networkFormLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.adhocEnabled)
        self.networkInfo = QtGui.QPlainTextEdit(self.formLayoutWidget)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(244, 244, 244))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        self.networkInfo.setPalette(palette)
        self.networkInfo.setFrameShape(QtGui.QFrame.NoFrame)
        self.networkInfo.setFrameShadow(QtGui.QFrame.Plain)
        self.networkInfo.setObjectName(_fromUtf8("networkInfo"))
        self.networkFormLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.networkInfo)
        self.FluidNexusPreferencesTabWidget.addTab(self.networkTab, _fromUtf8(""))
        self.bluetoothTab = QtGui.QWidget()
        self.bluetoothTab.setObjectName(_fromUtf8("bluetoothTab"))
        self.formLayoutWidget_2 = QtGui.QWidget(self.bluetoothTab)
        self.formLayoutWidget_2.setGeometry(QtCore.QRect(9, 9, 391, 241))
        self.formLayoutWidget_2.setObjectName(_fromUtf8("formLayoutWidget_2"))
        self.formLayout = QtGui.QFormLayout(self.formLayoutWidget_2)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.scanFrequencyLabel = QtGui.QLabel(self.formLayoutWidget_2)
        self.scanFrequencyLabel.setObjectName(_fromUtf8("scanFrequencyLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.scanFrequencyLabel)
        self.bluetoothScanFrequency = QtGui.QComboBox(self.formLayoutWidget_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bluetoothScanFrequency.sizePolicy().hasHeightForWidth())
        self.bluetoothScanFrequency.setSizePolicy(sizePolicy)
        self.bluetoothScanFrequency.setObjectName(_fromUtf8("bluetoothScanFrequency"))
        self.bluetoothScanFrequency.addItem(_fromUtf8(""))
        self.bluetoothScanFrequency.addItem(_fromUtf8(""))
        self.bluetoothScanFrequency.addItem(_fromUtf8(""))
        self.bluetoothScanFrequency.addItem(_fromUtf8(""))
        self.bluetoothScanFrequency.addItem(_fromUtf8(""))
        self.bluetoothScanFrequency.addItem(_fromUtf8(""))
        self.bluetoothScanFrequency.addItem(_fromUtf8(""))
        self.bluetoothScanFrequency.addItem(_fromUtf8(""))
        self.bluetoothScanFrequency.addItem(_fromUtf8(""))
        self.bluetoothScanFrequency.addItem(_fromUtf8(""))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.bluetoothScanFrequency)
        self.FluidNexusPreferencesTabWidget.addTab(self.bluetoothTab, _fromUtf8(""))
        self.zeroconfTab = QtGui.QWidget()
        self.zeroconfTab.setObjectName(_fromUtf8("zeroconfTab"))
        self.formLayoutWidget_3 = QtGui.QWidget(self.zeroconfTab)
        self.formLayoutWidget_3.setGeometry(QtCore.QRect(9, 9, 391, 241))
        self.formLayoutWidget_3.setObjectName(_fromUtf8("formLayoutWidget_3"))
        self.formLayout_2 = QtGui.QFormLayout(self.formLayoutWidget_3)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.zeroconfScanFrequencyLabel = QtGui.QLabel(self.formLayoutWidget_3)
        self.zeroconfScanFrequencyLabel.setObjectName(_fromUtf8("zeroconfScanFrequencyLabel"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.zeroconfScanFrequencyLabel)
        self.zeroconfScanFrequency = QtGui.QComboBox(self.formLayoutWidget_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.zeroconfScanFrequency.sizePolicy().hasHeightForWidth())
        self.zeroconfScanFrequency.setSizePolicy(sizePolicy)
        self.zeroconfScanFrequency.setObjectName(_fromUtf8("zeroconfScanFrequency"))
        self.zeroconfScanFrequency.addItem(_fromUtf8(""))
        self.zeroconfScanFrequency.addItem(_fromUtf8(""))
        self.zeroconfScanFrequency.addItem(_fromUtf8(""))
        self.zeroconfScanFrequency.addItem(_fromUtf8(""))
        self.zeroconfScanFrequency.addItem(_fromUtf8(""))
        self.zeroconfScanFrequency.addItem(_fromUtf8(""))
        self.zeroconfScanFrequency.addItem(_fromUtf8(""))
        self.zeroconfScanFrequency.addItem(_fromUtf8(""))
        self.zeroconfScanFrequency.addItem(_fromUtf8(""))
        self.zeroconfScanFrequency.addItem(_fromUtf8(""))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.zeroconfScanFrequency)
        self.FluidNexusPreferencesTabWidget.addTab(self.zeroconfTab, _fromUtf8(""))
        self.adhocWifiTab = QtGui.QWidget()
        self.adhocWifiTab.setObjectName(_fromUtf8("adhocWifiTab"))
        self.FluidNexusPreferencesTabWidget.addTab(self.adhocWifiTab, _fromUtf8(""))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.formLayoutWidget_4 = QtGui.QWidget(self.tab)
        self.formLayoutWidget_4.setGeometry(QtCore.QRect(10, 10, 451, 241))
        self.formLayoutWidget_4.setObjectName(_fromUtf8("formLayoutWidget_4"))
        self.formLayout_3 = QtGui.QFormLayout(self.formLayoutWidget_4)
        self.formLayout_3.setObjectName(_fromUtf8("formLayout_3"))
        self.keyLabel = QtGui.QLabel(self.formLayoutWidget_4)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.keyLabel.sizePolicy().hasHeightForWidth())
        self.keyLabel.setSizePolicy(sizePolicy)
        self.keyLabel.setObjectName(_fromUtf8("keyLabel"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.LabelRole, self.keyLabel)
        self.keyInput = QtGui.QLineEdit(self.formLayoutWidget_4)
        self.keyInput.setMaxLength(20)
        self.keyInput.setObjectName(_fromUtf8("keyInput"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.FieldRole, self.keyInput)
        self.secretLabel = QtGui.QLabel(self.formLayoutWidget_4)
        self.secretLabel.setObjectName(_fromUtf8("secretLabel"))
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.LabelRole, self.secretLabel)
        self.secretInput = QtGui.QLineEdit(self.formLayoutWidget_4)
        self.secretInput.setMaxLength(20)
        self.secretInput.setObjectName(_fromUtf8("secretInput"))
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.FieldRole, self.secretInput)
        self.generateRequestTokenButton = QtGui.QPushButton(self.formLayoutWidget_4)
        self.generateRequestTokenButton.setObjectName(_fromUtf8("generateRequestTokenButton"))
        self.formLayout_3.setWidget(2, QtGui.QFormLayout.FieldRole, self.generateRequestTokenButton)
        self.noteLabel = QtGui.QLabel(self.formLayoutWidget_4)
        self.noteLabel.setEnabled(False)
        self.noteLabel.setObjectName(_fromUtf8("noteLabel"))
        self.formLayout_3.setWidget(3, QtGui.QFormLayout.FieldRole, self.noteLabel)
        self.tokenLabel = QtGui.QLabel(self.formLayoutWidget_4)
        self.tokenLabel.setEnabled(False)
        self.tokenLabel.setObjectName(_fromUtf8("tokenLabel"))
        self.formLayout_3.setWidget(4, QtGui.QFormLayout.LabelRole, self.tokenLabel)
        self.tokenInput = QtGui.QLineEdit(self.formLayoutWidget_4)
        self.tokenInput.setEnabled(False)
        self.tokenInput.setObjectName(_fromUtf8("tokenInput"))
        self.formLayout_3.setWidget(4, QtGui.QFormLayout.FieldRole, self.tokenInput)
        self.tokenSecretLabel = QtGui.QLabel(self.formLayoutWidget_4)
        self.tokenSecretLabel.setEnabled(False)
        self.tokenSecretLabel.setObjectName(_fromUtf8("tokenSecretLabel"))
        self.formLayout_3.setWidget(5, QtGui.QFormLayout.LabelRole, self.tokenSecretLabel)
        self.tokenSecretInput = QtGui.QLineEdit(self.formLayoutWidget_4)
        self.tokenSecretInput.setEnabled(False)
        self.tokenSecretInput.setObjectName(_fromUtf8("tokenSecretInput"))
        self.formLayout_3.setWidget(5, QtGui.QFormLayout.FieldRole, self.tokenSecretInput)
        self.FluidNexusPreferencesTabWidget.addTab(self.tab, _fromUtf8(""))

        self.retranslateUi(FluidNexusPreferences)
        self.FluidNexusPreferencesTabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FluidNexusPreferences.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FluidNexusPreferences.reject)
        QtCore.QObject.connect(self.bluetoothScanFrequency, QtCore.SIGNAL(_fromUtf8("activated(int)")), FluidNexusPreferences.bluetoothScanFrequencyChanged)
        QtCore.QObject.connect(self.bluetoothEnabled, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), FluidNexusPreferences.bluetoothChanged)
        QtCore.QObject.connect(self.zeroconfEnabled, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), FluidNexusPreferences.zeroconfChanged)
        QtCore.QObject.connect(self.zeroconfScanFrequency, QtCore.SIGNAL(_fromUtf8("activated(int)")), FluidNexusPreferences.zeroconfScanFrequencyChanged)
        QtCore.QObject.connect(self.keyInput, QtCore.SIGNAL(_fromUtf8("editingFinished()")), FluidNexusPreferences.nexusKeyFinished)
        QtCore.QObject.connect(self.secretInput, QtCore.SIGNAL(_fromUtf8("editingFinished()")), FluidNexusPreferences.nexusSecretFinished)
        QtCore.QObject.connect(self.generateRequestTokenButton, QtCore.SIGNAL(_fromUtf8("clicked()")), FluidNexusPreferences.onRequestAuthorization)
        QtCore.QObject.connect(self.ttlSpinBox, QtCore.SIGNAL(_fromUtf8("editingFinished()")), FluidNexusPreferences.ttlFinished)
        QtCore.QMetaObject.connectSlotsByName(FluidNexusPreferences)

    def retranslateUi(self, FluidNexusPreferences):
        FluidNexusPreferences.setWindowTitle(QtGui.QApplication.translate("FluidNexusPreferences", "Fluid Nexus Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.sendBlacklistedMessagesCheckbox.setText(QtGui.QApplication.translate("FluidNexusPreferences", "Send blacklisted messages?", None, QtGui.QApplication.UnicodeUTF8))
        self.ttlSpinBox.setToolTip(QtGui.QApplication.translate("FluidNexusPreferences", "Default Time to Live (TTL), or the maximum number of \"hops\" allowed for a public message to attempt to be posted to the Nexus.", None, QtGui.QApplication.UnicodeUTF8))
        self.ttlLabel.setText(QtGui.QApplication.translate("FluidNexusPreferences", "Default TTL", None, QtGui.QApplication.UnicodeUTF8))
        self.FluidNexusPreferencesTabWidget.setTabText(self.FluidNexusPreferencesTabWidget.indexOf(self.generalTab), QtGui.QApplication.translate("FluidNexusPreferences", "General", None, QtGui.QApplication.UnicodeUTF8))
        self.bluetoothEnabled.setToolTip(QtGui.QApplication.translate("FluidNexusPreferences", "Whether or not the Bluetooth client/server is enabled", None, QtGui.QApplication.UnicodeUTF8))
        self.bluetoothEnabled.setText(QtGui.QApplication.translate("FluidNexusPreferences", "Bluetooth", None, QtGui.QApplication.UnicodeUTF8))
        self.zeroconfEnabled.setText(QtGui.QApplication.translate("FluidNexusPreferences", "Zeroconf", None, QtGui.QApplication.UnicodeUTF8))
        self.adhocEnabled.setText(QtGui.QApplication.translate("FluidNexusPreferences", "Ad-hoc Wifi", None, QtGui.QApplication.UnicodeUTF8))
        self.networkInfo.setPlainText(QtGui.QApplication.translate("FluidNexusPreferences", "If you make changes to these values you must restart the program for the changes to take effect.", None, QtGui.QApplication.UnicodeUTF8))
        self.FluidNexusPreferencesTabWidget.setTabText(self.FluidNexusPreferencesTabWidget.indexOf(self.networkTab), QtGui.QApplication.translate("FluidNexusPreferences", "Network", None, QtGui.QApplication.UnicodeUTF8))
        self.scanFrequencyLabel.setText(QtGui.QApplication.translate("FluidNexusPreferences", "Scan Frequency:", None, QtGui.QApplication.UnicodeUTF8))
        self.bluetoothScanFrequency.setToolTip(QtGui.QApplication.translate("FluidNexusPreferences", "How often to scan for nearby devices.  Lower values will severely impact battery life.", None, QtGui.QApplication.UnicodeUTF8))
        self.bluetoothScanFrequency.setItemText(0, QtGui.QApplication.translate("FluidNexusPreferences", "5 seconds", None, QtGui.QApplication.UnicodeUTF8))
        self.bluetoothScanFrequency.setItemText(1, QtGui.QApplication.translate("FluidNexusPreferences", "10 seconds", None, QtGui.QApplication.UnicodeUTF8))
        self.bluetoothScanFrequency.setItemText(2, QtGui.QApplication.translate("FluidNexusPreferences", "30 seconds", None, QtGui.QApplication.UnicodeUTF8))
        self.bluetoothScanFrequency.setItemText(3, QtGui.QApplication.translate("FluidNexusPreferences", "1 minute", None, QtGui.QApplication.UnicodeUTF8))
        self.bluetoothScanFrequency.setItemText(4, QtGui.QApplication.translate("FluidNexusPreferences", "2 minutes", None, QtGui.QApplication.UnicodeUTF8))
        self.bluetoothScanFrequency.setItemText(5, QtGui.QApplication.translate("FluidNexusPreferences", "5 minutes", None, QtGui.QApplication.UnicodeUTF8))
        self.bluetoothScanFrequency.setItemText(6, QtGui.QApplication.translate("FluidNexusPreferences", "10 minutes", None, QtGui.QApplication.UnicodeUTF8))
        self.bluetoothScanFrequency.setItemText(7, QtGui.QApplication.translate("FluidNexusPreferences", "20 minutes", None, QtGui.QApplication.UnicodeUTF8))
        self.bluetoothScanFrequency.setItemText(8, QtGui.QApplication.translate("FluidNexusPreferences", "30 minutes", None, QtGui.QApplication.UnicodeUTF8))
        self.bluetoothScanFrequency.setItemText(9, QtGui.QApplication.translate("FluidNexusPreferences", "1 hour", None, QtGui.QApplication.UnicodeUTF8))
        self.FluidNexusPreferencesTabWidget.setTabText(self.FluidNexusPreferencesTabWidget.indexOf(self.bluetoothTab), QtGui.QApplication.translate("FluidNexusPreferences", "Bluetooth", None, QtGui.QApplication.UnicodeUTF8))
        self.zeroconfScanFrequencyLabel.setText(QtGui.QApplication.translate("FluidNexusPreferences", "Scan Frequency:", None, QtGui.QApplication.UnicodeUTF8))
        self.zeroconfScanFrequency.setToolTip(QtGui.QApplication.translate("FluidNexusPreferences", "How often to scan for nearby devices.  Lower values will severely impact battery life.", None, QtGui.QApplication.UnicodeUTF8))
        self.zeroconfScanFrequency.setItemText(0, QtGui.QApplication.translate("FluidNexusPreferences", "5 seconds", None, QtGui.QApplication.UnicodeUTF8))
        self.zeroconfScanFrequency.setItemText(1, QtGui.QApplication.translate("FluidNexusPreferences", "10 seconds", None, QtGui.QApplication.UnicodeUTF8))
        self.zeroconfScanFrequency.setItemText(2, QtGui.QApplication.translate("FluidNexusPreferences", "30 seconds", None, QtGui.QApplication.UnicodeUTF8))
        self.zeroconfScanFrequency.setItemText(3, QtGui.QApplication.translate("FluidNexusPreferences", "1 minute", None, QtGui.QApplication.UnicodeUTF8))
        self.zeroconfScanFrequency.setItemText(4, QtGui.QApplication.translate("FluidNexusPreferences", "2 minutes", None, QtGui.QApplication.UnicodeUTF8))
        self.zeroconfScanFrequency.setItemText(5, QtGui.QApplication.translate("FluidNexusPreferences", "5 minutes", None, QtGui.QApplication.UnicodeUTF8))
        self.zeroconfScanFrequency.setItemText(6, QtGui.QApplication.translate("FluidNexusPreferences", "10 minutes", None, QtGui.QApplication.UnicodeUTF8))
        self.zeroconfScanFrequency.setItemText(7, QtGui.QApplication.translate("FluidNexusPreferences", "20 minutes", None, QtGui.QApplication.UnicodeUTF8))
        self.zeroconfScanFrequency.setItemText(8, QtGui.QApplication.translate("FluidNexusPreferences", "30 minutes", None, QtGui.QApplication.UnicodeUTF8))
        self.zeroconfScanFrequency.setItemText(9, QtGui.QApplication.translate("FluidNexusPreferences", "1 hour", None, QtGui.QApplication.UnicodeUTF8))
        self.FluidNexusPreferencesTabWidget.setTabText(self.FluidNexusPreferencesTabWidget.indexOf(self.zeroconfTab), QtGui.QApplication.translate("FluidNexusPreferences", "Zeroconf", None, QtGui.QApplication.UnicodeUTF8))
        self.FluidNexusPreferencesTabWidget.setTabText(self.FluidNexusPreferencesTabWidget.indexOf(self.adhocWifiTab), QtGui.QApplication.translate("FluidNexusPreferences", "Ad-hoc Wifi", None, QtGui.QApplication.UnicodeUTF8))
        self.keyLabel.setText(QtGui.QApplication.translate("FluidNexusPreferences", "Key:", None, QtGui.QApplication.UnicodeUTF8))
        self.secretLabel.setText(QtGui.QApplication.translate("FluidNexusPreferences", "Secret:", None, QtGui.QApplication.UnicodeUTF8))
        self.generateRequestTokenButton.setText(QtGui.QApplication.translate("FluidNexusPreferences", "Request Authorization", None, QtGui.QApplication.UnicodeUTF8))
        self.noteLabel.setText(QtGui.QApplication.translate("FluidNexusPreferences", "The values below should not need to be changed. ", None, QtGui.QApplication.UnicodeUTF8))
        self.tokenLabel.setText(QtGui.QApplication.translate("FluidNexusPreferences", "Token: ", None, QtGui.QApplication.UnicodeUTF8))
        self.tokenSecretLabel.setText(QtGui.QApplication.translate("FluidNexusPreferences", "Token Secret: ", None, QtGui.QApplication.UnicodeUTF8))
        self.FluidNexusPreferencesTabWidget.setTabText(self.FluidNexusPreferencesTabWidget.indexOf(self.tab), QtGui.QApplication.translate("FluidNexusPreferences", "Nexus", None, QtGui.QApplication.UnicodeUTF8))

import FluidNexus_rc
