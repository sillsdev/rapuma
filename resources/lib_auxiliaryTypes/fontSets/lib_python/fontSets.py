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

import os, sys, shutil
from configobj import ConfigObj, Section

# Load the local classes
from tools import *
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

        # Take out only the stuff from the proj.comp that this aux needs and
        # pass that on to the stuff below.
        self.typeSettings = ConfigObj()
        self.typeSettings['AuxiliaryTypes'] = {} 
        print self.typeSettings
        self.typeSettings.merge(aProject._projConfig['AuxiliaryTypes'][auxType['auxType']])
        print self.typeSettings

        # From the installedAuxiliaries settings we can get a list of this type
        # of auxiliary that is installed.  Bring in all their settings to so
        # they can be worked with too.
        for at in self.typeSettings['installedAuxiliaries'] :
            print at

        print self.typeSettings

# FIXME: How do I get the local settings to be linked with the global settings
# so that when the class is done the results will be written out?

        self.aProject   = aProject
        self.auxType    = auxType
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

        # Copy the contents of the target font folder to the project Fonts folder
        if not os.path.isdir(os.path.join(self.aProject.projHome, 'Fonts')) :
            os.mkdir(os.path.join(self.aProject.projHome, 'Fonts'))

        if not os.path.isdir(os.path.join(self.aProject.projHome, 'Fonts')) :
            shutil.copytree(fontDir, os.path.join(self.aProject.projHome, 'Fonts', font))
        else :
            self.aProject.writeToLog('ERR', 'Folder already there. Did not copy ' + font + ' to Fonts folder.')

        # Now inject the font info into the fontset component section in the
        # project.conf. Enough information should be there for the component init.
        fInfo = getXMLSettings(fontInfo)
        self.aProject._projConfig['Auxiliaries'][ftype].merge(fInfo)


        ############ START HERE ############
        self.writeOutProjConfFile = True
        self.aProject.writeToLog('MSG', font + ' font setup information added to [' + ftype + '] component')     
        
