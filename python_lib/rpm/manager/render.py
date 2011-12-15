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
import render_command as rndCmd


###############################################################################
################################## Begin Class ################################
###############################################################################

class Render (Manager) :

    def __init__(self, project) :
        '''Do the primary initialization for this manager.'''

        super(Render, self).__init__(project)

        terminal("Initializing Render Manager")

        # Add commands for this manager
#        project.addCommand("???", rndCmd.???(self))

        # Set values for this manager
        self.renderers          = ['tex', 'vmapper']


###############################################################################
############################ Project Level Functions ##########################
###############################################################################



