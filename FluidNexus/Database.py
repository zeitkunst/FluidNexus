# vim: set fileencoding=utf-8
# Copyright (C) 2011, Nicholas Knouf
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
import logging

# Other imports
from sqlalchemy import create_engine, desc
from sqlalchemy import Table, Column, Integer, String, Boolean, Float, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, object_mapper
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm.attributes import instance_dict

Base = declarative_base()

# my imports
import Log

def createDataDict(table):
    data = {}

    mapper = object_mapper(table)
    for prop in mapper.iterate_properties:
        data[prop.key] = getattr(table, prop.key)

    return data

class Messages(Base):
    __tablename__ = 'messages'

    id = Column('id', Integer, primary_key=True)
    message_type = Column('type', Integer, nullable = False, default = 0)
    message_title = Column('title', String, nullable = False)
    message_content = Column('content', String, nullable = False)
    message_hash = Column('hash', String(length = 64), nullable = False, unique = True)
    message_timestamp = Column('time', Float, default = float(0.0))
    message_received_timestamp = Column('received_time', Float, default = float(0.0))
    message_attachment_path = Column('attachment_path', String, default = "")
    message_attachment_original_filename = Column('attachment_original_filename', String, default = "")
    message_mine = Column('mine', Boolean, default = 0)
    message_blacklist = Column('blacklist', Boolean, default = 0)
    message_public = Column('public', Boolean, default = 0)
    message_ttl = Column('ttl', Integer, default = 0)
    message_uploaded = Column('uploaded', Boolean, default = 0)
    message_priority = Column('priority', Integer, default = 0)

    def __repr__(self):
        return "<Messages('%d', '%s', '%s', '%s', '%f', '%f', '%s', '%s', '%s', '%s')>" % (self.message_type, self.message_title, self.message_content, self.message_hash, self.message_timestamp, self.message_received_timestamp, self.message_attachment_path, self.message_mine, self.message_blacklist, self.message_priority)

