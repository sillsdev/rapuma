#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project tasks.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, zipfile
from configobj                      import ConfigObj, Section

# Load the local classes
from rapuma.core.tools              import Tools
from rapuma.core.user_config        import UserConfig
from rapuma.core.proj_local         import ProjLocal
from rapuma.core.proj_log           import ProjLog
from rapuma.project.proj_config     import Config
from rapuma.project.proj_macro      import Macro


###############################################################################
################################## Begin Class ################################
###############################################################################

class ProjFont (object) :

    def __init__(self, pid, gid) :
        '''Do the primary initialization for this class.'''

        self.pid                            = pid
        self.tools                          = Tools()
        self.user                           = UserConfig()
        self.log                            = ProjLog(pid)
        self.userConfig                     = self.user.userConfig
        self.proj_macro                     = Macro(pid, gid)
        self.proj_config                    = Config(pid, gid)
        self.proj_config.getProjectConfig()
        self.projectConfig                  = self.proj_config.projectConfig
        self.local                          = ProjLocal(pid, gid, self.projectConfig)
        self.cType                          = self.projectConfig['Groups'][gid]['cType']
        self.Ctype                          = self.cType.capitalize()
        self.macPack                        = None
        self.macPackConfig                  = None
        if self.projectConfig['CompTypes'][self.Ctype].has_key('macroPackage') and self.projectConfig['CompTypes'][self.Ctype]['macroPackage'] != '' :
            self.macPack                    = self.projectConfig['CompTypes'][self.Ctype]['macroPackage']
            self.proj_macro.getMacPackConfig(self.macPack)
            self.proj_macro.loadMacPackFunctions(self.macPack)
            self.macPackConfig              = self.proj_macro.macPackConfig

        # The first time this is initialized make sure we have a FontSettings section
        if self.macPackConfig and not self.macPackConfig.has_key('FontSettings') :
            self.tools.buildConfSection(self.macPackConfig, 'FontSettings')

        # Load all font settings for use in this module
        if self.macPackConfig :
            for k, v in self.macPackConfig['FontSettings'].iteritems() :
                setattr(self, k, v)

        # Log messages for this module
        self.errorCodes     = {
            'FONT-000' : ['MSG', 'Font module messages'],
            'FONT-005' : ['MSG', 'FONT-005 - Unassigned error message ID.'],
            'FONT-015' : ['MSG', 'FONT-015 - Unassigned error message ID.'],
            'FONT-020' : ['ERR', 'Failed to find font setting in ParaTExt project (.ssf file). A primary font must be set before this component can be successfully rendered.'],
            'FONT-025' : ['ERR', 'No source editor was found for this project. Please enter this setting before continuing.'],
            'FONT-042' : ['MSG', 'The [<<1>>] font setup information was added to project config'],
            'FONT-050' : ['ERR', 'Halt! [<<1>>] not found. - font.copyInFont()'],
            'FONT-070' : ['LOG', 'Copied the [<<1>>] font file into the project. - proj_font.copyInFont()'],
            'FONT-100' : ['ERR', 'This function has not been implemented yet!.  - proj_font.setGlyphMap()'],

            '0010' : ['LOG', 'Wrote out new font configuration (font.__init__())'],

            '1220' : ['ERR', 'The Font bundle file [<<1>>] could not be found. Process halted.'],
            '1235' : ['MSG', 'Font [<<1>>] has been installed into the project.'],
            '1237' : ['MSG', 'Font [<<1>>] has been updated.'],
            '1240' : ['ERR', 'Font bundle file [<<1>>] not found.'],
            '1241' : ['ERR', 'Font bundle [<<1>>] not found.'],
            '1245' : ['LOG', '<<1>> font setup information added to project config'],
            '1247' : ['LOG', 'The [<<1>>] font already has a listing in the configuration.'],
            '1260' : ['MSG', 'The <<1>> font bundle has been copied into the project font folder. - proj_font.installFont()'],
            '1262' : ['LOG', 'The <<1>> font bundle already exsits in the font folder. - proj_font.installFont()'],
            '1265' : ['ERR', 'Failed to extract the [<<1>>] font bundle into the project. Font install process failed.'],
            '1267' : ['LOG', 'The <<1>> font bundle has been copied into the project font folder. - proj_font.installFont()'],
            '1280' : ['ERR', 'The [<<1>>] font bundle failed to be installed.'],
            '1380' : ['MSG', 'Removed the [<<1>>] font from the [<<2>>] component type settings. - proj_font.removeFont()'],
            '1382' : ['MSG', 'Force switch was set (-f). This process has completely removed the [<<1>>] font and settings from the project. - proj_font.removeFont()'],
            '1385' : ['WRN', 'Could not remove! The [<<1>>] font is not listed in the configuration settings.'],
            '1390' : ['LOG', 'Removed the [<<1>>] font package.'],
            '1395' : ['MSG', 'Could not remove the [<<1>>] font package. It may be used by another group. Use force (-f) to remove the package from the font folder.'],

            '2430' : ['WRN', 'Font [<<1>>] is already the primary font for the [<<2>>] component type.'],
            '2435' : ['MSG', 'The primary font for component type [<<1>>] has been set to [<<2>>]'],

        }


