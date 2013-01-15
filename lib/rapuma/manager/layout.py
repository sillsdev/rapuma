#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project tasks.

# History:
# 20120218 - djd - Started with intial format manager file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil


# Load the local classes
from rapuma.core.tools import *
from rapuma.core.pt_tools import *
from rapuma.project.manager import Manager


###############################################################################
################################## Begin Class ################################
###############################################################################

class Layout (Manager) :

    def __init__(self, project, cfg, cType) :
        '''Do the primary initialization for this manager.'''

        super(Layout, self).__init__(project, cfg)

        # List the renderers this manager supports
        self.cType                          = cType
        self.manager                        = self.cType + '_Layout'
        self.layoutConfig                   = ConfigObj()
        self.project                        = project
        self.sourcePath                     = getSourcePath(self.project.userConfig, self.project.projectIDCode, self.cType)
        # Overrides
        self.project.local.layoutConfFile   = os.path.join(self.project.local.projConfFolder, self.manager + '.conf')

        # Create a new default layout config file if needed
        if not os.path.isfile(self.project.local.layoutConfFile) :
            self.layoutConfig  = ConfigObj(getXMLSettings(self.project.local.rapumaLayoutDefaultFile))
            self.layoutConfig.filename = self.project.local.layoutConfFile
            writeConfFile(self.layoutConfig)
            self.project.log.writeToLog('LYOT-010')
        else :
            self.layoutConfig = ConfigObj(self.project.local.layoutConfFile)


###############################################################################
############################ Manager Level Functions ##########################
###############################################################################





