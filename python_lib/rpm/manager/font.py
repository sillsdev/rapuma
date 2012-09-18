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

import os, shutil, zipfile


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


    def setPrimaryFont (self, cType, font, force = None) :
        '''Set the primary font for the project.'''

        def setIt (Ctype, font) :
            self.project.projConfig['CompTypes'][Ctype]['primaryFont'] = font
            writeConfFile(self.project.projConfig)
            # Sanity check
            if self.project.projConfig['CompTypes'][Ctype]['primaryFont'] == font :
                return True

        Ctype = cType.capitalize()
        # First check to see if it is already has a primary font set
        if self.project.projConfig['CompTypes'][Ctype]['primaryFont'] == '' :
            if setIt(Ctype, font) :
                self.project.log.writeToLog('FONT-035', [Ctype,font])
                return True
        elif force :
            if setIt(Ctype, font) :
                self.project.log.writeToLog('FONT-032', [font,Ctype])
                return True
        elif self.project.projConfig['CompTypes'][Ctype]['primaryFont'] :
            self.project.log.writeToLog('FONT-037', [self.project.projConfig['CompTypes'][Ctype]['primaryFont'],Ctype])
            return True
        else :
            self.project.log.writeToLog('FONT-030', [font,Ctype])
            return True

        return False


    def checkForSubFont (self, font) :
        '''Return the true name of the font to be used if the one given
        is pointing to a substitute font in the same font family.'''

        # Check for the font family bundle
        zipSource = os.path.join(self.project.local.rpmFontsFolder, font + '.zip')
        if isInZip(font + '.xml', zipSource) :
            xmlFile = font + '/' + font + '.xml'
            tmpFolder = os.path.join(self.project.local.projConfFolder, font)
            # Extract to a temp file/folder
            myzip = zipfile.ZipFile(zipSource)
            myzip.extract(xmlFile, self.project.local.projConfFolder)
            metaDataSource = os.path.join(self.project.local.projConfFolder, xmlFile)
            myzip.close()
            fInfo = getXMLSettings(metaDataSource)
            # Now kill the temp file and folder
            os.remove(metaDataSource)
            if os.path.isdir(tmpFolder) :
                shutil.rmtree(tmpFolder)
            # Finally check for a substitute font name
            if testForSetting(fInfo['FontInformation'], 'substituteFontName') :
                return fInfo['FontInformation']['substituteFontName']
            else :
                return font
        else :
            self.project.log.writeToLog('FONT-040', [font])
            dieNow()


    def recordFont (self, cType, font, force = None) :
        '''Check for the exsitance of the specified font in the font folder.
        Then extract the meta data into the appropreate configurations.
        If the force flag has been set then delete the old settings and
        install the new settings (or just reset to default settings).'''

        # Set vars do initial checks
        metaDataSource = os.path.join(self.project.local.projFontsFolder, font, font + '.xml')
        Ctype = cType.capitalize()
        if not os.path.isfile(metaDataSource) :
            self.project.log.writeToLog('FONT-040', [font])
            dieNow()

        # See if this font is already in the font config file
        if not testForSetting(self.fontConfig, 'Fonts', font) :
            buildConfSection(self.fontConfig, 'Fonts')

        # Set as primary for the calling cType if there is none now
        if not self.project.projConfig['CompTypes'][Ctype]['primaryFont'] :
            self.project.projConfig['CompTypes'][Ctype]['primaryFont'] = font

        # If force was set, force the settings, otherwise, let them be
        if force :
            try :
                del self.fontConfig['Fonts'][font]
            except :
                pass
            # (Re)Inject the font info into the project format config file.
            fInfo = getXMLSettings(metaDataSource)
            self.fontConfig['Fonts'][font] = fInfo.dict()
            writeConfFile(self.fontConfig)
            # Adjust installed fonts list if needed
            if len(self.project.projConfig['CompTypes'][Ctype]['installedFonts']) == 0 :
                self.project.projConfig['CompTypes'][Ctype]['installedFonts'] = [font]
            else :
                fontList = self.project.projConfig['CompTypes'][Ctype]['installedFonts']
                if fontList != [font] :
                    self.project.projConfig['CompTypes'][Ctype]['installedFonts'] = addToList(fontList, font)
            primFont = self.project.projConfig['CompTypes'][Ctype]['primaryFont']
            if primFont != font and (primFont == '' or primFont == 'None') :
                self.project.projConfig['CompTypes'][Ctype]['primaryFont'] = font

            self.project.log.writeToLog('FONT-045', [font])
            writeConfFile(self.project.projConfig)
            return True

        else :
            if testForSetting(self.fontConfig['Fonts'], font) :
                self.project.log.writeToLog('FONT-047', [font])
            else :
                # Inject the font info into the project font config file if it is not there.
                try :
                    x = self.fontConfig['Fonts'][font]
                except :
                    fInfo = getXMLSettings(metaDataSource)
                    self.fontConfig['Fonts'][font] = fInfo.dict()
                    writeConfFile(self.fontConfig)
                    self.project.log.writeToLog('FONT-045', [font])

            # Adjust installed fonts list if needed
            if len(self.project.projConfig['CompTypes'][Ctype]['installedFonts']) == 0 :
                self.project.projConfig['CompTypes'][Ctype]['installedFonts'] = [font]
            else :
                fontList = self.project.projConfig['CompTypes'][Ctype]['installedFonts']
                if fontList != [font] :
                    self.project.projConfig['CompTypes'][Ctype]['installedFonts'] = addToList(fontList, font)

            primFont = self.project.projConfig['CompTypes'][Ctype]['primaryFont']
            if primFont != font and (primFont == '' or primFont == 'None') :
                self.project.projConfig['CompTypes'][Ctype]['primaryFont'] = font

            self.project.log.writeToLog('FONT-045', [font])
            writeConfFile(self.project.projConfig)
            return True



    def installFont (self, font, force = None) :
        '''Install (copy) a font into a project. The font is bundled with
        other necessary components in a .zip file. If the font folder is
        already there we assume there is a font there and we do not proceed.
        If the force flag is set, then we delete any exsisting font and
        extract a new one in its place.'''

        def extract (source, confXml) :
            if zipfile.is_zipfile(source) :
                myzip = zipfile.ZipFile(source, 'r')
                myzip.extractall(self.project.local.projFontsFolder)
                # Double check extract
                if os.path.isfile(confXml) :
                    return True

        source = os.path.join(self.project.local.rpmFontsFolder, font + '.zip')
        confXml = os.path.join(self.project.local.projFontsFolder, font, font + '.xml')
        if force :
            try :
                shutil.rmtree(os.path.join(self.project.local.projFontsFolder, font))
            except :
                pass
            if extract(source, confXml) :
                self.project.log.writeToLog('FONT-060', [fName(source)])
                return True
            else :
                self.project.log.writeToLog('FONT-065', [fName(source)])
                return False
        else :
            # With nothing done yet, check for meta data file
            if os.path.isfile(confXml) :
                self.project.log.writeToLog('FONT-062', [fName(source)])
                return True
            else :
                if extract(source, confXml) :
                    self.project.log.writeToLog('FONT-067', [fName(source)])
                    return True
                else :
                    self.project.log.writeToLog('FONT-065')
                    return False



