#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (sparkycbr at gmail dot com)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project hyphenation tasks.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, codecs

# Load the local classes
from rapuma.core.tools              import Tools
from rapuma.manager.manager         import Manager
from rapuma.project.proj_config     import Config
from rapuma.core.proj_local         import ProjLocal
from rapuma.core.proj_log           import ProjLog
from rapuma.core.user_config        import UserConfig

###############################################################################
################################## Begin Class ################################
###############################################################################

class ProjHyphenation (object) :

    def __init__(self, pid, gid=None) :
        '''Do the primary initialization for this class.'''

#        import pdb; pdb.set_trace()

        self.pid                        = pid
        self.gid                        = gid
        self.tools                      = Tools()
        self.local                      = ProjLocal(pid)
        self.user                       = UserConfig()
        self.userConfig                 = self.user.userConfig
        self.proj_config                = Config(pid, gid)
        self.proj_config.getProjectConfig()
        self.projectConfig              = self.proj_config.projectConfig
        self.log                        = ProjLog(pid)
        self.hyphenationOn              = self.tools.str2bool(self.projectConfig['ProjectInfo']['hyphenationOn'])
        # Get lid and sid, if these do not exist, we need to catch it during processing
        self.plid                       = self.projectConfig['ProjectInfo']['languageCode']
        self.psid                       = self.projectConfig['ProjectInfo']['scriptCode']
        if gid :
            self.glid                   = self.projectConfig['Groups'][gid]['groupLanguageCode']
            self.gsid                   = self.projectConfig['Groups'][gid]['groupScriptCode']

        # Determine the prefix for the target files, this should match the 
        # system for everthing to work.
        if gid :
            if self.glid and self.gsid :
                self.prefix                 = self.glid + '-' + self.gsid + '_'
            else :
                self.prefix                 = self.plid + '-' + self.psid + '_'
        else :
            self.prefix                 = self.plid + '-' + self.psid + '_'

        # File names
        self.rpmHyphCharTexFile         = self.local.rpmHyphCharTexFile
        self.rpmHyphExcTexFile          = self.local.rpmHyphExcTexFile
        self.rpmHyphSetTexFile          = self.local.rpmHyphSetTexFile

        # Folder paths
        self.projHyphenationFolder      = self.local.projHyphenationFolder
        self.rapumaHyphenationFolder    = self.local.rapumaHyphenationFolder

        # Log messages for this module
        self.errorCodes     = {

            '0000' : ['MSG', 'Placeholder message'],
            '1100' : ['ERR', 'Language and/or writing system codes for the project have not been properly set. Please set these values before continuing. Check Hyphenation documentation for more information.'],
            '1200' : ['ERR', 'The path and/or file name given does not appear to be valid: [<<1>>]'],
            '1300' : ['ERR', 'Rapuma is looking for a file named: [<<1>>], it cannot be found. Are all the files correctly named? Check Hyphenation documentation for more information.'],
            '1400' : ['ERR', 'One or more hyphenation files were found in this project. Please use "remove" to get them out first, then "add" to replace with the files you want.'],
            '1500' : ['MSG', 'Copied file: [<<1>>] to folder: [<<2>>]'],
            '1550' : ['ERR', 'Copied file failed for file: [<<1>>]'],
            '1600' : ['MSG', 'Added hyphenation files to the project.'],
            '2000' : ['LOG', 'When trying to remove hyphenation files, this file was not found: [<<1>>]'],
            '2100' : ['LOG', 'Set ProjectInfo/hyphenationOn to False, turning off hyphenation for the project.'],
            '2600' : ['MSG', 'Removed all hyphenation files from the project.'],
            '3500' : ['MSG', 'Updated file: [<<1>>]'],
            '3600' : ['MSG', 'The updating of hyphenation files is complete.']

        }

        # Build some file names that are shared by other functions and modules
        # Note these names will not be any good if the lid and sid are not there.
        self.projHyphExcTexFile     = os.path.join(self.projHyphenationFolder, self.prefix + self.tools.fName(self.rpmHyphExcTexFile))
        self.projHyphCharTexFile    = os.path.join(self.projHyphenationFolder, self.prefix + self.tools.fName(self.rpmHyphCharTexFile))
        self.projHyphSetTexFile     = os.path.join(self.projHyphenationFolder, self.prefix + self.tools.fName(self.rpmHyphSetTexFile))
        self.projHyphFiles          = [self.projHyphCharTexFile, self.projHyphExcTexFile, self.projHyphSetTexFile]
        self.baseFileNames          = [self.tools.fName(self.rpmHyphCharTexFile), self.tools.fName(self.rpmHyphExcTexFile), self.tools.fName(self.rpmHyphSetTexFile)]

