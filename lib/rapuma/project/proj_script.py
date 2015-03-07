#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project script management tasks.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, codecs, subprocess

# Load the local classes
from rapuma.core.tools              import Tools
from rapuma.manager.manager         import Manager
from rapuma.project.proj_config     import Config
from rapuma.project.proj_macro      import Macro
from rapuma.core.proj_local         import ProjLocal
from rapuma.core.proj_log           import ProjLog
from rapuma.core.user_config        import UserConfig

###############################################################################
################################## Begin Class ################################
###############################################################################

class ProjScript (object) :

    def __init__(self, pid, gid) :
        '''Do the primary initialization for this class.'''

        self.pid                        = pid
        self.gid                        = gid
        self.tools                      = Tools()
        self.local                      = ProjLocal(pid)
        self.user                       = UserConfig()
        self.userConfig                 = self.user.userConfig
        self.proj_config                = Config(pid, gid)
        self.proj_config.getProjectConfig()
        self.projectConfig              = self.proj_config.projectConfig
        self.cType                      = self.projectConfig['Groups'][gid]['cType']
        self.Ctype                      = self.cType.capitalize()
        self.log                        = ProjLog(pid)



        # Log messages for this module
        self.errorCodes     = {

            '0000' : ['MSG', 'Placeholder message'],

            '1010' : ['MSG', 'Script install process for [<<1>>] Succeeded.'],
            '1020' : ['ERR', 'Script install process for [<<1>>] failed.'],
            '1030' : ['ERR', 'Script type [<<1>>] not supported.'],
            '1040' : ['ERR', 'Script install cannot proceed for [<<1>>] because this script already exists in the project. You must remove it first before you can add another script.'],

            '2010' : ['MSG', 'Script remove process for [<<1>>] Succeeded.'],
            '2020' : ['ERR', 'Script remove process for [<<1>>] failed.'],

            '4210' : ['MSG', 'Processes completed successfully on: [<<1>>] by [<<2>>]'],
            '4220' : ['ERR', 'Processes for [<<1>>] failed. Script [<<2>>] returned this error: [<<3>>]'],
            '4260' : ['ERR', 'Installed the default component preprocessing script. Editing will be required for it to work with your project.'],
            '4265' : ['LOG', 'Component preprocessing script is already installed.'],
            '4310' : ['ERR', 'Script is an unrecognized type: [<<1>>] Cannot continue with installation.']


        }

###############################################################################
############################# Script Add Functions ############################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################


    def addScriptFiles (self, path, scriptType) :
        '''Import/add processing script files for a group that are found
        in the given path. Assumes valid path. Will fail if a copy
        doesn't succeed. If the file is already there, give a warning and
        will not copy.'''

#        import pdb; pdb.set_trace()

        source = path
        fileName = self.tools.fName(path)
        target = os.path.join(self.local.projScriptFolder, fileName)
        
        # Do an initial check to see if the script is already there
        # Never copy over the top of an existing script
        if os.path.isfile(target) :
            self.log.writeToLog(self.errorCodes['1040'], [fileName])
        # Make script folder if needed
        if not os.path.isdir(self.local.projScriptFolder) :
            os.makedirs(self.local.projScriptFolder)
        # Copy in the script
        if self.scriptInstall(source, target) :
            # Record the script file name
            if scriptType == 'preprocess' :
                self.projectConfig['Groups'][self.gid]['preprocessScript'] = fileName
            elif scriptType == 'postprocess' :
                self.projectConfig['Groups'][self.gid]['postprocessScript'] = fileName
            else :
                self.log.writeToLog(self.errorCodes['1030'], [scriptType])

            self.tools.writeConfFile(self.projectConfig)
            self.log.writeToLog(self.errorCodes['1010'], [fileName])
            return True
        else :
            self.log.writeToLog(self.errorCodes['1020'], [fileName])


###############################################################################
############################ Script Remove Functions ##########################
###############################################################################
######################## Error Code Block Series = 2000 #######################
###############################################################################


    def removeScriptFiles (self, scriptType) :
        '''Remove processing script files for a group.'''

        if scriptType == 'preprocess' :
            fileName = self.projectConfig['Groups'][self.gid]['preprocessScript']
        elif scriptType == 'postprocess' :
            fileName = self.projectConfig['Groups'][self.gid]['postprocessScript']
        else :
            self.log.writeToLog(self.errorCodes['1030'], [scriptType])

        target = os.path.join(self.local.projScriptFolder, fileName)
        # Remove the script (if it's not there, we don't care)
        try :
            os.remove(target)
        except :
            pass
        if not os.path.isfile(target) :
            if scriptType == 'preprocess' :
                self.projectConfig['Groups'][self.gid]['preprocessScript'] = ''
            elif scriptType == 'postprocess' :
                self.projectConfig['Groups'][self.gid]['postprocessScript'] = ''
            else :
                self.log.writeToLog(self.errorCodes['1030'], [scriptType])
            self.tools.writeConfFile(self.projectConfig)
            self.log.writeToLog(self.errorCodes['2010'], [fileName])
            return True
        else :
            self.log.writeToLog(self.errorCodes['2020'], [fileName])


###############################################################################
########################## General Script Functions ###########################
###############################################################################
######################## Error Code Block Series = 4000 #######################
###############################################################################


    def runProcessScript (self, target, scriptFile) :
        '''Run a text processing script on a component. This assumes the 
        component and the script are valid and the component lock is turned 
        off. If not, you cannot expect any good to come of this.'''

        # subprocess will fail if permissions are not set on the
        # script we want to run. The correct permission should have
        # been set when we did the installation.
        err = subprocess.call([scriptFile, target])
        if err == 0 :
            self.log.writeToLog(self.errorCodes['4210'], [self.tools.fName(target), self.tools.fName(scriptFile)])
        else :
            self.log.writeToLog(self.errorCodes['4220'], [self.tools.fName(target), self.tools.fName(scriptFile), str(err)])
            return False

        return True


    def scriptInstall (self, source, target) :
        '''Install a script. A script can be a collection of items in
        a zip file or a single .py script file.'''

        scriptTargetFolder, fileName = os.path.split(target)
        if self.tools.isExecutable(source) :
            if not shutil.copy(source, target) :
                self.tools.makeExecutable(target)
                return True
        elif self.tools.fName(source).split('.')[1].lower() == 'zip' :
            myZip = zipfile.ZipFile(source, 'r')
            for f in myZip.namelist() :
                data = myZip.read(f, source)
                # Pretty sure zip represents directory separator char as "/" regardless of OS
                myPath = os.path.join(scriptTargetFolder, f.split("/")[-1])
                try :
                    myFile = open(myPath, "wb")
                    myFile.write(data)
                    myFile.close()
                except :
                    pass
            myZip.close()
            return True
        else :
            self.log.writeToLog(self.errorCodes['4310'], [self.tools.fName(source)])

