#!/usr/bin/env python

import glob
import os
import subprocess
import sys
sys.path.append(r"C:\WINDOWS\WinSxS\x86_Microsoft.VC90.CRT_1fc8b3b9a1e18e3b_9.0.21022.8_x-ww_d08d0375")

from distutils.command.build_py import build_py as _build_py
from distutils.core import setup
from setuptools import find_packages
#from setuptools.command.build_py import build_py as _build_py
#from setuptools import setup, find_packages

import FluidNexus
from FluidNexus.BuildManpage import build_manpage

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
        'textile',
        'simplejson',
        'pybonjour',
        'sqlalchemy',
        'oauth2',
        ]

if sys.version_info[:3] < (2,5,0):
    requires.append('pysqlite')

if (sys.platform.startswith("linux")):
    os_name = "posix"
elif (sys.platform == "win32"):
    os_name = "windows"
elif (sys.platform == "darwin"):
    os_name = "darwin"

if (os_name == "windows"):
    import py2exe

if (os_name == "darwin"):
    setup_requires = ["py2app"]
else:
    setup_requires = []


def get_messages():
    """Get the QT translations."""
    msgfiles = []
    for filename in os.listdir("l10n/"):
        if filename.endswith(".qm"):
            msgfiles.append("l10n/%s" % filename)
    return msgfiles

def get_manual_images():
    """Get all of the images in the manual."""
    manual_filenames = []
    for dirpath, dirs, filenames in os.walk(os.path.join("share", "fluid-nexus", "manual", "images")):
        manual_filenames.extend([os.path.join(dirpath, filename) for filename in filenames])
        
    return manual_filenames

def regen_messages():
    """Regenerate QT translations."""
    for filename in os.listdir("l10n/"):
        if filename.endswith(".ts"):
            outFile = filename.replace(".ts", ".qm")
            command = ["lconvert", "-i", "l10n/%s" % filename, "-o", "l10n/%s" % outFile]
            subprocess.call(command)

class build_py(_build_py):
    """Builds our PyQt files from the ui files."""
    def run(self):
        uis = []
        for filename in os.listdir(os.path.join("FluidNexus", "ui")):
            if filename.endswith(".ui"):
                uis.append(os.path.join("FluidNexus", "ui", filename))

        for ui in uis:
            out = ui.replace(".ui", "UI.py")
            if (os_name == "windows"):
                command = ["pyuic4.bat", ui, "-o", out]
            else:
                command = ["pyuic4", ui, "-o", out]

            # For some reason pyuic4 doesn't want to work here...
            subprocess.call(command)
            self.byte_compile(out)

        res = "FluidNexus/ui/FluidNexus_rc.py"
        if (os_name == "windows"):
            command = ["pyrcc4.exe", "FluidNexus/ui/res/FluidNexus.qrc", "-o", res]
        else:
            command = ["pyrcc4", "FluidNexus/ui/res/FluidNexus.qrc", "-o", res]
        subprocess.call(command)
       
        # Removing the language conversion for now
        #if (os_name != "windows"):
        #    regen_messages()
        _build_py.run(self)



# Add in our manual and translation files
data_files = [("share/fluid-nexus/l10n", get_messages()), 
              ("share/applications", ["share/applications/fluid-nexus.desktop"]),
              ("share/pixmaps", ["share/pixmaps/fluid-nexus.png"]),
              ("share/fluid-nexus/manual", ["share/fluid-nexus/manual/index.html"]),
             ("share/fluid-nexus/manual/images", get_manual_images())]

# Add in Visual Studio runtime on windows
if (os_name == "windows"):
    data_files.append(("Microsoft.VC90.CRT", glob.glob(r"C:\WINDOWS\WinSxS\x86_Microsoft.VC90.CRT_1fc8b3b9a1e18e3b_9.0.21022.8_x-ww_d08d0375\*.*")))
    data_files.append(("Microsoft.VC90.CRT", [r"scripts\Microsoft.VC90.CRT.manifest"]))

setup(name='fluid-nexus',
    version=FluidNexus.__version__,
    description='PyQt4 application that enables one to share messages and data independent of centralized data networks',
    author='Nicholas Knouf',
    author_email='fluidnexus@fluidnexus.net',
    url='http://fluidnexus.net',
    download_url="http://fluidnexus.net/download",
    long_description=README + '\n\n' +  CHANGES,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: Artistic Software",
        "Topic :: Communications",
    ],
    keywords=["ad-hoc networking", "activism", "bluetooth", "zeroconf", "communication"],
    packages=find_packages(),
    package_data={"FluidNexus.ui":["*.ui"]},
    data_files = data_files,
    scripts=["scripts/fluid-nexus"],
    setup_requires=setup_requires,
    zipfile = "lib/library.zip",
    windows=[{
        "script": "scripts/fluid-nexus",
        "icon_resources": [(1, "FluidNexus/ui/res/icons/fluid_nexus_icon.ico")]}],
    app=["FluidNexusApp.py"],
    options = {
        "py2exe": { 
            "includes": ["sip", "simplejson", "pysqlite2", "google.protobuf", "sqlalchemy"], 
            "packages": ["sqlalchemy.dialects.sqlite", "FluidNexus.ui"]
        },
        "py2app": {
            "argv_emulation": True,
            "iconfile": "FluidNexus/ui/res/icons/fluid_nexus_icon.icns",
            "includes": ["sip", "LightAquaBlue", "lightblue", "pysqlite2", "simplejson", "sqlalchemy", "google.protobuf", "sqlalchemy.dialects.sqlite"],
            "packages": ["Foundation"],
            "plist": dict(
                CFBundleName               = "FluidNexus",
                CFBundleShortVersionString = FluidNexus.version.__version__,     # must be in X.X.X format
                CFBundleGetInfoString      = "Fluid Nexus %s" % FluidNexus.version.__version__,
                #CFBundleExecutable         = "FluidNexusApp.py",
                CFBundleIdentifier         = "net.fluidnexus.FluidNexus",
            ),
        },
    },
    include_package_data=True,
    zip_safe=False,
    install_requires = requires,
    cmdclass={"build_py": build_py, "build_manpage": build_manpage}
)
