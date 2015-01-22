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


###############################################################################
################################## Begin Class ################################
###############################################################################

class ProjFont (object) :

    def __init__(self, pid, gid) :
        '''Do the primary initialization for this class.'''

        self.pid                            = pid
        self.gid                            = gid
        self.tools                          = Tools()
        self.user                           = UserConfig()
        self.log                            = ProjLog(pid)
        self.userConfig                     = self.user.userConfig
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
            self.proj_config.getMacPackConfig(self.macPack)
            self.proj_config.loadMacPackFunctions(self.macPack)
            self.macPackConfig      = self.proj_config.macPackConfig

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
            'FONT-042' : ['MSG', 'Force switch was set (-f). [<<1>>] font setup information was force added to project config'],
            'FONT-050' : ['ERR', 'Halt! [<<1>>] not found. - font.copyInFont()'],
            'FONT-070' : ['LOG', 'Copied the [<<1>>] font file into the project. - proj_font.copyInFont()'],
            'FONT-100' : ['ERR', 'This function has not been implemented yet!.  - proj_font.setGlyphMap()'],

            '0010' : ['LOG', 'Wrote out new font configuration (font.__init__())'],

            '1220' : ['ERR', 'The Font bundle file [<<1>>] could not be found. Process halted.'],
            '1235' : ['MSG', 'Font [<<1>>] has been (or was already) installed into the project.'],
            '1237' : ['MSG', 'Font [<<1>>] has been updated.'],
            '1240' : ['ERR', 'Font bundle file [<<1>>] not found.'],
            '1241' : ['ERR', 'Font bundle [<<1>>] not found.'],
            '1245' : ['LOG', '<<1>> font setup information added to project config'],
            '1247' : ['LOG', 'The [<<1>>] font already has a listing in the configuration.'],
            '1260' : ['MSG', 'Force switch was set (-f). The <<1>> font bundle has been force copied into the project font folder. - proj_font.installFont()'],
            '1262' : ['LOG', 'The <<1>> font bundle already exsits in the font folder. - proj_font.installFont()'],
            '1265' : ['ERR', 'Failed to extract the [<<1>>] font bundle into the project. Font install process failed.'],
            '1267' : ['LOG', 'The <<1>> font bundle has been copied into the project font folder. - proj_font.installFont()'],
            '1380' : ['MSG', 'Removed the [<<1>>] font from the [<<2>>] component type settings. - proj_font.removeFont()'],
            '1382' : ['MSG', 'Force switch was set (-f). This process has completely removed the [<<1>>] font and settings from the project. - proj_font.removeFont()'],
            '1385' : ['ERR', 'Could not remove! The [<<1>>] font is not listed in the configuration settings.'],
            '1390' : ['MSG', 'Force was set to true, removed the [<<1>>] font package.'],
            '1395' : ['MSG', 'Could not remove the [<<1>>] font package. It may be used by another group. Use force (-f) to remove the package from the font folder.'],

            '2430' : ['ERR', 'Font [<<1>>] is already the primary font for the [<<2>>] component type.'],
            '2432' : ['MSG', 'Force switch was set (-f). Forced font [<<1>>] to be the primary font for the [<<2>>] component type.'],
            '2435' : ['MSG', 'The primary font for component type [<<1>>] has been set to [<<2>>]'],
            '2437' : ['MSG', 'The font [<<1>>] is already set for component type [<<2>>]. Use -f to force change it to another font.']

        }


###############################################################################
############################ Project Level Functions ##########################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################


    def setGlyphMap (self, cType, font) :
        '''If needed, set the glyph map used for this component type font.'''

        self.log.writeToLog('FONT-100')


    def checkForSubFont (self, font) :
        '''Return the true name of the font to be used if the one given
        is pointing to a substitute font in the same font family.'''

