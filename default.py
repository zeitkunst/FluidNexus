# Copyright (C) 2008, Nick Knouf, Bruno Vianna, and Luis Ayuso
# 
# This file is part of Fluid Nexus
#
# Fluid Nexus is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


# Standard library imports
import thread
import socket
import sys
import os
import md5
import time

# @HACK@
# Adding paths to find the modules
sys.path.append('.')
sys.path.append(os.getcwd())
sys.path.append('C:\\System\\Apps\\Python\\my\\')
sys.path.append('E:\\System\\Apps\\Python\\my\\')
sys.path.append('C:\\Python')
sys.path.append('E:\\Python')

from logger import Logger
from database import FluidNexusDatabase
from FluidNexusNetworking import FluidNexusServer, FluidNexusClient
global options
options = {}

# Series 60 specific imports
try:
    # On phone?
    import appuifw
    import e32
    import e32db
    import graphics
    import codecs

    # @SEMI-HACK@
    # At the moment, set global variable that determines where our data is      going to live
    try:
        os.listdir("E:")
        dataPath = u'E:\\System\\Data\\FluidNexusData'
    except OSError:
        # there is no memory card
        dataPath = u'C:\\System\\Data\\FluidNexusData'

    # Setup our data path
    if not os.path.isdir(dataPath):
        os.makedirs(dataPath)

    # Setup logging and redirect standard input and output
    log = Logger(dataPath + u'\\FluidNexus.log', prefix = 'FluidNexus UI: ')
    sys.stderr = sys.stdout = log
    
    
    # loadPreferences
    f = codecs.open(dataPath + u'\\FluidNexus.ini', 'r', 'utf_8')
    
    options_file = f.read()
    options_lines = options_file.split('\n')
    for options_line in options_lines:
	options_list = options_line.split(':')
	if options_list[0] != "":
	    options[options_list[0]] = options_list[1]
	
    f.close()    
    #options = { "language": "English", "viewMessages" : "True"}
    
    onPhone = True
except ImportError:
    from s60Compat import appuifw
    from s60Compat import e32
    dataPath = '.'
    log = Logger(dataPath + u'\\FluidNexus.log', prefix = 'FluidNexusServer: ')
    sys.stderr = sys.stdout = log

    onPhone = False

except IOError, e:
    #there is no file yet, create one with default preferences
    global options
    f = codecs.open(dataPath + u'\\FluidNexus.ini', 'w', 'utf_8')
    newline = "\n"
    settings  = "language:English" + newline
    settings += "viewMessages:Yes" + newline
    f.write(settings)
    f.close()
    options = { "language": "English", "viewMessages" : "True"}
    

# @TODO@
# These methods should be moved into methods of one of our classes instead of being left here in a global context
### localization stuff -- reading from translations file
global translation_dicts
translation_dicts = dict()
new_dict_set = dict()
try:

   f = codecs.open(dataPath + u'\\FN_translations.txt', 'r', 'utf_8')
   translation_file = f.read()
   translation_lines = translation_file.split("\n")
   for line in translation_lines:
     if line.startswith("---table"):
        def_line = line.rstrip().split(",")
        new_dict = dict()
        translation_dicts[def_line[1]]= new_dict
     else:
        dict_line = line.split("\t")
        new_dict[dict_line[0]] = dict_line[1]
   #print translation_dicts

except IOError, e:
   print "Couldn't open translations file!"   	   
   

def _(s):
    global options, translation_dicts
    if options['language'] != u'English':
	curr_dict = translation_dicts[options['language']]
	if curr_dict.has_key(s):
	   return curr_dict[s]
	else:
	    return s
    else:
	return s    

views = []

#declaring the options form so it's global and accessible from other places
settingsForm = None

# For the release we will get rid of source and time (because we don't want tracking)
# Type is: text = 0, image, audio, video
# for type values > 0, the data value will be a path to the file
# files should be kept under the databaseDir directory

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
        return [appuifw.app.body, appuifw.app.exit_key_handler, appuifw.app.focus, appuifw.app.menu, appuifw.app.screen, appuifw.app.title]


