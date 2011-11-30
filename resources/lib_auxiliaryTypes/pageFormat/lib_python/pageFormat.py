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
from tools import *
from pageFormat_command import Command
from auxiliary import Auxiliary


###############################################################################
############################ Define Global Functions ##########################
###############################################################################

# These root level functions work at a fundamental level of the system


###############################################################################
################################## Begin Class ################################
###############################################################################

class PageFormat (Auxiliary) :

    type = "pageFormat"
    
    def __init__(self, aProject, auxConfig, typeConfig, aid) :
        '''Initialize this class.'''
        
        # Make it available to the Project Class with this
        super(PageFormat, self).__init__(aProject, auxConfig, typeConfig, aid)
        # no file system work to be done in this method!


###############################################################################
############################# Begin Main Functions ############################
###############################################################################

    @classmethod
    def initType (cls, aProject, typeConfig) :
        '''Initialize a component in this project.  This will put all the files
        in place for this type of component so it can be rendered.'''
        super(PageFormat, cls).initType(aProject, typeConfig)

    def initAuxiliary (self) :
        '''Initialize this component.  This is a generic named function that
        will be called from the project initialisation process.'''

        # Bail out now if this has already been initialized
        if self.initialized :
            return True

        # Start with default settings
        self._formatConfig = {}
        self._defaultConfig = {}
        self._initConfig = getAuxInitSettings(self.project.userHome, self.project.rpmHome, self.type)
        # Set values for this method
        setattr(self, 'processFolderName', self._initConfig['Folders']['Process']['name'])
        setattr(self, 'formatFileName', self._initConfig['Files']['Format']['name'])
        setattr(self, 'processFolder', os.path.join(self.project.projHome, self.processFolderName))
        setattr(self, 'formatConfFile', os.path.join(self.processFolder, self.formatFileName))
        setattr(self, 'defaultFormatValuesFile', os.path.join(self.project.rpmAuxTypes, self.type, self.type + '_values.xml'))

        # Bring in any known files for this auxiliary
        self.initAuxFiles(self.type, self._initConfig)

        # Make a format file if it isn't there already then
        # load the project's format configuration. Or, load
        # the existing file
        self._defaultConfig = getXMLSettings(self.defaultFormatValuesFile)
        print self.defaultFormatValuesFile
        if not os.path.isfile(self.formatConfFile) :
            writeConfFile(self._formatConfig, self.formatFileName, self.processFolder)
        else :
            self._formatConfig = ConfigObj(self.formatConfFile)

        self.project.writeToLog('LOG', "Initialized [" + self.aid + "] for the PageFormat auxiliary component type.")     
        self.initialized = True
        return True






