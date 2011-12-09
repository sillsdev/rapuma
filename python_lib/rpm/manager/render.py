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
import render_command


###############################################################################
################################## Begin Class ################################
###############################################################################

class Render (Manager) :

###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def initManager (self) :
        '''Initialize a book project.'''

        print "Initializing Render Manager"
        super(Render, self).initManager()

