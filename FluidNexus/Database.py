# vim: set fileencoding=utf-8
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
import sys
import time
import os
import re
import hashlib

# Other imports
from sqlalchemy import create_engine, desc
from sqlalchemy import Table, Column, Integer, String, Boolean, Float, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm.attributes import instance_dict

Base = declarative_base()

# my imports
import Log

## @HACK@
## Adding paths to find the modules
#sys.path.append('.')
#sys.path.append(os.getcwd())
#sys.path.append('C:\\System\\Apps\\Python\\my\\')
#sys.path.append('E:\\System\\Apps\\Python\\my\\')
#sys.path.append('C:\\Python')
#sys.path.append('E:\\Python')
#
#sys.path.append('C:\\System\\Apps\\Python\\my\\')
#from logger import Logger

# Series 60 specific imports
try:
    # On phone?
    import e32
    import e32db
    
    # @SEMI-HACK@
    # At the moment, set global variable that determines where our data is going to live
    availableDrives = e32.drive_list()
    #if 'E:' in availableDrives:
    #    dataPath = u'E:\\System\\Data\\FluidNexusData'
    #else:
    #    dataPath = u'C:\\System\\Data\\FluidNexusData'
 
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
    log = Logger(dataPath + u'\\FluidNexus.log', prefix = 'database: ')
    #sys.stderr = sys.stdout = log
    #log = sys.stderr = sys.stdout
    
    # For those extraneous errors floating around...
    class OperationalError(Exception): pass
    
    onPhone = True
except ImportError:
    #from s60Compat import e32
    from pysqlite2 import dbapi2 as sqlite

    from pysqlite2.dbapi2 import OperationalError
    # For those extraneous errors floating around...
    class SymbianError(Exception): pass

    dataPath = '.'
    #log = Logger(os.path.join(dataPath, u'FluidNexus.log'), prefix = 'database: ')
    #sys.stderr = sys.stdout = log

    onPhone = False


class Messages(Base):
    __tablename__ = 'messages'

    id = Column('id', Integer, primary_key=True)
    message_type = Column('type', Integer, nullable = False, default = 0)
    title = Column('title', String, nullable = False)
    content = Column('content', String, nullable = False)
    message_hash = Column('hash', String(length = 64), nullable = False, unique = True)
    time = Column('time', Float, default = float(0.0))
    attachment_path = Column('attachment_path', String, default = "")
    attachment_original_filename = Column('attachment_original_filename', String, default = "")
    mine = Column('mine', Boolean, default = 0)
    blacklist = Column('blacklist', Boolean, default = 0)

    def __repr__(self):
        return "<Messages('%d', '%s', '%s', '%s', '%f', '%s', '%s', '%s', '%s')>" % (self.message_type, self.title, self.content, self.message_hash, self.time, self.attachment_path, self.attachment_mimetype, self.mine, self.blacklist)

class Blacklist(Base):
    __tablename__ = 'blacklist'

    id = Column('id', Integer, primary_key=True)
    message_type = Column('message_type', Integer, nullable = False, default = 0)
    title = Column('title', String)
    message_hash = Column('hash', String(length = 64))
    time = Column('time', Float)

    def __repr__(self):
        return "<Blacklist('%d', '%s', '%s', '%f')>" % (self.message_type, self.title, self.message_hash, self.time)

