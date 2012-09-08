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
        self.project                    = project
        self.cfg                        = cfg
        self.cType                      = cType
        self.Ctype                      = cType.capitalize()
        self.fontConfig                 = ConfigObj()
        self.project                    = project
        self.rpmXmlFontConfig   = os.path.join(self.project.local.rpmConfigFolder, self.xmlConfFile)

        # Create an empty default font config file if needed
        if not os.path.isfile(self.project.local.fontConfFile) :
            self.fontConfig.filename = self.project.local.fontConfFile
            writeConfFile(self.fontConfig)
            self.project.log.writeToLog('FONT-010')
        else :
            self.fontConfig = ConfigObj(self.project.local.fontConfFile)

        # Get persistant values from the config if there are any
        manager = self.cType + '_Font'
        newSectionSettings = getPersistantSettings(self.project.projConfig['Managers'][manager], os.path.join(self.project.local.rpmConfigFolder, self.xmlConfFile))
        if newSectionSettings != self.project.projConfig['Managers'][manager] :
            self.project.projConfig['Managers'][manager] = newSectionSettings
            # Save the setting rightaway
            writeConfFile(self.project.projConfig)

        self.compSettings = self.project.projConfig['Managers'][manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)


###############################################################################
############################ Project Level Functions ##########################
###############################################################################



    def setPrimaryFont (self, cType, font) :
        '''Set the primary font for the project.'''

        if not font :
            sEditor = self.project.projConfig['CompTypes'][self.Ctype]['sourceEditor']
            if sEditor.lower() == 'paratext' :
                font = getPTFont(self.project.local.projHome)
                # Test for font
                if not font :
                    self.project.log.writeToLog('FONT-020')
                    dieNow()
            else :
                # Quite here
                if not sEditor :
                    self.project.log.writeToLog('FONT-025')
                else :
                    self.project.log.writeToLog('FONT-030', [sEditor])
                dieNow()

        # If this didn't die already we should be able to record and install now
        self.project.projConfig['CompTypes'][cType]['primaryFont'] = font
        # Load the primary font if it is not there already
        self.recordFont(cType, font)
        self.installFont(cType)
        writeConfFile(self.project.projConfig)
        self.project.log.writeToLog('FONT-035', [font])
        return True


    def recordFont (self, cType, font) :
        '''Check for the exsitance of a font in the font conf file.
        If there is one, return, if not add it.'''

        # It is expected that all the necessary meta data for this font is in
        # a file located with the font. The system expects to find it in:
        # ~/resources/lib_share/Fonts/[FontID]
        fontDir = os.path.join(self.project.local.rpmFontsFolder, font)
        fontInfo = os.path.join(self.project.local.rpmFontsFolder, font, font + '.xml')
        if not os.path.isfile(fontInfo) :
            self.project.log.writeToLog('FONT-040', [font])
            dieNow()

        # See if this is already in the config
        if not testForSetting(self.fontConfig, 'Fonts') :
            buildConfSection (self.fontConfig, 'Fonts')

        record = False
        if not testForSetting(self.fontConfig['Fonts'], font) :
            buildConfSection (self.fontConfig['Fonts'], font)
            record = True

        if record :
            # Inject the font info into the project format config file.
            fInfo = getXMLSettings(fontInfo)
            self.fontConfig['Fonts'][font] = fInfo.dict()

            # Record the font with the component type that called it
            if not self.project.projConfig['CompTypes'][cType]['primaryFont'] :
                self.project.projConfig['CompTypes'][cType]['primaryFont'] = font

            if len(self.project.projConfig['CompTypes'][cType]['installedFonts']) == 0 :
                self.project.projConfig['CompTypes'][cType]['installedFonts'] = [font]
            else :
                fontList = self.project.projConfig['CompTypes'][cType]['installedFonts']
                if fontList != [font] :
                    self.project.projConfig['CompTypes'][cType]['installedFonts'] = addToList(fontList, font)

            writeConfFile(self.fontConfig)
            writeConfFile(self.project.projConfig)
            self.project.log.writeToLog('FONT-045', [font])
            return True

        else :
            self.project.log.writeToLog('FONT-047', [font])
            return False


    def installFont (self, cType) :
        '''Install (copy) a font into a project. This needs to take place
        after the font has been recorded in the project configuration file.'''

        for font in self.project.projConfig['CompTypes'][cType]['installedFonts'] :
            fontInfo = self.fontConfig['Fonts'][font]
            # Make the font family folder for this typeface
            fontFamilyFolder = os.path.join(self.project.local.projFontsFolder, fontInfo['FontInformation']['fontFolder'])
            if not os.path.isdir(fontFamilyFolder) :
                os.makedirs(fontFamilyFolder)

        # Copy in all the files
        copied  = self.copyInFont(fontInfo)

        if copied > 0 :
            self.project.log.writeToLog('FONT-060', [str(copied), fontFamilyFolder])
        else :
            self.project.log.writeToLog('FONT-062')

        return True


    def removeFont (self, cType, font) :
        '''Remove a font from a project, unless it is in use by another 
        component type. Then just disconnect it from the calling component type.'''

        def removePConfSettings (cType, font) :
            print 'remove settings only'


        # Look in other cTypes for the same font
        for ct in self.project.projConfig['CompTypes'].keys() :
            if ct != cType :
                fonts = self.project.projConfig['CompTypes'][ct]['installedFonts']
                # If we find the font is in another cType we only remove it from the
                # target component settings
                if font in fonts :
                    removePConfSettings(cType, font)
                    return True



    def copyInFont (self, fontConfig) :
        '''Copy a font into a project and register it in the config.'''

        copied = 0
        # Now loop through all the typefaces in this family and copy over the files
        for tf in fontConfig.keys() :
            thisFolder = fontConfig['FontInformation']['fontFolder']
            if tf[:8] == 'Typeface' :
                # Find the source font file name and path, always use the user's version
                fontFileName = fontConfig[tf]['file']
                fontSource = None
                # System font version
                if os.path.isfile(os.path.join(self.project.local.rpmFontsFolder, thisFolder, fontFileName)) :
                    fontSource = os.path.join(self.project.local.rpmFontsFolder, thisFolder, fontFileName)

                # Crash and burn if the font file is not found
                if not fontSource :
                    self.project.log.writeToLog('FONT-050', [fontSource])
                    return False
                # Copy the font file if need be
                fontFilePath = os.path.join(self.project.local.projFontsFolder, thisFolder, fontFileName)
                if not os.path.isfile(fontFilePath) :
                    shutil.copy(fontSource, fontFilePath)
                    self.project.log.writeToLog('FONT-070', [fontFilePath])
                    copied +=1

        return copied

