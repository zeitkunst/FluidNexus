# Standard library imports
import thread
import socket
import sys
import os
import md5

# @HACK@
# Adding paths to find the modules
sys.path.append('.')
sys.path.append(os.getcwd())
sys.path.append('E:\\System\\Apps\\Python\\my\\')
sys.path.append('C:\\Python')
sys.path.append('E:\\Python')

from logger import Logger
from database import FluidNexusDatabase

# Series 60 specific imports
try:
    # On phone?
    import appuifw
    import e32
    import e32db
    import graphics

    # @SEMI-HACK@
    # At the moment, set global variable that determines where our data is      going to live
    availableDrives = e32.drive_list()
    if 'E:' in availableDrives:
        dataPath = u'E:\\System\\Data\\FluidNexusData'
    else:
        dataPath = u'C:\\System\\Data\\FluidNexusData'

    # Setup our data path
    if not os.path.isdir(dataPath):
        os.makedirs(dataPath)

    # Setup logging and redirect standard input and output
    log = Logger(dataPath + u'\\FluidNexus.log', prefix = 'FluidNexus UI: ')
    sys.stderr = sys.stdout = log

    onPhone = True
except ImportError:
    from s60Compat import appuifw
    from s60Compat import e32
    dataPath = '.'
    log = Logger(dataPath + u'\\FluidNexus.log', prefix = 'FluidNexusServer: ')
    sys.stderr = sys.stdout = log

    onPhone = False

views = []

# @TODO@
# Add in new tables: 
# * One that keeps track of the hashes that we're currently advertising on the services
# * One that keeps track of inputed data that we're wanting to send out

# For the database we should have the following table:
# FluidNexus
# with columns:
# id counter
# source varchar(18)
# time timestamp
# type integer
# title varchar(40)
# data long varchar
# hash varchar(32)
#
#create table FluidNexus (id counter, source varchar(18), time timestamp, type integer, title varchar(40), data long varchar)

# For the release we will get right of source and time (because we don't want tracking)
# Type is: text = 0, image, audio, video
# for type values > 0, the data value will be a path to the file
# files should be kept under the databaseDir directory


class FluidNexusClientThread:
    """This thread searches for open bluetooth services of the correct type and tries to send appropriate messages to them.

    @TODO@  Need better description, name."""

    def __init__(self):
        self.lock = thread.allocate_lock()
        self.counter = 0

    def run(self):
        # Dummy run program for right now
        while 1:
            self.lock.acquire()
            e32.ao_sleep(1)
            print "client thread %d" % self.counter
            self.counter += 1
            self.lock.release()

class FluidNexusServerThread:
    """This thread accepts connections and appropriate data.

    @TODO@ Need better description, name."""


    def __init__(self, serviceName = u'FluidNexus'):
        self.lock = thread.allocate_lock()
        self.counter = 0

        self.serviceName = serviceName
        self.serverSocket = socket.socket(socket.AF_BT, socket.SOCK_STREAM)
        self.serverPort = socket.bt_rfcomm_get_available_server_channel(self.   serverSocket)
        self.serverSocket.bind(("", self.serverPort))

        socket.set_security(self.serverSocket,
                            socket.AUTH)

        # Only listen for one connection
        self.serverSocket.listen(1)

        # Advertise my service
        socket.bt_advertise_service(serviceName,
                                    self.serverSocket,
                                    True,
                                    socket.RFCOMM)
        self.serverSocket.setblocking(False)

    def acceptCallback(self, clientSocket, clientAddress):
        print "in accept callback"
        print clientAddress
        clientSocket.close()

    def run(self):
        # Dummy run program for right now
        while 1:
            self.lock.acquire()
            e32.ao_sleep(1)
            print 'before accept'
            clientSocket, clientAddress = self.serverSocket.accept()
            print 'after accept'
            print clientAddress
            print "server thread %d" % self.counter
            self.counter += 1
            clientSocket.close()
            self.lock.release()

class ViewBase:

    def __init__(self):
        pass

    def pushView(self, view):
        global views
        views.append(view)

    def popView(self):
        global views
        if len(views) - 1 > 0:
            views.pop()
            self.show()

    def show(self):
        global views
        if len(views) > 0:
            currentView = views[-1]
            appuifw.app.body = currentView[0]
            appuifw.app.exit_key_handler = currentView[1]
            appuifw.app.focus = currentView[2]
            appuifw.app.menu = currentView[3]
            appuifw.app.screen = currentView[4]
            appuifw.app.title = currentView[5]
            print "current view="+currentView[5]
            
    def getViewState(self):
        """Return the view state as a tuple."""
        return (appuifw.app.body, appuifw.app.exit_key_handler, appuifw.app.focus, appuifw.app.menu, appuifw.app.screen, appuifw.app.title)


