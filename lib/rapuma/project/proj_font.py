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

    def __init__(self, pid) :
        '''Do the primary initialization for this class.'''

        self.pid                            = pid
        self.tools                          = Tools()
        self.user                           = UserConfig()
        self.log                            = ProjLog(pid)
        self.userConfig                     = self.user.userConfig
        self.proj_config                    = Config(pid)
        self.proj_config.getProjectConfig()
        self.projectConfig                  = self.proj_config.projectConfig
        self.proj_config.getFontConfig()
        self.fontConfig                     = self.proj_config.fontConfig
        self.local                          = ProjLocal(pid, self.projectConfig)

        # Load all font settings for use in this module
        if self.fontConfig :
            for k, v in self.fontConfig['GeneralSettings'].iteritems() :
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
            '1250' : ['ERR', 'The [<<1>>] font is apparently part of this project. Please remove before trying to re-add this font.'],
            '1260' : ['MSG', 'The <<1>> font bundle has been copied into the project font folder.'],
            '1262' : ['LOG', 'The <<1>> font bundle already exsits in the font folder.'],
            '1265' : ['ERR', 'Failed to extract the [<<1>>] font bundle into the project. Font install process failed.'],
            '1267' : ['LOG', 'The <<1>> font bundle has been copied into the project font folder.'],
            '1280' : ['MSG', 'Failed to install the font: [<<1>>] into the project.'],
            '1370' : ['LOG', 'Removed [<<1>>] font name from project component type: [<<2>>].'],
            '1380' : ['MSG', 'Removed the [<<1>>] font from the project.'],
            '1382' : ['MSG', 'Force switch was set (-f). This process has completely removed the [<<1>>] font and settings from the project. - proj_font.removeFont()'],
            '1390' : ['LOG', 'Removed the [<<1>>] font package.'],
            '1395' : ['MSG', 'Could not remove the [<<1>>] font package. It may be used by another group. Use force (-f) to remove the package from the font folder.']

        }


###############################################################################
############################ Project Level Functions ##########################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################


    def setGlyphMap (self, cType, font) :
        '''If needed, set the glyph map used for this component type font.'''

        self.log.writeToLog('FONT-100')


    def getFontIdFromFileName (self, fileName) :
        '''Return the font ID based on the file name'''

        # File name less ext is the font ID
        parts = len(fileName.split('.'))
        return '.'.join(fileName.split('.')[:parts-1])
    
    
    def getFontIdFromSource (self, source) :
        '''Return the font ID based on the complete path and file name.'''

        # Get the file name from the path
        fileName = self.tools.fName(source)
        # Return the font ID
        return self.getFontIdFromFileName(fileName)


    def recordFont (self, fontId, cType=None) :
        '''Check for the exsitance of the specified font in the font folder.
        Then extract the meta data into the appropreate configurations.'''

#        import pdb; pdb.set_trace()

        # Set vars do initial checks
        metaDataSource = os.path.join(self.local.projFontFolder, fontId, fontId + '.xml')
        if not os.path.isfile(metaDataSource) :
            self.log.writeToLog(self.errorCodes['1240'], [fontId + '.xml', 'proj_font.recordFont():1240'])
        
        # Build the Fonts section in the config (if needed)
        self.tools.buildConfSection(self.fontConfig, 'Fonts')

        # (Re)Inject the font info into the macPack config file.
        fInfo = self.tools.getXMLSettings(metaDataSource)
        self.fontConfig['Fonts'][fontId] = fInfo.dict()

        # Save the settings now
        self.tools.writeConfFile(self.fontConfig)
        
        # If a component type was specified, record that as well
        if cType :
            self.projectConfig['CompTypes'][cType.capitalize()]['fontName'] = fontId
            self.tools.writeConfFile(self.projectConfig)
        
        return True


    def copyInFont (self, source) :
        '''Copy a font into a project. The font is bundled with other 
        necessary components in a .zip file. If the font folder is
        already there we assume there is a font there and we do not 
        proceed. The user will be prompted to remove the old one first.'''

        fontId = self.getFontIdFromSource(source)
        confXml = os.path.join(self.local.projFontFolder, fontId, fontId + '.xml')
        if not os.path.isfile(source) :
            self.log.writeToLog(self.errorCodes['1220'], [source])

        # Install new copy
        if self.tools.pkgExtract(source, self.local.projFontFolder, confXml) :
            self.log.writeToLog(self.errorCodes['1260'], [self.tools.fName(source)])
            return True
        else :
            self.log.writeToLog(self.errorCodes['1265'], [fontId])
            return False


    def addFont (self, source, cType=None) :
        '''It is a three step process to install a font. This will both
        copy in a font and record it in one call. Do not try to 
        install a substitute font. Path is assumed to exsist and contains
        the file name too.'''

