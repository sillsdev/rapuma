#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111019
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle the management of USFM TeX macros for publication
# projects.

# History:
# 20111019 - djd - Intial draft


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, sys, shutil
from configobj import ConfigObj, Section

# Load the local classes
from tools import *
from usfmTex_command import Command
from auxiliary import Auxiliary


###############################################################################
############################ Define Global Functions ##########################
###############################################################################

# These root level functions work at a fundamental level of the system


###############################################################################
################################## Begin Class ################################
###############################################################################

class UsfmTex (Auxiliary) :

    type = "usfmTex"
    
    def __init__(self, aProject, auxConfig, typeConfig) :
        '''Initialize this class.'''
        
        # Make it available to the Project Class with this
        super(UsfmTex, self).__init__(aProject, auxConfig, typeConfig)


###############################################################################
############################# Begin Main Functions ############################
###############################################################################

    @classmethod
    def initType (cls, aProject, typeConfig) :
        '''Initialize a component in this project.  This will put all the files
        in place for this type of component so it can be rendered.'''
        super(UsfmTex, cls).initType(aProject, typeConfig)


    def initAuxiliary (self, aux) :
        '''Initialize this component.  This is a generic named function that
        will be called from the project initialisation process.'''
        
        self.project.writeToLog('LOG', "Initialized xxxxxx [" + aux + "] for the UsfmTex auxiliary component type.")     
        return True


    def setTexMacros (self, macros) :
        '''Indicate to the system what TeX macros are going to be used for
        processing this USFM text.'''
        
        self.project.writeToLog('LOG', "Setting up this project to use the [" + macros + "] TeX macros.")     
        return True
       
        