class FluidNexusDatabase(object):
    """Uses sqlalchemy and ORM to work with the Fluid Nexus database."""

    def __init__(self, databaseDir = dataPath, databaseType = "e32", databaseName = 'FluidNexus.db', logPath = "FluidNexus.log"):
        """Initialization method that makes sure the database file and directory exist, and creates/opens the database file, and prepares the database view."""

        self.logger = Log.getLogger(logPath = logPath)
        #self.logger = Logger(os.path.join(databaseDir, u'FluidNexus.log'), prefix = 'database: ')
        #sys.stderr = sys.stdout = self.logger

        self.databaseDir = databaseDir
        self.databaseName = databaseName
        
        if not os.path.isdir(databaseDir):
            os.makedirs(databaseDir)

        self.databaseType = databaseType

        self.__setupSQLAlchemy()

    def __setupSQLAlchemy(self, echo = True):
        path = os.path.join(self.databaseDir, self.databaseName)
        self.engine = create_engine('sqlite:///%s' % path, echo=echo)

        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def addDummyData(self):
        """Add some dummy data to the database."""
        # Insert some dummy data
        # This is from text messages listed in the TxTMob CHI paper
        title = u'Run'
        content = u'Run against Bush in progress (just went through times sq).  media march starts at 7, 52nd and broadway'
        now = time.time()
        message_hash = hashlib.sha256(title + content).hexdigest()
        self.session.add(Messages(title = title, content = content, time = now, message_hash = message_hash))

        title = u'Federal agents'
        content = u'Video dispatch. Federal agents trailing activists at 6th Ave and 9th St. Situation tense.'
        message_hash = hashlib.sha256(title + content).hexdigest()
        now = time.time()
        self.session.add(Messages(title = title, content = content, time = now, message_hash = message_hash))

        title = u'Mobilize to dine'
        content = u'CT delegation @ Maison (7th Ave. & 53rd).  Outdoor dining area.  Try to get people there.'
        message_hash = hashlib.sha256(title + content).hexdigest()
        now = time.time()
        self.session.add(Messages(title = title, content = content, time = now, message_hash = message_hash))
        self.session.commit()

    def hashes(self):
        """Get a list of hashes from the database, ordered by time desc."""

        hashes = []
        for message_hash in self.session.query(Messages.message_hash).order_by(desc(Messages.time)):
            hashes.append(message_hash[0])

        return hashes

    def addMine(self, message_type = 0, title = "", content = "", attachment_path = None, attachment_original_filename = None):
        """Add one of our own messages to the database."""
        message_hash = hashlib.sha256(title.encode("utf-8") + content.encode("utf-8")).hexdigest()
        now = time.time()
        if (attachment_path is not None):
            message = Messages(message_type = message_type, title = title, content = content, message_hash = message_hash, time = now, attachment_path = attachment_path, attachment_original_filename = attachment_original_filename, mine = True)
        else:
            message = Messages(message_type = message_type, title = title, content = content, message_hash = message_hash, time = now, mine = True)

        self.session.add(message)
        self.session.commit()

    def addReceived(self, message_type = 0, title = "", content = "", timestamp = time.time(), attachment_path = None, attachment_original_filename = None):
        """Add one of our own messages to the database."""
        message_hash = hashlib.sha256(title.encode("utf-8") + content.encode("utf-8")).hexdigest()
        if (attachment_path is not None):
            message = Messages(message_type = message_type, title = title, content = content, message_hash = message_hash, time = timestamp, attachment_path = attachment_path, attachment_original_filename = attachment_original_filename, mine = False)
        else:
            message = Messages(message_type = message_type, title = title, content = content, message_hash = message_hash, time = timestamp, mine = False)

        self.session.add(message)
        self.session.commit()

    def checkForMessageByHash(self, message_hash):
        """Look for the given hash in the database, returning True if found, False otherwise."""
        try:
            result = self.session.query(Messages).filter(Messages.message_hash == message_hash).one()
            return True
        except NoResultFound, e:
            return False
        except MultipleResultsFound, e:
            self.logger.error("Multiple results found for hash %s; this should never happen!" % message_hash)
            return False

    def getMessageByHash(self, message_hash):
        """Get a message for a given hash."""
        try:
            result = self.session.query(Messages).filter(Messages.message_hash == message_hash).one()
            return instance_dict(result)
        except NoResultFound, e:
            return None
        except MultipleResultsFound, e:
            self.logger.error("Multiple results found for hash %s; this should never happen!" % message_hash)
            return None

    def getMessageByHashORM(self, message_hash):
        """Get a message for a given hash."""
        try:
            result = self.session.query(Messages).filter(Messages.message_hash == message_hash).one()
            return result
        except NoResultFound, e:
            return None
        except MultipleResultsFound, e:
            self.logger.error("Multiple results found for hash %s; this should never happen!" % message_hash)
            return None


    def removeByMessageHash(self, message_hash):
        """Remove an item by the given message hash."""
        self.session.query(Messages).filter(Messages.message_hash == message_hash).delete()
        self.session.commit()

    def updateByMessageHash(self, message_hash = "", new_message_hash = "", new_title = "", new_content = "", new_timestamp = 0.0, new_attachment_path = "", new_attachment_original_filename = ""):
        """Update an item by a message hash with a new hash."""
        message = self.getMessageByHashORM(message_hash)
        message.message_hash = new_message_hash
        message.title = new_title
        message.content = new_content
        message.timestamp = new_timestamp
        message.attachment_path = new_attachment_path
        message.attachment_original_filename = new_attachment_original_filename

        self.session.merge(message)
        self.session.commit()

    def all(self, limit = None, includeBlacklist = False):
        """Return all of the items in the database,  with optional limit."""
        if (limit is not None):
            if (includeBlacklist):
                rows = self.session.query(Messages).order_by(desc(Messages.time)).all()[0:limit]
            else:
                rows = self.session.query(Messages).filter(Messages.blacklist == False).order_by(desc(Messages.time)).all()[0:limit]
        else:
            if (includeBlacklist):
                rows = self.session.query(Messages).order_by(desc(Messages.time)).all()
            else:
                rows = self.session.query(Messages).filter(Messages.blacklist == False).order_by(desc(Messages.time)).all()

        results = []
        for row in rows:
            results.append(instance_dict(row))

        return results 

    def close(self):
        """Close the database, committing if needed."""
        self.session.commit()
        self.session.close()

