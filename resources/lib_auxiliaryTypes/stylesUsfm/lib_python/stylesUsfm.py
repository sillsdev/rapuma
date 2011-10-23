#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111013
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle the configuration of style type elements for
# publication projects.

# History:
# 20111013 - djd - Intial draft


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, sys

# Load the local classes
from stylesUsfm_command import Command
from auxiliary import Auxiliary


###############################################################################
############################ Define Global Functions ##########################
###############################################################################

# These root level functions work at a fundamental level of the system


###############################################################################
################################## Begin Class ################################
###############################################################################

class StylesUsfm (Auxiliary) :

    type = "stylesUsfm"
    
    def __init__(self, aProject, auxConfig, typeConfig) :
        '''Initialize this class.'''
        
        # Make it available to the Project Class with this
        super(StylesUsfm, self).__init__(aProject, auxConfig, typeConfig)


###############################################################################
############################# Begin Main Functions ############################
###############################################################################

    @classmethod
    def initType (cls, aProject, typeConfig) :
        '''Initialize a component in this project.  This will put all the files
        in place for this type of component so it can be rendered.'''
        super(StylesUsfm, cls).initType(aProject, typeConfig)
        

    def initAuxiliary (self, aux) :
        '''Initialize this component.  This is a generic named function that
        will be called from the project initialisation process.'''
        
        self.project.writeToLog('LOG', "Initialized [" + aux + "] for the StylesUsfm auxiliary component type.")     
        return True


    def setStyle (self, ctype, style) :
        '''Setup a style type for a specific component.'''
        
        print "Setting up style type auxiliary for this component"
        


