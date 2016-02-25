#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (sparkycbr at gmail dot com)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle upper level project tasks for the book media type.

# History:
# 20111207 - djd - Started with initial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

#import os


# Load the local classes
#from rapuma.core.tools import *
from rapuma.manager.project      import Project


###############################################################################
################################## Begin Class ################################
###############################################################################

class Book (Project) :
    '''This contains basic information and functions for a type of project media.'''


    configFile = "book.xml"



