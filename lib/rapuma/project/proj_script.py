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

import os, shutil, codecs

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
        self.proj_macro                 = Macro(pid, gid)
        self.proj_config.getProjectConfig()
        self.projectConfig              = self.proj_config.projectConfig
        self.cType                      = self.projectConfig['Groups'][gid]['cType']
        self.Ctype                      = self.cType.capitalize()
        self.log                        = ProjLog(pid)



        # Log messages for this module
        self.errorCodes     = {

            '0000' : ['MSG', 'Placeholder message'],

        }

###############################################################################
############################# Script Add Functions ############################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################


    def addScriptFiles (self, path) :
        '''Import/add processing script files for a group that are found
        in the given path. Assumes valid path. Will fail if a copy
        doesn't succeed. If the file is already there, give a warning and
        will not copy.'''

        pass


###############################################################################
############################# Script Add Functions ############################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################


    def removeScriptFiles (self) :
        '''Remove processing script files for a group.'''

        pass



###############################################################################
############################# Script Add Functions ############################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################


    def updateScriptFiles (self, path) :
        '''Update processing script files for a group that are found
        in the given path. Assumes valid path. Will fail if a copy
        doesn't succeed.'''

        pass

