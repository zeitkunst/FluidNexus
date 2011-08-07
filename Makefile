PYTHON=`which python`
PKGNAME=fluid-nexus
BUILDDIR=builddeb
PROJECT=fluid-nexus
ISCC=iscc
VERSION:=$(shell grep "^__version__ =" FluidNexus/version.py | sed 's/__version__ = //g' | sed 's/"//g')
DEBFLAGS=

# For making dmg's
NAME ?= FluidNexus
SOURCE_DIR ?= dist
SOURCE_FILES ?= FluidNexus.app
TEMPLATE_DMG ?= template.dmg
MASTER_DMG=$(NAME)-$(VERSION).dmg
WC_DMG=wc.dmg
WC_DIR=wc


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

osxapp: dist-clean
	$(PYTHON) setup.py py2app

osx: osxapp $(MASTER_DMG)

clean:
	$(PYTHON) setup.py clean
	rm -Rf build $(BUILDDIR)

dist-clean: clean
	rm -Rf dist

$(TEMPLATE_DMG): $(TEMPLATE_DMG).bz2
	bunzip2 -k $<

$(TEMPLATE_DMG).bz2: 
	@echo
	@echo --------------------- Generating empty template --------------------
	mkdir template
	hdiutil create -fs HFSX -layout SPUD -size 70m "$(TEMPLATE_DMG)" -srcfolder template -format UDRW -volname "$(NAME)" -quiet
	rmdir template
	bzip2 "$(TEMPLATE_DMG)"
	@echo

$(WC_DMG): $(TEMPLATE_DMG)
	cp $< $@

$(MASTER_DMG): $(WC_DMG) $(addprefix $(SOURCE_DIR)/,$(SOURCE_FILES))
	@echo
	@echo --------------------- Creating Disk Image --------------------
	mkdir -p $(WC_DIR)
	hdiutil attach "$(WC_DMG)" -noautoopen -quiet -mountpoint "$(WC_DIR)"
	for i in $(SOURCE_FILES); do  \
		rm -rf "$(WC_DIR)/$$i"; \
		ditto -rsrc "$(SOURCE_DIR)/$$i" "$(WC_DIR)/$$i"; \
	done
	#rm -f "$@"
	#hdiutil create -srcfolder "$(WC_DIR)" -format UDZO -imagekey zlib-level=9 "$@" -volname "$(NAME) $(VERSION)" -scrub -quiet
	WC_DEV=`hdiutil info | grep "$(WC_DIR)" | grep "Apple_HFS" | awk '{print $$1}'` && \
	hdiutil detach $$WC_DEV -quiet -force
	rm -f "$(MASTER_DMG)"
	hdiutil convert "$(WC_DMG)" -quiet -format UDZO -imagekey zlib-level=9 -o "$@"
	rm -rf $(WC_DIR)
	@echo