###############################################################################
############################ Hyphenation Functions ############################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################

    def crossCheckSettings (self) :
        '''Cross check settings and die here if we are missing anything.'''
        
        # May need to add more things to check
        if not self.plid or not self.psid :
            self.log.writeToLog(self.errorCodes['1100'])


    def addHyphenationFiles (self, path = None) :
        '''Import necessary hyphenation files from the specified path.
        If no path is given and a file is not found in the project,
        create place holder file(s) that the user will modify.'''

        self.crossCheckSettings()

        # If needed, logically assemble the target file names. This is what
        # Rapuma is expecting to see.
        if path :
            # Check to see if the path given is valid. It should only be a folder, not a file.
            if not os.path.isdir(path) :
                self.log.writeToLog(self.errorCodes['1200'], [path])

            # Check to see if the files we need are at the specified location
            for f in self.baseFileNames :
                if not os.path.isfile(os.path.join(path, self.prefix + f)) :
                    self.log.writeToLog(self.errorCodes['1300'], [self.prefix + f])

        # Check to see if any of the hyphenation files are present
        # in the project. If there are any, hault the process and advise
        # the user to remove them first.
        for f in self.baseFileNames :
            if os.path.isfile(os.path.join(self.projHyphenationFolder, self.prefix, f)) :
                self.log.writeToLog(self.errorCodes['1400'], [self.prefix + f])
                
        # If we make it this far we should be good to go
        if not os.path.isdir(self.projHyphenationFolder) :
            os.makedirs(self.projHyphenationFolder)

        if path : 
            # Copy user provided files
            for f in self.baseFileNames :
                if not shutil.copy(os.path.join(path, self.prefix + f), self.projHyphenationFolder) :
                    self.log.writeToLog(self.errorCodes['1500'], [f, self.projHyphenationFolder])
                    # Double check that it happened
                    if not os.path.isfile(os.path.join(path, self.prefix + f)) :
                        self.log.writeToLog(self.errorCodes['1550'], [f])            
        else :
            # Copy system model files
            for f in self.baseFileNames :
                if not shutil.copy(os.path.join(self.rapumaHyphenationFolder, f), os.path.join(self.projHyphenationFolder, self.prefix + f)) :
                    self.log.writeToLog(self.errorCodes['1500'], [self.prefix + f, self.projHyphenationFolder])
                    # Double check that it happened
                    if not os.path.isfile(os.path.join(self.projHyphenationFolder, self.prefix + f)) :
                        self.log.writeToLog(self.errorCodes['1550'], [f])            

        # Report and return
        self.log.writeToLog(self.errorCodes['1600'])
        return True


    def removeHyphenationFiles (self) :
        '''Remove all the hyphenation files from the hyphenation folder.
        This is currently not smart enough to turn off hyphenation at the
        group level but will switch off hyphenation at the project level
        to avoid problems at rendering time.'''

        self.crossCheckSettings()

        for f in self.projHyphFiles :
            if os.path.isfile(f) :
                os.remove(f)
            else :
                self.log.writeToLog(self.errorCodes['2000'], [self.tools.fName(f)])
                
        # Just to be safe, turn off hyphenation for the project if needed
        if self.hyphenationOn == True :
            self.projectConfig['ProjectInfo']['hyphenationOn'] = 'False'
            self.tools.writeConfFile(self.projectConfig)
            self.log.writeToLog(self.errorCodes['2100'])

        # Report and return
        self.log.writeToLog(self.errorCodes['2600'])
        return True


    def updateHyphenationFiles (self, path) :
        '''Update all the hyphenation files for a language in a project.
        Add any that are not in the target folder. Overwrite any that are
        in the target folder. Skip any that are not in the source path.
        A path must be specified.'''

        self.crossCheckSettings()

        # Bulk update using all valid files found in a valid folder
        if os.path.isdir(path) :
            # Look for and copy the files to be updated in this folder.
            for f in self.baseFileNames :
                if os.path.isfile(os.path.join(path, self.prefix + f)) :
                    if not shutil.copy(os.path.join(path, self.prefix + f), os.path.join(self.projHyphenationFolder, self.prefix + f)) :
                        self.log.writeToLog(self.errorCodes['1500'], [self.prefix + f, self.projHyphenationFolder])
                        # Double check that it happened
                        if not os.path.isfile(os.path.join(self.projHyphenationFolder, self.prefix + f)) :
                            self.log.writeToLog(self.errorCodes['1550'], [f])            
        # Update using a single valid file
        elif os.path.isfile(path) :
            copied = False
            # Validate file name
            for f in self.baseFileNames :
                if self.prefix + f == self.tools.fName(path) :
                    if not shutil.copy(path, self.prefix + f) :
                        self.log.writeToLog(self.errorCodes['1500'], [self.prefix + f, self.projHyphenationFolder])
                        # Double check that it happened
                        if not os.path.isfile(os.path.join(self.projHyphenationFolder, self.prefix + f)) :
                            self.log.writeToLog(self.errorCodes['1550'], [f]) 
        # Neither file or folder found, throw error
        else :
            self.log.writeToLog(self.errorCodes['1200'], [path])

        # Report and return
        self.log.writeToLog(self.errorCodes['3600'])
        return True

