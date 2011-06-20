#!/bin/bash
for file in `ls FluidNexus/ui/*.ui`; 
do 
    echo "Generating python file for $file";
    file_ui=$(echo ${file%.*}UI.py); 
    pyuic4 $file -o $file_ui
done
