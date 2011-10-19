#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110823
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle USFM component processing tasks.

# History:
# 20110823 - djd - Started with intial file from RPM project


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, sys

# Load the local classes
from usfm_command import Command
from component import Component


###############################################################################
############################ Define Global Functions ##########################
###############################################################################

# These root level functions work at a fundamental level of the system


###############################################################################
################################## Begin Class ################################
###############################################################################

class Usfm (Component) :
    type = "usfm"

    def __init__(self, aProject, compType, typeConfig) :
        '''Initialize this class.'''
        
        # Make it available to the Project Class with this
        super(Usfm, self).__init__(aProject, compType, typeConfig)




###############################################################################
############################# Begin Main Functions ############################
###############################################################################

    @classmethod
    def initType (cls, aProject, typeConfig) :
        '''Initialize a component in this project.  This will put all the files
        in place for this type of component so it can be rendered.'''
        super(Usfm, cls).initType(aProject, typeConfig)
        
        print "(usfm.initType) Initializing this component:", cls


    def preProcess(self) :
        # Do pre processing of a usfm component here
        print "PreProcessing a USFM component"
        
        

