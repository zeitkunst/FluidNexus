Windows
=======

1.  Checkout latest git source

2.  Update scripts/fluid_nexus.iss with latest version

4.  Edit version number in fluid_nexus.iss script

5.  Run makeWindowsSetup.sh from mingw prompt
    
6.  Upload to pypi and Fluid Nexus website

Mac OS X
========

1.  Checkout latest git source

2.  Update version number in Makefile

3.  Remove old dist directory

4.  python setup.py py2app

5.  Test that app works

6.  Run make to create dmg

7.  Upload to pypi and Fluid Nexus website
