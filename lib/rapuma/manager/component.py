#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project component tasks.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil


# Load the local classes
from rapuma.core.tools import *
from rapuma.project.manager import Manager
from rapuma.group.usfm import PT_Tools

###############################################################################
################################## Begin Class ################################
###############################################################################

class Component (Manager) :

    # Shared values
    xmlConfFile     = 'component.xml'

    def __init__(self, project, cfg, cType) :
        '''Initialize the Illustration manager.'''

        '''Do the primary initialization for this manager.'''

        super(Component, self).__init__(project, cfg)

        # Set values for this manager
        self.pt_tools                   = PT_Tools(project)
        self.project                    = project
        self.cfg                        = cfg
        self.cType                      = cType
        self.Ctype                      = cType.capitalize()
        self.gid                        = project.gid
        self.projConfig                 = self.project.projConfig
        self.userConfig                 = self.project.userConfig
        self.manager                    = self.cType + '_Component'
        self.csid                       = self.projConfig['Groups'][self.gid]['csid']
        # File names
        # Folder path
        # File names with folder paths

        # Get persistant values from the config if there are any
        newSectionSettings = getPersistantSettings(self.projConfig['Managers'][self.manager], os.path.join(self.project.local.rapumaConfigFolder, self.xmlConfFile))
        if newSectionSettings != self.projConfig['Managers'][self.manager] :
            self.projConfig['Managers'][self.manager] = newSectionSettings

        self.compSettings = self.projConfig['Managers'][self.manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)


###############################################################################
############################ Manager Level Functions ##########################
###############################################################################

    def makeFileName(self, cid) :
        '''From what we know, return the full file name.'''

        return cid + '_' + self.csid


    def makeFileNameWithExt(self, cid) :
        '''From what we know, return the full file name.'''

        return self.makeFileName(cid) + '.' + self.cType





