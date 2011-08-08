Ubuntu
======

PyPi
++++

1.  Edit version number

2.  python setup.py sdist upload

PPA
+++

1.  cd debian; dch -i (Update changelog; then, update manually for building maverick and natty releases, at least until we've created a recipe)

2.  make builddeb

3.  sudo pbuilder build builddeb/<package_version>.dsc (to test)

4.  dput fluidnexus-ppa <packages_version_source.changes>

5.  Wait for build on launchpad

6.  To test in chroot: sudo schroot -c maverick -p; install package(s)

Windows
=======

1.  Checkout latest git source

2.  Update scripts/fluid_nexus.iss with latest version

3.  mingw32-win make win
    
4.  Upload installer to pypi and Fluid Nexus website

Mac OS X
========

1.  Checkout latest git source

2.  Update version number in Makefile

3.  Remove old dist directory

4.  python setup.py py2app

5.  Test that app works

6.  Run make to create dmg

7.  Upload to pypi and Fluid Nexus website
