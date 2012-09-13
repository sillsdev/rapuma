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

import os, shutil, tarfile


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

#        if not font :
#            sEditor = self.project.projConfig['CompTypes'][self.Ctype]['sourceEditor']
#            if sEditor.lower() == 'paratext' :
#                font = getPTFont(self.project.local.projHome)
#                # Test for font
#                if not font :
#                    self.project.log.writeToLog('FONT-020')
#                    dieNow()
#            else :
#                # Quite here
#                if not sEditor :
#                    self.project.log.writeToLog('FONT-025')
#                else :
#                    self.project.log.writeToLog('FONT-030', [sEditor])
#                dieNow()

        # If this didn't die already we should be able to record and install now
        self.project.projConfig['CompTypes'][cType]['primaryFont'] = font
#        # Load the primary font if it is not there already
#        self.recordFont(cType, font)
# #       self.installFont(cType)
        writeConfFile(self.project.projConfig)
#        self.project.log.writeToLog('FONT-035', [font])
        return True


    def checkForSubFont (self, font) :
        '''Return the true name of the font to be used if the one given
        is pointing to a substitute font in the same font family.'''

        metaDataSource = os.path.join(self.project.local.projFontsFolder, font, font + '.xml')
        if not os.path.isfile(metaDataSource) :
            self.project.log.writeToLog('FONT-040', [font])
            dieNow()

        fInfo = getXMLSettings(metaDataSource)
        if testForSetting(fInfo['FontInformation'], 'substituteFontName') :
            return fInfo['FontInformation']['substituteFontName']
        else :
            return font


    def recordFont (self, cType, font) :
        '''Check for the exsitance of the specified font in the font folder.
        Then extract the meta data into the appropreate configurations.'''

        metaDataSource = os.path.join(self.project.local.projFontsFolder, font, font + '.xml')
        if not os.path.isfile(metaDataSource) :
            self.project.log.writeToLog('FONT-040', [font])
            dieNow()

        # See if this font is already in the config
        if not testForSetting(self.fontConfig, 'Fonts', font) :
            # Inject the font info into the project format config file.
            fInfo = getXMLSettings(metaDataSource)
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


    def installFont (self, font) :
        '''Install (copy) a font into a project. The font is bundled with
        other necessary components in a tar.gz file. It will need to be
        extrcted into the project font folder before the meta data can
        be looked at and added to the project to be acted on. This function 
        does that.'''

        source = os.path.join(self.project.local.rpmFontsFolder, font + '.tar.gz')
        if tarfile.is_tarfile(source) :
            mytar = tarfile.open(source, 'r')
            mytar.extractall(self.project.local.projFontsFolder)
            # Double check extract operation by looking for meta data file
            if os.path.join(self.project.local.projFontsFolder, font, font + '.xml') :
                self.project.log.writeToLog('FONT-060', [fName(source)])
                return True
            else :
                self.project.log.writeToLog('FONT-065')
                return False


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



