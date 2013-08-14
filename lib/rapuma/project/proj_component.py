
#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle components in book projects.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, codecs

# Load the local classes
from rapuma.core.tools              import Tools, ToolsPath
from rapuma.core.proj_config        import ProjConfig
from rapuma.core.user_config        import UserConfig
from rapuma.core.proj_local         import ProjLocal
from rapuma.core.proj_log           import ProjLog


###############################################################################
################################## Begin Class ################################
###############################################################################

class ProjComponent (object) :

    def __init__(self, pid, gid) :
        '''Do the primary initialization for this class.'''

        self.pid                        = pid
        self.gid                        = gid
        self.tools                      = Tools()
        self.user                       = UserConfig()
        self.userConfig                 = self.user.userConfig
        self.projHome                   = self.userConfig['Projects'][pid]['projectPath']
        self.pmid                       = self.userConfig['Projects'][pid]['projectMediaIDCode']
        self.local                      = ProjLocal(pid)
        self.projConfig                 = ProjConfig(self.local).projConfig
        self.log                        = ProjLog(pid)
        self.tools_path                 = ToolsPath(pid)
        # File names

        # Folder paths
        self.projMacroFolder            = self.local.projMacroFolder
        # File names with paths


        # Log messages for this module
        self.errorCodes     = {

            '0050' : ['MSG', 'Placeholder message'],

        }


###############################################################################
################################ Add Functions ################################
###############################################################################
######################## Error Code Block Series = 0200 #######################
###############################################################################

    def addComponent (self, component, force = False) :
        '''Add a component to a project.'''

        return True


###############################################################################
############################## Remove Functions ###############################
###############################################################################
######################## Error Code Block Series = 0400 #######################
###############################################################################

    def removeComponent (self, component, force = False) :
        '''Remove a component from a project.'''

        return True


###############################################################################
############################## Update Functions ###############################
###############################################################################
######################## Error Code Block Series = 0600 #######################
###############################################################################

    def updateComponent (self, component, force = False) :
        '''Update a component from the latest source.'''

        pass


###############################################################################
############################## Editing Functions ##############################
###############################################################################
######################## Error Code Block Series = 0800 #######################
###############################################################################

    def editComponent (self, component) :
        '''Edit a text component.'''

        pass


