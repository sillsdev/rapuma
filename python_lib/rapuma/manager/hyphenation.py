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


###############################################################################
################################## Begin Class ################################
###############################################################################

class Hyphenation (Manager) :

    # Shared values
    xmlConfFile     = 'hyphenation.xml'


###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def __init__(self, project, cfg, cType) :
        '''Initialize the Hyphenation manager.'''

        '''Do the primary initialization for this manager.'''

        super(Hyphenation, self).__init__(project, cfg)


        print "Initializing Hyphenation Manager"


# FIXME: 
# Functions will need to be added that will process hyphenation data into a
# file that can be used by the renderer to hyphenate the text it is working
# with. Initially this will be for TeX rendering but can/should be expanded
# to other types of renderers.



