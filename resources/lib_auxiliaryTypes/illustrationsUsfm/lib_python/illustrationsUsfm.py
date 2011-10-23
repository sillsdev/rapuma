#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110907
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle the production of vernacular maps for publication
# projects.

# History:
# 20110907 - djd - Intial draft


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, sys

# Load the local classes
from illustrationsUsfm_command import Command
from auxiliary import Auxiliary


###############################################################################
############################ Define Global Functions ##########################
###############################################################################

# These root level functions work at a fundamental level of the system


###############################################################################
################################## Begin Class ################################
###############################################################################

class IllustrationsUsfm (Auxiliary) :

    type = 'illustrationsUsfm'

    def __init__(self, aProject, auxConfig, typeConfig) :
        '''Initialize this class.'''
        
        # Make it available to the Project Class with this
        super(IllustrationsUsfm, self).__init__(aProject, auxConfig, typeConfig)


###############################################################################
############################# Begin Main Functions ############################
###############################################################################

    @classmethod
    def initType (cls, aProject, typeConfig) :
        '''Initialize a component in this project.  This will put all the files
        in place for this type of component so it can be rendered.'''
        super(IllustrationsUsfm, cls).initType(aProject, typeConfig)
        
        
    def initAuxiliary (self, aux) :
        '''Initialize this component.  This is a generic named function that
        will be called from the project initialisation process.'''
        
        self.project.writeToLog('LOG', "Initialized [" + aux + "] for the IllustrationsUsfm auxiliary component type.")     
        return True



