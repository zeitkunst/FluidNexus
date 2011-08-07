PYTHON=`which python`
PKGNAME=fluid-nexus
BUILDDIR=builddeb
PROJECT=fluid-nexus
ISCC=iscc
VERSION:=$(shell grep "^__version__ =" FluidNexus/version.py | sed 's/__version__ = //g' | sed 's/"//g')
DEBFLAGS=

all:
	@echo "make builddeb - Generate a deb package"
	@echo "make osx - Generate a OS X dmg"
	@echo "make sdist - Generate an sdist"
	@echo "make win - Generate a windows installer"

builddeb: dist-clean
	@echo "Building debian source and binary packages"
	$(PYTHON) setup.py sdist
	mkdir -p $(BUILDDIR)/$(PROJECT)-$(VERSION)/debian
	cp dist/$(PROJECT)-$(VERSION).tar.gz $(BUILDDIR)
	cd $(BUILDDIR) && tar xfz $(PROJECT)-$(VERSION).tar.gz
	mv $(BUILDDIR)/$(PROJECT)-$(VERSION).tar.gz $(BUILDDIR)/$(PROJECT)-$(VERSION)/
	cp -R debian/* $(BUILDDIR)/$(PROJECT)-$(VERSION)/debian/
	cd $(BUILDDIR)/$(PROJECT)-$(VERSION) && debuild -S $(DEBFLAGS)
	cd $(BUILDDIR)/$(PROJECT)-$(VERSION) && debuild $(DEBFLAGS)

sdist: dist-clean
	$(PYTHON) setup.py sdist

win: dist-clean
	$(PYTHON) setup.py py2exe
	$(ISCC) scripts/fluid-nexus.iss

osx: dist-clean
	$(PYTHON) setup.py py2app

clean:
	$(PYTHON) setup.py clean
	rm -Rf build $(BUILDDIR)

dist-clean: clean
	rm -Rf dist
