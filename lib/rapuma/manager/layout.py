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

    # Shared values
    xmlConfFile     = 'layout_default.xml'

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
        # File names
        self.layoutDefaultXmlConfFileName   = 'layout_default.xml'
        self.layoutConfFile                 = os.path.join(self.project.local.projConfFolder, self.manager + '.conf')
        # Set local var and override in project object (if needed)
        self.project.local.layoutConfFile   = self.layoutConfFile
        self.layoutDefaultXmlConfFile       = os.path.join(self.project.local.rapumaConfigFolder, self.layoutDefaultXmlConfFileName)
        # Grab the projConfig settings for this manager
        self.compSettings = self.project.projConfig['Managers'][self.manager]
        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)

        # Load the layoutConfFile
        if not os.path.isfile(self.layoutConfFile) :
            self.layoutConfig           = ConfigObj(getXMLSettings(self.layoutDefaultXmlConfFile), encoding='utf-8')
            self.layoutConfig.filename  = self.layoutConfFile
            writeConfFile(self.layoutConfig)
            self.project.log.writeToLog('LYOT-010')
        else :
            self.layoutConfig           = ConfigObj(self.layoutConfFile, encoding='utf-8')
            self.layoutConfig.filename  = self.layoutConfFile
            self.project.log.writeToLog('LYOT-020')


###############################################################################
############################ Manager Level Functions ##########################
###############################################################################


# FIXME: We may want to move to this manager some more general functions
# from other managers


