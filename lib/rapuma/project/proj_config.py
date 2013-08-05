#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

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
from rapuma.core.tools                  import Tools, ToolsPath, ToolsGroup
from rapuma.core.user_config            import UserConfig
from rapuma.core.proj_local             import ProjLocal
from rapuma.core.proj_log               import ProjLog
from rapuma.group.usfmTex               import UsfmTex

###############################################################################
################################## Begin Class ################################
###############################################################################

class ProjConfig (object) :

    def __init__(self, pid, gid = None) :
        '''Do the primary initialization for this class.'''

        self.pid                            = pid
        self.gid                            = gid
        self.user                           = UserConfig()
        self.userConfig                     = self.user.userConfig
        self.projHome                       = self.userConfig['Projects'][pid]['projectPath']
        self.mType                          = self.userConfig['Projects'][pid]['projectMediaIDCode']
        self.local                          = ProjLocal(pid)
        self.tools                          = Tools()
        self.log                            = ProjLog(pid)
        # File names
        self.projConfFileName               = 'project.conf'
        self.progConfXmlFileName            = self.mType + '.xml'
        self.layoutConfFileName             = 'layout.conf'
        self.layoutXmlConfFileName          = self.mType + '_layout.xml'
        self.adjustmentConfFileName         = 'adjustment.conf'
        self.adjustmentXmlConfFileName      = 'adjustment.xml'
        self.hyphenConfFileName             = 'hyphenation.conf'
        self.hyphenXmlConfFileName          = 'hyphenation.xml'
        self.illustrationConfFileName       = 'illustration.conf'
        self.illustrationXmlConfFileName    = 'illustration.xml'
        # Paths
        self.projConfFolder                 = self.local.projConfFolder
        self.rapumaConfigFolder             = self.local.rapumaConfigFolder
        # Files with paths
        self.projConfFile                   = os.path.join(self.projConfFolder, self.projConfFileName)
        self.projConfXmlFile                = os.path.join(self.rapumaConfigFolder, self.progConfXmlFileName)
        self.layoutConfFile                 = os.path.join(self.projConfFolder, self.layoutConfFileName)
        self.layoutXmlConfFile              = os.path.join(self.rapumaConfigFolder, self.layoutXmlConfFileName)
        self.adjustmentConfFile             = os.path.join(self.projConfFolder, self.adjustmentConfFileName)
        self.adjustmentXmlConfFile          = os.path.join(self.rapumaConfigFolder, self.adjustmentXmlConfFileName)
        self.hyphenConfFile                 = os.path.join(self.projConfFolder, self.hyphenConfFileName)
        self.hyphenXmlConfFile              = os.path.join(self.rapumaConfigFolder, self.hyphenXmlConfFileName)
        self.illustrationConfFile           = os.path.join(self.projConfFolder, self.illustrationConfFileName)
        self.illustrationXmlConfFile        = os.path.join(self.rapumaConfigFolder, self.illustrationXmlConfFileName)
        # Load the config objects
        self.adjustmentConfig               = self.tools.initConfig(self.adjustmentConfFile, self.adjustmentXmlConfFile)
        self.layoutConfig                   = self.tools.initConfig(self.layoutConfFile, self.layoutXmlConfFile)
        self.projConfig                     = self.tools.initConfig(self.local.projConfFile, self.projConfXmlFile)
        self.hyphenConfig                   = self.tools.initConfig(self.hyphenConfFile, self.hyphenXmlConfFile)
        self.illustrationConfig             = self.tools.initConfig(self.illustrationConfFile, self.illustrationXmlConfFile)

        self.macPackFunctions               = UsfmTex(self.layoutConfig)
        self.tools_path                     = ToolsPath(self.local, self.projConfig, self.userConfig)
        self.tools_group                    = ToolsGroup(self.local, self.projConfig, self.userConfig)

        # Log messages for this module
        self.errorCodes     = {

            '3100' : ['ERR', 'Macro package: [<<1>>] already exists in the project. Use force (-f) to reinstall.'],
            '3200' : ['ERR', 'Failed to install macro package: [<<1>>]'],
            '3300' : ['MSG', 'Install macro package: [<<1>>], Reinitialized [<<2>>]'],
            '3310' : ['ERR', 'Failed to copy [<<1>>] to folder [<<2>>].'],
            '3400' : ['MSG', 'Force set to True. Removed macro package configuration file: [<<1>>]'],
            '3500' : ['MSG', 'Removed macro package [<<1>>] folder and all files contained.'],
            '3600' : ['MSG', 'Updated macro package [<<1>>]']

        }

        # Test for gid before trying to finish the init
        if gid :
            self.csid                           = self.projConfig['Groups'][gid]['csid']
            self.cType                          = self.projConfig['Groups'][gid]['cType']
            self.Ctype                          = self.cType.capitalize()
            # Folder paths
            self.projComponentFolder            = self.local.projComponentFolder
            self.projFontFolder                 = self.local.projFontFolder
            self.projStyleFolder                = self.local.projStyleFolder
            self.projTexFolder                  = self.local.projTexFolder
            self.projMacroFolder                = self.local.projMacroFolder
            self.projHyphenationFolder          = self.local.projHyphenationFolder
            self.rapumaMacroFolder              = self.local.rapumaMacroFolder
            self.rapumaScriptFolder             = self.local.rapumaScriptFolder
            # Just in case source path has not been defined
            try :
                self.sourcePath                 = self.userConfig['Projects'][pid][self.csid + '_sourcePath']
            except :
                self.sourcePath                 = ''
            # Handle macPack data separately
            self.macPack                        = None
            if self.projConfig['CompTypes'][self.Ctype].has_key('macroPackage') and self.projConfig['CompTypes'][self.Ctype]['macroPackage'] != '' :
                self.macPack                    = self.projConfig['CompTypes'][self.Ctype]['macroPackage']
            if self.macPack :
                # File Names
                self.macPackXmlConfFileName     = self.macPack + '.xml'
                self.macPackConfFileName        = self.macPack + '.conf'
                self.macPackFileName            = self.macPack + '.zip'
                # Folder
                self.projMacPackFolder          = os.path.join(self.local.projMacroFolder, self.macPack)

                # File names with paths
                self.macPackConfFile            = os.path.join(self.projConfFolder, self.macPackConfFileName)
                self.macPackXmlConfFile         = os.path.join(self.projMacroFolder, self.macPack, self.macPackXmlConfFileName)
                self.rapumaMacPackFile          = os.path.join(self.rapumaMacroFolder, self.macPackFileName)
                # Load the macro package config
                if not os.path.exists(self.macPackXmlConfFile) :
                    self.addMacPack(self.macPack)

                # Load macPackConfig
                self.macPackConfig              = self.tools.initConfig(self.macPackConfFile, self.macPackXmlConfFile)

                # File names (from a dict made from the macPack XML file)
                # This is used in other modules so we make it a more portable dict format
                self.macPackDict                = self.tools.xmlFileToDict(self.macPackXmlConfFile)
                self.macPackFilesDict = {}
                for sections in self.macPackDict['root']['section'] :
                    if sections['sectionID'] == 'Files' :
                        for section in sections :
                            secItem = sections[section]
                            if type(secItem) is list :
                                for f in secItem :
                                    self.macPackFilesDict[f['moduleID']] = self.processNestedPlaceholders(f['fileName'])

                # Add these file names for this module here
                for k, v in self.macPackFilesDict.iteritems() :
                    setattr(self, k, v)
        else :
            self.cType                      = ''
            self.Ctype                      = ''
            self.macPack                    = ''