class DataStoreView(ViewBase):
    """This class defines the view of the texts, images, etc. that are in the local data store.  It is the first view that is seen on application load."""

    def __init__(self, database = None):
        # TODO make this not a dummy store :-)
        #self.entries = [(u"Police were here", u"A sample description"),
        #                (u"What we need to do", u"Some text here"),
        #                (u"Where were you?", u"Something about it")]
                        #u"We have to go now",
                        #u"Planning meeting monday",
                        #u"Last time we met",
                        #u"Where to go from here"]
        #super(DataStoreView, self).__init__()

        self.lock = e32.Ao_lock()

        # Save our database object
        self.database = database

        self.menuItems = [(u"Add Outgoing", self.addOutgoingCallback),
                          (u"View Outgoing", self.viewOutgoingCallback),
                          (u"Send FluidNexus", self.sendFluidNexusCallback),
                          (u"Settings", self.settingsCallback)]

    def sendFluidNexusCallback(self):
        appuifw.note(u"Feature not implemented yet", "error")

    def exitCallback(self):
        print 'trying to exit'
        self.running = False

    def saveOutgoingData(self, formData):
        # @TODO@
        # This will change if we change the design of the form
        # Also!  We need to have a way so that we aren't saving form items
        # that are somehow saved during the process of editing...there isn't
        # really any way for me to tell that right now, as far as I know
        # If we don't watch for that, we might be saving many copies of the
        # same data while we're editing the form
        try:
            print formData
            title = unicode(formData[0][2])
            data = unicode(formData[1][2])
    
            hash = unicode(md5.md5(title + data).hexdigest())
            self.database.add_new('source', 23, title, data, hash, 'cell')
            returnValue = 1
            #returnValue = self.database.query("insert into FluidNexusOutgoing (source, type, title, data, hash) values ('00:02:EE:6B:86:09', 0, '%s', '%s', '%s')" % (title, data, hash))
        except:
            log.print_exception_trace()

        return True

    def addOutgoingCallback(self):
        formData = [(u'Title', 'text'),
                    (u'Text', 'text')]
        flags = appuifw.FFormEditModeOnly
        form = appuifw.Form(formData, flags)
        form.save_hook = self.saveOutgoingData
        oldTitle = appuifw.app.title
        appuifw.app.title = u'Add Outgoing'
        form.execute()
        appuifw.app.title = oldTitle

    def viewOutgoingCallback(self):
        # @TODO@
        # Change the menu items to allow us to delete items from this database
        # when we have selected them

        # Get all items from the database
        #self.database.query('select * from FluidNexusOutgoing')
        self.database.outgoing()
        listItems = []
        
        for item in database:
            print item
            listItems.append(item)

        self.createListView(listItems)

    def settingsCallback(self):
        appuifw.note(u"Feature not implemented yet", "error")

    def listCallback(self):
        # @TODO@
        # Write new class that is a text view (or form view) that gives the full information about the selected data item
        # This new view should save the old views and then replace them with the new ones
        # on the "exit" key, the new view should restore the old views

        index = self.listbox.current()
        dataItem = self.listItems[index]

        self.createTextView(dataItem)

    def createTextView(self, dataItem):
        # Start setting up our new view
        
        appuifw.app.body = textCanvas= appuifw.Canvas()
        textCanvas.text ((10,20), unicode(dataItem[4]), font=(None, None, graphics.FONT_BOLD))
        self.writeTextAcrossLines (10,36, 8, 14, textCanvas, dataItem[5])

        appuifw.app.exit_key_handler = self.textViewCallback
        appuifw.app.title = dataItem[4]
        self.pushView(self.getViewState())
        
        #it can't call app.body = canvas another time otherwise it breaks
        #self.show()
        
        #print self.entries[index]

        # The form method...doesn't work as I would like it, as it cuts off all text that is longer than one line
