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
from rapuma.core.paratext           import Paratext
from rapuma.core.user_config        import UserConfig
from rapuma.core.proj_local         import ProjLocal
from rapuma.core.proj_log           import ProjLog
from rapuma.project.proj_config     import ProjConfig


###############################################################################
################################## Begin Class ################################
###############################################################################

class ProjFont (object) :

    def __init__(self, pid, gid) :
        '''Do the primary initialization for this class.'''

        self.pid                        = pid
        self.gid                        = gid
        self.tools                      = Tools()
        self.pt_tools                   = Paratext(pid, gid)
        self.user                       = UserConfig()
        self.userConfig                 = self.user.userConfig
        self.proj_config                = ProjConfig(pid, gid)
        self.projConfig                 = self.proj_config.projConfig
        self.fontConfig                 = self.proj_config.fontConfig
        self.local                      = ProjLocal(pid)
        self.log                        = ProjLog(pid)
        self.cType                      = self.projConfig['Groups'][gid]['cType']
        self.Ctype                      = self.cType.capitalize()
        self.mType                      = self.userConfig['Projects'][self.pid]['projectMediaIDCode']

        self.generalSettings            = self.fontConfig['GeneralSettings']

        for k, v in self.generalSettings.iteritems() :
            setattr(self, k, v)

        # Get our component sourceEditor
        self.sourceEditor               = self.pt_tools.getSourceEditor(self.cType)
        if self.ptDefaultFont == '' :
            ptSet = self.pt_tools.getPTSettings()
            if ptSet :
                setattr(self, 'ptDefaultFont', ptSet['ScriptureText']['DefaultFont'])
                self.fontConfig['GeneralSettings']['ptDefaultFont'] = self.ptDefaultFont
                self.tools.writeConfFile(self.fontConfig)

        # Log messages for this module
        self.errorCodes     = {
            'FONT-000' : ['MSG', 'Font module messages'],
            'FONT-005' : ['MSG', 'FONT-005 - Unassigned error message ID.'],
            'FONT-015' : ['MSG', 'FONT-015 - Unassigned error message ID.'],
            'FONT-020' : ['ERR', 'Failed to find font setting in ParaTExt project (.ssf file). A primary font must be set before this component can be successfully rendered.'],
            'FONT-025' : ['ERR', 'No source editor was found for this project. Please enter this setting before continuing.'],
            'FONT-042' : ['MSG', 'Force switch was set (-f). [<<1>>] font setup information was force added to project config'],
            'FONT-050' : ['ERR', 'Halt! [<<1>>] not found. - font.copyInFont()'],
            'FONT-070' : ['LOG', 'Copied the [<<1>>] font file into the project. - font.copyInFont()'],
            'FONT-080' : ['MSG', 'Removed the [<<1>>] font from the [<<2>>] component type settings. - font.removeFont()'],
            'FONT-082' : ['MSG', 'Force switch was set (-f). This process has completely removed the [<<1>>] font and settings from the project. - font.removeFont()'],
            'FONT-085' : ['ERR', 'Could not remove! The [<<1>>] font was not listed in the [<<2>>] component type settings. - font.removeFont()'],
            'FONT-090' : ['WRN', 'No replacement for primary font found.  - font.removeFont()'],
            'FONT-100' : ['ERR', 'This function has not been implemented yet!.  - font.setGlyphMap()'],

            '0010' : ['LOG', 'Wrote out new font configuration (font.__init__())'],

            '0210' : ['ERR', 'This editor: [<<1>>] is not recognized by the system.'],
            '0220' : ['ERR', 'The Font bundle file [<<1>>] could not be found. Process halted.'],
            '0235' : ['LOG', 'Font [<<1>>] has been (or was already) installed into the project.'],
            '0240' : ['ERR', 'Font bundle file [<<1>>] not found.'],
            '0241' : ['ERR', 'Font bundle [<<1>>] not found.'],
            '0245' : ['LOG', '<<1>> font setup information added to project config'],
            '0247' : ['LOG', 'The [<<1>>] font already has a listing in the configuration.'],
            '0260' : ['MSG', 'Force switch was set (-f). The <<1>> font bundle has been force copied into the project font folder. - font.installFont()'],
            '0262' : ['LOG', 'The <<1>> font bundle already exsits in the font folder. - font.installFont()'],
            '0265' : ['ERR', 'Failed to extract the [<<1>>] font bundle into the project. Font install process failed. - font.installFont()'],
            '0267' : ['MSG', 'The <<1>> font bundle has been copied into the project font folder. - font.installFont()'],

            '0430' : ['ERR', 'Font [<<1>>] is already the primary font for the [<<2>>] component type.'],
            '0432' : ['MSG', 'Force switch was set (-f). Forced font [<<1>>] to be the primary font for the [<<2>>] component type.'],
            '0435' : ['MSG', 'The primary font for component type [<<1>>] has been set to [<<2>>]'],
            '0437' : ['MSG', 'The font [<<1>>] is already set for component type [<<2>>]. Use -f to force change it to another font.'],
        }


