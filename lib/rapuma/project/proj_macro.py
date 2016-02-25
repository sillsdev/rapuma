#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (sparkycbr at gmail dot com)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project macro configuration tasks.


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
from rapuma.project.proj_config         import Config

#from rapuma.group.usfmTex               import UsfmTex


###############################################################################
################################## Begin Class ################################
###############################################################################

class Macro (object) :

    def __init__(self, pid, cType, gid=None) :
        '''Do the primary initialization for this class.'''

        self.pid                            = pid
        self.gid                            = gid
        self.cType                          = cType
        self.user                           = UserConfig()
        self.userConfig                     = self.user.userConfig
        self.projHome                       = os.path.join(os.path.expanduser(self.userConfig['Resources']['projects']), self.pid)
        self.local                          = ProjLocal(pid, gid, cType)


#        import pdb; pdb.set_trace()


        self.proj_config                    = Config(pid)
        self.proj_config.getProjectConfig()
        self.projectConfig                  = self.proj_config.projectConfig
        self.layoutConfig                   = self.proj_config.layoutConfig
        self.tools                          = Tools()
        self.log                            = ProjLog(pid)
        # Create config placeholders
        self.layoutConfig                   = None
        self.illustrationConfig             = None
        self.macroConfig                    = self.tools.loadConfig(self.local.macroConfFile, self.local.macroConfXmlFile)

        # Log messages for this module
        self.errorCodes     = {
            '3010' : ['ERR', 'No macro package is registered for the [<<1>>] component type.'],
            '3020' : ['ERR', 'Cannot update! No macro package is registered for the [<<1>>] component type.'],
            '3050' : ['ERR', 'Macro package file not found: [<<1>>]'],
            '3100' : ['ERR', 'Macro package: [<<1>>] already exists in the project. I am not allowed to copy over an existing package.'],
            '3200' : ['ERR', 'Failed to install macro package: [<<1>>]'],
            '3300' : ['MSG', 'Installed macro package: [<<1>>], Reinitialized [<<2>>]'],
            '3310' : ['ERR', 'Failed to copy [<<1>>] to folder [<<2>>].'],
            '3400' : ['MSG', 'Removed macro package configuration settings for: [<<1>>] from the macro.conf file.'],
            '3500' : ['MSG', 'Removed macro package [<<1>>] folder and all files contained.'],
            '3600' : ['MSG', 'Updated component type [<<1>>] with macro package [<<2>>]'],
            '3650' : ['ERR', 'Failed to updated macro package [<<1>>]']
        }

###############################################################################
###################### Macro Package Handling Functions #######################
###############################################################################
######################## Error Code Block Series = 3000 #######################
###############################################################################

    def createMacroFiles (self, macPackId) :
        '''Create all the necessary macro file names with their assigned paths.'''

        self.projMacPackFolder = os.path.join(self.local.projMacPackFolder, macPackId)

        texFileIds = {'preStyTexExtFile':'preSty-ext.tex', 'macSettingsFile':'settings.tex', 
                        'extTexFile':'extension.tex', 'grpExtTexFile': self.gid + '-extension.tex', 
                        '':'', '':'', '':'', '':'', '':'', }
        styFileIds = {'glbExtStyFile':'extension.sty', 'grpExtStyFile': self.gid + '-extension.sty', 
                        '':'', '':'', '':'', '':'', '':''}


        #<file>
            #<name>TeX lccode Definition File</name>
            #<description>The TeX file that contains lccode definitions and is linked with the hypenation exclusions file.</description>
            #<fileID>lccodeTexFile</fileID>
            #<fileName>[self:gid]-lccode.tex</fileName>
            #<filePath>[self:projGidFolder]</filePath>
            #<depends></depends>
            #<relies></relies>
            #<note>This file is located in the component group folder to allow more segregated processing.</note>
        #</file>
        #<file>
            #<name>TeX Group Hyphenation Exclusions File</name>
            #<description>The file that contains the hypenation words exclusions list for the current group that TeX will use to render the text.</description>
            #<fileID>grpHyphExcTexFile</fileID>
            #<fileName>[self:gid]-hyphenation.tex</fileName>
            #<filePath>[self:projGidFolder]</filePath>
            #<depends></depends>
            #<relies></relies>
            #<note>This file is located in the component group folder to allow more segregated processing.</note>
        #</file>



    def getMacPackIdFromFileName (self, fileName) :
        '''Return the macPack ID based on the file name'''

        # File name less ext is the ID
        parts = len(fileName.split('.'))
        return '.'.join(fileName.split('.')[:parts-1])
    
    
    def getMacPackIdFromSource (self, source) :
        '''Return the macPack ID based on the complete path and file name.'''

        # Get the file name from the path
        fileName = self.tools.fName(source)
        # Return the ID
        return self.getMacPackIdFromFileName(fileName)


    def addMacPack (self, source) :
        '''Add a macro package to the project. It will not work if
        the same package is already present. Remove must be used
        to get rid of the existing one first.'''