################################################################################
############        DATABASE CLASS                                ##############
############  Stores every data in system                         ##############
################################################################################

class FluidNexusDatabaseOld:
    """Provide a light wrapper around the standard database functions.  We could probably make this more robust and make it an actual wrapper around both e32db and sqlite, but not right now...

    @TODO@ Make this a wrapper around pysqlite as well"""

################################################################################
################         Constructor                   #########################
################################################################################
    def __init__(self, databaseDir = dataPath, databaseType = "e32", databaseName = 'FluidNexus.db', logPath = "FluidNexus.log"):
        """Initialization method that makes sure the database file and directory exist, and creates/opens the database file, and prepares the database view."""

        self.logger = Log.getLogger(logPath = logPath)
        #self.logger = Logger(os.path.join(databaseDir, u'FluidNexus.log'), prefix = 'database: ')
        #sys.stderr = sys.stdout = self.logger

        self.databaseDir = databaseDir
        self.databaseName = databaseName
        
        if not os.path.isdir(databaseDir):
            os.makedirs(databaseDir)

        self.databaseType = databaseType

        if (self.databaseType == "e32"):
            self.db = e32db.Dbms()
            self.dbv = e32db.Db_view()
            try:
                self.db.open(unicode(os.path.join(databaseDir, databaseName)))
            except:
                self.db.create(unicode(os.path.join(databaseDir, databaseName)))
                self.db.open(unicode(os.path.join(databaseDir, databaseName)))
        elif (self.databaseType == "pysqlite2"):
            self.con = sqlite.connect(unicode(os.path.join(databaseDir, databaseName)), isolation_level=None)
            self.db = self.con.cursor()

        # Counter for keeping track of our result set
        self.__counter = 0

        # Get the system directory for python
        # @HACK@
        # We take the first directory of the python path to be the base directory for Python, since Python might be installed on a memory card.  There is probably a better way of getting this info.
        #pythonDir = sys.path[0]

        #databaseDir = os.path.join(pythonDir, databaseDir)


    def openDB(self):
        """Need to open a new connection, because of problems of sharing connections between threads."""
        if (self.databaseType == "e32"):
            self.db = e32db.Dbms()
            self.dbv = e32db.Db_view()
            try:
                self.db.open(unicode(os.path.join(databaseDir, databaseName)))
            except:
                self.db.create(unicode(os.path.join(databaseDir, databaseName)))
                self.db.open(unicode(os.path.join(databaseDir, databaseName)))
        elif (self.databaseType == "pysqlite2"):
            self.con = sqlite.connect(unicode(os.path.join(self.databaseDir, self.databaseName)), isolation_level=None)
            self.db = self.con.cursor()



