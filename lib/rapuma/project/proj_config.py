#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (sparkycbr at gmail dot com)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project configuration tasks.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, re
from configobj                          import ConfigObj

# Load the local classes
from rapuma.core.tools                  import Tools
from rapuma.core.user_config            import UserConfig
from rapuma.core.proj_local             import ProjLocal
from rapuma.core.proj_log               import ProjLog
from rapuma.group.usfmTex               import UsfmTex
#from rapuma.project.proj_macro          import Macro

###############################################################################
################################## Begin Class ################################
###############################################################################

class Config (object) :

    def __init__(self, pid, gid=None) :
        '''Do the primary initialization for this class.'''

        self.pid                            = pid
        self.gid                            = gid
        self.user                           = UserConfig()
        self.userConfig                     = self.user.userConfig
        self.projHome                       = os.path.join(os.path.expanduser(os.environ['RAPUMA_PROJECTS']), self.pid)
        self.local                          = ProjLocal(pid, gid)
        self.tools                          = Tools()
        self.log                            = ProjLog(pid)
        # Create config placeholders
        self.projectConfig                  = None
        self.adjustmentConfig               = None
        self.layoutConfig                   = None
        self.illustrationConfig             = None
        self.fontConfig                     = None
        self.macroConfig                    = None

        # Log messages for this module
        self.errorCodes     = {
            '3100' : ['ERR', 'Macro package: [<<1>>] already exists in the project. Use force (-f) to reinstall.'],
            '3200' : ['ERR', 'Failed to install macro package: [<<1>>]'],
            '3300' : ['MSG', 'Install macro package: [<<1>>], Reinitialized [<<2>>]'],
            '3310' : ['ERR', 'Failed to copy [<<1>>] to folder [<<2>>].'],
            '3400' : ['MSG', 'Force set to True. Removed macro package configuration file: [<<1>>]'],
            '3500' : ['MSG', 'Removed macro package [<<1>>] folder and all files contained.'],
            '3600' : ['MSG', 'Updated macro package [<<1>>]'],
            '3650' : ['ERR', 'Failed to updated macro package [<<1>>]']
        }

        # Test for gid before trying to finish the init

#        import pdb; pdb.set_trace()

        if gid :
            if not self.projectConfig :
                self.getProjectConfig()
            # We need to skip over this if the group doesn't exist
            try :
                # Reinitialize local
                self.cType                      = self.projectConfig['Groups'][gid]['cType']
                self.Ctype                      = self.cType.capitalize()
                self.local                      = ProjLocal(pid, gid, self.cType)
            except :
                self.cType                      = None
                self.Ctype                      = None
        else :
            self.cType                      = None
            self.Ctype                      = None



###############################################################################
############################# Get Config Functions ############################
###############################################################################
####################### Error Code Block Series = 0500 ########################
###############################################################################


    def getProjectConfig (self) :
        '''Load/return the project configuation object.'''

#        import pdb; pdb.set_trace()

        self.projectConfig = self.tools.loadConfig(self.local.projectConfFile, self.local.projectConfXmlFile)


    def getAdjustmentConfig (self) :
        '''Load/return the adjustment configuation object.'''

        self.adjustmentConfig = self.tools.loadConfig(self.local.adjustmentConfFile, self.local.adjustmentConfXmlFile)


    def getLayoutConfig (self) :
        '''Load/return the layout configuation object.'''

        self.layoutConfig = self.tools.loadConfig(self.local.layoutConfFile, self.local.layoutConfXmlFile)


    def getIllustrationConfig (self) :
        '''Load/return the illustration configuation object.'''
        
        self.illustrationConfig = self.tools.loadConfig(self.local.illustrationConfFile, self.local.illustrationConfXmlFile)


    def getFontConfig (self) :
        '''Load/return the font configuation object.'''
        
        self.fontConfig = self.tools.loadConfig(self.local.fontConfFile, self.local.fontConfXmlFile)


    def getMacroConfig (self) :
        '''Load/return the macro configuration object.'''

        self.macroConfig = self.tools.loadConfig(self.local.macroConfFile, self.local.macroConfXmlFile)


###############################################################################
############################ Manager Level Functions ##########################
###############################################################################
####################### Error Code Block Series = 1000 ########################
###############################################################################


    def makeNewprojectConf (self, local, pid, cVersion, pmid='book') : 
        '''Create a new project configuration file for a new project.'''

        self.projectConfig = ConfigObj(self.tools.getXMLSettings(os.path.join(local.rapumaConfigFolder, pmid + '.xml')), encoding='utf-8')
        # Insert intitial project settings
        self.projectConfig['ProjectInfo']['projectMediaIDCode']        = pmid
        self.projectConfig['ProjectInfo']['creatorID']                 = self.userConfig['System']['userID']
        self.projectConfig['ProjectInfo']['projectCreatorVersion']     = cVersion
        self.projectConfig['ProjectInfo']['projectCreateDate']         = self.tools.tStamp()
        self.projectConfig['ProjectInfo']['projectIDCode']             = pid
        self.projectConfig['Backup']['ownerID']                        = self.userConfig['System']['userID']
        self.projectConfig['Groups']                                   = {}
        # Even though there was no push, we need a time stamp to avoid confusion
        self.projectConfig['Backup']['lastCloudPush']                  = self.tools.fullFileTimeStamp()
        self.projectConfig.filename                                    = local.projectConfFile
        self.projectConfig.write()