###############################################################################
############################ Project Level Functions ##########################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################


    def setGlyphMap (self, cType, font) :
        '''If needed, set the glyph map used for this component type font.'''

        self.log.writeToLog('FONT-100')


    def getFontId (self, fileName) :
        '''Return the font ID based on the file name'''

        # File name less ext is the font ID
        parts = len(fileName.split('.'))
        return '.'.join(fileName.split('.')[:parts-1])


    def checkForSubFont (self, source) :
        '''Return the true name of the font to be used if the one given
        is pointing to a substitute font in the same font family.'''

#        import pdb; pdb.set_trace()

        # Reality check
        if not os.path.isfile(source) :
            self.log.writeToLog(self.errorCodes['1241'], [source], 'proj_font.checkForSubFont():1241')

        fileName = self.tools.fName(source)
        fontId = self.getFontId(fileName)

        if self.tools.isInZip(fontId + '.xml', source) :
            xmlFile = fontId + '/' + fontId + '.xml'
            tmpFolder = os.path.join(self.local.projConfFolder, fontId)
            # Extract to a temp file/folder
            myzip = zipfile.ZipFile(source)
            myzip.extract(xmlFile, self.local.projConfFolder)
            metaDataSource = os.path.join(self.local.projConfFolder, xmlFile)
            myzip.close()
            fInfo = self.tools.getXMLSettings(metaDataSource)
            # Now kill the temp file and folder
            os.remove(metaDataSource)
            if os.path.isdir(tmpFolder) :
                shutil.rmtree(tmpFolder)
            # Finally check for a substitute font name
            if fInfo['FontInformation'].has_key('substituteFontName') :
                return fInfo['FontInformation']['substituteFontName']
            else :
                return fontId
        else :
            self.log.writeToLog(self.errorCodes['1240'], [fontId + '.xml'], 'proj_font.checkForSubFont():1240')


    def makeFontSettings (self) :
        '''Create a FontSettings section in the macPack config file.
        The assumption is there are no general settings there right now.'''

        xmlFile = os.path.join(self.local.rapumaConfigFolder, 'font.xml')
        keyVals = self.tools.getXMLSettings(xmlFile)
        self.macPackConfig['FontSettings'] = keyVals.dict()
        self.tools.writeConfFile(self.macPackConfig)


    def recordFont (self, fontId) :
        '''Check for the exsitance of the specified font in the font folder.
        Then extract the meta data into the appropreate configurations.'''

#        import pdb; pdb.set_trace()

        # Set vars do initial checks
        metaDataSource = os.path.join(self.local.projFontFolder, fontId, fontId + '.xml')
        if not os.path.isfile(metaDataSource) :
            self.log.writeToLog(self.errorCodes['1240'], [fontId + '.xml', 'proj_font.recordFont():1240'])
            self.tools.dieNow()

        # Set up the font settings section if needed
        if not self.macPackConfig['FontSettings'].has_key('primaryFont') :
            self.makeFontSettings()

        # Make sure the Fonts section is in the macPack config file
        if not self.macPackConfig.has_key('Fonts') :
            self.tools.buildConfSection(self.macPackConfig, 'Fonts')

        # Remove the old settings
        self.removeFontSettings(fontId)

        # (Re)Inject the font info into the macPack config file.
        fInfo = self.tools.getXMLSettings(metaDataSource)
        self.macPackConfig['Fonts'][fontId] = fInfo.dict()

        # Set as primary for the calling cType if there is none right now
        if self.macPackConfig['FontSettings']['primaryFont'] == '' :
            self.macPackConfig['FontSettings']['primaryFont'] = fontId
        # Save the settings now
        self.tools.writeConfFile(self.macPackConfig)

        return True


    def copyInFont (self, source) :
        '''Copy a font into a project. The font is bundled with other 
        necessary components in a .zip file. If the font folder is
        already there we assume there is a font there and we do not 
        proceed. The user will be prompted to remove the old one first.'''

        # First be sure this is a font we can work with
        fontId = self.checkForSubFont(source)

#        import pdb; pdb.set_trace()

        confXml = os.path.join(self.local.projFontFolder, fontId, fontId + '.xml')
        if not os.path.isfile(source) :
            self.log.writeToLog(self.errorCodes['1220'], [source])

        # Remove old copy
        if os.path.exists(os.path.join(self.local.projFontFolder, fontId)) :
            shutil.rmtree(os.path.join(self.local.projFontFolder, fontId))
        # Install new copy
        if self.tools.pkgExtract(source, self.local.projFontFolder, confXml) :
            self.log.writeToLog(self.errorCodes['1260'], [self.tools.fName(source)])
            return True
        else :
            self.log.writeToLog(self.errorCodes['1265'], [fontId], 'proj_font.installFont():1265')
            return False


    def installFont (self, fileName, path, primary = False) :
        '''It is a three step process to install a font. This will both
        copy in a font and record it in one call. Do not try to 
        install a substitute font.'''