################################################################################
###############         Setup                        ###########################
################################################################################
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
        except OperationalError:
            pass

        try:
            self.db.execute(unicode('drop table FluidNexusSignal'))
        except SymbianError:
            pass
        except OperationalError:
            pass


        # Create the data table
        ######################################
        # This table saves the data that we have accepted and can browse
        if (self.databaseType == "e32"):
            self.db.execute(unicode('create table FluidNexusData (id counter, source varchar(32), time float, type integer, title varchar(40), data long varchar, hash varchar(64), attachment blob, mine bit)'))
            self.db.execute(unicode('create table FluidNexusSignal (id counter, signal bit)'))
        elif (self.databaseType == "pysqlite2"):
            self.db.execute(unicode("create table FluidNexusData (id integer primary key autoincrement, source varchar(32), time float default '0', type integer default '0', title varchar(40), data varchar, hash varchar(64), attachment blob, mine integer default '0')"))
            self.db.execute(unicode("create table FluidNexusSignal (id integer primary key autoincrement, signal integer default '0')"))

        sql = unicode("insert into FluidNexusSignal (signal) values (0)")
        self.__query(sql)

        # Insert some dummy data
        # This is from text messages listed in the TxTMob CHI paper
        title = u'Run'
        data = u'Run against Bush in progress (just went through times sq).  media march starts at 7, 52nd and broadway'
        now = time.time()
        messageHash = hashlib.sha256(title + data).hexdigest()
        self.db.execute(unicode("insert into FluidNexusData (source, time, type, title, data, hash) values ('00:02:EE:6B:86:09', %f, 0, '%s', '%s', '%s')" % (now, title, data, messageHash)))

        title = u'Federal agents'
        data = u'Video dispatch. Federal agents trailing activists at 6th Ave and 9th St. Situation tense.'
        messageHash = hashlib.sha256(title + data).hexdigest()
        self.db.execute(unicode("insert into FluidNexusData (source, time, type, title, data, hash) values ('00:02:EE:6B:86:09', %f, 0, '%s', '%s', '%s')" % (now, title, data, messageHash)))

        title = u'Mobilize to dine'
        data = u'CT delegation @ Maison (7th Ave. & 53rd).  Outdoor dining area.  Try to get people there.'
        messageHash = hashlib.sha256(title + data).hexdigest()
        self.db.execute(unicode("insert into FluidNexusData (source, time, type, title, data, hash) values ('00:02:EE:6B:86:09', %f, 0, '%s', '%s', '%s')" % (now, title, data, messageHash)))

        print 'finished populating the database'


################################################################################
###################   do a query  (private method)   ###########################
################################################################################
    def __query(self, SQLQuery, params = None):
        """Run the SQL query, preparing ourselves for returning the results."""

        # If we have a select statement, prepare the view
        if SQLQuery.lower().startswith('select'):
            if (self.databaseType == "e32"):
                # Prepare for handling the select statement
                self.dbv.prepare(self.db, unicode(SQLQuery))
                # Position ourselves at the beginning of the rowset
                self.dbv.first_line()
                self.numRows = self.dbv.count_line()
            elif (self.databaseType == "pysqlite2"):
                self.db.execute(SQLQuery)
        else:
            # TODO
            # Check to see if this works on s60
            if (params is not None):
                self.affectedRows = self.db.execute(unicode(SQLQuery), params)
            else:
                self.affectedRows = self.db.execute(unicode(SQLQuery))

            self.con.commit()

################################################################################
###################   return number of rows          ###########################
################################################################################
    def getNumRows(self):
        """Return the number of affected rows."""
        return getNumRows

################################################################################
##################       Recover row        ####################################
################################################################################
    def next(self):
        if (self.databaseType == "e32"):
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
        elif (self.databaseType == "pysqlite2"):
            return self.db.next()


    def __iter__(self):
        return self

    def close(self):
        if (self.databaseType == "e32"):
            pass
        elif (self.databaseType == "pysqlite2"):
            self.db.close()
            self.con.close()

################################################################################
#################        Outgoing messages  ####################################
################################################################################
    def outgoing(self):
        """ queries about the outgoing messages, the ones witch are mine"""
        self.__query ('select * from FluidNexusData where mine = 1')

################################################################################
#################        Non-outgoing messages  ################################
################################################################################
    def non_outgoing(self):
        """ queries about the outgoing messages, the ones witch are mine"""
        self.__query ('select * from FluidNexusData where mine = 0')


################################################################################
#################        All messages       ####################################
################################################################################
    def all(self):
        """ queries about all the messages in system """
        self.__query ('select * from FluidNexusData order by time DESC')

