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
from fontsTex_command import Command
from auxiliary import Auxiliary


###############################################################################
############################ Define Global Functions ##########################
###############################################################################

# These root level functions work at a fundamental level of the system


###############################################################################
################################## Begin Class ################################
###############################################################################

class FontsTex (Auxiliary) :

    type = "fontsTex"
    
    def __init__(self, aProject, auxConfig, typeConfig) :
        '''Initialize this class.'''
        
        # Make it available to the Project Class with this
        super(FontsTex, self).__init__(aProject, auxConfig, typeConfig)


###############################################################################
############################# Begin Main Functions ############################
###############################################################################

    @classmethod
    def initType (cls, aProject, typeConfig) :
        '''Initialize a component in this project.  This will put all the files
        in place for this type of component so it can be rendered.'''
        super(FontsTex, cls).initType(aProject, typeConfig)


    def initAuxiliary (self, aux) :
        '''Initialize this component.  This is a generic named function that
        will be called from the project initialisation process.'''
        
        self.project.writeToLog('LOG', "Initialized [" + aux + "] for the FontsTex auxiliary component type.")     
        return True


    def makeContentFontFile (self, aux) :
        '''Create a font file for the content font.'''
        
        initSettings = getXMLSettings('fontsTex_init.xml')
        folderPath = initSettings['Folders']['FontFolder']['name']
        fileName = initSettings['Files']['FontDefFile']['name']
        typeFace = aProject._projConfig['Auxiliaries'][aux]['primary']['TypefaceRegular']['file']
        regFilePath = folderPath + typeFace + aProject._projConfig['Auxiliaries'][aux]['primary']['TypefaceRegular']['file']

        regular = "\\def\\regular{" + regFilePath

#\def\bold{"[../Fonts/CharisSIL/CharisSILB.ttf]/GR"}
#\def\italic{"[../Fonts/CharisSIL/CharisSILI.ttf]/GR"}
#\def\bolditalic{"[../Fonts/CharisSIL/CharisSILBI.ttf]/GR"}


    def setFont (self, ftype, font, rank) :
        '''Setup a font for a specific typeface.'''

        # It is expected that all the necessary meta data for this font is in
        # a file located with the font. The system expects to find it in:
        # ~/lib_share/Fonts/[FontID]
        # There will be a minimal number of fonts in the system but we will look
        # in the user area first. That is where the fonts really should be kept.
        # If it is unable to find the font in either the user area or the system
        # resources shared area, it will fail.
        if os.path.isfile(os.path.join(self.project.userFonts, font, font + '.xml')) :
            self.project.writeToLog('LOG', 'Found ' + font + '.xml in user resources.')
            fontDir = os.path.join(self.project.userFonts, font)
            fontInfo = os.path.join(self.project.userFonts, font, font + '.xml')
        elif os.path.isfile(os.path.join(self.project.rpmFonts, font, font + '.xml')) :
            self.project.writeToLog('LOG', 'Found ' + font + '.xml in RPM resources.')
            fontDir = os.path.join(self.project.rpmFonts, font)
            fontInfo = os.path.join(self.project.rpmFonts, font, font + '.xml')
        else :
            self.project.writeToLog('ERR', 'Halt! ' + font + '.xml not found.')
            return False

        # Copy the contents of the target font folder to the project Fonts folder
        if not os.path.isdir(os.path.join(self.project.projHome, 'Fonts')) :
            os.mkdir(os.path.join(self.project.projHome, 'Fonts'))

        # FIXME-Later: At this point it might be nice if we queried the settings
        # (xml) file for the exact files that need to be copied into the
        # project.  For now we'll just do a blind copy of the folder and take
        # everything and trust it is all good to have in the project.'
        if not os.path.isdir(os.path.join(self.project.projHome, 'Fonts', font)) :
            shutil.copytree(fontDir, os.path.join(self.project.projHome, 'Fonts', font))
        else :
            self.project.writeToLog('ERR', 'Folder already there. Did not copy ' + font + ' to Fonts folder.')

        # Now inject the font info into the fontset component section in the
        # project.conf. Enough information should be there for the component init.
        fInfo = getXMLSettings(fontInfo)
        self.auxConfig[rank] = fInfo.dict()

        self.project.writeOutProjConfFile = True
        self.project.writeToLog('MSG', font + ' font setup information added to [' + ftype + '] component')     
        
