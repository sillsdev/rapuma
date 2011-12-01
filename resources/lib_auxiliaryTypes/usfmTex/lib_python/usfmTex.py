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
    
    def __init__(self, aProject, auxConfig, typeConfig, aid) :
        '''Initialize this class.'''
        
        # Make it available to the Project Class with this
        super(UsfmTex, self).__init__(aProject, auxConfig, typeConfig, aid)
        # no file system work to be done in this method!


###############################################################################
############################# Begin Main Functions ############################
###############################################################################

    @classmethod
    def initType (cls, aProject, typeConfig) :
        '''Initialize a component in this project.  This will put all the files
        in place for this type of component so it can be rendered.'''
        super(UsfmTex, cls).initType(aProject, typeConfig)


    def initAuxiliary (self) :
        '''This is will initiate this component and will override the function
        of the same name in the component.py module'''

        # Bail out now if this has already been initialized
        if self.initialized :
            return True

        print dir(self)

        # Start with default settings
        self._initConfig = getAuxInitSettings(self.project.userHome, self.project.rpmHome, self.type)
        # Set values for this method
        setattr(self, 'processFolderName', self._initConfig['Folders']['Process']['name'])
        setattr(self, 'texMacroSetupFileName', self._initConfig['Files']['TexMacroSetup']['name'])
        setattr(self, 'processFolder', os.path.join(self.project.projHome, self.processFolderName))
        setattr(self, 'texMacroSetupFile', os.path.join(self.processFolder, self.texMacroSetupFileName))
        setattr(self, 'formatConfFile', os.path.join(self.processFolder, self.formatFileName))
        setattr(self, 'defaultFormatValuesFile', os.path.join(self.project.rpmAuxTypes, self.type, self.type + '_values.xml'))

        # Create all necessary (empty) folders and bring in any known
        # files for this component. (This will do both.)
        self.initAuxFiles(self.type, self._initConfig)

        # Get our format settings, use defaults if necessary
        if not os.path.isfile(self.formatConfFile) or os.path.getsize(self.formatConfFile) == 0 :
            self._formatConfig = getXMLSettings(self.defaultFormatValuesFile)
        else :
            self._formatConfig = ConfigObj(self.formatConfFile)

        # Create the TeX Macro master setup file
        if not os.path.isfile(self.texMacroSetupFile) or os.path.getsize(self.texMacroSetupFile) == 0 :
            print 'file not found!'

        self.project.writeToLog('LOG', "Initialized [" + self.aid + "] for the UsfmTex auxiliary component type.")
        return True


    def setTexMacros (self, macros) :
        '''Indicate to the system what TeX macros are going to be used for
        processing this USFM text.'''
        
        self.project.writeToLog('LOG', "Setting up this project to use the [" + macros + "] TeX macros.")     
        self.initialized = True
        return True
       
        