#        import pdb; pdb.set_trace()

        fontId = self.getFontId(fileName)
        # Initial source file with path
        source = os.path.join(path, fileName)
        # See if we are working with a substitute
        subId = self.checkForSubFont(source)
        if subId != fontId :
            source = os.path.join(path, subId + '.zip')
            fontId = subId
        # Now install and record
        if self.copyInFont(source) and self.recordFont(fontId) :
            self.log.writeToLog(self.errorCodes['1235'], [fontId])
            return True
        else :
            self.log.writeToLog(self.errorCodes['1280'], [fontId])
            return False


    def updateFontPack (self, fileName, path) :
        '''Update a font package but do not change any of the existing
        settings. If there are setting issues (changes) it would be
        best to remove, then reinstall.'''

        # Set the vars
        fontId      = self.getFontId(fileName)
        source      = os.path.join(path, fileName)
        fontDir     = os.path.join(self.local.projFontFolder, fontId)
        # Be sure the font is in the project
        if self.varifyFont(fontId) :
            # Bring in a fresh copy
            if self.copyInFont(source) :
                self.log.writeToLog(self.errorCodes['1237'], [fontId])
                return True


    def varifyFont (self, fontId) :
        '''Varify that a font has been installed into the project.'''

        if os.path.isdir(os.path.join(self.local.projFontFolder, fontId)) \
            and self.macPackConfig['Fonts'][fontId].has_key('FontInformation') :
            return True


    def verifyPrimaryFont (self) :
        '''Return True if a primary font is installed in the project. This will
        go as far as looking for the font package folder and if there is any
        information about the font in the macPackConfig.'''

#        import pdb; pdb.set_trace()

        if self.macPackConfig['FontSettings'].has_key('primaryFont') :
            if self.macPackConfig['FontSettings']['primaryFont'] :
                fontId = self.macPackConfig['FontSettings']['primaryFont']
                if self.varifyFont :
                    return True


    def removeFontSettings (self, fontId) :
        '''Remove the font settings from the project.'''

#        import pdb; pdb.set_trace()

        if self.macPackConfig['Fonts'].has_key(fontId) :
            del self.macPackConfig['Fonts'][fontId]
            self.log.writeToLog(self.errorCodes['1380'], [fontId, self.Ctype])
            # Adjust installed fonts list if needed
            primFont = self.macPackConfig['FontSettings']['primaryFont']
            # There has to be a primary font no matter what. If the font being
            # removed was primary, then try setting the first 
            if primFont == fontId :
                newPrim = ''
                if len(self.macPackConfig['Fonts'].keys()) > 0 :
                    newPrim = self.macPackConfig['Fonts'].keys()[0]
                self.setPrimaryFont(newPrim)
            return True
        else :
            self.log.writeToLog(self.errorCodes['1385'], [fontId], 'proj_font.removeFont():1385')
            return False


    def removeFontPack (self, fileName) :
        '''Remove a font from a component type which will virtually disconnect 
        it from the calling component type. However, if the force switch is set,
        then remove the font, regardless as to if it is used by another component
        or not. This is useful for purging a font from a project but should be
        used with care.'''

        fontId = self.getFontId(fileName)
        # Purge the font files and folder
        fontDir = os.path.join(self.local.projFontFolder, fontId)
        if os.path.exists(fontDir) :
            shutil.rmtree(fontDir)
            self.log.writeToLog(self.errorCodes['1390'], [fontId])

        self.removeFontSettings(fontId)

        # Write out the new settings files
        self.tools.writeConfFile(self.macPackConfig)
        return True


###############################################################################
############################ Font Settings Functions ##########################
###############################################################################
######################## Error Code Block Series = 2400 #######################
###############################################################################


    def setPrimaryFont (self, fontId) :
        '''Set the primary font for the project.'''

        def setIt (fontId) :
            self.macPackConfig['FontSettings']['primaryFont'] = fontId
            self.tools.writeConfFile(self.macPackConfig)
            # Sanity check
            if self.macPackConfig['FontSettings']['primaryFont'] == fontId :
                return True

        # Might be a file name, not ID
        if fontId.find('.zip') > 0 :
            fontId = self.getFontId(fontId)

        # First check to see if it is already has a primary font set
        if not self.macPackConfig['FontSettings']['primaryFont'] == fontId :
            if setIt(fontId) :
                self.log.writeToLog(self.errorCodes['2435'], [self.Ctype, fontId])
                return True
        else :
            self.log.writeToLog(self.errorCodes['2430'], [fontId, self.Ctype])
            return True



