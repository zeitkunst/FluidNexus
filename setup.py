#!/usr/bin/env python

import os
import subprocess
import sys

from distutils.command.build_py import build_py as _build_py
from distutils.core import setup
from setuptools import find_packages
#from setuptools.command.build_py import build_py as _build_py
#from setuptools import setup, find_packages

import FluidNexus

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

if (os.name == "posix"):
    os_name = "posix"
elif (os.name in ["nt", "dos"]):
    os_name = "windows"

if (os_name == "windows"):
    import py2exe

def get_messages():
    msgfiles = []
    for filename in os.listdir("l10n/"):
        if filename.endswith(".qm"):
            msgfiles.append("l10n/%s" % filename)
    return msgfiles

def regen_messages():
    for filename in os.listdir("l10n/"):
        if filename.endswith(".ts"):
            outFile = filename.replace(".ts", ".qm")
            command = ["lconvert", "-i", "l10n/%s" % filename, "-o", "l10n/%s" % outFile]
            subprocess.call(command)

class build_py(_build_py):
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
        regen_messages()
        _build_py.run(self)

setup(name='fluid_nexus',
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
    data_files = [("share/FluidNexus/l10n", get_messages())],
    scripts=["scripts/fluid_nexus"],
    include_package_data=True,
    zip_safe=False,
    install_requires = requires,
    cmdclass={"build_py": build_py}
)