#        import pdb; pdb.set_trace()

        macPackId = self.getMacPackIdFromSource(source)
        confXml = os.path.join(self.local.projMacroFolder, macPackId, macPackId + '.xml')
        if not os.path.isfile(source) :
            self.log.writeToLog(self.errorCodes['3050'], [source])

        # Do not add/install if there seems to be a macro package there already
        if self.projectConfig['CompTypes'][self.cType.capitalize()]['macroPackage'] and os.path.exists(self.local.macroConfFile) :
            self.log.writeToLog(self.errorCodes['3100'], [macPackId])
            return False

        # Set the projectConf to the new/same package
        self.projectConfig['CompTypes'][self.cType.capitalize()]['macroPackage'] = macPackId
        self.tools.writeConfFile(self.projectConfig)

        # If we got this far, install the a fresh copy of the macPack
        self.installMacPackOnly(source)
        # Move the style files and custom TeX files out of the macPack
        self.moveMacStyles(macPackId)
        self.moveMacTex(macPackId)

        # Create a fresh macro.conf file if it dosn't exist
        if not os.path.isfile(self.local.macroConfFile) :
            self.macroConfig = self.tools.initNewConfig(self.local.macroConfFile, self.local.macroConfXmlFile)
        # Inject information from this particular macro package
        mInfo = self.tools.getXMLSettings(confXml)
        self.macroConfig['Macros'][macPackId] = mInfo.dict()

        # Save the settings now
        self.tools.writeConfFile(self.macroConfig)

        self.log.writeToLog(self.errorCodes['3300'], [macPackId, self.local.macroConfFileName])
        
        return True


    def moveMacStyles (self, macPackId) :
        '''Move the default macro package styles out of the freshly installed
        project macro package folder to the project Style folder.'''


#        import pdb; pdb.set_trace()

        # Collect the style files to copy
        for f in self.getMacStyExtFiles(macPackId) :
            source = os.path.join(os.path.join(self.local.projMacroFolder, macPackId, f))
            target = os.path.join(self.local.projStyleFolder, f)
            self.tools.makedirs(self.local.projStyleFolder)
            # Do not overwrite existing files unless force is used
            if not os.path.exists(target) :
                shutil.copy(source, target)
                # Look for default and set to read-only
                defaultStyFile = os.path.join(self.local.projStyleFolder, macPackId + '.sty')
                if target == defaultStyFile :
                    self.tools.makeReadOnly(defaultStyFile)
            # Remove the source to avoid confusion
            if os.path.exists(target) :
                os.remove(source)
            else :
                self.log.writeToLog(self.errorCodes['3310'], [source,self.local.projStyleFolder])


    def getMacStyExtFiles (self, macPackId) :
        '''Return a list of macro package style extention files.'''

        sFiles = []
        macPackFiles = os.listdir(os.path.join(self.local.projMacroFolder, macPackId))
        for f in macPackFiles :
            if f.split('.')[1].lower() == 'sty' :
                sFiles.append(f)
        return sFiles


    def moveMacTex (self, macPackId) :
        '''Move the custom macro package TeX out of the freshly installed
        project macro package folder to the project TeX folder.'''

        # Collect the TeX extention files to copy
        for f in self.getMacTexExtFiles(macPackId) :
            source = os.path.join(os.path.join(self.local.projMacroFolder, macPackId, f))
            target = os.path.join(self.local.projTexFolder, f)
            self.tools.makedirs(self.local.projTexFolder)
            # Do not overwrite existing files
            if not os.path.exists(target) :
                shutil.copy(source, target)
            # Remove the source to avoid confusion
            if os.path.exists(target) :
                os.remove(source)
            else :
                self.log.writeToLog(self.errorCodes['3310'], [source,self.local.projTexFolder])


    def getMacTexExtFiles (self, macPackId) :
        '''Return a list of macro package TeX extention files.'''

        tFiles = []
        macPackFiles = os.listdir(os.path.join(self.local.projMacroFolder, macPackId))
        for f in macPackFiles :
            if f.find('ext.tex') > 0 :
                tFiles.append(f)
        return tFiles


    def removeMacPack (self) :
        '''Remove the macro package from a component type'''

