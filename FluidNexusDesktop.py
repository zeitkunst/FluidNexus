import sys
from PyQt4 import QtCore, QtGui
from ui.FluidNexusDesktopUI import Ui_FluidNexus
from database import FluidNexusDatabase

class StartQT4(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_FluidNexus()
        self.ui.setupUi(self)

        self.database = FluidNexusDatabase(databaseType = "pysqlite2")
        self.database.setupDatabase()
        self.setupView()

        self.statusBar().showMessage("Messages loaded.")

    def setupView(self):
        self.database.all()

        for item in self.database:
            a = QtGui.QTreeWidgetItem(self.ui.incomingMessagesList)
            a.setText(1, item[4])
            a.setText(2, item[5])

    def incomingMessageClicked(self):
        currentItem = self.ui.incomingMessagesList.currentItem()

        # HACK -- need better way of accessing items
        allItems = []
        self.database.all()
        for item in self.database:
            allItems.append(item)
        
        te = self.ui.incomingMessageText
        te.clear()
        te.setPlainText(currentItem.data(2, 0).toString())

if __name__ == "__main__":
    print "here"
    app = QtGui.QApplication(sys.argv)
    fluidNexus = StartQT4()
    fluidNexus.show()
    sys.exit(app.exec_())

