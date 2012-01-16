#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project tasks.

# History:
# 20111207 - djd - Started with intial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil


# Load the local classes
from tools import *
from manager import Manager
import font_command as fntCmd


###############################################################################
################################## Begin Class ################################
###############################################################################

class Font (Manager) :

    # Shared values
    xmlConfFile     = 'font.xml'
    xmlInitFile     = 'font_init.xml'

    def __init__(self, project, cfg, cType) :
        '''Do the primary initialization for this manager.'''

        super(Font, self).__init__(project, cfg)

        # Set values for this manager
        self.project            = project
        self.cfg                = cfg
        self.cType              = cType
        self.fontFileName       = 'fonts.conf'
        self.fontFolderName     = 'Fonts'
        self.fontFolder         = os.path.join(self.project.projHome, self.fontFolderName)
#        self.fontConfFile       = os.path.join(self.project.projConfFolder, self.fontFileName)
        self.rpmXmlFontConfig   = os.path.join(self.project.rpmConfigFolder, self.xmlConfFile)
        self.fontInitFile       = os.path.join(self.project.rpmConfigFolder, self.xmlInitFile)

        # Get persistant values from the config if there are any
        newSectionSettings = getPersistantSettings(self.project._projConfig['Managers'][self.cType + '_Font'], os.path.join(self.project.rpmConfigFolder, 'font.xml'))
        if newSectionSettings != self.project._projConfig['Managers'][self.cType + '_Font'] :
            self.project._projConfig['Managers'][self.cType + '_Font'] = newSectionSettings
            self.project.writeOutProjConfFile = True

        self.compSettings = self.project._projConfig['Managers'][self.cType + '_Font']

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)


###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def recordFont (self, font, manager, compType) :
        '''Check for the exsitance of a font in the project conf file.
        If there is one, return, if not add it.'''

# FIXME: Need to find way to know if the font is already recorded

        # It is expected that all the necessary meta data for this font is in
        # a file located with the font. The system expects to find it in:
        # ~/resources/lib_share/Fonts/[FontID]
        fontDir = os.path.join(self.project.rpmFontsFolder, font)
        fontInfo = os.path.join(self.project.rpmFontsFolder, font, font + '.xml')
        if not os.path.isfile(fontInfo) :
            self.project.writeToLog('ERR', 'Halt! ' + font + '.xml not found.')
            return False

        # See if this is already in the config
        if not testForSetting(self.project._projConfig, 'Fonts') :
            buildConfSection (self.project._projConfig, 'Fonts')
            
        elif not testForSetting(self.project._projConfig['Fonts'], font) :
            buildConfSection (self.project._projConfig['Fonts'], font)

            # Inject the font info into the project format config file.
            fInfo = getXMLSettings(fontInfo)
            
            self.project._projConfig['Fonts'][font] = fInfo.dict()

            flag = False
            # Record the font with the component type that called it
            if not self.project._projConfig['CompTypes'][compType]['primaryFont'] :
                self.project._projConfig['CompTypes'][compType]['primaryFont'] = font
                flag = True

            if len(self.project._projConfig['CompTypes'][compType]['installedFonts']) == 0 :
                self.project._projConfig['CompTypes'][compType]['installedFonts'] = [font]
                flag = True
            else :
                fontList = self.project._projConfig['CompTypes'][compType]['installedFonts']
                if fontList != [font] :
                    self.project._projConfig['CompTypes'][compType]['installedFonts'] = addToList(fontList, font)
                    flag = True
            print flag
            if flag :
                self.project.writeOutProjConfFile = True
                self.project.writeToLog('LOG', font + ' font setup information added to project config')

            return True


    def installFont (self, font, manager, compType) :
        '''Install (copy) a font into a project.'''

        for font in self.project._projConfig['CompTypes'][compType]['installedFonts'] :
            fontInfo = self.project._projConfig['Fonts'][font]
            # Make the font family folder for this typeface
            fontFamilyFolder = os.path.join(self.fontFolder, fontInfo['FontInformation']['fontFolder'])
            if not os.path.isdir(fontFamilyFolder) :
                os.makedirs(fontFamilyFolder)

            self.copyInFont(fontInfo)

        return True


    def copyInFont (self, fontConfig) :
        '''Copy a font into a project and register it in the config.'''

            # Now loop through all the typefaces in this family and copy over the files
        for tf in fontConfig.keys() :
            thisFolder = fontConfig['FontInformation']['fontFolder']
            if tf[:8] == 'Typeface' :
                # Find the source font file name and path, always use the user's version
                fontFileName = fontConfig[tf]['file']
                fontSource = None
                # System version
                if os.path.isfile(os.path.join(self.project.rpmFontsFolder, thisFolder, fontFileName)) :
                    fontSource = os.path.join(self.project.rpmFontsFolder, thisFolder, fontFileName)
                # Crash and burn if the font file is not found
                if not fontSource :
                    self.project.writeToLog('ERR', 'Halt! ' + fontSource + 'not found.', 'fontsTex.initAuxiliary()')
                    return False
                # Copy the font file if need be
                fontFilePath = os.path.join(self.fontFolder, thisFolder, fontFileName)
                if not os.path.isfile(fontFilePath) :
                    shutil.copy(fontSource, fontFilePath)


