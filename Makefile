PYTHON=`which python`
PKGNAME=fluid-nexus
BUILDDIR=builddeb
PROJECT=fluid-nexus
VERSION:=$(shell grep "^__version__ =" FluidNexus/version.py | sed 's/__version__ = //g' | sed 's/"//g')
DEBFLAGS=

all:
	@echo "make builddeb - Generate a deb package"
	@echo "make osx - Generate a OS X dmg"
	@echo "make sdist - Generate an sdist"
	@echo "make win - Generate a windows installer"

builddeb: dist-clean
	$(PYTHON) setup.py sdist
	mkdir -p $(BUILDDIR)/$(PROJECT)-$(VERSION)/debian
	cp dist/$(PROJECT)-$(VERSION).tar.gz $(BUILDDIR)
	cd $(BUILDDIR) && tar xfz $(PROJECT)-$(VERSION).tar.gz
	mv $(BUILDDIR)/$(PROJECT)-$(VERSION).tar.gz $(BUILDDIR)/$(PROJECT)-$(VERSION)/
	cp -R debian/* $(BUILDDIR)/$(PROJECT)-$(VERSION)/debian/
	cd $(BUILDDIR)/$(PROJECT)-$(VERSION) && dpkg-buildpackage $(DEBFLAGS)

sdist: dist-clean
	$(PYTHON) setup.py sdist

clean:
	$(PYTHON) setup.py clean
	rm -Rf build $(BUILDDIR)
	find . -name '*.pyc' -delete

dist-clean: clean
	rm -Rf dist
	rm -Rf $(BUILDDIR)
