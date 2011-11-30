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

        # Start with default settings
        self._fontConfig = {}
        self._initConfig = getAuxInitSettings(self.project.userHome, self.project.rpmHome, self.type)
        # Set values for this method
        setattr(self, 'fontFolderName', self._initConfig['Folders']['Fonts']['name'])
        setattr(self, 'processFolderName', self._initConfig['Folders']['Process']['name'])
        setattr(self, 'fontFileName', self._initConfig['Files']['FontConfig']['name'])
        setattr(self, 'fontFolder', os.path.join(self.project.projHome, self.fontFolderName))
        setattr(self, 'processFolder', os.path.join(self.project.projHome, self.processFolderName))
        setattr(self, 'fontConfFile', os.path.join(self.processFolder, self.fontFileName))

        # Bring in any known files for this component
        self.initAuxFiles(self.type, self._initConfig)

        # Make a font conf file if it isn't there already or if it is empty.
        try :
            self._fontConfig = ConfigObj(self.fontConfFile)
            x = self._fontConfig['GeneralSettings']['lastEdit']
        except :
            buildConfSection (self._fontConfig, 'Fonts')
            writeConfFile(self._fontConfig, self.fontFileName, self.processFolder)
            self._fontConfig = ConfigObj(self.fontConfFile)

        # Init the font folder
        self.initFonts()

        # Now create a tex font information file for this aux component if needed.
        self.makeFontInfoTexFile()

        self.project.writeToLog('LOG', "Initialized [" + self.aid + "] for the UsfmTex auxiliary component type.")     
        self.initialized = True
        return True


    def makeFontInfoTexFile (self) :
        '''Create a TeX info font file that TeX will use for rendering.'''

        print 'We are in!:::::::::::::::::::::::::::::::::::::'
        # We will not make this file if it is already there
        fontInfoFileName = os.path.join(self.processFolder, self.aid + '.tex')

        # The rule is that we only create this file if it is not there,
        # otherwise it will silently fail.  If one already exists the file will
        # need to be removed by some other process before it can be recreated.
        if not os.path.isfile(fontInfoFileName) or self.project._projConfig['Auxiliaries'][self.aid]['remakeTexFile'] == 'True' :
            writeObject = codecs.open(fontInfoFileName, "w", encoding='utf_8')
            writeObject.write('# ' + self.aid + '.tex' + ' created: ' + tStamp() + '\n')
            auxFonts = self.project._projConfig['Auxiliaries'][self.aid]['installedFonts']
            for f in auxFonts :
                print f
                fInfo = self._fontConfig['Fonts'][f]
                # Create the primary fonts that will be used with TeX
                if self.project._projConfig['Auxiliaries'][self.aid]['primaryFont'] == f :
                    writeObject.write('\n# These are normal use fonts for this type of component.\n')
                    features = self.project._projConfig['Auxiliaries'][self.aid][f]['features']
                    for tf in fInfo :
                        if tf[:8] == 'Typeface' :
                            # Make all our line components (More will need to be added)
                            startDef    = '\\def\\' + fInfo[tf]['texMapping'] + '{'
                            fpath       = "\"[" + os.path.join('..', self.fontFolderName, fInfo[tf]['file']) + "]\""
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
                            fpath       = "\"[" + os.path.join('..', self.fontFolderName, fInfo[tf]['file']) + "]\""
                            endDef      = "}\n"
                            featureString = ''
                            for i in features :
                                featureString += ':' + i

                            writeObject.write(startDef + fpath + featureString + endDef)

            # Finish the process
            writeObject.close()
            self.project._projConfig['Auxiliaries'][self.aid]['remakeTexFile'] = False
            self.project.writeOutProjConfFile = True
            return True


    def initFonts (self) :
        '''Initialize the fonts for this auxiliary component by finding and
        copying the fonts into the project from the source.  Of course this only
        works if there are any fonts set for a given aux.'''

        for font in self.project._projConfig['Auxiliaries'][self.aid]['installedFonts'] :
            fontInfo = self._fontConfig['Fonts'][font]
            # Make the font family folder for this typeface
            fontFamilyFolder = os.path.join(self.fontFolder, fontInfo['FontInformation']['fontFolder'])
            if not os.path.isdir(fontFamilyFolder) :
                os.mkdir(fontFamilyFolder)
                
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
                    fontFilePath = os.path.join(self.fontFolder, font, fontFileName)
                    if not os.path.isfile(fontFilePath) :
                        shutil.copy(fontSource, fontFilePath)

        return True


    def setFont (self, ftype, font, rank='None') :
        '''Setup a font for a specific typeface and create a fonts.conf file in
        the process folder.'''

        # First, delete the existing font info TeX file.  Everything changes if
        # we add a font to this aux
        if os.path.isfile(os.path.join(self.processFolder, self.aid + '.tex')) :
            os.remove(os.path.join(self.processFolder, self.aid + '.tex'))

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

        # Inject the font info into the project format config file.
        fInfo = getXMLSettings(fontInfo)
        buildConfSection (self._fontConfig['Fonts'], font)
        self._fontConfig['Fonts'][font] = fInfo.dict()

        # Add to installed fonts list for this auxiliary type, only one instance allowed
        if font not in self.project._projConfig['AuxiliaryTypes'][self.type]['installedFonts'] :
            listOrder = []
            listOrder = self.project._projConfig['AuxiliaryTypes'][self.type]['installedFonts']
            listOrder.append(font)
            self.project._projConfig['AuxiliaryTypes'][self.type]['installedFonts'] = listOrder

        if font not in self.project._projConfig['Auxiliaries'][self.aid]['installedFonts'] :
            listOrder = []
            listOrder = self.project._projConfig['Auxiliaries'][self.aid]['installedFonts']
            listOrder.append(font)
            self.project._projConfig['Auxiliaries'][self.aid]['installedFonts'] = listOrder

        # Check to see if the primary font has been set
        if rank.lower() == 'primary' :
            self.project._projConfig['Auxiliaries'][self.aid]['primaryFont'] = self._fontConfig['Fonts'][font]['FontInformation']['fontID']

        # Add any features that this aux needs to have with this specific font.
        buildConfSection(self.project._projConfig['Auxiliaries'][self.aid], font)
        self.project._projConfig['Auxiliaries'][self.aid][font]['features'] = self._fontConfig['Fonts'][font]['FontInformation']['features']

        # Set conf write flag and report
        self.project._projConfig['Auxiliaries'][self.aid]['remakeTexFile'] = True
        self.project.writeOutProjConfFile = True
        writeConfFile(self._fontConfig, self.fontFileName, self.processFolder)
        self.project.writeToLog('MSG', font + ' font setup information added to [' + ftype + '] component')     
        return True


    def removeAuxFont (self, ftype, font) :
        '''Remove a font from only this aux.'''

        # FIXME: This will work at the aux level but needs expanding to work
        # more globally

        # Remove from aux font listing
        if font in self.project._projConfig['Auxiliaries'][self.aid]['installedFonts'] :
            listOrder = []
            listOrder = self.project._projConfig['Auxiliaries'][self.aid]['installedFonts']
            listOrder.pop(listOrder.index(font))
            self.project._projConfig['Auxiliaries'][self.aid]['installedFonts'] = listOrder

        # Remove any features that this aux needed to have with this specific font.
        if font in self.project._projConfig['Auxiliaries'][self.aid] :
            del self.project._projConfig['Auxiliaries'][self.aid][font]

        # Change the primary font setting if needed
        if self.project._projConfig['Auxiliaries'][self.aid]['primaryFont'] == font :
            self.project._projConfig['Auxiliaries'][self.aid]['primaryFont'] = self.project._projConfig['Auxiliaries'][self.aid]['installedFonts'][0]
        else :
            self.project._projConfig['Auxiliaries'][self.aid]['primaryFont'] = 'None'

        # Set conf write flag and report
        self.project._projConfig['Auxiliaries'][self.aid]['remakeTexFile'] = True
        self.project.writeOutProjConfFile = True
        self.project.writeToLog('MSG', font + ' font setup information removed from [' + ftype + '] component')
        return True


