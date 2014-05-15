#!/bin/sh

# Setup a development for Rapuma so it runs from the repo

export PYTHONPATH=`pwd`/lib:$PYTHONPATH
export RAPUMA_CMD=`pwd`/scripts/rapuma
export RAPUMA_BASE=`pwd`

export PYTHONPATH=`pwd`/lib:$PYTHONPATH

echo
echo "Rapuma development environment is now set up."
echo
