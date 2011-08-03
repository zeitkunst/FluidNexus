#!/bin/bash

cd "/c/Documents and Settings/Nicholas Knouf/Development/Android/FluidNexus"

echo "Removing dist dir"
rm -Rf dist

echo "Running py2exe"
python setup.py py2exe

echo "Running InnoSetup compiler"
iscc scripts/fluid_nexus.iss
