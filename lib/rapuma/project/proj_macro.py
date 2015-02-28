#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

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

    def __init__(self, pid, gid=None) :
        '''Do the primary initialization for this class.'''

        self.pid                            = pid
        self.gid                            = gid
        self.user                           = UserConfig()
        self.userConfig                     = self.user.userConfig
        self.projHome                       = os.path.join(os.path.expanduser(self.userConfig['Resources']['projects']), self.pid)
        self.local                          = ProjLocal(pid)
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
            '3050' : ['ERR', 'Macro package file not found: [<<1>>]'],
            '3100' : ['ERR', 'Macro package: [<<1>>] already exists in the project. I am not allowed to copy over an existing package.'],
            '3200' : ['ERR', 'Failed to install macro package: [<<1>>]'],
            '3300' : ['MSG', 'Installed macro package: [<<1>>], Reinitialized [<<2>>]'],
            '3310' : ['ERR', 'Failed to copy [<<1>>] to folder [<<2>>].'],
            '3400' : ['MSG', 'Removed macro package configuration settings for: [<<1>>] from the macro.conf file.'],
            '3500' : ['MSG', 'Removed macro package [<<1>>] folder and all files contained.'],
            '3600' : ['MSG', 'Updated macro package [<<1>>]'],
            '3650' : ['ERR', 'Failed to updated macro package [<<1>>]']
        }

###############################################################################
###################### Macro Package Handling Functions #######################
###############################################################################
######################## Error Code Block Series = 3000 #######################
###############################################################################


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


    def getMacPackConfig (self, macPack) : 
        '''Load/return the macPack configuration object. This is handled different from
        other configs.'''

#        import pdb; pdb.set_trace()

        # Re/Load the macro package config
        self.local = ProjLocal(self.pid, self.gid, self.projectConfig)

# FIXME: We should not be pulling the macPack from inside this function
# It should be tied to asset management. However, we somehow need to get
# the xml file from it so for now, we have to install it here.
        if not os.path.exists(self.local.macroConfXmlFile) :
            self.addMacPack(macPack)

        # Load macPackConfig
        self.macroConfig = self.tools.loadConfig(self.local.macroConfFile, self.local.macroConfXmlFile)








# FIXME: Is this needed?
    #def loadMacPackFunctions (self, macPack) :
        #'''Load the macro package functions that may be used in this module.'''

        ## Create an object that contains the macPack functions
        #self.macPackFunctions = UsfmTex(self.layoutConfig)


    def addMacPack (self, source, cType) :
        '''Add a macro package to the project. It will not work if
        the same package is already present. Remove must be used
        to get rid of the existing one first.'''

#        import pdb; pdb.set_trace()

        macPackId = self.getMacPackIdFromSource(source)
        confXml = os.path.join(self.local.projMacroFolder, macPackId, macPackId + '.xml')
        if not os.path.isfile(source) :
            self.log.writeToLog(self.errorCodes['3050'], [source])

        # Do not add/install if there seems to be a macro package there already
        if self.projectConfig['CompTypes'][cType.capitalize()]['macroPackage'] and os.path.exists(self.local.macroConfFile) :
            self.log.writeToLog(self.errorCodes['3100'], [macPackId])
            return False

        # Set the projectConf to the new/same package
        self.projectConfig['CompTypes'][cType.capitalize()]['macroPackage'] = macPackId
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

        # Collect the style files to copy
        for f in self.getMacStyExtFiles(macPackId) :
            source = os.path.join(os.path.join(self.local.projMacroFolder, macPackId, f))
            target = os.path.join(self.local.projStyleFolder, f)
            self.tools.makedirs(self.local.projStyleFolder)
            # Do not overwrite existing files unless force is used
            if not os.path.exists(target) :
                shutil.copy(source, target)
                # Look for default and set to read-only
                if target == self.local.defaultStyFile :
                    self.tools.makeReadOnly(self.local.defaultStyFile)
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
            # Do not overwrite existing files unless force is used
            if not os.path.exists(target) :
                shutil.copy(source, target)
            # Remove the source to avoid confusion
            if os.path.exists(target) :
                os.remove(source)
            else :
                self.log.writeToLog(self.errorCodes['3310'], [source,self.local.projStyleFolder])


    def getMacTexExtFiles (self, macPackId) :
        '''Return a list of macro package TeX extention files.'''

        tFiles = []
        macPackFiles = os.listdir(os.path.join(self.local.projMacroFolder, macPackId))
        for f in macPackFiles :
            if f.find('-ext.tex') > 0 :
                tFiles.append(f)
        return tFiles


    def removeMacPack (self, cType) :
        '''Remove the macro package from a component type'''