#        import pdb; pdb.set_trace()

        # Check for the font family bundle, look in user resources first
        userSource = os.path.join(self.tools.resolvePath(self.userConfig['Resources']['font']), font + '.zip')
        rapumaSource = os.path.join(self.local.rapumaFontFolder, font + '.zip')
        source = ''
        if os.path.isfile(userSource) :
            source = userSource
        elif os.path.isfile(rapumaSource) :
            source = rapumaSource
        else :
            self.log.writeToLog(self.errorCodes['1220'], [userSource], 'proj_font.checkForSubFont():1220')
        # Double check
        if not os.path.isfile(source) :
            self.log.writeToLog(self.errorCodes['1241'], [source], 'proj_font.checkForSubFont():1241')

        if self.tools.isInZip(font + '.xml', source) :
            xmlFile = font + '/' + font + '.xml'
            tmpFolder = os.path.join(self.local.projConfFolder, font)
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
                return font
        else :
            self.log.writeToLog(self.errorCodes['1240'], [font + '.xml'], 'proj_font.checkForSubFont():1240')


    def makeFontSettings (self) :
        '''Create a FontSettings section in the macPack config file.
        The assumption is there are no general settings there right now.'''

        xmlFile = os.path.join(self.local.rapumaConfigFolder, 'font.xml')
        keyVals = self.tools.getXMLSettings(xmlFile)
        self.macPackConfig['FontSettings'] = keyVals.dict()
        self.tools.writeConfFile(self.macPackConfig)





    def recordFont (self, cType, font, force = None) :
        '''Check for the exsitance of the specified font in the font folder.
        Then extract the meta data into the appropreate configurations.
        If the force flag has been set then delete the old settings and
        install the new settings (or just reset to default settings).'''

#        import pdb; pdb.set_trace()

        # Set vars do initial checks
        metaDataSource = os.path.join(self.local.projFontFolder, font, font + '.xml')
        if not os.path.isfile(metaDataSource) :
            self.log.writeToLog(self.errorCodes['1240'], [font + '.xml', 'proj_font.recordFont():1240'])
            self.tools.dieNow()

        # Set up the font settings section if needed
        if not self.macPackConfig['FontSettings'].has_key('primaryFont') :
            self.makeFontSettings()

        # Make sure the Fonts section is in the macPack config file
        if not self.macPackConfig.has_key('Fonts') :
            self.tools.buildConfSection(self.macPackConfig, 'Fonts')

        # Now check for the font
        if not self.macPackConfig['Fonts'].has_key(font) :
            self.tools.buildConfSection(self.macPackConfig['Fonts'], font)
        else :
            # If force was set, remove the exsisting font info if it is there
            if force :
                #self.removeFontPack(font, True)
                self.removeFontSettings(font)

        # (Re)Inject the font info into the macPack config file.
        fInfo = self.tools.getXMLSettings(metaDataSource)
        self.macPackConfig['Fonts'][font] = fInfo.dict()

        # Set as primary for the calling cType if there is none right now
        if self.macPackConfig['FontSettings']['primaryFont'] == '' :
            self.macPackConfig['FontSettings']['primaryFont'] = font
        # Save the settings now
        self.tools.writeConfFile(self.macPackConfig)

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

#        import pdb; pdb.set_trace()

        # Look in user resources first
        userSource = os.path.join(self.tools.resolvePath(self.userConfig['Resources']['font']), font + '.zip')
        rapumaSource = os.path.join(self.local.rapumaFontFolder, font + '.zip')
        confXml = os.path.join(self.local.projFontFolder, font, font + '.xml')
        if os.path.isfile(userSource) :
            source = userSource
        elif os.path.isfile(rapumaSource) :
            source = rapumaSource
        else :
            self.log.writeToLog(self.errorCodes['1220'], [source])

        # When is force is used, delete the existing font to ensure a clean copy
        if force :
            try :
                shutil.rmtree(os.path.join(self.local.projFontFolder, font))
            except :
                pass
            if self.tools.pkgExtract(source, self.local.projFontFolder, confXml) :
                self.log.writeToLog(self.errorCodes['1260'], [self.tools.fName(source)])
                return True
            else :
                self.log.writeToLog(self.errorCodes['1265'], [font], 'proj_font.installFont():1265')
                return False
        else :
            # With nothing done yet, check for meta data file
            if os.path.isfile(confXml) :
                self.log.writeToLog(self.errorCodes['1262'], [self.tools.fName(source)])
                return True
            else :
                if self.tools.pkgExtract(source, self.local.projFontFolder, confXml) :
                    self.log.writeToLog(self.errorCodes['1267'], [self.tools.fName(source)])
                    return True
                else :

                    self.log.writeToLog(self.errorCodes['1265'], [font])
                    return False


    def installFont (self, font, primary = False) :
        '''It is a three step process to install a font. This will both
        copy in a font and record a font in one call. Do not try to 
        install a substitute font. If force is used, It is assumed 
        that the font being installed will be the primary font so it 
        sets it to be so.'''

