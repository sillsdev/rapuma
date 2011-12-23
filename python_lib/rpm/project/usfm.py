#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project tasks.

# History:
# 20111222 - djd - Started with intial file


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


class Usfm (Project) :
    '''This class contains information about a type of component used in type of project.'''

#    # The default managers are named here in this dictionary with name:type
#    # format. Where the 'name' is for this text type. The 'type' is the kind of
#    # manager to use.
#    # by the Book project type right here.
#    defaultManagers = {'FontUsfmMain' : 'font', 'FormatUsfmMain' : 'format', 'StyleUsfmMain' : 'style',
#        'FontUsfmFront' : 'font', 'FormatUsfmFront' : 'format', 'StyleUsfmFront' : 'style'}

    terminal('Loading: ' + usfm)

    components = {'scripture' : ['mat', 'mrk', 'luk', 'jhn', 'act', 'rom', '1co', '2co', 'gal', 'eph', 'php', 'col', '1th', '2th', '1ti', '2ti', 'tit', 'phm', 'heb', 'jas', '1pe', '2pe', '1jn', '2jn', '3jn', 'jud', 'rev'] }


