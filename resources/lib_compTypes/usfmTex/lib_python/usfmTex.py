#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110811
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project infrastructure tasks.

# History:
# 20110811 - djd - Initial draft


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, sys

# Load the local classes
from usfmTex_command import Command
from component import Component


###############################################################################
############################ Define Global Functions ##########################
###############################################################################

# These root level functions work at a fundamental level of the system


###############################################################################
################################## Begin Class ################################
###############################################################################

class UsfmTex (Component) :

    def __init__(self, aProject) :
        '''Initialize this class.'''
        
        # Make it available to the Project Class with this
        super(UsfmTex, self).__init__(aProject._projConfig, aProject._projInit, aProject._userConfig, aProject.projHome, aProject.userHome, aProject.tipeHome)

        # Set class vars
        self._projConfig = aProject._projConfig
        self._projInit = aProject._projInit
        self._userConfig = aProject._userConfig
        self.projHome = aProject.projHome
        self.userHome = aProject.userHome
        self.tipeHome = aProject.tipeHome




###############################################################################
############################# Begin Main Functions ############################
###############################################################################

    @classmethod
    def initType (cls, aProject) :
        '''Initialize a component in this project.  This will put all the files
        in place for this type of component so it can be rendered.'''
        
        
        print "(usfmTex.initType) Initializing this component:", cls
        
    def preProcess(self) :
        # do pre processing of a usfmtex component here
        print "PreProcessing a usfmtex component""

