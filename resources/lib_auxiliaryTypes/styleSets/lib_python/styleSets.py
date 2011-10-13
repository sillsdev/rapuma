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
from styleSets_command import Command
from component import Component


###############################################################################
############################ Define Global Functions ##########################
###############################################################################

# These root level functions work at a fundamental level of the system


###############################################################################
################################## Begin Class ################################
###############################################################################

class StyleSets (Component) :

    type = "styleSets"
    
    def __init__(self, aProject, compType, typeConfig) :
        '''Initialize this class.'''
        
        # Make it available to the Project Class with this
        super(StyleSets, self).__init__(aProject, compType, typeConfig)

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
        super(StyleSets, cls).initType(aProject, typeConfig)
        

    def setStyle (self, cType, style) :
        '''Setup a style type for a specific component.'''
        
        print "Setting up style type auxiliary for this component"
        


