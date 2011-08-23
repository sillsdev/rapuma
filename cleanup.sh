#!/bin/sh

# Clean up the project, remove most of the unnecessary files

find . -name "*~" -exec rm -rfv {} \;
find . -name "*.pyc" -exec rm -rfv {} \;
find . -name "*.bak" -exec rm -rfv {} \;
