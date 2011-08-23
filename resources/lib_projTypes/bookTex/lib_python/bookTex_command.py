#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110727
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle specific commands for this project type.  General
# project commands can be found in the proj_command.py module.  This relys a lot
# on the optparse lib.  Documentation can be found here:
# http://docs.python.org/library/optparse.html

# History:
# 20110727 - djd - Begin initial draft


###############################################################################
################################# Command Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os
from optparse import OptionParser
from sys_command import Command

###############################################################################
########################### Command Classes Go Here ###########################
###############################################################################
# Insert the commands you want visable to the system here in the order you want
# them to appear when listed.