# Working on removeal, not all there yet



    def removeFont (self, cType, font, force = None) :
        '''Remove a font from a project, unless it is in use by another 
        component type. Then just disconnect it from the calling component
        type. However, if the force switch is set, remove it, regardless.'''

        def removePConfSettings (Ctype, font) :
            # Adjust installed fonts list if needed
            fontList = self.project.projConfig['CompTypes'][Ctype]['installedFonts']
            primFont = self.project.projConfig['CompTypes'][Ctype]['primaryFont']
            if fontList == [font] :
                fontList.remove(font)
                self.project.projConfig['CompTypes'][Ctype]['installedFonts'] = fontList
            print primFont
            if primFont == font :
                self.project.projConfig['CompTypes'][Ctype]['primaryFont'] = None

        def removeFConfSettings (font) :
            try :
                del self.fontConfig['Fonts'][font]
                return True
            except :
                return False


        Ctype = cType.capitalize()

        # Look in other cTypes for the same font
        for ct in self.project.projConfig['CompTypes'].keys() :
            useCount = 0
            if ct != cType :
                fonts = self.project.projConfig['CompTypes'][ct]['installedFonts']
                # If we find the font is in another cType we only remove it from the
                # target component settings
                if font in fonts :
                    useCount +=1
                    removePConfSettings(Ctype, font)
                    removeFConfSettings(font)
                    writeConfFile(self.fontConfig)
                    writeConfFile(self.project.projConfig)
                    return True




