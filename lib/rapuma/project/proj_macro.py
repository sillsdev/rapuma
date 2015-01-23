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
from rapuma.group.usfmTex               import UsfmTex
from rapuma.project.proj_config         import Config


###############################################################################
################################## Begin Class ################################
###############################################################################

class Macro (object) :

    def __init__(self, pid, gid = None) :
        '''Do the primary initialization for this class.'''

        self.pid                            = pid
        self.gid                            = gid
        self.user                           = UserConfig()
        self.userConfig                     = self.user.userConfig
        self.projHome                       = os.path.join(os.path.expanduser(self.userConfig['Resources']['projects']), self.pid)
        self.local                          = ProjLocal(pid)
        self.tools                          = Tools()
        self.log                            = ProjLog(pid)
        # Create config placeholders
        self.projectConfig                  = None
        self.adjustmentConfig               = None
        self.layoutConfig                   = None
        self.illustrationConfig             = None
        self.macPackConfig                  = None

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
                self.proj_config                    = Config(pid, gid)
                self.proj_config.getProjectConfig()
                self.projectConfig                  = self.proj_config.projectConfig
                self.layoutConfig               = self.proj_config.layoutConfig
            # Reinitialize local
            self.local                      = ProjLocal(pid, gid, self.projectConfig)
            self.cType                      = self.projectConfig['Groups'][gid]['cType']
            self.Ctype                      = self.cType.capitalize()
        else :
            self.cType                      = None
            self.Ctype                      = None


###############################################################################
###################### Macro Package Handling Functions #######################
###############################################################################
######################## Error Code Block Series = 3000 #######################
###############################################################################


    def getMacPackConfig (self, macPack) : 
        '''Load/return the macPack configuration object. This is handled different from
        other configs.'''

#        import pdb; pdb.set_trace()

        # Re/Load the macro package config
        self.local = ProjLocal(self.pid, self.gid, self.projectConfig)

# FIXME: We should not be pulling the macPack from inside this function
# It should be tied to asset management. However, we somehow need to get
# the xml file from it so for now, we have to install it here.
        if not os.path.exists(self.local.macPackConfXmlFile) :
            self.addMacPack(macPack)

        # Load macPackConfig
        self.macPackConfig = self.tools.loadConfig(self.local.macPackConfFile, self.local.macPackConfXmlFile)


    def loadMacPackFunctions (self, macPack) :
        '''Load the macro package functions that may be used in this module.'''

        # Create an object that contains the macPack functions
        self.macPackFunctions = UsfmTex(self.layoutConfig)


    def addMacPack (self, macPack) :
        '''Add a macro package to the project. It will not work if
        there already is a macPack present. Remove must be used
        to get rid of the existing one first.'''

#        import pdb; pdb.set_trace()


# Do checks here to see if the macPack exists, if so, stop here.




        # Set the projectConf to the new/same package
        self.projectConfig['CompTypes'][self.Ctype]['macroPackage'] = macPack
        self.tools.writeConfFile(self.projectConfig)

        # If we got this far, install the a fresh copy of the macPack
        self.installMacPackOnly(macPack)
        # Move the style files and custom TeX files out of the macPack
        self.moveMacStyles()
        self.moveMacTex()
        self.macPackConfig = self.tools.initNewConfig(self.local.macPackConfFile, self.local.macPackConfXmlFile)
        self.log.writeToLog(self.errorCodes['3300'], [macPack, self.local.macPackConfFileName])


    def moveMacStyles (self) :
        '''Move the default macro package styles out of the freshly installed
        project macro package folder to the project Style folder.'''

        # Collect the style files to copy
        for f in self.getMacStyExtFiles() :
            source = os.path.join(self.local.projMacPackFolder, f)
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


    def getMacStyExtFiles (self) :
        '''Return a list of macro package style extention files.'''

        sFiles = []
        macPackFiles = os.listdir(self.local.projMacPackFolder)
        for f in macPackFiles :
            if f.split('.')[1].lower() == 'sty' :
                sFiles.append(f)
        return sFiles


    def moveMacTex (self) :
        '''Move the custom macro package TeX out of the freshly installed
        project macro package folder to the project TeX folder.'''

        # Collect the TeX extention files to copy
        for f in self.getMacTexExtFiles() :
            source = os.path.join(self.local.projMacPackFolder, f)
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


    def getMacTexExtFiles (self) :
        '''Return a list of macro package TeX extention files.'''

        tFiles = []
        macPackFiles = os.listdir(self.local.projMacPackFolder)
        for f in macPackFiles :
            if f.find('-ext.tex') > 0 :
                tFiles.append(f)
        return tFiles


    def removeMacPack (self, package, force = False) :
        '''Remove a macro package from a project. Using this will break a project
        as installed font information will be lost from the macro config file
        when it is deleted if force is used. However, there may be times this
        is necessary. If force is not used it will retain the macro config file.
        This is useful when you want to freshen the macro package but bad in
        that custom style and TeX code.'''

        # Remove the macPack config file if required
        if os.path.exists(self.local.macPackConfFile) and force :
            os.remove(self.local.macPackConfFile)
            self.log.writeToLog(self.errorCodes['3400'], [self.local.macPackConfFileName])

        # Now remove the macro folder (with all its contents)
        if os.path.exists(self.local.projMacPackFolder) :
            shutil.rmtree(self.local.projMacPackFolder)
            self.log.writeToLog(self.errorCodes['3500'], [package])

        # Remove the reference for this macro package from any component type
        # that uses it. Normally that would probably be just be one of them.
        for comp in self.projectConfig['CompTypes'].keys() :
            if self.projectConfig['CompTypes'][comp]['macroPackage'] == package :
                self.projectConfig['CompTypes'][comp]['macroPackage'] = ''
                self.tools.writeConfFile(self.projectConfig)


    def updateMacPack (self, macPack) :
        '''Update a macro package with the latest version from Rapuma
        but do not touch the config file.'''

#        import pdb; pdb.set_trace()

        # Be sure we have file names
        self.proj_config.getMacPackConfig(macPack)
        # Delete the existing macro package (but not the settings)
        # but make a backup first
        macDir          = os.path.join(self.local.projMacroFolder, macPack)
        macDirBak       = macDir + '.bak'
        if os.path.exists(macDir) :
            shutil.copytree(macDir, macDirBak)
            shutil.rmtree(macDir)
        # Reinstall the macPack
        if self.installMacPackOnly(macPack) :
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
            shutil.copy(os.path.join(macDir, macPack + '.sty'), self.local.defaultStyFile)
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
            self.log.writeToLog(self.errorCodes['3600'], [macPack])
            return True
        # But if the install fails we need to put things back as they were
        else :
            if os.path.exists(macDirBak) :
                shutil.copytree(macDirBak, macDir)
            # Report the failure
            self.log.writeToLog(self.errorCodes['3650'], [macPack])
            return False


    def installMacPackOnly (self, package) :
        '''Install the new macro package but only that.'''

        if self.tools.pkgExtract(self.local.rapumaMacPackFile, self.local.projMacroFolder, self.local.macPackConfXmlFile) :
            return True
        else :
            self.log.writeToLog(self.errorCodes['3200'], [package])
            return False