###############################################################################
############################ Manager Level Functions ##########################
###############################################################################
####################### Error Code Block Series = 1000 ########################
###############################################################################


    def makeNewProjConf (self, local, pid, pmid, pname, cVersion) :
        '''Create a new project configuration file for a new project.'''

        self.projConfig = ConfigObj(self.tools.getXMLSettings(os.path.join(local.rapumaConfigFolder, pmid + '.xml')), encoding='utf-8')
        # Insert intitial project settings
        self.projConfig['ProjectInfo']['projectMediaIDCode']        = pmid
        self.projConfig['ProjectInfo']['projectName']               = pname
        self.projConfig['ProjectInfo']['creatorID']                 = self.userConfig['System']['userID']
        self.projConfig['ProjectInfo']['projectCreatorVersion']     = cVersion
        self.projConfig['ProjectInfo']['projectCreateDate']         = self.tools.tStamp()
        self.projConfig['ProjectInfo']['projectIDCode']             = pid
        self.projConfig['Backup']['ownerID']                        = self.userConfig['System']['userID']
        # Even though there was no push, we need a time stamp to avoid confusion
        self.projConfig['Backup']['lastCloudPush']                  = self.tools.fullFileTimeStamp()
        self.projConfig.filename                                    = local.projConfFile
        self.projConfig.write()


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
        elif holderKey and holderType == 'function' :
            fnc = getattr(self.macPackFunctions, holderKey)
            result = fnc()
        # A value that is a special character (escaped character)
        elif holderKey and holderType == 'esc' :
            result = self.getEscapeCharacter(holderKey)
        # A value that is a font setting
        elif holderKey and holderType == 'font' :
            result = self.getFontSetting(holderKey)
        # A value that is a path separater character
        elif holderType == 'pathSep' :
            result = os.sep
        # A value that contains a system delclaired value
        # Note this only works if the value we are looking for has
        # been declaired above in the module init
        elif holderType == 'self' :
            result = getattr(self, holderKey)

        return result


    def getFontSetting (self, value) :
        '''Get a special font setting if there is one. Otherwise
        return null.'''

        # FIXME: This may need to be moved to Fonts
        result = ''
        if value == 'mapping' :
            useMapping = self.macPackConfig['FontSettings']['useMapping']
            if useMapping :
                result = ':mapping=' + os.path.join(self.projFontFolder, useMapping)
        elif value == 'renderer' :
            useRenderingSystem = self.macPackConfig['FontSettings']['useRenderingSystem']
            if useRenderingSystem :
                result = '/' + useRenderingSystem
        elif value == 'language' :
            useLanguage = self.macPackConfig['FontSettings']['useLanguage']
            if useLanguage :
                result = ':language=' + useLanguage

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


    def getConfigValue (self, val) :
        '''Return the value from a config function or just pass the
        value through, unchanged.'''

        val = val.split('|')
        dct = ['self.' + val[0]]
        val.remove(val[0])
        for i in val :
            dct.append('["' + i + '"]')

        return eval(''.join(dct))


    def getMeasureUnit (self) :
        '''Return the value with the specified measurement unit attached.'''
        
        return self.layoutConfig['GeneralSettings']['measurementUnit']


