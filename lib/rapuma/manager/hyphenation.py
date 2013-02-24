#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle generic project hyphenation tasks.

# History:
# 20111207 - djd - Started with intial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, re


# Load the local classes
from rapuma.core.tools import *
from rapuma.project.manager import Manager


###############################################################################
################################## Begin Class ################################
###############################################################################

class Hyphenation (Manager) :

#    _hyphens_re = re.compile(u'\u002D|\u00AD|\u2010') # Don't include U+2011 so we don't break on it.

    # Shared values
    xmlConfFile     = 'hyphenation.xml'


###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def __init__(self, project, cfg, cType) :
        '''Initialize the Hyphenation manager.'''

        super(Hyphenation, self).__init__(project, cfg)

        # Set values for this manager
        self.project                    = project
        self.cfg                        = cfg
        self.cType                      = cType

###############################################################################
############################ Manager Level Functions ##########################
###############################################################################

    def hardenExceptWords (self, words) :
        '''Harden a list of hyphated words by changing soft hyphens
        for non-breaking hyphens.'''

        for w in list(words) :
            nw = re.sub(u'\u002D', u'\u2011', w)
            if w != nw :
                words.add(nw)
            words.remove(w)

        return words





