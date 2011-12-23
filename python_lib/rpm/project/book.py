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


###############################################################################
################################## Begin Class ################################
###############################################################################

class Book (Project) :
    '''This contains basic information about a type of project.'''

    # Text types that can be used in this type of project.
    textTypes = {'Scripture' : 'usfm', 'FrontMatter' : 'usfm', 'BackMatter' : 'usfm'}

    optionalManagers = ['illustration', 'hyphenation']
    configfile = "book.xml"

    # The default managers by text type are defined in this section.
    # They are named here in this dictionary with a name:type format.
    # Where the 'name' is for this text type. The 'type' is the kind of
    # manager to use.
    usfm_Managers = {'FontUsfmMain' : 'font', 'FormatUsfmMain' : 'format', 'StyleUsfmMain' : 'style',
        'FontUsfmFront' : 'font', 'FormatUsfmFront' : 'format', 'StyleUsfmFront' : 'style'}


