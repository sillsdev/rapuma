#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle upper level project tasks for the book media type.

# History:
# 20111207 - djd - Started with intial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os


# Load the local classes
from rapuma.core.tools import *
from rapuma.project.project import Project


###############################################################################
################################## Begin Class ################################
###############################################################################

class Book (Project) :
    '''This contains basic information about a type of project.'''

    configFile = "book.xml"