################################################################################
#################     services  offering    ####################################
################################################################################
    def services(self):
        """ it makes the old stigmergy work 
             returns id & hash for the last msgs, ordered by date
             newer before"""
        self.__query ('select id, hash  from FluidNexusData order by time DESC')

################################################################################
#################     Add a self made mesage   #################################
################################################################################
    def add_new(self, source, messageType, title, data, messageHash):
        """ creates a new message created by user 
            this computes actual time and fills the mine field as 1
              - source: the source's MAC address hash
              - type:   kind of data stored
              - title:  title
              - data:   data itself
              - hash:   message hash """
        now = float(time.time())
        sql = unicode("insert into FluidNexusData (source,time,type,title,data,hash, mine) values (?, ?, ?, ?, ?, ?, 1)")
        t = (source, now, messageType, title, data, messageHash)
        self.__query(sql, params = t)

################################################################################
#################     Add a recived mesage     #################################
################################################################################
    def add_received(self, source, time, messageType, title, data, messageHash):
        """ stores a message
            fills the mine field as 0
              - source: the source's MAC address hash
              - type:   kind of data stored
              - title:  title
              - data:   data itself
              - hash:   message hash """
        try:
            sql = "insert into FluidNexusData (source, time, type, title, data, hash, mine) values (?, ?, ?, ?, ?, ?, 0)"
            t = (source, float(time), int(messageType), title, data, messageHash)

            print sql
            numRows = self.__query(sql, params = t)
        except Exception, e:
            print e

################################################################################
#################     remove  message       ####################################
################################################################################
    def remove_by_id (self, id):
        """ removes a message by id, returns number of affected records"""
        sql = unicode("delete from FluidNexusData where id = %d" % (id))
        rows = self.__query(sql)
        return rows

################################################################################
#################     remove  message          #################################
################################################################################
    def remove_by_hash (self, hash):
        """ removes a message by hash, returns number of affected records"""
        sql = unicode("delete from FluidNexusData where hash = '%s'" % (hash))
        rows = self.__query(sql)
        return rows

################################################################################
#################     ask database about a hash º##############################
################################################################################
    def look_for_hash (self, hash):
        """ look in database for a hash, 
                returns this entry id if found
                returns -1 if not"""
        sql = unicode("select id from FluidNexusData where hash = '%s'" % unicode(hash))
        rows = self.__query(sql)
        if self.getNumRows == 0:
            return False
        else:
            id = None 
            for item in self:
                id = item
            return id

    def updateItem(self, hash, title, data):
        sql = unicode("update FluidNexusData set title = '%s', data = '%s' where hash = '%s'" (title, data, hash))
        rows = self.__query(sql)
        return rows

################################################################################
#################    return item based on hash      ############################
################################################################################
    def returnItemBasedOnHash(self, hashName):
        """ look in database for a hash, 
                returns this entry id if found
                returns -1 if not"""
        hashName = hashName.lower()
        sql = unicode("select * from FluidNexusData where hash = '%s'" % unicode(hashName))
        rows = self.__query(sql)
        row = None
        for item in self:
            row = item
        return row

################################################################################
#################    signal that new data exists    ############################
################################################################################
    def setSignal(self):
        """signal that there is data"""
        sql = unicode("update FluidNexusSignal set signal = 1 where id = 0")
        rows = self.__query(sql)
        return rows

################################################################################
#################    clear signal that new data exists   #######################
################################################################################
    def clearSignal(self):
        """clear signal that there is data"""
        sql = unicode("update FluidNexusSignal set signal = 0 where id = 0")
        rows = self.__query(sql)
        self.logger.write(str(rows))
        return rows

################################################################################
#################    check the signal               ############################
################################################################################
    def checkSignal(self):
        """check the data signal"""
        sql = unicode("select signal from FluidNexusSignal where id = 0")
        self.__query(sql)
        signalValue = 0
        for item in self:
            signalValue = item[0]
        return signalValue


################################################################################
#################        DEBUG LIB          ####################################
################################################################################
if __name__ == "__main__":
    database = FluidNexusDatabase()
    database.setupDatabase()
#if __name__ == "__main__":
#    # Run this script standalone to reset the database
#    database = FluidNexusDatabase()
#    database.setupDatabase()
#    database.add_new('source', 23,'title','data','hash','cell')