###############################################################################
############################ Project Level Functions ##########################
###############################################################################
######################## Error Code Block Series = 0200 #######################
###############################################################################


    def setGlyphMap (self, cType, font) :
        '''If needed, set the glyph map used for this component type font.'''

        self.log.writeToLog('FONT-100')


    def checkForSubFont (self, font) :
        '''Return the true name of the font to be used if the one given
        is pointing to a substitute font in the same font family.'''

#        import pdb; pdb.set_trace()

        # Check for the font family bundle, look in user resources first
        userSource = os.path.join(self.tools.resolvePath(self.userConfig['Resources']['fonts']), font + '.zip')
        rapumaSource = os.path.join(self.local.rapumaFontsFolder, font + '.zip')
        source = ''
        if os.path.isfile(userSource) :
            source = userSource
        elif os.path.isfile(rapumaSource) :
            source = rapumaSource
        else :
            self.log.writeToLog(self.errorCodes['0220'], [userSource], 'font.checkForSubFont():0220')
        # Double check
        if not os.path.isfile(source) :
            self.log.writeToLog(self.errorCodes['0241'], [source], 'font.checkForSubFont():0241')

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
            self.log.writeToLog(self.errorCodes['0240'], [font + '.xml'], 'font.checkForSubFont():0240')


    def recordFont (self, cType, font, force = None) :
        '''Check for the exsitance of the specified font in the font folder.
        Then extract the meta data into the appropreate configurations.
        If the force flag has been set then delete the old settings and
        install the new settings (or just reset to default settings).'''

        # Set vars do initial checks
        metaDataSource = os.path.join(self.local.projFontsFolder, font, font + '.xml')
        if not os.path.isfile(metaDataSource) :
            self.log.writeToLog('FONT-040', [self.tools.fName(metaDataSource)])
            self.tools.dieNow()

        # See if this font is already in the font config file
        if not self.fontConfig.has_key('Fonts') :
            
#            import pdb; pdb.set_trace()

            self.tools.buildConfSection(self.fontConfig, 'Fonts')
            if not self.fontConfig['Fonts'].has_key(font) :
                self.tools.buildConfSection(self.fontConfig['Fonts'], font)

        # Set as primary for the calling cType if there is none now
        if not self.fontConfig['GeneralSettings']['primaryFont'] :
            self.fontConfig['GeneralSettings']['primaryFont'] = font

        # If force was set, force the settings, otherwise, let them be
        if force :
            try :
                del self.fontConfig['Fonts'][font]
            except :
                pass
            # (Re)Inject the font info into the project format config file.
            fInfo = self.tools.getXMLSettings(metaDataSource)
            self.fontConfig['Fonts'][font] = fInfo.dict()
            self.tools.writeConfFile(self.fontConfig)
            # Adjust installed fonts list if needed
            if len(self.fontConfig['GeneralSettings']['installedFonts']) == 0 :
                self.fontConfig['GeneralSettings']['installedFonts'] = [font]
            else :
                fontList = self.fontConfig['GeneralSettings']['installedFonts']
                if fontList != [font] :
                    self.fontConfig['GeneralSettings']['installedFonts'] = self.tools.addToList(fontList, font)
            primFont = self.fontConfig['GeneralSettings']['primaryFont']
            if primFont != font and (primFont == '' or primFont == 'None') :
                self.fontConfig['GeneralSettings']['primaryFont'] = font

            self.log.writeToLog(self.errorCodes['0245'], [font])
            self.tools.writeConfFile(self.projConfig)
            return True

        else :
#            if len(self.fontConfig['Fonts'].get(font)) != 0 :
            if self.fontConfig['Fonts'].has_key(font) :
                self.log.writeToLog(self.errorCodes['0247'], [font])
            else :
                # Inject the font info into the project font config file if it is not there.
                fInfo = self.tools.getXMLSettings(metaDataSource)
                self.fontConfig['Fonts'][font] = fInfo.dict()
                self.tools.writeConfFile(self.fontConfig)
                self.log.writeToLog(self.errorCodes['0245'], [font])

            # Adjust installed fonts list if needed
            if len(self.fontConfig['GeneralSettings']['installedFonts']) == 0 :
                self.fontConfig['GeneralSettings']['installedFonts'] = [font]
            else :
                fontList = self.fontConfig['GeneralSettings']['installedFonts']
                if fontList != [font] :
                    self.fontConfig['GeneralSettings']['installedFonts'] = self.tools.addToList(fontList, font)

            primFont = self.fontConfig['GeneralSettings']['primaryFont']
            if primFont != font and (primFont == '' or primFont == 'None') :
                self.fontConfig['GeneralSettings']['primaryFont'] = font

            self.log.writeToLog(self.errorCodes['0245'], [font])
            self.tools.writeConfFile(self.fontConfig)
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
        userSource = os.path.join(self.tools.resolvePath(self.userConfig['Resources']['fonts']), font + '.zip')
        rapumaSource = os.path.join(self.local.rapumaFontsFolder, font + '.zip')
        confXml = os.path.join(self.local.projFontsFolder, font, font + '.xml')
        if os.path.isfile(userSource) :
            source = userSource
        elif os.path.isfile(rapumaSource) :
            source = rapumaSource
        else :
            self.log.writeToLog(self.errorCodes['0220'], [source])

        # When is force is used, delete the existing font to ensure a clean copy
        if force :
            try :
                shutil.rmtree(os.path.join(self.local.projFontsFolder, font))
            except :
                pass
            if self.tools.pkgExtract(source, self.local.projFontsFolder, confXml) :
                self.log.writeToLog(self.errorCodes['0260'], [self.tools.fName(source)])
                return True
            else :
                self.log.writeToLog(self.errorCodes['0265'], [font])
                return False
        else :
            # With nothing done yet, check for meta data file
            if os.path.isfile(confXml) :
                self.log.writeToLog(self.errorCodes['0262'], [self.tools.fName(source)])
                return True
            else :
                if self.tools.pkgExtract(source, self.local.projFontsFolder, confXml) :
                    self.log.writeToLog(self.errorCodes['0267'], [self.tools.fName(source)])
                    return True
                else :

                    self.log.writeToLog(self.errorCodes['0265'], [font])
                    return False


    def installFont (self, font, force = False) :
        '''It is a two step process to install a font. This will both 
        copy in a font and record a font in one call. Do not try to
        install a substitute font.'''

