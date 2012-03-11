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
from pt_tools import *
from manager import Manager


###############################################################################
################################## Begin Class ################################
###############################################################################

class Font (Manager) :

    # Shared values
    xmlConfFile     = 'font.xml'

    def __init__(self, project, cfg, cType) :
        '''Do the primary initialization for this manager.'''

        super(Font, self).__init__(project, cfg)

        # Set values for this manager
        self.project            = project
        self.cfg                = cfg
        self.cType              = cType
        self.rpmXmlFontConfig   = os.path.join(self.project.local.rpmConfigFolder, self.xmlConfFile)

        # Get persistant values from the config if there are any
        manager = self.cType + '_Font'
        newSectionSettings = getPersistantSettings(self.project.projConfig['Managers'][manager], os.path.join(self.project.local.rpmConfigFolder, self.xmlConfFile))
        if newSectionSettings != self.project.projConfig['Managers'][manager] :
            self.project.projConfig['Managers'][manager] = newSectionSettings

        self.compSettings = self.project.projConfig['Managers'][manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)


###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def recordFont (self, font, manager, compType) :
        '''Check for the exsitance of a font in the project conf file.
        If there is one, return, if not add it.'''

        # It is expected that all the necessary meta data for this font is in
        # a file located with the font. The system expects to find it in:
        # ~/resources/lib_share/Fonts/[FontID]
        fontDir = os.path.join(self.project.rpmFontsFolder, font)
        fontInfo = os.path.join(self.project.rpmFontsFolder, font, font + '.xml')
        if not os.path.isfile(fontInfo) :
            self.project.writeToLog('ERR', 'Halt! ' + font + '.xml not found.')
            return False

        # See if this is already in the config
        if not testForSetting(self.project.projConfig, 'Fonts') :
            buildConfSection (self.project.projConfig, 'Fonts')
            
        record = False
        if not testForSetting(self.project.projConfig['Fonts'], font) :
            buildConfSection (self.project.projConfig['Fonts'], font)
            record = True

        if record :
            # Inject the font info into the project format config file.
            fInfo = getXMLSettings(fontInfo)
            
            self.project.projConfig['Fonts'][font] = fInfo.dict()

            # Record the font with the component type that called it
            if not self.project.projConfig['CompTypes'][compType]['primaryFont'] :
                self.project.projConfig['CompTypes'][compType]['primaryFont'] = font

            if len(self.project.projConfig['CompTypes'][compType]['installedFonts']) == 0 :
                self.project.projConfig['CompTypes'][compType]['installedFonts'] = [font]
            else :
                fontList = self.project.projConfig['CompTypes'][compType]['installedFonts']
                if fontList != [font] :
                    self.project.projConfig['CompTypes'][compType]['installedFonts'] = addToList(fontList, font)

            writeToLog(self.project.local, self.project.userConfig, 'LOG', font + ' font setup information added to project config')
            return True

        else :
            return False


    def installFont (self, font, manager, compType) :
        '''Install (copy) a font into a project.'''

        for font in self.project.projConfig['CompTypes'][compType]['installedFonts'] :
            fontInfo = self.project.projConfig['Fonts'][font]
            # Make the font family folder for this typeface
            fontFamilyFolder = os.path.join(self.project.fontsFolder, fontInfo['FontInformation']['fontFolder'])
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
                fontFilePath = os.path.join(self.project.fontsFolder, thisFolder, fontFileName)
                if not os.path.isfile(fontFilePath) :
                    shutil.copy(fontSource, fontFilePath)


