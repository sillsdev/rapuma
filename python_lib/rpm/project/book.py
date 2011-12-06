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


###############################################################################
################################## Begin Class ################################
###############################################################################

class Book (object) :

    def __init__(self, projConfig) :
        '''Instantiate this class.'''

        self._projConfig            = projConfig

###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def initBook (self) :
        '''Initialize a book project.'''

        # Some things this project type needs to know about
        # Valid Component Types: usfm, admin, maps, notes
        # Project Managers: font, format, style, illustration, hyphenation, render

        pass
