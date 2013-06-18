
#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle macros in book projects.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, codecs

# Load the local classes
from rapuma.core.tools              import Tools, ToolsPath, ToolsGroup
from rapuma.core.proj_config        import ProjConfig
from rapuma.core.user_config        import UserConfig
from rapuma.core.proj_local         import ProjLocal
from rapuma.core.proj_log           import ProjLog


###############################################################################
################################## Begin Class ################################
###############################################################################

class ProjMacro (object) :

    def __init__(self, pid, gid) :
        '''Do the primary initialization for this class.'''

        self.pid                        = pid
        self.gid                        = gid
        self.tools                      = Tools()
        self.user                       = UserConfig()
        self.userConfig                 = self.user.userConfig
        self.projHome                   = self.userConfig['Projects'][self.pid]['projectPath']
        self.pmid                       = self.userConfig['Projects'][self.pid]['projectMediaIDCode']
        self.local                      = ProjLocal(self.pid)
        self.projConfig                 = ProjConfig(self.local).projConfig
        self.log                        = ProjLog(self.pid)
        self.tools_path                 = ToolsPath(self.local, self.projConfig, self.userConfig)
        self.tools_group                = ToolsGroup(self.local, self.projConfig, self.userConfig)
        # File names

        # Folder paths
        self.projMacroFolder            = self.local.projMacroFolder
        # File names with paths


        self.finishInit()

        # Log messages for this module
        self.errorCodes     = {

            '0050' : ['MSG', 'Placeholder message'],

        }

    def finishInit (self) :
        '''If this is a new project some settings need to be handled special.'''

        pass


###############################################################################
################################ Add Functions ################################
###############################################################################
######################## Error Code Block Series = 0200 #######################
###############################################################################



###############################################################################
############################## Remove Functions ###############################
###############################################################################
######################## Error Code Block Series = 0400 #######################
###############################################################################

    def removeMacPack (self, package, force = False) :
        '''Remove a macro package from a project.'''

        return True


###############################################################################
############################## Update Functions ###############################
###############################################################################
######################## Error Code Block Series = 0600 #######################
###############################################################################

    def updateMacPack (self, package, force = False) :
        '''Update a macro package with the latest version from Rapuma.'''

        pass


###############################################################################
########################### TeX Handling Functions ############################
###############################################################################
######################## Error Code Block Series = 0800 #######################
###############################################################################