#        formData = [(u'Title', 'text', unicode(dataItem[4])),
#                    (u'Text', 'text', unicode(dataItem[5]))]
#        flags = appuifw.FFormViewModeOnly
#        form = appuifw.Form(formData, flags)
#        form.execute()
#        print dir(form)

    def writeTextAcrossLines (self, startX, startY, wordSpacing, lineSpacing, grObj, txt):
        #grObj.text ((startX, startY), unicode(txt))
        words = txt.split(' ')
        text_x = startX
        text_y = startY
        for w in words:
            text_end = text_x + grObj.measure_text(w)[1]    
            if (text_end < grObj.size[0]):
                grObj.text ((text_x,text_y),unicode(w))
                text_x = text_end + wordSpacing
            else:
                text_y = text_y + lineSpacing
		text_x = startX
                grObj.text ((text_x,text_y),unicode(w))
                text_x = text_x + wordSpacing + grObj.measure_text(w)[1] 
                
    def textViewCallback(self):
        # Return back to our old view
        self.popView()

    def setup(self, listItems = None):
        """Setup our view by creating the listbox"""

        self.listItems = listItems

        appuifw.app.screen = 'normal'
        appuifw.app.title = u'FluidNexus'
        appuifw.app.exit_key_handler = self.exitCallback

        if listItems is None:
            self.entires = [(u'foo', u'bar')]
        else:
            # @TODO@
            # This is a place that things will break if we end up changing the database schema...
            self.entries = []
            for item in listItems:
                self.entries.append((item[4], 
                                     item[5][0:20] + u' ...'))

        self.listbox = appuifw.Listbox(self.entries, self.listCallback)
        appuifw.app.body = self.listbox
        appuifw.app.menu = self.menuItems
        self.pushView(self.getViewState())
        self.running = True
        self.show()
        #self.lock.wait()

    def createListView(self, listItems):
        # @TODO@
        # * Need to refactor the saving of listItems for all of our different list views
        # * Add menu options for deleting of outgoing items

        if ((listItems is None) or (listItems == [])):
            appuifw.note(u'Nothing to show...', 'error')
            return

        entries = []
        for item in listItems:
            entries.append((item[4], 
                                item[5][0:20] + u' ...'))

        self.outgoingListItems = listItems

        # @TODO@
        # Add menu item to edit the outgoing item
        # We will need ability to delete old item from database
        # And then insert this item into the database (since the hash will have changed)
        outgoingMenuItems = [(u"Delete", self.deleteOutgoingCallback)]

        listbox = appuifw.Listbox(entries, self.outgoingListCallback)
        appuifw.app.body = listbox
        appuifw.app.title = u'Outgoing Items'
        appuifw.app.menu = outgoingMenuItems
        appuifw.app.exit_key_handler = self.textViewCallback
        self.pushView(self.getViewState())
        self.show()

    def deleteOutgoingCallback(self):
        index = appuifw.app.body.current()
        dataItem = self.outgoingListItems[index]

        answer = appuifw.query(u"Do you really want to delete this item?", "query")

        if answer:
            hash = dataItem[6]
            self.database.query("delete from FluidNexusOutgoing where hash = '%s'" % hash)
            # @TODO@
            # Make this update the view on the stack properly, so that when we return to this view from the textbox view we get the correct list
            self.outgoingListItems.pop(index)
            
            entries = []
            for item in self.outgoingListItems:
                entries.append((item[4], 
                                item[5][0:20] + u' ...'))

            if entries == []:
                entries.append((u'None', u'None'))

            appuifw.app.body = appuifw.Listbox(entries, self.outgoingListCallback)

            
    def outgoingListCallback(self):
        index = appuifw.app.body.current()
        dataItem = self.outgoingListItems[index]

        self.createTextView(dataItem)

    def getView(self):
        """Return the view object."""

        return self.listbox

    def checkActive(self):
        """Check if we're the active view; if not, we should raise the object that we created to replace us."""
        return self.active

    def run(self):
        while self.running:
            e32.ao_yield()
        self.lock.signal()

class FluidNexus:
    def __init__(self):
        self.lock = e32.Ao_lock()
        self.views = []
        self.threads = []

    def exitCallback(self):
        self.lock.signal()

    def setup(self):
        appuifw.app.screen = 'normal'
        appuifw.app.title = u'FluidNexus'
        appuifw.app.exit_key_handler = self.exitCallback
        self.lock.wait()

    def addThread(self, threadName):
        """Add a thread that we should start."""
        self.threads.append(threadName)

    def pushView(self, view):
        self.views.append(view)

    def popView(self):
        if len(self.views) - 1 > 0:
            self.views.pop()
            self.show()

    def show(self):
        if len(self.views) > 0:
            appuifw.app.body = self.views[-1].getView()

    def run(self):
        #if self.threads != []:
        #    for threadName in self.threads:
        #        thread.start_new_thread(threadName.run, ())
        self.lock.wait()
        while 1:
            if False:
                self.show()


if __name__ == "__main__":
    # Get the data from our database
    database = FluidNexusDatabase()
    # @TODO@ Remove this line after we've gotten some things going :-)
    #database.setupDatabase()

    # Get all items from the database
    #database.query('select * from FluidNexusData')
    database.all()
    listItems = []

    for item in database:
        listItems.append(item)

    dataView = DataStoreView(database = database)
    dataView.setup(listItems = listItems)
    dataView.run()

    #FluidNexus = FluidNexus()
    #FluidNexus.pushView(dataView)
    #FluidNexus.setup()

    # Get client and server objects
    #client = FluidNexusClientThread()
    #server = FluidNexusServerThread()
    #FluidNexus.addThread(client)
    #FluidNexus.addThread(server)

    #FluidNexus.run()
