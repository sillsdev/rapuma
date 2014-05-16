#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111210
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book component group tasks.

###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, codecs


# Load the local classes
from rapuma.core.tools import Tools


###############################################################################
################################## Begin Class ################################
###############################################################################

class Group (object) :

    # Shared values
    xmlConfFile     = 'group.xml'

    def __init__(self, project, cfg, parent = None) :
        '''Initialize this class.'''

        self.project = project
        self.cfg = cfg
        self.parent = parent or project
        self.managers = {}
        self.tools = Tools()


    def render(self) :
        '''Render a group.'''

        self.tools.terminal("Warning: Calling dummy rendering in the group class.")


