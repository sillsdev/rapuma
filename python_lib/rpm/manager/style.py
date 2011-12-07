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
from project import Project
import style_command


###############################################################################
################################## Begin Class ################################
###############################################################################

class Style (Project) :

###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def initManager (self) :
        '''Initialize the style manager.'''

        print "Initializing Style Manager"
        super(Style, self).initManager()