#        import pdb; pdb.set_trace()

        font = self.checkForSubFont(font)
        cRes = self.copyInFont(font, primary)
        rRes = self.recordFont(self.cType, font, force)
        pRes = ''
        if force :
            pRes = self.setPrimaryFont(font, force)
        if cRes and rRes and pRes :
            self.log.writeToLog(self.errorCodes['1235'], [font])
            return True


    def updateFontPack (self, font) :
        '''Update a font package but do not change any of the existing settings.'''

        # Delete the existing font package (but not the settings)
        # but make a backup of it in case there is a problem
        fontDir     = os.path.join(self.local.projFontFolder, font)
        fontDirBak  = fontDir + '.bak'
        if os.path.exists(fontDir) :
            shutil.copytree(fontDir, fontDirBak)
            shutil.rmtree(fontDir)
        # Bring in a fresh copy
        cRes = self.copyInFont(font)
        if cRes :
            shutil.rmtree(fontDirBak)
            self.log.writeToLog(self.errorCodes['1237'], [font])
            return True
        else :
            shutil.copytree(fontDirBak, fontDir)


    def varifyFont (self) :
        '''Return True if a primary font is installed in the project. This will
        go as far as looking for the font package folder and if there is any
        information about the font in the macPackConfig.'''

#        import pdb; pdb.set_trace()

        if self.macPackConfig['FontSettings'].has_key('primaryFont') :
            if self.macPackConfig['FontSettings']['primaryFont'] :
                font = self.macPackConfig['FontSettings']['primaryFont']
                if os.path.isdir(os.path.join(self.local.projFontFolder, font)) \
                    and self.macPackConfig['Fonts'][font].has_key('FontInformation') :
                    return True


    def removeFontSettings (self, font) :
        '''Remove the font settings from the project.'''

        if self.macPackConfig['Fonts'].has_key(font) :
            del self.macPackConfig['Fonts'][font]
            self.log.writeToLog(self.errorCodes['1380'], [font,self.Ctype])
            # Adjust installed fonts list if needed
            primFont = self.macPackConfig['FontSettings']['primaryFont']
            # There has to be a primary font no matter what. If the font being
            # removed was primary, then try setting the first 
            if primFont == font :
                newPrim = ''
                if len(self.macPackConfig['Fonts'].keys()) > 0 :
                    newPrim = self.macPackConfig['Fonts'].keys()[0]
                self.setPrimaryFont(newPrim, True)
            return True
        else :
            self.log.writeToLog(self.errorCodes['1385'], [font], 'proj_font.removeFont():1385')
            return False


    def removeFontPack (self, font, force = False) :
        '''Remove a font from a component type which will virtually disconnect 
        it from the calling component type. However, if the force switch is set,
        then remove the font, regardless as to if it is used by another component
        or not. This is useful for purging a font from a project but should be
        used with care.'''

        # First purge the font if force is set
        if force :
            fontDir = os.path.join(self.local.projFontFolder, font)
            if os.path.exists(fontDir) :
                shutil.rmtree(fontDir)
                self.log.writeToLog(self.errorCodes['1390'], [font])
        else :
            self.log.writeToLog(self.errorCodes['1395'], [font])

            self.removeFontSettings(font)

            # Write out the new settings files
            self.tools.writeConfFile(self.macPackConfig)
            return True


###############################################################################
############################ Font Settings Functions ##########################
###############################################################################
######################## Error Code Block Series = 2400 #######################
###############################################################################


    def setPrimaryFont (self, font, force = None) :
        '''Set the primary font for the project.'''

        def setIt (font) :
            self.macPackConfig['FontSettings']['primaryFont'] = font
            self.tools.writeConfFile(self.macPackConfig)
            # Sanity check
            if self.macPackConfig['FontSettings']['primaryFont'] == font :
                return True

        # First check to see if it is already has a primary font set
        if self.macPackConfig['FontSettings']['primaryFont'] == '' :
            if setIt(font) :
                self.log.writeToLog(self.errorCodes['2435'], [self.Ctype,font])
                return True
        elif force :
            if setIt(font) :
                self.log.writeToLog(self.errorCodes['2432'], [font,self.Ctype])

                return True
        elif self.macPackConfig['FontSettings']['primaryFont'] :
            self.log.writeToLog(self.errorCodes['2437'], [self.macPackConfig['FontSettings']['primaryFont'],self.Ctype])
            return True
        else :
            self.log.writeToLog(self.errorCodes['2430'], [font,self.Ctype])
            return True

        return False