#        import pdb; pdb.set_trace()

        fontId = self.getFontIdFromSource(source)
        # Check for existance, never copy over
        if self.isFont(fontId) :
            self.log.writeToLog(self.errorCodes['1250'], [fontId])
        # Now install and record
        if self.copyInFont(source) and self.recordFont(fontId, cType) :
            self.log.writeToLog(self.errorCodes['1235'], [fontId])
            return True
        else :
            self.log.writeToLog(self.errorCodes['1280'], [fontId])
            return False


    def updateFontPack (self, source) :
        '''Update a font package but do not change any of the existing
        settings. If there are setting issues (changes) it would be
        best to remove, then reinstall.'''

#        import pdb; pdb.set_trace()

        # Get the font ID
        fontId      = self.getFontIdFromSource(source)
        # Be sure the font is in the project
        if self.isFont(fontId) :
            # Remove old copy
            if os.path.exists(os.path.join(self.local.projFontFolder, fontId)) :
                shutil.rmtree(os.path.join(self.local.projFontFolder, fontId))
            # Bring in a fresh copy
            if self.copyInFont(source) :
                self.log.writeToLog(self.errorCodes['1237'], [fontId])
                return True


    def removeFontSettings (self, fontId) :
        '''Remove the font settings from the project.'''

#        import pdb; pdb.set_trace()
        if self.fontConfig.has_key('Fonts') :
            if self.fontConfig['Fonts'].has_key(fontId) :
                del self.fontConfig['Fonts'][fontId]
                # Write out the new settings files
                self.tools.writeConfFile(self.fontConfig)
                self.log.writeToLog(self.errorCodes['1380'], [fontId])
            # Check to see if this font is listed in any of the cTypes
            # If so, remove it.
            found = 0
            for cType in self.projectConfig['CompTypes'].keys() :
                if self.projectConfig['CompTypes'][cType.capitalize()]['fontName'] == fontId :
                    self.projectConfig['CompTypes'][cType.capitalize()]['fontName'] = ''
                    self.log.writeToLog(self.errorCodes['1370'], [fontId, cType])
                    found +=1
            if found > 0 :
                self.tools.writeConfFile(self.projectConfig)

            return True


    def removeFontPack (self, fontId) :
        '''Remove a font from a component type which will virtually disconnect 
        it from the calling component type. However, if the force switch is set,
        then remove the font, regardless as to if it is used by another component
        or not. This is useful for purging a font from a project but should be
        used with care.'''

        # Purge the font files and folder
        fontDir = os.path.join(self.local.projFontFolder, fontId)
        if os.path.exists(fontDir) :
            shutil.rmtree(fontDir)
            self.log.writeToLog(self.errorCodes['1390'], [fontId])

        if self.removeFontSettings(fontId) :
            return True


###############################################################################
############################ Font Settings Functions ##########################
###############################################################################
######################## Error Code Block Series = 2000 #######################
###############################################################################

    def isFont (self, fontId) :
        '''Return if it is varified that this font is part of the project.'''
        
        # First do a cusory check to see if at least the font folder is there
        fontDir = os.path.join(self.local.projFontFolder, fontId)
        if not os.path.exists(fontDir) :
            return False
            
        # If the above passed, check in the font config to see if it is listed
        if not self.fontConfig['Fonts'].has_key(fontId) :
            return False
        
        # If the two tests above passed it is probably there
        return True
