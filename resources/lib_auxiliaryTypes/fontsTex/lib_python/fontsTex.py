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
    
    def __init__(self, aProject, auxConfig, typeConfig, aid) :
        '''Initialize this class.'''
        
        # Make it available to the Project Class with this
        super(FontsTex, self).__init__(aProject, auxConfig, typeConfig, aid)
        # no file system work to be done in this method!


###############################################################################
############################# Begin Main Functions ############################
###############################################################################

    @classmethod
    def initType (cls, aProject, typeConfig) :
        '''Initialize a component in this project.  This will put all the files
        in place for this type of component so it can be rendered.'''
        super(FontsTex, cls).initType(aProject, typeConfig)


    def initAuxiliary (self) :
        '''Initialize this component.  This is a generic named function that
        will be called from the project initialisation process.'''
        
        # Bail out now if this has already been initialized
        if self.initialized :
            return True
        
        # Pull the information from the project init xml file
        initInfo = getAuxInitSettings(self.project.userHome, self.project.rpmHome, self.type)

        # Project Font folder path
        projFontFolder = os.path.join(self.project.projHome, initInfo['Folders']['Fonts']['name'])
        
        # Bring in any know files for this component
        self.initAuxFiles(self.type, initInfo)
        
        # Init (copy) the fonts that have been recored with the project
        for aux in self.project._projConfig['Auxiliaries'].keys() :
            if self.project._projConfig['Auxiliaries'][self.aid]['auxType'] == self.type :
                # FIXME: Right now we only allow for one primary font for each
                # font aux, we need to allow for a secondary and tertiary too.
                for tf in self.project._projConfig['Auxiliaries'][self.aid]['primary'].keys() :
                    fontInfo = getFontInitSettings(self.project.userHome, self.project.rpmHome, self.project._projConfig['Auxiliaries'][self.aid]['primary'][tf]['fontFolder'])
                    # Make the font family folder for this typeface
                    projFontFamilyFolder = os.path.join(projFontFolder, fontInfo[tf]['fontFolder'])
                    if not os.path.isdir(projFontFamilyFolder) :
                        os.mkdir(projFontFamilyFolder)
                    # Find the source font file name and path, always use the user's version
                    fontFileName = fontInfo[tf]['file']
                    fontSource = None
                    # System version
                    if os.path.isfile(os.path.join(self.project.rpmFonts, fontInfo[tf]['fontFolder'], fontFileName)) :
                        fontSource = os.path.join(self.project.rpmFonts, fontInfo[tf]['fontFolder'], fontFileName)
                    # User version
                    if os.path.isfile(os.path.join(self.project.userFonts, fontInfo[tf]['fontFolder'], fontFileName)) :
                        fontSource = os.path.join(self.project.userFonts, fontInfo[tf]['fontFolder'], fontFileName)
                    # Crash and burn if the font file is not found
                    if not fontSource :
                        self.project.writeToLog('ERR', 'Halt! ' + fontFileName + 'not found.', 'fontsTex.initAuxiliary()')
                        return False
                    # Copy the font file if need be
                    projFontFilePath = os.path.join(projFontFolder, fontFileName)
                    if not os.path.isfile(projFontFilePath) :
                        shutil.copy(fontSource, projFontFilePath)
        
        # Now create the right font information file for this aux component.
        
        if not os.path.isfile(os.path.join(projFontFolder, self.aid + '.tex')) :
            self.makeFontInfoTexFile(projFontFolder, self.aid)
        
        self.project.writeToLog('LOG', "Initialized [" + self.aid + "] for the UsfmTex auxiliary component type.")     
        self.initialized = True
        return True


    def makeFontInfoTexFile (self, fontFolder, aid) :
        '''Create a TeX info font file that TeX will use for rendering.'''
        
        fontInfoFileName = os.path.join(fontFolder, aid + '.tex')
        
#        initSettings = getXMLSettings('fontsTex_init.xml')
#        folderPath = initSettings['Folders']['FontFolder']['name']
#        fileName = initSettings['Files']['FontDefFile']['name']
#        typeFace = aProject._projConfig['Auxiliaries'][aux]['primary']['TypefaceRegular']['file']
#        regFilePath = folderPath + typeFace + aProject._projConfig['Auxiliaries'][aux]['primary']['TypefaceRegular']['file']

#        regular = "\\def\\regular{" + regFilePath

#####################################################################################################
        fontInfo = self.project._projConfig['Auxiliaries'][aid]['primary'].keys()
        print fontInfo
        for tf in fontInfo :
            print fontInfo[tf]['texMapping']

        if not os.path.isfile(fontInfoFileName) :
            writeObject = codecs.open(fontInfoFileName, "w", encoding='utf_8')
            writeObject.write('# ' + aid + '.tex' + ' created: ' + tStamp() + '\n')
            # Create the font mappings that will populate this font aux component
            # FIXME: Note this is only for the primary font, we are stuck if there are more
#            fontInfo = self.project._projConfig['Auxiliaries'][aid]['primary'].keys()
#            print fontInfo
#            for tf in fontInfo :
#                print fontInfo[tf]['texMapping']
#                writeObject.write("\\def\\" + fontInfo[tf]['texMapping'] + "{" + fontInfo[tf]['file'] + "}\n")
#                writeObject.write("}\n")
            
            
            
            writeObject.close()
        



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

        # Inject the font info into the fontset component section in the
        # project.conf. Enough information should be there for the component init.
        fInfo = getXMLSettings(fontInfo)
        self.auxConfig[rank] = fInfo.dict()

        self.project.writeOutProjConfFile = True
        self.project.writeToLog('MSG', font + ' font setup information added to [' + ftype + '] component')     
        