###############################################################################
###################### Macro Package Handling Functions #######################
###############################################################################
######################## Error Code Block Series = 3000 #######################
###############################################################################


    def addMacPack (self, package, force = False) :
        '''Add a macro package to the project. If force is set to True
        user style and TeX files will be overwritten.'''

#        import pdb; pdb.set_trace()

        # Set the projConf to the new/same package
        self.projConfig['CompTypes'][self.Ctype]['macroPackage'] = package
        self.tools.writeConfFile(self.projConfig)

        # Recreate some necessary values
        self.macPackFileName            = package + '.zip'
        self.macPackXmlConfFileName     = package + '.xml'
        self.macPackConfFileName        = package + '.conf'
        self.macPackConfFile            = os.path.join(self.projConfFolder, self.macPackConfFileName)
        self.macPackXmlConfFile         = os.path.join(self.projMacroFolder, package, self.macPackXmlConfFileName)
        self.rapumaMacPackFile          = os.path.join(self.rapumaMacroFolder, self.macPackFileName)
        self.projMacPackFolder          = os.path.join(self.local.projMacroFolder, package)


        # Update existing macPack (but not conf file)
        if os.path.exists(self.projMacPackFolder) :
            self.updateMacPack(package, force)

        # If we got this far, install the a fresh copy of the macPack
        self.installMacPackOnly(package)
        # Move the style files and custom TeX files out of the macPack
        self.moveMacStyles(force)
        self.moveMacTex(force)
        self.macPackConfig = self.tools.initConfig(self.macPackConfFile, self.macPackXmlConfFile)
        self.log.writeToLog(self.errorCodes['3300'], [package,self.macPackConfFileName])


    def moveMacStyles (self, force) :
        '''Move the default macro package styles out of the freshly installed
        project macro package folder to the project Style folder.'''

        # Get a list of style files to copy
        styFiles = []
        macPackFiles = os.listdir(self.projMacPackFolder)
        for f in macPackFiles :
            if f.split('.')[1].lower() == 'sty' :
                styFiles.append(f)
        # Collect the style files to copy
        for f in styFiles :
            source = os.path.join(self.projMacPackFolder, f)
            target = os.path.join(self.local.projStyleFolder, f)
            # Do not overwrite existing files unless force is used
            if not os.path.exists(target) or force :
                shutil.copy(source, target)
            # Remove the source to avoid confusion
            if os.path.exists(target) :
                os.remove(source)
            else :
                self.log.writeToLog(self.errorCodes['3310'], [source,self.local.projStyleFolder])


    def moveMacTex (self, force) :
        '''Move the custom macro package TeX out of the freshly installed
        project macro package folder to the project TeX folder.'''

        # Get a list of style files to copy
        texFiles = []
        macPackFiles = os.listdir(self.projMacPackFolder)
        for f in macPackFiles :
            if f.find('-ext.tex') > 0 :
                texFiles.append(f)
        # Collect the style files to copy
        for f in texFiles :
            source = os.path.join(self.projMacPackFolder, f)
            target = os.path.join(self.local.projTexFolder, f)
            # Do not overwrite existing files unless force is used
            if not os.path.exists(target) or force :
                shutil.copy(source, target)
            # Remove the source to avoid confusion
            if os.path.exists(target) :
                os.remove(source)
            else :
                self.log.writeToLog(self.errorCodes['3310'], [source,self.local.projStyleFolder])


    def removeMacPack (self, package, force = False) :
        '''Remove a macro package from a project. Using this will break a project
        as installed font information will be lost from the macro config file
        when it is deleted if force is used. However, there may be times this
        is necessary. If force is not used it will retain the macro config file.
        This is useful when you want to freshen the macro package but bad in
        that custom style and TeX code.'''

        # Set names and path for specified package
        macPackConfFile     = os.path.join(self.local.projConfFolder, package + '.conf')
        macPackFolder       = os.path.join(self.projMacroFolder, package)

        # Remove the macPack config file if required
        if os.path.exists(macPackConfFile) and force :
            os.remove(macPackConfFile)
            self.log.writeToLog(self.errorCodes['3400'], [self.tools.fName(macPackConfFile)])

        # Now remove the macro folder (with all its contents)
        if os.path.exists(macPackFolder) :
            shutil.rmtree(macPackFolder)
            self.log.writeToLog(self.errorCodes['3500'], [package])

        # Remove the reference for this macro package from any component type
        # that uses it. Normally that would probably be just be one of them.
        for comp in self.projConfig['CompTypes'].keys() :
            if self.projConfig['CompTypes'][comp]['macroPackage'] == package :
                self.projConfig['CompTypes'][comp]['macroPackage'] = ''
                self.tools.writeConfFile(self.projConfig)


    def updateMacPack (self, package, force = False) :
        '''Update a macro package with the latest version from Rapuma
        but do not touch the config file. Force must be used.'''

        if force :
            self.installMacPackOnly(package)
            self.log.writeToLog(self.errorCodes['3600'], [package])
        else :
            self.log.writeToLog(self.errorCodes['3100'], [package])


    def installMacPackOnly (self, package) :
        '''Install macro package.'''

        if self.tools.pkgExtract(self.rapumaMacPackFile, self.projMacroFolder, self.macPackXmlConfFile) :
            return True
        else :
            self.log.writeToLog(self.errorCodes['3200'], [package])
            return False



