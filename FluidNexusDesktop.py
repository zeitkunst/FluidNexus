import md5
import sys
from PyQt4 import QtCore, QtGui
from ui.FluidNexusDesktopUI import Ui_FluidNexus
from ui.FluidNexusNewMessageUI import Ui_FluidNexusNewMessage
from database import FluidNexusDatabase

DEFAULTS = {
    "database": {
        "type": "pysqlite2",
        "name": "FluidNexus.db"
    }
}

class FluidNexusNewMessageDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.parent = parent

        self.ui = Ui_FluidNexusNewMessage()
        self.ui.setupUi(self)
        
        self.connect(self.ui.cancelButton, QtCore.SIGNAL("clicked()"), self.closeDialog)
        self.connect(self, QtCore.SIGNAL("saveButtonClicked"), self.parent.newMessageSaveButtonClicked)

    def closeDialog(self):
        self.close()

    def saveButtonClicked(self):
        print "save button clicked"
        self.emit(QtCore.SIGNAL("saveButtonClicked"), self.ui.newMessageTitle.text(), self.ui.newMessageBody.document().toPlainText())
        self.close()

class FluidNexusDesktop(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_FluidNexus()
        self.ui.setupUi(self)

        self.database = FluidNexusDatabase(databaseType = "pysqlite2")
        self.database.setupDatabase()
        self.setupView()

        self.statusBar().showMessage("Messages loaded.")
        
        self.settings = QtCore.QSettings("zeitkunst", "Fluid Nexus")
        
        self._setupSettings()

    def _setupSettings(self):
        self.settings.clear()

        for section in DEFAULTS.keys():
            for key in DEFAULTS[section].keys():
                name = section + "/" + key
                self.settings.setValue(name, DEFAULTS[section][key])


    def setupView(self):
        self.database.all()
        
        # column 6 is the hash
        for item in self.database:
            a = QtGui.QTreeWidgetItem(self.ui.incomingMessagesList)
            a.setText(0, item[6])
            a.setText(1, item[4])
            a.setText(2, item[5][0:20] + "...")

        self.ui.incomingMessagesList.hideColumn(0)
        
    def incomingMessageClicked(self):
        currentItem = self.ui.incomingMessagesList.currentItem()
        item = self.database.returnItemBasedOnHash(currentItem.data(0, 0).toString())
        te = self.ui.incomingMessageText
        te.clear()
        te.setPlainText(item[5])
    
    def showNewMessageWindow(self):
        self.newMessageDialog = FluidNexusNewMessageDialog(parent = self)
        self.newMessageDialog.exec_()

    def newMessageSaveButtonClicked(self, title, body):
        outgoing = QtGui.QTreeWidgetItem(self.ui.outgoingMessagesList)
        outgoing.setText(0, md5.md5(title + body).hexdigest())
        outgoing.setText(1, title)
        outgoing.setText(2, body[0:20] + "...")


if __name__ == "__main__":
    print "here"
    app = QtGui.QApplication(sys.argv)
    fluidNexus = FluidNexusDesktop()
    fluidNexus.show()
    sys.exit(app.exec_())

