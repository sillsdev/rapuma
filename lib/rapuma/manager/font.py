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
from rapuma.core.tools import *
from rapuma.core.pt_tools import *
from rapuma.project.manager import Manager


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
        self.project                = project
        self.cfg                    = cfg
        self.cType                  = cType
        self.Ctype                  = cType.capitalize()
        self.fontConfig             = ConfigObj(encoding='utf-8')
        self.project                = project
        self.manager                = self.cType + '_Font'
        self.rapumaXmlFontConfig    = os.path.join(self.project.local.rapumaConfigFolder, self.xmlConfFile)
        self.sourcePath             = getattr(self.project, self.cType + '_sourcePath')

        # Create an empty default font config file if needed
        if not os.path.isfile(self.project.local.fontConfFile) :
            self.fontConfig.filename = self.project.local.fontConfFile
            writeConfFile(self.fontConfig)
            self.project.log.writeToLog('FONT-010')
        else :
            self.fontConfig = ConfigObj(self.project.local.fontConfFile, encoding='utf-8')

        # Get persistant values from the config if there are any
        newSectionSettings = getPersistantSettings(self.project.projConfig['Managers'][self.manager], os.path.join(self.project.local.rapumaConfigFolder, self.xmlConfFile))
        if newSectionSettings != self.project.projConfig['Managers'][self.manager] :
            self.project.projConfig['Managers'][self.manager] = newSectionSettings
            # Save the setting rightaway
            writeConfFile(self.project.projConfig)

        self.compSettings = self.project.projConfig['Managers'][self.manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)

        # Get our component sourceEditor
        self.sourceEditor = getSourceEditor(self.project.projConfig, self.sourcePath, self.cType)

        if not self.ptDefaultFont :
            ptSet = getPTSettings(self.sourcePath)
            if ptSet :
                setattr(self, 'ptDefaultFont', ptSet['ScriptureText']['DefaultFont'])
                self.project.projConfig['Managers'][self.cType + '_Font']['ptDefaultFont'] = self.ptDefaultFont
                writeConfFile(self.project.projConfig)

###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def setGlyphMap (self, cType, font) :
        '''If needed, set the glyph map used for this component type font.'''

        self.project.log.writeToLog('FONT-100')

    def setPrimaryFont (self, cType, font, force = None) :
        '''Set the primary font for the project.'''

        def setIt (Ctype, font) :
            self.project.projConfig['Managers'][self.manager]['primaryFont'] = font
            writeConfFile(self.project.projConfig)
            # Sanity check
            if self.project.projConfig['Managers'][self.manager]['primaryFont'] == font :
                return True

        Ctype = cType.capitalize()
        # First check to see if it is already has a primary font set
        if self.project.projConfig['Managers'][self.manager]['primaryFont'] == '' :
            if setIt(Ctype, font) :
                self.project.log.writeToLog('FONT-035', [Ctype,font])
                return True
        elif force :
            if setIt(Ctype, font) :
                self.project.log.writeToLog('FONT-032', [font,Ctype])
                return True
        elif self.project.projConfig['Managers'][self.manager]['primaryFont'] :
            self.project.log.writeToLog('FONT-037', [self.project.projConfig['Managers'][self.manager]['primaryFont'],Ctype])
            return True
        else :
            self.project.log.writeToLog('FONT-030', [font,Ctype])
            return True

        return False


    def checkForSubFont (self, font) :
        '''Return the true name of the font to be used if the one given
        is pointing to a substitute font in the same font family.'''

        # Check for the font family bundle, look in user resources first
        userSource = os.path.join(self.project.userConfig['Resources']['fonts'], font + '.zip')
        rapumaSource = os.path.join(self.project.local.rapumaFontsFolder, font + '.zip')
        source = ''
        if os.path.isfile(userSource) :
            source = userSource
        elif os.path.isfile(rapumaSource) :
            source = rapumaSource
        else :
            self.project.log.writeToLog('FONT-120', [font + '.zip'])
            dieNow()

        if not os.path.isfile(source) :
            self.project.log.writeToLog('FONT-041', [fName(source)])
            dieNow()

        if isInZip(font + '.xml', source) :
            xmlFile = font + '/' + font + '.xml'
            tmpFolder = os.path.join(self.project.local.projConfFolder, font)
            # Extract to a temp file/folder
            myzip = zipfile.ZipFile(source)
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
            self.project.log.writeToLog('FONT-040', [font + '.xml'])
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
            self.project.log.writeToLog('FONT-040', [fName(metaDataSource)])
            dieNow()

        # See if this font is already in the font config file
        if not testForSetting(self.fontConfig, 'Fonts', font) :
            buildConfSection(self.fontConfig, 'Fonts')

        # Set as primary for the calling cType if there is none now
        if not self.project.projConfig['Managers'][self.manager]['primaryFont'] :
            self.project.projConfig['Managers'][self.manager]['primaryFont'] = font

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
            if len(self.project.projConfig['Managers'][self.manager]['installedFonts']) == 0 :
                self.project.projConfig['Managers'][self.manager]['installedFonts'] = [font]
            else :
                fontList = self.project.projConfig['Managers'][self.manager]['installedFonts']
                if fontList != [font] :
                    self.project.projConfig['Managers'][self.manager]['installedFonts'] = addToList(fontList, font)
            primFont = self.project.projConfig['Managers'][self.manager]['primaryFont']
            if primFont != font and (primFont == '' or primFont == 'None') :
                self.project.projConfig['Managers'][self.manager]['primaryFont'] = font

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
            if len(self.project.projConfig['Managers'][self.manager]['installedFonts']) == 0 :
                self.project.projConfig['Managers'][self.manager]['installedFonts'] = [font]
            else :
                fontList = self.project.projConfig['Managers'][self.manager]['installedFonts']
                if fontList != [font] :
                    self.project.projConfig['Managers'][self.manager]['installedFonts'] = addToList(fontList, font)

            primFont = self.project.projConfig['Managers'][self.manager]['primaryFont']
            if primFont != font and (primFont == '' or primFont == 'None') :
                self.project.projConfig['Managers'][self.manager]['primaryFont'] = font

            self.project.log.writeToLog('FONT-045', [font])
            writeConfFile(self.project.projConfig)
            return True


    def copyInFont (self, font, force = False) :
        '''Copy a font into a project. The font is bundled with other 
        necessary components in a .zip file. If the font folder is
        already there we assume there is a font there and we do not 
        proceed unless force is set to True.

        If the force flag is set, then we delete any exsisting font and
        extract a new one in its place.'''

        # First be sure this is a font we can work with
        font = self.checkForSubFont(font)

        def extract (source, confXml) :
            if zipfile.is_zipfile(source) :
                myzip = zipfile.ZipFile(source, 'r')
                myzip.extractall(self.project.local.projFontsFolder)
                # Double check extract
                if os.path.isfile(confXml) :
                    return True


