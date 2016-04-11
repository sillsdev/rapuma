#!/bin/sh

# A simple script that tries to get everything in place for for Rapuma
# to install. This assumes there are a few of the core things in place
# like the repository paths, etc. This will try to put the rest of the
# packages in place. This is very experimental.

# Make sure the repo is up to date
sudo apt-get update
sudo apt-get upgrade

# This is the basic set of packages needed to run Rapuma from the CLI
# (Command Line Interface) and headless access by a web server-based
# interface:

sudo apt-get install python-configobj python-argparse python-pypdf pdftk librsvg2-bin

# Now get the USFM parser installed, first down load
sudo apt-get install mercurial
hg clone http://hg.palaso.org/palaso-python ~/Projects/palaso-python
# Now setup and install
cd ~/Projects/palaso-python
./setup.py --nokmn build
sudo ./setup.py --nokmn install

