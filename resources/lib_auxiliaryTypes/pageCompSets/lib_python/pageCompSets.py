#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110907
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle the configuration of page composition elements for
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
from pageCompSets_command import Command
from component import Component


###############################################################################
############################ Define Global Functions ##########################
###############################################################################

# These root level functions work at a fundamental level of the system


###############################################################################
################################## Begin Class ################################
###############################################################################

class PageCompSets (Component) :

    type = "pageCompSets"
    
    def __init__(self, aProject, compType, typeConfig) :
        '''Initialize this class.'''
        
        # Make it available to the Project Class with this
        super(PageCompSets, self).__init__(aProject, compType, typeConfig)

        self.aProject   = aProject
        self.compType   = compType
        self.typeConfig = typeConfig



###############################################################################
############################# Begin Main Functions ############################
###############################################################################

    @classmethod
    def initType (cls, aProject, typeConfig) :
        '''Initialize a component in this project.  This will put all the files
        in place for this type of component so it can be rendered.'''
        super(PageCompSets, cls).initType(aProject, typeConfig)
        

    def setPageComp (self, cType, pcType) :
        '''Setup a page composition type for a specific component.'''
        
        print "Setting up page composition auxiliary for this component"
        


