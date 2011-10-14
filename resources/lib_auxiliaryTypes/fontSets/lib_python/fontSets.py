#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110907
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle the management of fonts for publication projects.

# History:
# 20110907 - djd - Intial draft


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, sys

# Load the local classes
from fontSets_command import Command
from auxiliary import Auxiliary


###############################################################################
############################ Define Global Functions ##########################
###############################################################################

# These root level functions work at a fundamental level of the system


###############################################################################
################################## Begin Class ################################
###############################################################################

class FontSets (Auxiliary) :
    type = "fontSets"
    
    def __init__(self, aProject, auxType, typeConfig) :
        '''Initialize this class.'''
        
        # Make it available to the Project Class with this
        super(FontSets, self).__init__(aProject, auxType, typeConfig)

        self.aProject   = aProject
        self.auxType   = auxType
        self.typeConfig = typeConfig



###############################################################################
############################# Begin Main Functions ############################
###############################################################################

    @classmethod
    def initType (cls, aProject, typeConfig) :
        '''Initialize a component in this project.  This will put all the files
        in place for this type of component so it can be rendered.'''
        super(FontSets, cls).initType(aProject, typeConfig)
        
        
    def preProcess(self) :
        # do pre processing of a usfmtex component here
        print "PreProcessing an FontSets component"
        
        
    def setFont (self, ftype, font) :
        '''Setup a font for a specific typeface.'''
        
        # It is expected that all the necessary meta data for this font is in
        # a file located with the font. The system expects to find it in:
        # ~/lib_share/Fonts/[FontID]
        # There will be a minimal number of fonts in the system but we will look
        # in the user area first. That is where the fonts really should be kept.
        # If it is unable to find the font in either the user area or the system
        # resources shared area, it will fail.
        if os.path.isfile(os.path.join(self.aProject.userFonts, font, font + '.xml')) :
            self.aProject.writeToLog('LOG', 'Found ' + font + '.xml in user resources.')
            fontDir = os.path.join(self.aProject.userFonts, font)
            fontInfo = os.path.join(self.aProject.userFonts, font, font + '.xml')
        elif os.path.isfile(os.path.join(self.aProject.rpmFonts, font, font + '.xml')) :
            self.aProject.writeToLog('LOG', 'Found ' + font + '.xml in RPM resources.')
            fontDir = os.path.join(self.aProject.rpmFonts, font)
            fontInfo = os.path.join(self.aProject.rpmFonts, font, font + '.xml')
        else :
            self.aProject.writeToLog('ERR', 'Halt! ' + font + '.xml not found.')
            return False

        # Now inject the font info into the fontset component section in the
        # project.conf. Enough information should be there for the component init.

        ############ START HERE ############

        self.aProject.writeToLog('MSG', font + ' font setup information added to [' + ftype + '] component')     
        
