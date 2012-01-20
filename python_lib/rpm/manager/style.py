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
import style_command as styCmd


###############################################################################
################################## Begin Class ################################
###############################################################################

class Style (Manager) :

    # Shared values
    xmlConfFile     = 'style.xml'

    def __init__(self, project, cfg, cType) :
        '''Do the primary initialization for this manager.'''

        super(Style, self).__init__(project, cfg)

        # Set values for this manager
        self.project            = project
        self.cfg                = cfg
        self.cType              = cType
        self.rpmXmlFontConfig   = os.path.join(self.project.rpmConfigFolder, self.xmlConfFile)

        # Get persistant values from the config if there are any
        manager = self.cType + '_Style'
        newSectionSettings = getPersistantSettings(self.project._projConfig['Managers'][manager], os.path.join(self.project.rpmConfigFolder, self.xmlConfFile))
        if newSectionSettings != self.project._projConfig['Managers'][manager] :
            self.project._projConfig['Managers'][manager] = newSectionSettings
            self.project.writeOutProjConfFile = True

        self.compSettings = self.project._projConfig['Managers'][manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)

###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def recordStyle (self, cType) :

        pass

    def installStyle (self, cType) :
    
        pass






