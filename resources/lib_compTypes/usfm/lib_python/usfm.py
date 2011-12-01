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

import os, sys, shutil

# Load the local classes
from tools import *
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

    def __init__(self, aProject, compType, typeConfig, cid) :
        '''Initialize this class.'''
        
        # Make it available to the Project Class with this
        super(Usfm, self).__init__(aProject, compType, typeConfig, cid)
        # no file system work to be done in this method!


###############################################################################
############################# Begin Main Functions ############################
###############################################################################

    @classmethod
    def initType (cls, aProject, typeConfig) :
        '''Initialize a component in this project.  This will put all the files
        in place for this type of component so it can be rendered.'''
        super(Usfm, cls).initType(aProject, typeConfig)
        

    def initComponent(self) :
        '''This is will initiate this component and will override the function
        of the same name in the component.py module'''

        # Pull the information from the project init xml file
        initInfo = getCompInitSettings(self.project.userHome, self.project.rpmHome, self.type)

        # Bring in any know files for this component. This will also
        # create necessary folders for this component.
        self.initCompFiles(initInfo)

        self.project.writeToLog('LOG', "Initialized [" + self.cid + "] for the UsfmTex auxiliary component type.")     
        return True   


    def render (self) :
        '''Render a single project component.  Before starting, make sure
        everything necessary has been initialized.'''

        self.project.writeToLog('MSG', 'Rendered: [' + self.cid + ']', 'project.renderComponent()')

        return True



