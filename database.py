# Standard library imports
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

# Series 60 specific imports
try:
    # On phone?
    import e32
    import e32db
    
    # @SEMI-HACK@
    # At the moment, set global variable that determines where our data is going to live
    availableDrives = e32.drive_list()
    if 'E:' in availableDrives:
        dataPath = u'E:\\System\\Data\\FluidNexusData'
    else:
        dataPath = u'C:\\System\\Data\\FluidNexusData'

    # Setup our data path
    if not os.path.isdir(dataPath):
        os.makedirs(dataPath)

    # Setup logging and redirect standard input and output
    log = Logger(dataPath + u'\\FluidNexus.log', prefix = 'database: ')
    sys.stderr = sys.stdout = log

    onPhone = True
except ImportError:
    from s60Compat import e32
    dataPath = '.'
    log = Logger(dataPath + u'\\FluidNexus.log', prefix = 'database: ')
    sys.stderr = sys.stdout = log

    onPhone = False


class FluidNexusDatabase:
    """Provide a light wrapper around the standard database functions.  We could probably make this more robust and make it an actual wrapper around both e32db and sqlite, but not right now...

    @TODO@ Make this a wrapper around pysqlite as well"""

    def __init__(self, databaseDir = dataPath, databaseName = 'FluidNexus.db'):
        """Initialization method that makes sure the database file and directory exist, and creates/opens the database file, and prepares the database view."""

        self.db = e32db.Dbms()
        self.dbv = e32db.Db_view()
        self.databaseDir = databaseDir
        self.databaseName = databaseName

        # Counter for keeping track of our result set
        self.__counter = 0

        # Get the system directory for python
        # @HACK@
        # We take the first directory of the python path to be the base directory for Python, since Python might be installed on a memory card.  There is probably a better way of getting this info.
        #pythonDir = sys.path[0]

        #databaseDir = os.path.join(pythonDir, databaseDir)

        print 'before making the directory'

        if not os.path.isdir(databaseDir):
            os.makedirs(databaseDir)

        try:
            self.db.open(unicode(os.path.join(databaseDir, databaseName)))
        except:
            self.db.create(unicode(os.path.join(databaseDir, databaseName)))
            self.db.open(unicode(os.path.join(databaseDir, databaseName)))

    def setupDatabase(self):
        """This sets up the database with the necessary table structure and some dummy data.

        WARNING!  WARNING!  WARNING!  WARNING!

        This method wipes your database clean...make sure this is what you want to do before calling the code!"""

        print 'setting up the database'

        # These lines remove your existing tables!
        try:
            self.db.execute(unicode('drop table FluidNexusData'))
        except SymbianError:
            pass

        try:
            self.db.execute(unicode('drop table FluidNexusOutgoing'))
        except SymbianError:
            pass

        try:
            self.db.execute(unicode('drop table FluidNexusStigmergy'))
        except SymbianError:
            pass


        ######################################
        # Create the data table
        ######################################
        # This table saves the data that we have accepted and can browse
        self.db.execute(unicode('create table FluidNexusData (id counter, source varchar(18), time timestamp, type integer, title varchar(40), data long varchar, hash varchar(32))'))

        # Insert some dummy data
        # This is from text messages listed in the TxTMob CHI paper
        title = u'Run'
        data = u'Run against Bush in progress (just went through times sq).  media march starts at 7, 52nd and broadway'
        hash = unicode(md5.md5(title + data).hexdigest())
        self.db.execute(unicode("insert into FluidNexusData (source, type, title, data, hash) values ('00:02:EE:6B:86:09', 0, '%s', '%s', '%s')" % (title, data, hash)))

        title = u'Federal agents'
        data = u'Video dispatch. Federal agents trailing activists at 6th Ave and 9th St. Situation tense.'
        hash = unicode(md5.md5(title + data).hexdigest())
        self.db.execute(unicode("insert into FluidNexusData (source, type, title, data, hash) values ('00:02:EE:6B:86:09', 0, '%s', '%s', '%s')" % (title, data, hash)))

        title = u'Mobilize to dine'
        data = u'CT delegation @ Maison (7th Ave. & 53rd).  Outdoor dining area.  Try to get people there.'
        hash = unicode(md5.md5(title + data).hexdigest())
        self.db.execute(unicode("insert into FluidNexusData (source, type, title, data, hash) values ('00:02:EE:6B:86:09', 0, '%s', '%s', '%s')" % (title, data, hash)))

        ######################################
        # Create the outgoing table
        ######################################
        # This table saves the data that we would like to send to other devices
        self.db.execute(unicode('create table FluidNexusOutgoing (id counter, source varchar(18), time timestamp, type integer, title varchar(40), data long varchar, hash varchar(32))'))

        ######################################
        # Create the stigmergy table
        ######################################
        # This table saves the hashes of the recently accepted data items
        self.db.execute(unicode('create table FluidNexusStigmergy (id counter, dataHash varchar(32))'))
        # For testing purposes, input the last hash value that we had
        self.db.execute(unicode("insert into FluidNexusStigmergy (dataHash) values ('%s')" % (hash)))

        print 'finished populating the database'

    def query(self, SQLQuery):
        """Run the SQL query, preparing ourselves for returning the results."""

        # If we have a select statement, prepare the view
        if SQLQuery.lower().startswith('select'):
            # Prepare for handling the select statement
            self.dbv.prepare(self.db, unicode(SQLQuery))
            # Position ourselves at the beginning of the rowset
            self.dbv.first_line()
            self.numRows = self.dbv.count_line()
        else:
            self.affectedRows = self.db.execute(unicode(SQLQuery))

    def next(self):
        row = []

        if self.numRows < 1:
            # We actually returned nothing
            raise StopIteration
        elif self.__counter < self.numRows:
            self.dbv.get_line()
            for column in range(self.dbv.col_count()):
                row.append(self.dbv.col(column + 1))
            self.dbv.next_line()
            self.__counter += 1
            return row
        else:
            self.__counter = 0
            raise StopIteration

    def __iter__(self):
        return self

if __name__ == "__main__":
    # Run this script standalone to reset the database
    database = FluidNexusDatabase()
    database.setupDatabase()
