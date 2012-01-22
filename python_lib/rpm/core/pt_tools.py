#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110823
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This module will hold all the miscellaneous functions that are used for
# Paratext project processing

# History:
# 20120122 - djd - New file


###############################################################################
################################## Tools Class ################################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, sys
from datetime import *
from xml.etree import ElementTree
from configobj import ConfigObj, Section
from tools import *


###############################################################################
############################ Functions Begin Here #############################
###############################################################################


def parseSSF (fileName) :
    '''Parse a Paratext SSF file and return a configobj to be used in
    other processes.'''

    # FIXME: This will take a little doing to generalize this so for
    # now I'll return a configobj with the stuff I need to have for testing.
    thisObj = ConfigObj()
    buildConfSection(thisObj, 'ScriptureText')
    thisObj['ScriptureText']['Name'] = 'SPT'
    thisObj['ScriptureText']['FileNamePostPart'] = 'SPT.SFM'
    thisObj['ScriptureText']['FileNameBookNameForm'] = '41MAT'
    thisObj['ScriptureText']['DefaultFont'] = 'Padauk'

    return thisObj


