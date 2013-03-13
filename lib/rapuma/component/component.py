#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111210
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project tasks.

# History:
# 20111210 - djd - Started with intial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, codecs


# Load the local classes
from rapuma.core.tools import *


###############################################################################
################################## Begin Class ################################
###############################################################################

class Component (object) :



    def __init__(self, project, cfg, parent = None) :
        '''Initialize this class.'''

        self.project = project
        self.cfg = cfg
        self.parent = parent or project
        self.managers = {}


    def render(self) :
        '''Render a component.'''

        terminal("Warning: Calling dummy rendering in the component class.")


