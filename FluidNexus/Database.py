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
import logging

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

class Messages(Base):
    __tablename__ = 'messages'

    id = Column('id', Integer, primary_key=True)
    message_type = Column('type', Integer, nullable = False, default = 0)
    title = Column('title', String, nullable = False)
    content = Column('content', String, nullable = False)
    message_hash = Column('hash', String(length = 64), nullable = False, unique = True)
    time = Column('time', Float, default = float(0.0))
    received_time = Column('received_time', Float, default = float(0.0))
    attachment_path = Column('attachment_path', String, default = "")
    attachment_original_filename = Column('attachment_original_filename', String, default = "")
    mine = Column('mine', Boolean, default = 0)
    blacklist = Column('blacklist', Boolean, default = 0)
    public = Column('public', Boolean, default = 0)
    ttl = Column('ttl', Integer, default = 0)
    uploaded = Column('uploaded', Boolean, default = 0)

    def __repr__(self):
        return "<Messages('%d', '%s', '%s', '%s', '%f', '%f', '%s', '%s', '%s', '%s')>" % (self.message_type, self.title, self.content, self.message_hash, self.time, self.received_time, self.attachment_path, self.attachment_mimetype, self.mine, self.blacklist)

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

    def addDummyData(self):
        """Add some dummy data to the database."""
        # Insert some dummy data
        # This is from text messages listed in the TxTMob CHI paper
        title = u'Run'
        content = u'Run against Bush in progress (just went through times sq).  media march starts at 7, 52nd and broadway'
        now = time.time()
        message_hash = hashlib.sha256(title + content).hexdigest()
        self.session.add(Messages(title = title, content = content, time = now, received_time = now, message_hash = message_hash))

        title = u'Federal agents'
        content = u'Video dispatch. Federal agents trailing activists at 6th Ave and 9th St. Situation tense.'
        message_hash = hashlib.sha256(title + content).hexdigest()
        now = time.time()
        self.session.add(Messages(title = title, content = content, time = now, received_time = now, message_hash = message_hash))

        title = u'Mobilize to dine'
        content = u'CT delegation @ Maison (7th Ave. & 53rd).  Outdoor dining area.  Try to get people there.'
        message_hash = hashlib.sha256(title + content).hexdigest()
        now = time.time()
        self.session.add(Messages(title = title, content = content, time = now, received_time = now, message_hash = message_hash))
        self.session.commit()

    def hashes(self):
        """Get a list of hashes from the database, ordered by time desc."""

        hashes = []
        for message_hash in self.session.query(Messages.message_hash).order_by(desc(Messages.received_time)):
            hashes.append(message_hash[0])

        return hashes

    def addMine(self, message_type = 0, title = "", content = "", attachment_path = None, attachment_original_filename = None, public = False, ttl = 30):
        """Add one of our own messages to the database."""
        message_hash = hashlib.sha256(title.encode("utf-8") + content.encode("utf-8")).hexdigest()

        # TODO
        # Ensure new message is not already in the database
        now = time.time()
        if (attachment_path is not None):
            message = Messages(message_type = message_type, title = title, content = content, message_hash = message_hash, time = now, received_time = now, attachment_path = attachment_path, attachment_original_filename = attachment_original_filename, mine = True, public = public, ttl = ttl)
        else:
            message = Messages(message_type = message_type, title = title, content = content, message_hash = message_hash, time = now, received_time = now, mine = True, public = public, ttl = ttl)

        self.session.add(message)
        self.session.commit()

    def addReceived(self, message_type = 0, title = "", content = "", timestamp = time.time(), received_timestamp = time.time(), attachment_path = None, attachment_original_filename = None, public = False, ttl = 30):
        """Add one of our own messages to the database."""
        message_hash = hashlib.sha256(title.encode("utf-8") + content.encode("utf-8")).hexdigest()

        # TODO
        # Ensure new message is not already in the database
        if (attachment_path is not None):
            message = Messages(message_type = message_type, title = title, content = content, message_hash = message_hash, time = timestamp, received_time = received_timestamp, attachment_path = attachment_path, attachment_original_filename = attachment_original_filename, mine = False, public = public, ttl = ttl)
        else:
            message = Messages(message_type = message_type, title = title, content = content, message_hash = message_hash, time = timestamp, received_time = received_timestamp, mine = False, public = public, ttl = ttl)

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
        message.blacklist = blacklist 
        self.session.merge(message)
        self.session.commit()

    def all(self, limit = None, includeBlacklist = False):
        """Return all of the items in the database,  with optional limit."""
        if (limit is not None):
            if (includeBlacklist):
                rows = self.session.query(Messages).order_by(desc(Messages.received_time)).all()[0:limit]
            else:
                rows = self.session.query(Messages).filter(Messages.blacklist == False).order_by(desc(Messages.received_time)).all()[0:limit]
        else:
            if (includeBlacklist):
                rows = self.session.query(Messages).order_by(desc(Messages.received_time)).all()
            else:
                rows = self.session.query(Messages).filter(Messages.blacklist == False).order_by(desc(Messages.received_time)).all()

        results = []
        for row in rows:
            results.append(instance_dict(row))

        return results 

    def public(self, limit = None, includeBlacklist = False):
        """Return all of the items in the database,  with optional limit."""
        if (limit is not None):
            if (includeBlacklist):
                rows = self.session.query(Messages).filter(Messages.public == 1).order_by(desc(Messages.received_time)).all()[0:limit]
            else:
                rows = self.session.query(Messages).filter(Messages.public == 1).filter(Messages.blacklist == False).order_by(desc(Messages.received_time)).all()[0:limit]
        else:
            if (includeBlacklist):
                rows = self.session.query(Messages).filter(Messages.public == 1).order_by(desc(Messages.received_time)).all()
            else:
                rows = self.session.query(Messages).filter(Messages.public == 1).filter(Messages.blacklist == False).order_by(desc(Messages.received_time)).all()

        results = []
        for row in rows:
            results.append(instance_dict(row))

        return results 


    def outgoing(self, limit = None):
        """Return outgoing items in the database,  with optional limit."""
        if (limit is not None):
            rows = self.session.query(Messages).filter(Messages.mine == True).order_by(desc(Messages.received_time)).all()[0:limit]
        else:
            rows = self.session.query(Messages).filter(Messages.mine == True).order_by(desc(Messages.received_time)).all()

        results = []
        for row in rows:
            results.append(instance_dict(row))

        return results 

    def blacklist(self, limit = None):
        """Return blacklisted items in the database,  with optional limit."""
        if (limit is not None):
            rows = self.session.query(Messages).filter(Messages.blacklist == True).order_by(desc(Messages.received_time)).all()[0:limit]
        else:
            rows = self.session.query(Messages).filter(Messages.blacklist == True).order_by(desc(Messages.received_time)).all()

        results = []
        for row in rows:
            results.append(instance_dict(row))

        return results 

    def close(self):
        """Close the database, committing if needed."""
        self.session.commit()
        self.session.close()
