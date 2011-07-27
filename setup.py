#!/usr/bin/env python

import os
import subprocess
import sys

from setuptools.command.build_py import build_py as _build_py
from setuptools import setup, find_packages

import FluidNexus

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README')).read()
CHANGES = open(os.path.join(here, 'CHANGES')).read()

requires = [
        'textile',
        'simplejson',
        'pybonjour',
        'sqlalchemy',
        ]

if sys.version_info[:3] < (2,5,0):
    requires.append('pysqlite')

def get_messages():
    msgfiles = []
    for filename in os.listdir("po/"):
        if filename.endswith(".qm"):
            msgfiles.append("po/%s" % filename)
    return msgfiles

def regen_messages():
    po_files = []
    for filename in os.listdir("po/"):
        if filename.endswith(".po"):
            po_files.append("-i")
            po_files.append(filename)
            po_files.append("-o")
            outFile = filename.replace(".po", ".qm")
            command = ["lconvert", "-i", "po/%s" % filename, "-o", "po/%s" % outFile]
            subprocess.call(command)

class build_py(_build_py):
    def run(self):
        uis = []
        for filename in os.listdir("FluidNexus/ui/"):
            if filename.endswith(".ui"):
                uis.append(filename)

        for ui in uis:
            out = ui.replace(".ui", "UI.py")
            command = ["pyuic4", "-o", out, ui]
            subprocess.call(command)
            self.byte_compile(out)

        res = "FluidNexus/ui/FluidNexus_rc.py"
        command = ["pyrcc4", "FluidNexus/ui/FluidNexus.qrc", "-o", res]
        subprocess.call(command)
        regen_messages()
        _build_py.run(self)

setup(name='FluidNexus',
    version=FluidNexus.__version__,
    description='PyQt4 application that enables one to share messages and data independent of centralized data networks',
    author='Nicholas Knouf',
    author_email='fluidnexus@fluidnexus.net',
    url='http://fluidnexus.net',
    long_description=README + '\n\n' +  CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    keywords='web wsgi bfg pylons pyramid',
    packages=find_packages(),
    package_data={"FluidNexus.ui":["*.ui"]},
    data_file = [("/usr/share/FluidNexus/lang", get_messages())],
    scripts=["scripts/fluid_nexus"],
    include_package_data=True,
    zip_safe=False,
    install_requires = requires,
    cmdclass={"build_py": build_py}
)