#        import pdb; pdb.set_trace()

        if self.projectConfig['CompTypes'][cType.capitalize()]['macroPackage'] != '' :
            macPackId = self.projectConfig['CompTypes'][cType.capitalize()]['macroPackage']
        else :
            self.log.writeToLog(self.errorCodes['3010'], [cType])
        # Aquire target to delete
        target = os.path.join(self.local.projMacroFolder, macPackId)

        # Remove the macPack settings from the config file
        print self.macroConfig['Macros'][macPackId]
        del self.macroConfig['Macros'][macPackId]
        # Save the settings now
        self.tools.writeConfFile(self.macroConfig)
        self.log.writeToLog(self.errorCodes['3400'], [macPackId])

        # Now remove the macro folder (with all its contents)
        if os.path.exists(target) :
            shutil.rmtree(target)
            self.log.writeToLog(self.errorCodes['3500'], [macPackId])

        # Remove the reference for this macro package from the component type
        # that uses it. Normally that would probably be just be one of them.
        self.projectConfig['CompTypes'][cType.capitalize()]['macroPackage'] = ''
        self.tools.writeConfFile(self.projectConfig)


    def updateMacPack (self, source, cType) :
        '''Update a macro package with the latest version but do not 
        touch the config file.'''

#        import pdb; pdb.set_trace()


# FIXME: work here on connecting cType to the update process
        macPackId = self.getMacPackIdFromSource(source)
        confXml = os.path.join(self.local.projMacroFolder, macPackId, macPackId + '.xml')



        # Be sure we have file names
        self.getMacPackConfig(packageId)
        # Delete the existing macro package (but not the settings)
        # but make a backup first
        macDir          = os.path.join(self.local.projMacroFolder, packageId)
        macDirBak       = macDir + '.bak'
        if os.path.exists(macDir) :
            shutil.copytree(macDir, macDirBak)
            shutil.rmtree(macDir)
        # Reinstall the macPack
        if self.installMacPackOnly(source) :
            # The current macro system must have a "master" style file.
            # This is a version of the ParaText style file. Because
            # an update might include an update to the style file,
            # we meed to copy that from the macro folder to the Style
            # folder. We will do that now. The name of the file should
            # be the macPack + ".sty", in theory. We will copy over the
            # top of the old one.
            # Unlock the old one so it can be copied over.
            self.tools.makeExecutable(self.local.defaultStyFile)
            # Now copy in the new one.
            shutil.copy(os.path.join(macDir, packageId + '.sty'), self.local.defaultStyFile)
            # The style file should never be edited by the user, relock it
            self.tools.makeReadOnly(self.local.defaultStyFile)
            # Remove un-needed sty and tex files from the macDir to
            # avoid confusion. The ext files never are updated because
            # they could contain custom project code that we don't want
            # to loose in an update.
            for f in self.getMacStyExtFiles() :
                source = os.path.join(self.local.projMacPackFolder, f)
                if os.path.exists(source) :
                    os.remove(source)
            for f in self.getMacTexExtFiles() :
                source = os.path.join(self.local.projMacPackFolder, f)
                if os.path.exists(source) :
                    os.remove(source)
            # Remove backup folder
            shutil.rmtree(macDirBak)
            self.log.writeToLog(self.errorCodes['3600'], [packageId])
            return True
        # But if the install fails we need to put things back as they were
        else :
            if os.path.exists(macDirBak) :
                shutil.copytree(macDirBak, macDir)
            # Report the failure
            self.log.writeToLog(self.errorCodes['3650'], [packageId])
            return False


    def installMacPackOnly (self, source) :
        '''Install the new macro package but only that.'''

#        import pdb; pdb.set_trace()

        if self.tools.pkgExtract(source, self.local.projMacroFolder, self.local.macroConfXmlFile) :
            return True
        else :
            self.log.writeToLog(self.errorCodes['3200'], [self.tools.fName(source)])
            return False



