#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20150117
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project fixed document tasks (PDF handling).


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, codecs, re, subprocess

# Load the local classes
from rapuma.core.tools              import Tools
from rapuma.manager.manager         import Manager


###############################################################################
################################## Begin Class ################################
###############################################################################

class Fixed (Manager) :

    # Shared values
    xmlConfFile     = 'fixed.xml'

    def __init__(self, project, cfg, cType) :
        '''Do the primary initialization for this manager.'''

        super(Fixed, self).__init__(project, cfg)

        # Set values for this manager
        self.gid                    = project.gid
        self.pid                    = project.projectIDCode
        self.tools                  = Tools()
        self.project                = project
        self.projectConfig          = project.projectConfig
        self.cfg                    = cfg
        self.cType                  = cType
        self.Ctype                  = cType.capitalize()
        self.log                    = project.log
        self.manager                = self.cType + '_Fixed'
        self.managers               = project.managers
        self.rapumaXmlTextConfig    = os.path.join(self.project.local.rapumaConfigFolder, self.xmlConfFile)

#        import pdb; pdb.set_trace()

        # Get persistant values from the config if there are any
        newSectionSettings = self.tools.getPersistantSettings(self.project.projectConfig['Managers'][self.manager], self.rapumaXmlTextConfig)
        if newSectionSettings != self.project.projectConfig['Managers'][self.manager] :
            self.project.projectConfig['Managers'][self.manager] = newSectionSettings
            self.tools.writeConfFile(self.project.projectConfig)

        self.compSettings = self.project.projectConfig['Managers'][self.manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)

        # Log messages for this module
        self.errorCodes     = {

            '0000' : ['MSG', 'Placeholder message'],

        }

###############################################################################
############################ Functions Begin Here #############################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################


# Actually, there's nothing I can think that needs to be done here. This is
# just a place holder class for the most part.
