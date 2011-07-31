Fluid Nexus v0.2.2 alpha
========================

Nicholas A. Knouf

http://fluidnexus.net

fluidnexus@fluidnexus.net

This software is ALPHA QUALITY and should only be used at your own risk.  More detailed instructions about theory, motivation, installation, and use can be found on the website.

The software has been testing on Ubuntu Maverick with python 2.6.6 and requires the following python modules: pyqt4, pybonjour, sqlalchemy, textile, pybluez, oauth2, protobuf (version 2.3.0 or higher).

Specific network modality notes
-------------------------------

Bluetooth:

* Should run without modification on Windows if pybluez is installed, but this hasn't been tested

* Will not run on OS X due to lack of pybluez; the networking code will have to be ported to lightblue

Zeroconf:

* Should run without modification on Windows if pybonjour is installed, along with the Bonjour library from Apple; this has not been tested

* Should run without modification on OS X if pybonjour is installed; this has not been tested

* Linux will require the installation of a avahi-bonjour compatability library; on ubuntu this is libavahi-compat-libdnssd1.

To run, type "fluid_nexus"; for help, type "fluid_nexus --help".

SECURITY NOTE
=============

Data is stored unencrypted in a local sqlite database.  It is best that you take care of encryption yourself, such as by using ecryptfs home directories or LUKS encrypted devices on Linux.

Data is sent over bluetooth without any transport layer encryption.  This is something we plan on implementing in the future.

Data is sent over link-local wifi using zeroconf for service discovery without any transport layer encryption.  This is something we plan on implementing in the future.

Licenses
========

MultipartPostHandlerUnicode.py is licensed under the LGPL and downloaded from http://peerit.blogspot.com/2007/07/multipartposthandler-doesnt-work-for.html