class DataStoreView(ViewBase):
    """This class defines the view of the texts, images, etc. that are in the local data store.  It is the first view that is seen on application load."""

    def __init__(self, database = None):
        # TODO make this not a dummy store :-)

        self.lock = e32.Ao_lock()

        # Save our database object
        self.database = database

        self.timer = e32.Ao_timer()
        self.timerRunning = False

        if dataPath[0] == 'C':
            pythonPath = u'C:\\System\\Apps\\Python\\my'
        elif dataPath[0] == 'E':
            pythonPath = u'E:\\System\\Apps\\Python\\my'

        # @TODO@
        # Update this to eventually not start servers (consumes too many resources)
        log.write('starting server')
        e32.start_server(pythonPath + u'\\FluidNexusServer.py')

        log.write('starting client')
        e32.start_server(pythonPath + u'\\FluidNexusClient.py')

    def sendFluidNexusCallback(self):
        appuifw.note(_(u"Feature not implemented yet"), _(u"error"))

    def exitCallback(self):
        """Called when we press the exit button in the main screen."""
        log.write('trying to exit')
        self.running = False

        appname = appuifw.app.full_name()
        if appname[-10:] != u"Python.app":
            log.write('calling set_exit')
            appuifw.app.set_exit()
        else:
            log.write('calling lock.signal')
            self.lock.signal()

    def saveOutgoingData(self, formData):
        """Save the data that we have entered into the outgoing message form."""

        # @TODO@
        # This will change if we change the design of the form
        global views
        try:
            print formData
            title = unicode(formData[0][2])
            data = unicode(formData[1][2])
    
            hash = unicode(md5.md5(title + data).hexdigest())
            self.database.add_new('source', 23, title, data, hash, 'cell')

            self.database.all()
            openingScreenItems = []
            self.listItems = []

            for item in self.database:
                self.listItems.append(item)
                openingScreenItems.append((item[4], 
                                item[5][0:20] + u' ...'))
            if openingScreenItems == []:
                openingScreenItems.append((_(u'None'), _(u'None')))
            views[0][0] = appuifw.Listbox(openingScreenItems, self.listCallback)
            appuifw.app.body = views[0][0]
        except:
            log.print_exception_trace()

        return True

    def addOutgoingCallback(self):
        """Create and manage the outgoing form."""

        formData = [(_(u'Title'), 'text'),
                    (_(u'Text'), 'text')]
        flags = appuifw.FFormEditModeOnly | appuifw.FFormDoubleSpaced
        form = appuifw.Form(formData, flags)
        form.save_hook = self.saveOutgoingData
        oldTitle = appuifw.app.title
        appuifw.app.title = _(u'Add Outgoing')
        form.execute()
        appuifw.app.title = oldTitle

    def viewOutgoingCallback(self):
        """Create the view for viewing outgoing messages."""

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
        """Called when we want to view and modify settings."""

        global translation_dicts
        languages = translation_dicts.keys()
        
        index_languages = 0
        
        for language in languages:
            if language == options['language']:
                break
            else:
                index_languages = index_languages + 1
        
        #if no language found, index will be length + 1 -- and we put english there
        languages.append(u'English')
        
        yesno = [_(u"yes"),_(u"no")]
        
        index_yesno = 0
        if options['viewMessages'] == "no":
            index_yesno = 1
           
        entries = [(_(u'Language'), 'combo', (languages,index_languages)),
                (_(u'Show incoming messages?'), 'combo', (yesno,index_yesno))]
        flags = appuifw.FFormEditModeOnly | appuifw.FFormDoubleSpaced
        settingsForm = appuifw.Form(entries)
        settingsForm.flags = flags
        settingsForm.save_hook = self.saveSettings
        oldTitle = appuifw.app.title
        appuifw.app.title = _(u'Settings')
        settingsForm.execute()
        appuifw.app.title = oldTitle

    def saveSettings (self, formData):
        """Called when we want to save setings."""

        global options
        options['language'] = unicode(formData[0][2][0][formData[0][2][1]])
        options['viewMessages'] = unicode(formData[1][2][0][formData[1][2][1]])

        print "printng language"
        #print formData[0][2][0][formData[0][2][1]]
	
        try:
            f = codecs.open(dataPath + u'\\FluidNexus.ini', 'w+', 'utf_8')
            newline = "\n"
            settings  = "language:" + unicode(formData[0][2][0][formData[0][2][1]]) + newline
            settings += "viewMessages:" + unicode(formData[1][2][0][formData[1][2][1]])
            f.write(settings)
            f.close()
           
           #this way i get english
           #print formData[0][2][0][1]
           
           #print unicode(formData[0][2][0][formData[0][2][1]])
           
        except IOError, e:
            log.print_exception_trace()
            appuifw.note(u"couldn't rewrite file", "info")

        self.setup()

        return True

    def listCallback(self):
        """Create a new text view for when we click on an item in a list view."""

        # @TODO@
        # Write new class that is a text view (or form view) that gives the full information about the selected data item
        # This new view should save the old views and then replace them with the new ones
        # on the "exit" key, the new view should restore the old views
        global views

        index = views[0][0].current()
        dataItem = self.listItems[index]

        log.write(index)
        log.write(dataItem)

        self.createTextView(dataItem)
    
    def createTextView(self, dataItem):
        """Create the text view with a textCanvas."""

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
        """Split our text across multiple lines within the text view."""

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
        
        
        self.menuItems = [(_(u"Add Outgoing"), self.addOutgoingCallback),
                        (_(u"View Outgoing"), self.viewOutgoingCallback),
                        (_(u"Send FluidNexus"), self.sendFluidNexusCallback),
                        (_(u"Settings"), self.settingsCallback)]

        appuifw.app.screen = 'normal'
        appuifw.app.title = _(u'FluidNexus')
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

        
        appuifw.app.body = appuifw.Listbox(self.entries, self.listCallback)
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
            appuifw.note(_(u'Nothing to show...'), 'error')
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
        outgoingMenuItems = [(_(u"Delete"), self.deleteOutgoingCallback)]

        appuifw.app.body = appuifw.Listbox(entries, self.outgoingListCallback)
        appuifw.app.title = _(u'Outgoing Items')
        appuifw.app.menu = outgoingMenuItems
        appuifw.app.exit_key_handler = self.textViewCallback
        self.pushView(self.getViewState())
        self.show()

    def deleteOutgoingCallback(self):
        global views
        index = appuifw.app.body.current()
        dataItem = self.outgoingListItems[index]

        answer = appuifw.query(_(u"Do you really want to delete this item?"), "query")

        if answer:
            hash = dataItem[6]
            self.database.remove_by_hash(hash)
            # @TODO@
            # Make this update the view on the stack properly, so that when we return to this view from the textbox view we get the correct list
            self.outgoingListItems.pop(index)
            
            entries = []
            self.listItems = []
            for item in self.outgoingListItems:
                entries.append((item[4], 
                                item[5][0:20] + u' ...'))

            if entries == []:
                entries.append((_(u'None'), _(u'None')))

            self.database.all()
            openingScreenItems = []
            for item in self.database:
                self.listItems.append(item)
                openingScreenItems.append((item[4], 
                                item[5][0:20] + u' ...'))
            if openingScreenItems == []:
                openingScreenItems.append((_(u'None'), _(u'None')))
            
            views[0][0] = appuifw.Listbox(openingScreenItems, self.listCallback)

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

    def timerCallback(self):
        """What happens when our timer is called."""

        if self.database.checkSignal():
            log.write('signal exists')
            self.database.clearSignal()
        self.timerRunning = 0

    def run(self):
        while self.running:
            if not self.timerRunning:
                log.write('calling timer')
                self.timer.after(30, self.timerCallback)
                self.timerRunning = 1
            e32.ao_yield()
        self.lock.signal()



if __name__ == "__main__":

    try:
        # Check to see if the database file exists
        foo = os.stat(dataPath + u'\\FluidNexus.db')

        # Create our database object
        database = FluidNexusDatabase()
    except OSError, e:
        # Create our database object
        database = FluidNexusDatabase()
        # Populate the database
        database.setupDatabase()

    # Get all items from the database
    database.all()
    listItems = []

    for item in database:
        listItems.append(item)

    dataView = DataStoreView(database = database)
    dataView.setup(listItems = listItems)
    dataView.run()
