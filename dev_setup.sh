#!/bin/sh

# Setup a development for Rapuma so it runs from the repo

export PYTHONPATH = `pwd`/python_lib : $PYTHONPATH
export RPM_CMD = `pwd`/bin/rapuma
export RPM_BASE = `pwd`