Fluid Nexus
===========

Nicholas A. Knouf

http://fluidnexus.net

fluidnexus@fluidnexus.net

The software has been testing on Ubuntu Maverick with python 2.6.6 and requires the following python modules: pyqt4, pybonjour, sqlalchemy, textile, pybluez, oauth2, protobuf (version 2.3.0 or higher).

Installing on Ubuntu
--------------------

Installation on Ubuntu requires a number of packages which can be installed using ``sudo apt-get apt-get install python-bluez python-qt4 pyqt4-dev-tools python-protobuf libavahi-compat-libdnssd1``.  Other distributions will need their equivalent.  The code should work on python 2.5, but this hasn't been tested.

Installing on Windows
---------------------

The setup file below will install all of the needed packages, including the python interpreter.  It's recommended to use this instead of download the source code, unless you know what you are doing.


Specific network modality notes
-------------------------------

Bluetooth
+++++++++

* Has been tested to work on Windows XP and Windows 7 using a dlink DBT-120 USB bluetooth adapter, the Windows bluetooth drivers, and pybluez.

* Will not run on OS X due to lack of pybluez; the networking code will have to be ported to lightblue

* Works on Linux using pybluez.

Zeroconf
++++++++

* Has been tested to work on Windows XP with Bonjour for Windows installed.  You may have to allow UDP port 5353 (for zeroconf) through your firewall.

* Should run without modification on OS X if pybonjour is installed; this has not been tested

* Linux will require the installation of a avahi-bonjour compatability library; on ubuntu this is libavahi-compat-libdnssd1.

To run, type "fluid-nexus"; for help, type "fluid-nexus --help".

SECURITY NOTE
=============

Data is stored unencrypted in a local sqlite database.  It is best that you take care of encryption yourself, such as by using ecryptfs home directories or LUKS encrypted devices on Linux.  On Windows, the database and received attachments are stored in the ``FluidNexusData`` folder in your home directory.  It ought to be possible to mount this folder from a TrueCrypt volume.

Data is sent over Bluetooth using the standard encryption facilities of the Bluetooth stack.

Data is sent over link-local wifi using zeroconf for service discovery without any transport layer encryption.

Licenses
========

Fluid Nexus is currently licensed under the GPLv3.

MultipartPostHandlerUnicode.py is licensed under the LGPL and downloaded from http://peerit.blogspot.com/2007/07/multipartposthandler-doesnt-work-for.html


