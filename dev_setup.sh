#!/bin/sh

# Setup a development for Rapuma so it runs from the repo

export PYTHONPATH=`pwd`/python_lib:$PYTHONPATH
export RAPUMA_CMD=`pwd`/bin/rapuma
export RAPUMA_BASE=`pwd`