###############################################################################
######################## Basic Config Handling Functions ######################
###############################################################################
####################### Error Code Block Series = 2000 ########################
###############################################################################


    def processSinglePlaceholder (self, ph, value) :
        '''Once we are sure we have a single placeholder (noting embedded) this
        will process it and replace it with the correct value.'''

        holderType = ph.split(':')[0]
        try :
            holderKey = ph.split(':')[1]
        except :
            holderKey = ''

        if self.hasPlaceHolder(value):
            value = self.processNestedPlaceholders(value, '')

        result = ph # If nothing matches below, default to returning placeholder unchanged
        if holderType == 'val' :
            result = value
        # A value that needs a measurement unit attached
        elif holderType == 'mu' :
            result = self.getMeasureUnit()
        # A value that is from a configObj
        elif holderKey and holderType == 'config' :
            result = self.getConfigValue(holderKey)
        # A value that is a path
        elif holderKey and holderType == 'path' :
            result = getattr(self.local, holderKey)
        # A value that is from a configObj
# FIXME: To work around a circular init problem between Config() and Macro()
# the macro package name (UsfmTex) has been hard coded. Not sure how to call
# another function in another class that relies on this class to work.
# This will break when the time comes that another macro family than UsfmTex
# is used to hold the functions needed to process values to be used
        elif holderKey and holderType == 'function' :
#            import pdb; pdb.set_trace()
            fnc = getattr(UsfmTex(self.layoutConfig), holderKey)
            result = fnc()
        # A value that is a special character (escaped character)
        elif holderKey and holderType == 'esc' :
            result = self.getEscapeCharacter(holderKey)
        # A value that is a font setting
        elif holderKey and holderType == 'font' :
            result = self.getFontSetting(holderKey)
        # A value that is a path separator character
        elif holderType == 'pathSep' :
            result = os.sep
        # A value that contains a system declared value
        # Note this only works if the value we are looking for has
        # been declared above in the module init
        elif holderType == 'self' :
#            if holderKey.find('.') >= 0 :
#                splitKey = holderKey.split('.')
#                if splitKey[0] == 'local' :
#                    result = getattr(self.local, splitKey[1])
#            else :
#                result = getattr(self, holderKey)
            result = getattr(self.local, holderKey)

        return result


    def getFontSetting (self, value) :
        '''Get a special font setting if there is one. Otherwise
        return null.'''

        # FIXME: This may need to be moved to Fonts, plus it might be a
        # little brittle. Using primaryFont for a default might be asking
        # for trouble
        result = ''
        if value == 'mapping' :
            useMapping      = self.fontConfig['GeneralSettings']['useMapping']
            primaryFont     = self.projectConfig['CompTypes'][self.cType.capitalize()]['fontName']
            if useMapping :
                result = ':mapping=' + os.path.join(self.local.projFontFolder, primaryFont, useMapping)
        elif value == 'renderer' :
            useRenderingSystem = self.fontConfig['GeneralSettings']['useRenderingSystem']
            if useRenderingSystem :
                result = '/' + useRenderingSystem
        elif value == 'language' :
            useLanguage = self.fontConfig['GeneralSettings']['useLanguage']
            if useLanguage :
                result = ':language=' + useLanguage
        elif value == 'feature' :
            useFeature = self.fontConfig['GeneralSettings']['useFeature']
            if useFeature :
                result = ':' + useFeature

        return result


    def getEscapeCharacter (self, value) :
        '''Return the character specified by the escape code.'''

        if value == 'lsBracket' :
            return '['
        elif value == 'rsBracket' :
            return ']'
        
        # Add more as needed...


    def processNestedPlaceholders (self, line, value = '') :
        '''Search a string (or line) for a type of Rapuma placeholder and
        insert the value. This is for building certain kinds of config values.'''

        result = []
        end_of_previous_segment = 0
        for (ph_start, ph_end) in self.getPlaceHolder(line) :
            unchanged_segment = line[end_of_previous_segment:ph_start]
            result.append(unchanged_segment)
            ph_text = line[ph_start+1:ph_end]
            replacement = self.processNestedPlaceholders(ph_text, value)
            result.append(unicode(replacement))
            end_of_previous_segment = ph_end+1  # Skip the closing bracket
        result.append(line[end_of_previous_segment:])
        resultline = "".join(result)
        result_text = self.processSinglePlaceholder(resultline, value)
        return result_text


    def hasPlaceHolder (self, line) :
        '''Return True if this line has a data place holder in it.'''

        # If things get more complicated we may need to beef this up a bit
        if line.find('[') > -1 and line.find(']') > -1 :
            return True


    def getPlaceHolder (self, line) :
        '''Return place holder type and a key if one exists from a TeX setting line.
        Pass over the line and return (yield) each placeholder found.'''

        nesting_level = 0
        remembered_idx = None
        for idx, ch in enumerate(line):
            if ch == '[':
                nesting_level += 1
                if remembered_idx is None:
                    remembered_idx = idx
            elif ch == ']':
                nesting_level -= 1
                if nesting_level <= 0:
                    found_idx = remembered_idx
                    remembered_idx = None
                    yield (found_idx, idx)


    def getConfigValue (self, val, default=None) :
        '''Return the value from a config function or just pass the
        value through, unchanged.'''

        keyparts = val.split('|')
        curval = getattr(self, keyparts[0], None)
        if curval is None: return default
        for key in keyparts[1:]:
            curval = curval.get(key, None)
            if curval is None: return default
        return curval


    def getMeasureUnit (self) :
        '''Return the value with the specified measurement unit attached.'''
        
        return self.layoutConfig['GeneralSettings']['measurementUnit']

