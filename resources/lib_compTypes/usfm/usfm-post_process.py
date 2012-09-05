#!/usr/bin/python
# -*- coding: utf_8 -*-


###############################################################################
############################## Setup Environment ##############################
###############################################################################

import os, sys

# Set the RPM base program path
rpmHome = os.environ.get('RPM_BASE')
if not rpmHome :
    rpmHome = os.path.join('usr', 'share', 'rpm')
    os.environ['RPM_BASE'] = rpmHome

# Set our paths to the RPM resources we might need
sys.path.insert(0, os.path.join(rpmHome, 'python_lib', 'rpm', 'core'))

from tools import *

###############################################################################
############################## Post Process Code ##############################
###############################################################################

# Report what we are doing
print fName(sys.argv[0]) + ': Post processes run on: ' + fName(sys.argv[1])


# Do something

# Return "0" if succeful
sys.exit(0)