#        import pdb; pdb.set_trace()

        font = self.checkForSubFont(font)
        cRes = self.copyInFont(font, force)
        rRes = self.recordFont(self.cType, font, force)
        if cRes and rRes :
            self.log.writeToLog(self.errorCodes['0235'], [font])
            return True


    def removeFont (self, cType, font, force = None) :
        '''Remove a font from a component type which will virtually disconnect 
        it from the calling component type. However, if the force switch is set,
        then remove the font, regardless as to if it is used by another component
        or not. This is useful for purging a font from a project but should be
        used with care.'''

        def removePConfSettings (Ctype, font) :
            # Adjust installed fonts list if needed
            fontList = self.fontConfig['GeneralSettings']['installedFonts']
            primFont = self.fontConfig['GeneralSettings']['primaryFont']
            if font in fontList :
                fontList.remove(font)
                self.fontConfig['GeneralSettings']['installedFonts'] = fontList
            # There has to be a primary font no matter what. If the font being
            # removed was primary, then try setting the first 
            if primFont == font :
                if len(fontList) == 0 :
                    self.fontConfig['GeneralSettings']['primaryFont'] = ''
                    self.log.writeToLog('FONT-090', [font,Ctype])
                else :
                    self.fontConfig['GeneralSettings']['primaryFont'] = fontList[0]

        def removeFConfSettings (font) :
            if self.fontConfig['Fonts'].has_key(font) :
                del self.fontConfig['Fonts'][font]
                return True

        # CompTypes need first letter capitalized to find them
        Ctype = cType.capitalize()

        # Remove settings for this font if we find it in the specified cType
        if font in self.fontConfig['GeneralSettings']['installedFonts'] :
            removePConfSettings(Ctype, font)
            self.log.writeToLog('FONT-080', [font,Ctype])
            if force :
                shutil.rmtree(os.path.join(self.local.projFontsFolder, font))
                # Since this is a force we want to delete settings in the fontConfFile too
                removeFConfSettings(font)
                # Now remove settings from all the other cTypes
                for ct in self.projConfig['CompTypes'].keys() :
                    if ct != cType :
                        removePConfSettings(ct.capitalize(), font)
                self.log.writeToLog('FONT-082', [font,])

            # Write out the new settings files
            self.tools.writeConfFile(self.fontConfig)
            self.tools.writeConfFile(self.projConfig)
            return True
        else :
            self.log.writeToLog('FONT-085', [font,Ctype])
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
            self.log.writeToLog(self.errorCodes['0210'], [self.sourceEditor], 'font.varifyFont():0210')

        if os.path.isdir(os.path.join(self.local.projFontsFolder, font)) and self.primaryFont == font :
            return True


###############################################################################
############################ Font Settings Functions ##########################
###############################################################################
######################## Error Code Block Series = 0400 #######################
###############################################################################


    def setPrimaryFont (self, font, force = None) :
        '''Set the primary font for the project.'''

        def setIt (font) :
            self.fontConfig['GeneralSettings']['primaryFont'] = font
            self.tools.writeConfFile(self.fontConfig)
            # Sanity check
            if self.fontConfig['GeneralSettings']['primaryFont'] == font :
                return True

        # First check to see if it is already has a primary font set
        if self.fontConfig['GeneralSettings']['primaryFont'] == '' :
            if setIt(font) :
                self.log.writeToLog(self.errorCodes['0435'], [self.Ctype,font])
                return True
        elif force :
            if setIt(font) :
                self.log.writeToLog(self.errorCodes['0432'], [font,self.Ctype])

                return True
        elif self.fontConfig['GeneralSettings']['primaryFont'] :
            self.log.writeToLog(self.errorCodes['0437'], [self.fontConfig['GeneralSettings']['primaryFont'],self.Ctype])
            return True
        else :
            self.log.writeToLog(self.errorCodes['0430'], [font,Ctype])
            return True

        return False



