# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FluidNexus/ui/FluidNexusPreferences.ui'
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

class Ui_FluidNexusPreferences(object):
    def setupUi(self, FluidNexusPreferences):
        FluidNexusPreferences.setObjectName(_fromUtf8("FluidNexusPreferences"))
        FluidNexusPreferences.resize(452, 357)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/fluid_nexus_icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        FluidNexusPreferences.setWindowIcon(icon)
        self.buttonBox = QtGui.QDialogButtonBox(FluidNexusPreferences)
        self.buttonBox.setGeometry(QtCore.QRect(90, 310, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.FluidNexusPreferencesTabWidget = QtGui.QTabWidget(FluidNexusPreferences)
        self.FluidNexusPreferencesTabWidget.setEnabled(True)
        self.FluidNexusPreferencesTabWidget.setGeometry(QtCore.QRect(10, 10, 421, 291))
        self.FluidNexusPreferencesTabWidget.setObjectName(_fromUtf8("FluidNexusPreferencesTabWidget"))
        self.generalTab = QtGui.QWidget()
        self.generalTab.setObjectName(_fromUtf8("generalTab"))
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
        self.zeroconfCheckbox = QtGui.QCheckBox(self.formLayoutWidget)
        self.zeroconfCheckbox.setEnabled(False)
        self.zeroconfCheckbox.setObjectName(_fromUtf8("zeroconfCheckbox"))
        self.networkFormLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.zeroconfCheckbox)
        self.adhocCheckbox = QtGui.QCheckBox(self.formLayoutWidget)
        self.adhocCheckbox.setEnabled(False)
        self.adhocCheckbox.setObjectName(_fromUtf8("adhocCheckbox"))
        self.networkFormLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.adhocCheckbox)
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
        self.FluidNexusPreferencesTabWidget.addTab(self.zeroconfTab, _fromUtf8(""))
        self.adhocWifiTab = QtGui.QWidget()
        self.adhocWifiTab.setObjectName(_fromUtf8("adhocWifiTab"))
        self.FluidNexusPreferencesTabWidget.addTab(self.adhocWifiTab, _fromUtf8(""))

        self.retranslateUi(FluidNexusPreferences)
        self.FluidNexusPreferencesTabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FluidNexusPreferences.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FluidNexusPreferences.reject)
        QtCore.QObject.connect(self.bluetoothScanFrequency, QtCore.SIGNAL(_fromUtf8("activated(int)")), FluidNexusPreferences.bluetoothScanFrequencyChanged)
        QtCore.QObject.connect(self.bluetoothEnabled, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), FluidNexusPreferences.bluetoothChanged)
        QtCore.QMetaObject.connectSlotsByName(FluidNexusPreferences)

    def retranslateUi(self, FluidNexusPreferences):
        FluidNexusPreferences.setWindowTitle(QtGui.QApplication.translate("FluidNexusPreferences", "Fluid Nexus Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.FluidNexusPreferencesTabWidget.setTabText(self.FluidNexusPreferencesTabWidget.indexOf(self.generalTab), QtGui.QApplication.translate("FluidNexusPreferences", "General", None, QtGui.QApplication.UnicodeUTF8))
        self.bluetoothEnabled.setToolTip(QtGui.QApplication.translate("FluidNexusPreferences", "Whether or not the Bluetooth client/server is enabled", None, QtGui.QApplication.UnicodeUTF8))
        self.bluetoothEnabled.setText(QtGui.QApplication.translate("FluidNexusPreferences", "Bluetooth", None, QtGui.QApplication.UnicodeUTF8))
        self.zeroconfCheckbox.setText(QtGui.QApplication.translate("FluidNexusPreferences", "Zeroconf", None, QtGui.QApplication.UnicodeUTF8))
        self.adhocCheckbox.setText(QtGui.QApplication.translate("FluidNexusPreferences", "Ad-hoc Wifi", None, QtGui.QApplication.UnicodeUTF8))
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
        self.FluidNexusPreferencesTabWidget.setTabText(self.FluidNexusPreferencesTabWidget.indexOf(self.zeroconfTab), QtGui.QApplication.translate("FluidNexusPreferences", "Zeroconf", None, QtGui.QApplication.UnicodeUTF8))
        self.FluidNexusPreferencesTabWidget.setTabText(self.FluidNexusPreferencesTabWidget.indexOf(self.adhocWifiTab), QtGui.QApplication.translate("FluidNexusPreferences", "Ad-hoc Wifi", None, QtGui.QApplication.UnicodeUTF8))

import FluidNexus_rc
