#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project tasks.

# History:
# 20111207 - djd - Started with intial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os


# Load the local classes
from tools import *
from manager import Manager
import style_command as styCmd


###############################################################################
################################## Begin Class ################################
###############################################################################

class Style (Manager) :

    # Shared values
    xmlConfFile     = ''
    xmlInitFile     = ''

    def __init__(self, project) :
        '''Do the primary initialization for this manager.'''

        super(Style, self).__init__(project)

        terminal("Initializing Style Manager")

        # Add commands for this manager
#        project.addCommand("???", styCmd.???(self))


###############################################################################
############################ Project Level Functions ##########################
###############################################################################



