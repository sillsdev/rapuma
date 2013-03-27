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
        self.Ctype                          = cType.capitalize()
        self.manager                        = self.cType + '_Layout'
        self.project                        = project
        self.managers                       = project.managers
        self.projConfig                     = self.project.projConfig
        self.projMediaType                  = self.project.projectMediaIDCode
        # File names
        self.defaultXmlConfFileName         = self.project.projectMediaIDCode + '_layout.xml'
        self.layoutConfFileName             = self.project.projectMediaIDCode + '_layout.conf'
        # Paths
        self.projConfFolder                 = self.project.local.projConfFolder
        self.rapumaConfigFolder             = self.project.local.rapumaConfigFolder
        # Files with paths
        self.layoutConfFile                 = os.path.join(self.projConfFolder, self.layoutConfFileName)
        self.defaultXmlConfFile             = os.path.join(self.rapumaConfigFolder, self.defaultXmlConfFileName)
        # Set local var and override in project object (if needed)
        self.project.local.layoutConfFile   = self.layoutConfFile
        # Load the config object
        self.layoutConfig = initConfig(self.layoutConfFile, self.defaultXmlConfFile)
        # Grab the projConfig settings for this manager
        for k, v in self.project.projConfig['Managers'][self.manager].iteritems() :
            setattr(self, k, v)

###############################################################################
############################ Manager Level Functions ##########################
###############################################################################


# FIXME: We may want to move to this manager some more general functions
# from other managers