# FIXME: Something is wrong here, font didn't install when called by text.py

#        import pdb; pdb.set_trace()

        # Look in user resources first
        userSource = os.path.join(self.project.userConfig['Resources']['fonts'], font + '.zip')
        rapumaSource = os.path.join(self.project.local.rapumaFontsFolder, font + '.zip')
        confXml = os.path.join(self.project.local.projFontsFolder, font, font + '.xml')
        if os.path.isfile(userSource) :
            source = userSource
        elif os.path.isfile(rapumaSource) :
            source = rapumaSource
        else :
            self.project.log.writeToLog('FONT-120', [source])

        # When is force is used, delete the existing font to ensure a clean copy
        if force :
            try :
                shutil.rmtree(os.path.join(self.project.local.projFontsFolder, font))
            except :
                pass
            if extract(source, confXml) :
                self.project.log.writeToLog('FONT-060', [fName(source)])
                return True
            else :
                self.project.log.writeToLog('FONT-065', [font])
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

                    self.project.log.writeToLog('FONT-065', [font])
                    return False


    def installFont (self, font, force = False) :
        '''It is a two step process to install a font. This will both 
        copy in a font and record a font in one call. Do not try to
        install a substitute font.'''

        font = self.checkForSubFont(font)
        cRes = self.copyInFont(font, force)
        rRes = self.recordFont(self.cType, font, force)
        if cRes and rRes :
            self.project.log.writeToLog('FONT-130', [font])
            return True


    def removeFont (self, cType, font, force = None) :
        '''Remove a font from a component type which will virtually disconnect 
        it from the calling component type. However, if the force switch is set,
        then remove the font, regardless as to if it is used by another component
        or not. This is useful for purging a font from a project but should be
        used with care.'''

        def removePConfSettings (Ctype, font) :
            # Adjust installed fonts list if needed
            fontList = self.project.projConfig['Managers'][self.manager]['installedFonts']
            primFont = self.project.projConfig['Managers'][self.manager]['primaryFont']
            if font in fontList :
                fontList.remove(font)
                self.project.projConfig['Managers'][self.manager]['installedFonts'] = fontList
            # There has to be a primary font no matter what. If the font being
            # removed was primary, then try setting the first 
            if primFont == font :
                if len(fontList) == 0 :
                    self.project.projConfig['Managers'][self.manager]['primaryFont'] = ''
                    self.project.log.writeToLog('FONT-090', [font,Ctype])
                else :
                    self.project.projConfig['Managers'][self.manager]['primaryFont'] = fontList[0]

        def removeFConfSettings (font) :
            if testForSetting(self.fontConfig['Fonts'], font) :
                del self.fontConfig['Fonts'][font]
                return True

        # CompTypes need first letter capitalized to find them
        Ctype = cType.capitalize()

        # Remove settings for this font if we find it in the specified cType
        if font in self.project.projConfig['Managers'][self.manager]['installedFonts'] :
            removePConfSettings(Ctype, font)
            self.project.log.writeToLog('FONT-080', [font,Ctype])
            if force :
                shutil.rmtree(os.path.join(self.project.local.projFontsFolder, font))
                # Since this is a force we want to delete settings in the fontConfFile too
                removeFConfSettings(font)
                # Now remove settings from all the other cTypes
                for ct in self.project.projConfig['CompTypes'].keys() :
                    if ct != cType :
                        removePConfSettings(ct.capitalize(), font)
                self.project.log.writeToLog('FONT-082', [font,])

            # Write out the new settings files
            writeConfFile(self.fontConfig)
            writeConfFile(self.project.projConfig)
            return True
        else :
            self.project.log.writeToLog('FONT-085', [font,Ctype])
            return False


    def varifyFont (self) :
        '''Varify a font is installed in the project.'''

#        import pdb; pdb.set_trace()

        if self.sourceEditor.lower() == 'paratext' :
            # If this a PT project there should be something in ptDefaultFont
            font = self.checkForSubFont(self.ptDefaultFont)
        elif self.sourceEditor.lower() == 'generic' :
            if self.primaryFont :
                font = self.primaryFont
            else :
                font = self.checkForSubFont('DefaultFont')
        else :
            self.project.log.writeToLog('FONT-110', [self.sourceEditor])

        if os.path.isdir(os.path.join(self.project.local.projFontsFolder, font)) and self.primaryFont == font :
            return True



