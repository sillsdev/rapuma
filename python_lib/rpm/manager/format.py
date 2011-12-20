#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project tasks.

# History:
# 20111207 - djd - Started with intial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os


# Load the local classes
from tools import *
from manager import Manager
import format_command as frmCmd


###############################################################################
################################## Begin Class ################################
###############################################################################

class Format (Manager) :

    # Shared values
    xmlConfFile     = ''
    xmlInitFile     = ''

    def __init__(self, project, cfg) :
        '''Do the primary initialization for this manager.'''

        super(Format, self).__init__(project, cfg)

        terminal("Initializing Format Manager")

        # Add commands for this manager
#        project.addCommand("???", frmCmd.???(self))

        # Set values for this manager
        self._formatConfig              = {}
        self.formatConfigFileName       = 'format.conf'
        self.formatDefaultFileName      = 'format_values.xml'
        self.formatConfFile             = os.path.join(self.project.projConfFolder, self.formatConfigFileName)
        self.defaultFormatValuesFile    = os.path.join(self.project.rpmConfigFolder, self.formatDefaultFileName)

        if not os.path.isfile(self.formatConfFile) :
            self._formatConfig = getXMLSettings(self.defaultFormatValuesFile)
            writeConfFile(self._formatConfig, self.formatConfFile)
        else :
            self._formatConfig = ConfigObj(self.formatConfFile)

###############################################################################
############################ Project Level Functions ##########################
###############################################################################



