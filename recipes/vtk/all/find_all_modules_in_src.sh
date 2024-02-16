#! /bin/sh

find $1 -name "vtk.module" -exec head -2 '{}' \; | grep -v ^NAME$ | grep "^  VTK::" | cut -c8- | sort | uniq | sed 's/\(.*\)/    "\1",/' > vtk-modules.txt