class FluidNexusDatabase(object):
    """Uses sqlalchemy and ORM to work with the Fluid Nexus database."""

    def __init__(self, databaseDir = ".", databaseType = "e32", databaseName = 'FluidNexus.db', logPath = "FluidNexus.log", level = logging.ERROR):
        """Initialization method that makes sure the database file and directory exist, and creates/opens the database file, and prepares the database view."""

        self.logger = Log.getLogger(logPath = logPath, level = level)
        self.logLevel = level

        #self.logger = Logger(os.path.join(databaseDir, u'FluidNexus.log'), prefix = 'database: ')
        #sys.stderr = sys.stdout = self.logger

        self.databaseDir = databaseDir
        self.databaseName = databaseName
        
        if not os.path.isdir(databaseDir):
            os.makedirs(databaseDir)

        self.databaseType = databaseType

        self.__setupSQLAlchemy()

    def __setupSQLAlchemy(self, echo = False):
        path = os.path.join(self.databaseDir, self.databaseName)
        self.engine = create_engine('sqlite:///%s' % path, echo=echo)

        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # TODO
        # This is hacky schema modifications...needs to be made better
        try:
            self.session.execute("alter table Messages add column 'priority'")
        except OperationalError:
            pass

    def createRandomMessages(self, number = 100):
        """Create a set of random messages; mainly used for testing UI rendering."""

        import uuid
        for x in xrange(0, number):
            self.addReceived(message_type = 0, title = str(uuid.uuid4()), content = "Random message", timestamp = time.time(), received_timestamp = time.time())

    def addDummyData(self):
        """Add some dummy data to the database."""
        # Insert some dummy data
        # This is from text messages listed in the TxTMob CHI paper
        title = u'Message One to send'
        content = u'[SAMPLE MESSAGE] Some sort of message to send to others.'
        now = time.time()
        message_hash = hashlib.sha256(title + content).hexdigest()
        data = {}
        data["message_title"] = title
        data["message_content"] = content
        data["message_timestamp"] = now
        data["message_received_timestamp"] = now
        data["message_hash"] = message_hash
        self.addMine(data = data)

        title = u'A sample message'
        content = u'[SAMPLE MESSAGE] A message with some sort of content.'
        message_hash = hashlib.sha256(title + content).hexdigest()
        now = time.time()
        data["message_title"] = title
        data["message_content"] = content
        data["message_timestamp"] = now
        data["message_received_timestamp"] = now
        data["message_hash"] = message_hash
        self.addReceived(data = data)

        title = u'Testing'
        content = u'[SAMPLE MESSAGE] Just a test.'
        message_hash = hashlib.sha256(title + content).hexdigest()
        now = time.time()
        data["message_title"] = title
        data["message_content"] = content
        data["message_timestamp"] = now
        data["message_received_timestamp"] = now
        data["message_hash"] = message_hash

        self.addReceived(data = data)

    def hashes(self):
        """Get a list of hashes from the database, ordered by time desc."""

        hashes = []
        for message_hash in self.session.query(Messages.message_hash).order_by(desc(Messages.message_received_timestamp)):
            hashes.append(message_hash[0])

        return hashes

    def hashesNoBlacklist(self):
        """Get a list of non-blacklisted hashes from the database, ordered by time desc."""

        hashes = []
        for message_hash in self.session.query(Messages.message_hash).filter(Messages.message_blacklist != True).order_by(desc(Messages.message_received_timestamp)):
            hashes.append(message_hash[0])

        return hashes

    def addMine(self, data = {}):
        """Add one of our own messages to the database."""
        message_hash = hashlib.sha256(data["message_title"].encode("utf-8") + data["message_content"].encode("utf-8")).hexdigest()
        message = Messages()
        now = time.time()
        for k in data.keys():
            setattr(message, k, data[k])
        message.message_hash = message_hash
        message.message_timestamp = now
        message.message_received_timestamp = now
        message.message_mine = True

        # TODO
        # Ensure new message is not already in the database
        self.session.add(message)
        self.session.commit()
        
        data = createDataDict(message)
        return data

    def addReceived(self, data = {}):
        """Add a received message to the database."""

        message_hash = hashlib.sha256(data["message_title"].encode("utf-8") + data["message_content"].encode("utf-8")).hexdigest()
        message = Messages()
        now = time.time()
        for k in data.keys():
            setattr(message, k, data[k])
        message.message_hash = message_hash
        message.message_received_timestamp = now
        message.message_mine = False

        self.session.add(message)
        self.session.commit()

        data = createDataDict(message)
        return data

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

    def setUploaded(self, message_hash):
        try:
            result = self.session.query(Messages).filter(Messages.message_hash == message_hash).one()
            result.uploaded = True
            self.session.add(result)
            self.session.commit()
            return True
        except NoResultFound, e:
            self.logger.error("No result found for hash %s; this should never happen!" % message_hash)
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

    def updateByMessageHash(self, message_hash = "", new_message_hash = "", new_title = "", new_content = "", new_timestamp = 0.0, new_attachment_path = "", new_attachment_original_filename = "", new_public = False, new_ttl = 30):
        """Update an item by a message hash with a new hash."""

        # TODO
        # Ensure that the updated message isn't already in the database
        message = self.getMessageByHashORM(message_hash)
        message.message_hash = new_message_hash
        message.title = new_title
        message.content = new_content
        message.timestamp = new_timestamp
        message.received_timestamp = new_timestamp
        message.attachment_path = new_attachment_path
        message.attachment_original_filename = new_attachment_original_filename
        message.public = new_public
        message.ttl = new_ttl

        self.session.merge(message)
        self.session.commit()

    def toggleBlacklist(self, message_hash, blacklist = True):
        """Toggle the blacklist status of the given message_hash."""
        message = self.getMessageByHashORM(message_hash)
        message.message_blacklist = blacklist 
        self.session.merge(message)
        self.session.commit()

    def all(self, limit = None, includeBlacklist = False):
        """Return all of the items in the database,  with optional limit."""
        if (limit is not None):
            if (includeBlacklist):
                rows = self.session.query(Messages).order_by(desc(Messages.message_priority)).order_by(desc(Messages.message_received_timestamp)).all()[0:limit]
            else:
                rows = self.session.query(Messages).filter(Messages.message_blacklist == False).order_by(desc(Messages.message_priority)).order_by(desc(Messages.message_received_timestamp)).all()[0:limit]
        else:
            if (includeBlacklist):
                rows = self.session.query(Messages).order_by(desc(Messages.message_priority)).order_by(desc(Messages.message_received_timestamp)).all()
            else:
                rows = self.session.query(Messages).filter(Messages.message_blacklist == False).order_by(desc(Messages.message_priority)).order_by(desc(Messages.message_received_timestamp)).all()

        results = []
        for row in rows:
            results.append(instance_dict(row))

        return results 

    def public(self, limit = None, includeBlacklist = False):
        """Return all of the items in the database,  with optional limit."""
        if (limit is not None):
            if (includeBlacklist):
                rows = self.session.query(Messages).filter(Messages.message_public == 1).order_by(desc(Messages.message_priority)).order_by(desc(Messages.message_received_timestamp)).all()[0:limit]
            else:
                rows = self.session.query(Messages).filter(Messages.message_public == 1).filter(Messages.message_blacklist == False).order_by(desc(Messages.message_priority)).order_by(desc(Messages.message_received_timestamp)).all()[0:limit]
        else:
            if (includeBlacklist):
                rows = self.session.query(Messages).filter(Messages.message_public == 1).order_by(desc(Messages.message_priority)).order_by(desc(Messages.message_received_timestamp)).all()
            else:
                rows = self.session.query(Messages).filter(Messages.message_public == 1).filter(Messages.message_blacklist == False).order_by(desc(Messages.message_priority)).order_by(desc(Messages.message_received_timestamp)).all()

        results = []
        for row in rows:
            results.append(instance_dict(row))

        return results 

    def highPriority(self, limit = None, includeBlacklist = False):
        """Return all of the items in the database,  with optional limit."""
        if (limit is not None):
            if (includeBlacklist):
                rows = self.session.query(Messages).filter(Messages.message_priority == 1).order_by(desc(Messages.message_received_timestamp)).all()[0:limit]
            else:
                rows = self.session.query(Messages).filter(Messages.message_priority == 1).filter(Messages.message_blacklist == False).order_by(desc(Messages.message_received_timestamp)).all()[0:limit]
        else:
            if (includeBlacklist):
                rows = self.session.query(Messages).filter(Messages.message_priority == 1).order_by(desc(Messages.message_received_timestamp)).all()
            else:
                rows = self.session.query(Messages).filter(Messages.message_priority == 1).filter(Messages.message_blacklist == False).order_by(desc(Messages.message_received_timestamp)).all()

        results = []
        for row in rows:
            results.append(instance_dict(row))

        return results 


    def outgoing(self, limit = None):
        """Return outgoing items in the database,  with optional limit."""
        if (limit is not None):
            rows = self.session.query(Messages).filter(Messages.message_mine == True).order_by(desc(Messages.message_priority)).order_by(desc(Messages.message_received_timestamp)).all()[0:limit]
        else:
            rows = self.session.query(Messages).filter(Messages.message_mine == True).order_by(desc(Messages.message_priority)).order_by(desc(Messages.message_received_timestamp)).all()

        results = []
        for row in rows:
            results.append(instance_dict(row))

        return results 

    def blacklist(self, limit = None):
        """Return blacklisted items in the database,  with optional limit."""
        if (limit is not None):
            rows = self.session.query(Messages).filter(Messages.message_blacklist == True).order_by(desc(Messages.message_priority)).order_by(desc(Messages.message_received_timestamp)).all()[0:limit]
        else:
            rows = self.session.query(Messages).filter(Messages.message_blacklist == True).order_by(desc(Messages.message_priority)).order_by(desc(Messages.message_received_timestamp)).all()

        results = []
        for row in rows:
            results.append(instance_dict(row))

        return results 

    def close(self):
        """Close the database, committing if needed."""
        self.session.commit()
        self.session.close()