#        import pdb; pdb.set_trace()

        if self.projectConfig['CompTypes'][self.cType.capitalize()]['macroPackage'] != '' :
            macPackId = self.projectConfig['CompTypes'][self.cType.capitalize()]['macroPackage']
        else :
            self.log.writeToLog(self.errorCodes['3010'], [self.cType])
        # Aquire target to delete
        target = os.path.join(self.local.projMacroFolder, macPackId)

        # Remove the macPack settings from the config file if it is there
        try :
            del self.macroConfig['Macros'][macPackId]
            # Save the settings now
            self.tools.writeConfFile(self.macroConfig)
            self.log.writeToLog(self.errorCodes['3400'], [macPackId])
        except :
            pass

        # Now remove the macro folder (with all its contents)
        if os.path.exists(target) :
            shutil.rmtree(target)
            self.log.writeToLog(self.errorCodes['3500'], [macPackId])

        # Remove any style files associated with the macro
        styTarget = os.path.join(self.local.projStyleFolder, macPackId + '.sty')
        self.tools.makeExecutable(styTarget)
        self.tools.removeFile(styTarget)

        # Remove the reference for this macro package from the component type
        # that uses it. Normally that would probably be just be one of them.
        self.projectConfig['CompTypes'][self.cType.capitalize()]['macroPackage'] = ''
        self.tools.writeConfFile(self.projectConfig)


    def updateMacPack (self, source) :
        '''Update a macro package with the latest version but do not 
        touch the config file.'''


        # Do not update if no macro package is registered in the projectConfig
        if not self.projectConfig['CompTypes'][self.cType.capitalize()]['macroPackage'] :
            self.log.writeToLog(self.errorCodes['3020'], [self.cType.capitalize()])
            return False

        macPackId = self.getMacPackIdFromSource(source)
        confXml = os.path.join(self.local.projMacroFolder, macPackId, macPackId + '.xml')
        oldMacPackId = self.projectConfig['CompTypes'][self.cType.capitalize()]['macroPackage']
        oldMacDir = os.path.join(self.local.projMacroFolder, oldMacPackId)
        newMacDir = os.path.join(self.local.projMacroFolder, macPackId)

        # Install the new macPack (but use the old settings)
        if self.installMacPackOnly(source) :
            # The current macro system must have a "master" style file.
            # This is a version of the ParaText style file. Because
            # an update might include an update to the style file,
            # we need to copy that from the macro folder to the Style
            # folder. We will do that now. The name of the file should
            # be the macPackId + ".sty", in theory.
            srcStyleFile = os.path.join(self.local.projMacroFolder, macPackId, macPackId + '.sty')
            oldStyleFile = os.path.join(self.local.projStyleFolder, oldMacPackId + '.sty')
            newStyleFile = os.path.join(self.local.projStyleFolder, macPackId + '.sty')
            # Unlock the old one so it can be deleted.
            self.tools.makeExecutable(oldStyleFile)
            self.tools.removeFile(oldStyleFile)
            # Now copy in the new one.
            shutil.copy(srcStyleFile, newStyleFile)
            # The style file should never be edited by the user, relock it
            self.tools.makeReadOnly(newStyleFile)
            # Update exsisting extention file names. We never want to loose 
            # any settings that the user may have added to the extention
            # files so we will rename the existing files to have the
            # new ID otherwise the system will not find them at render time.
            oldStyExtFile           = os.path.join(self.local.projStyleFolder, oldMacPackId + '_ext.sty')
            oldTexExtFile           = os.path.join(self.local.projTexFolder, oldMacPackId + '_ext.tex')
            oldTexPreStyExtFile     = os.path.join(self.local.projTexFolder, oldMacPackId + '_preSty-ext.tex')
            newStyExtFile           = os.path.join(self.local.projStyleFolder, macPackId + '_ext.sty')
            newTexExtFile           = os.path.join(self.local.projTexFolder, macPackId + '_ext.tex')
            newTexPreStyExtFile     = os.path.join(self.local.projTexFolder, macPackId + '_preSty-ext.tex')
            # By default, we protect any existing versions
            if os.path.exists(newStyExtFile) :
                os.remove(oldStyExtFile)
            else :
                self.tools.renameFile(oldStyExtFile, newStyExtFile)
            if os.path.exists(newTexExtFile) :
                os.remove(oldTexExtFile)
            else :
                self.tools.renameFile(oldTexExtFile, newTexExtFile)
            if os.path.exists(newTexPreStyExtFile) :
                os.remove(oldTexPreStyExtFile)
            else :
                self.tools.renameFile(oldTexPreStyExtFile, newTexPreStyExtFile)
            # Remove un-needed sty and tex files from the newMacDir to
            # avoid confusion. The ext files never are updated because
            # they could contain custom project code that we don't want
            # to loose in an update.
            for f in self.getMacStyExtFiles(macPackId) :
                source = os.path.join(newMacDir, f)
                if os.path.exists(source) :
                    os.remove(source)
            for f in self.getMacTexExtFiles(macPackId) :
                source = os.path.join(newMacDir, f)
                if os.path.exists(source) :
                    os.remove(source)
            # Remove the old macPack folder
            shutil.rmtree(oldMacDir)
            # Merge new settings into old section (change name to new ID)
            # When updating, we are assuming the new macro is in the same
            # family as the old one. As such, settings should be almost
            # identical, but in case new settings are being added, we will
            # merge them in now.
            oldConfSettings = self.macroConfig['Macros'][oldMacPackId]
            newConfSettings = self.tools.getXMLSettings(confXml)
            # Now merge
            newConfSettings.merge(oldConfSettings)
            # Inject the new section
#            self.tools.buildConfSection(self.macroConfig, macPackId)
            self.macroConfig['Macros'][macPackId] = newConfSettings.dict()
            # Delete the old section
            del self.macroConfig['Macros'][oldMacPackId]
            # Save the changes
            self.tools.writeConfFile(self.macroConfig)

            # Assuming everything went well we will change the macPackID on the cType
            self.projectConfig['CompTypes'][self.cType.capitalize()]['macroPackage'] = macPackId
            self.tools.writeConfFile(self.projectConfig)
            # Report success
            self.log.writeToLog(self.errorCodes['3600'], [self.cType.capitalize(), macPackId])
            return True
        # But if the install fails everything stays the same and we report
        else :
            self.log.writeToLog(self.errorCodes['3650'], [macPackId])
            return False


    def installMacPackOnly (self, source) :
        '''Install the new macro package but only that.'''

#        import pdb; pdb.set_trace()

        if self.tools.pkgExtract(source, self.local.projMacroFolder, self.local.macroConfXmlFile) :
            return True
        else :
            self.log.writeToLog(self.errorCodes['3200'], [self.tools.fName(source)])
            return False



