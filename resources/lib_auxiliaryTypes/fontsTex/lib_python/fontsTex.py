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

import os, sys, shutil, codecs
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

        # Project folder names and paths
        setattr(self, 'projFontFolderName', initInfo['Folders']['Fonts']['name'])
        setattr(self, 'projProcessFolderName', initInfo['Folders']['Process']['name'])
        setattr(self, 'projFontFolder', os.path.join(self.project.projHome, self.projFontFolderName))
        setattr(self, 'projProcessFolder', os.path.join(self.project.projHome, self.projProcessFolderName))

        # Bring in any know files for this component
        self.initAuxFiles(self.type, initInfo)

        # Init the fonts
        self.initFonts()

        # Now create the right font information file for this aux component.
        if not os.path.isfile(os.path.join(self.projFontFolder, self.aid + '.tex')) :
            self.makeFontInfoTexFile()

        self.project.writeToLog('LOG', "Initialized [" + self.aid + "] for the UsfmTex auxiliary component type.")     
        self.initialized = True
        return True


    def makeFontInfoTexFile (self) :
        '''Create a TeX info font file that TeX will use for rendering.'''

        # We will not make this file if it is already there
        fontInfoFileName = os.path.join(self.projProcessFolder, self.aid + '.tex')

        # The rule is that we only create this file if it is not there,
        # otherwise it will silently fail.  If one already exists the file will
        # need to be removed by some other process before it can be recreated.
        if not os.path.isfile(fontInfoFileName) :
            writeObject = codecs.open(fontInfoFileName, "w", encoding='utf_8')
            writeObject.write('# ' + self.aid + '.tex' + ' created: ' + tStamp() + '\n')
            auxFonts = self.project._projConfig['Auxiliaries'][self.aid]['installedFonts']
            for f in auxFonts :
                fInfo = self.project._projConfig['Fonts'][f]
                # Create the primary fonts that will be used with TeX
                if self.project._projConfig['Auxiliaries'][self.aid]['primaryFont'] == f :
                    features = self.project._projConfig['Auxiliaries'][self.aid][f]['features']
                    for tf in fInfo :
                        if tf[:8] == 'Typeface' :
                            # Make all our line components (More will need to be added)
                            startDef    = '\\def\\' + fInfo[tf]['texMapping'] + '{'
                            fpath       = "\"[" + os.path.join('..', self.projFontFolderName, fInfo[tf]['file']) + "]\""
                            endDef      = "}\n"
                            featureString = ''
                            for i in features :
                                featureString += ':' + i

                            writeObject.write(startDef + fpath + featureString + endDef)

                # Create defs with secondary fonts for special use with TeX in publication
                else :
                    writeObject.write('\n# These are special use fonts for this type of component.\n')
                    features = self.project._projConfig['Auxiliaries'][self.aid][f]['features']
                    for tf in fInfo :
                        if tf[:8] == 'Typeface' :
                            # Make all our line components (More will need to be added)
                            startDef    = '\\def\\' + f.lower() + tf[8:].lower() + '{'
                            fpath       = "\"[" + os.path.join('..', self.projFontFolderName, fInfo[tf]['file']) + "]\""
                            endDef      = "}\n"
                            featureString = ''
                            for i in features :
                                featureString += ':' + i

                            writeObject.write(startDef + fpath + featureString + endDef)

            writeObject.close()
            return True


    def initFonts (self) :
        '''Initialize the fonts for this auxiliary component by finding and
        copying the fonts into the project from the source.  Of course this only
        works if there are any fonts set for a given aux.'''

        for font in self.project._projConfig['Auxiliaries'][self.aid]['installedFonts'] :
            fontInfo = self.project._projConfig['Fonts'][font]
            # Make the font family folder for this typeface
            projFontFamilyFolder = os.path.join(self.projFontFolder, fontInfo['FontInformation']['fontFolder'])
            if not os.path.isdir(projFontFamilyFolder) :
                os.mkdir(projFontFamilyFolder)
                
            # Now loop through all the typefaces in this family and copy over the files
            for tf in fontInfo.keys() :
                if tf[:8] == 'Typeface' :
                    # Find the source font file name and path, always use the user's version
                    fontFileName = fontInfo[tf]['file']
                    fontSource = None
                    # System version
                    if os.path.isfile(os.path.join(self.project.rpmFonts, font, fontFileName)) :
                        fontSource = os.path.join(self.project.rpmFonts, font, fontFileName)
                    # User version
                    if os.path.isfile(os.path.join(self.project.userFonts, font, fontFileName)) :
                        fontSource = os.path.join(self.project.userFonts, font, fontFileName)
                    # Crash and burn if the font file is not found
                    if not fontSource :
                        self.project.writeToLog('ERR', 'Halt! ' + fontSource + 'not found.', 'fontsTex.initAuxiliary()')
                        return False
                    # Copy the font file if need be
                    projFontFilePath = os.path.join(self.projFontFolder, font, fontFileName)
                    if not os.path.isfile(projFontFilePath) :
                        shutil.copy(fontSource, projFontFilePath)

        return True


    def setFont (self, ftype, font, rank) :
        '''Setup a font for a specific typeface.'''

        # First, delete the font info TeX file.  Everything changes if we add a
        # font to this aux
        if os.path.isfile(os.path.join(self.projFontFolder, self.aid + '.tex')) :
            os.remove(os.path.join(self.projFontFolder, self.aid + '.tex'))

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

        # Make sure we have a fonts section in the conf file
        try :
            s = self.project._projConfig['Fonts']
        except :
            self.project._projConfig['Fonts'] = {}
            
        try :
            f = self.project._projConfig['Fonts'][font]
        except :
            self.project._projConfig['Fonts'][font] = {}

        # Inject the font info into the fontset component section in the
        # project.conf. Enough information should be there for the component init.
        fInfo = getXMLSettings(fontInfo)
        self.project._projConfig['Fonts'][font] = fInfo.dict()

        # Add to installed fonts list for this auxiliary type, only one instance allowed
        if font not in self.project._projConfig['AuxiliaryTypes'][self.type]['installedFonts'] :
            listOrder = []
            listOrder = self.project._projConfig['AuxiliaryTypes'][self.type]['installedFonts']
            listOrder.append(font)
            self.project._projConfig['AuxiliaryTypes'][self.type]['installedFonts'] = listOrder
            
        # We also keep a list of fonts that are installed in a specific font aux component
        try :
            fl = self.project._projConfig['Auxiliaries'][self.aid]['installedFonts']
        except :
            self.project._projConfig['Auxiliaries'][self.aid]['installedFonts'] = []

        if font not in self.project._projConfig['Auxiliaries'][self.aid]['installedFonts'] :
            listOrder = []
            listOrder = self.project._projConfig['Auxiliaries'][self.aid]['installedFonts']
            listOrder.append(font)
            self.project._projConfig['Auxiliaries'][self.aid]['installedFonts'] = listOrder

        # Check to see if the primary font has been set
        if self.project._projConfig['Auxiliaries'][self.aid]['primaryFont'] == 'None' :
            self.project._projConfig['Auxiliaries'][self.aid]['primaryFont'] = self.project._projConfig['Fonts'][font]['FontInformation']['fontID']

        # Add any features that this aux needs to have with this specific font.
        buildConfSection(self.project._projConfig['Auxiliaries'][self.aid], font)
        self.project._projConfig['Auxiliaries'][self.aid][font]['features'] = self.project._projConfig['Fonts'][font]['FontInformation']['features']

        # Now recreate the font info TeX file
        self.makeFontInfoTexFile()

        # Set conf write flag and report     
        self.project.writeOutProjConfFile = True
        self.project.writeToLog('MSG', font + ' font setup information added to [' + ftype + '] component')     



