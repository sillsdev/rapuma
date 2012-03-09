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

import os, shutil


# Load the local classes
from tools import *
from manager import Manager


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
        self.rpmXmlFontConfig   = os.path.join(self.project.local.rpmConfigFolder, self.xmlConfFile)

        # Get persistant values from the config if there are any
        manager = self.cType + '_Style'
        newSectionSettings = getPersistantSettings(self.project.projConfig['Managers'][manager], os.path.join(self.project.local.rpmConfigFolder, self.xmlConfFile))
        if newSectionSettings != self.project.projConfig['Managers'][manager] :
            self.project._projConfig['Managers'][manager] = newSectionSettings
            self.project.writeOutProjConfFile = True

        self.compSettings = self.project.projConfig['Managers'][manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)

###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def installPTStyles (self) :
        '''Go get the style sheet from the local PT project this is in
        and install it into the project where and how it needs to be.'''

        # As this is call is for a PT based project, it is certain the style
        # file should be found in the parent folder.
        ptStyles = os.path.join(os.path.dirname(self.project.local.projHome), self.mainStyleFile)
        ptCustomStyles = os.path.join(os.path.dirname(self.project.local.projHome), self.customStyleFile)
        projStyles = os.path.join(self.project.processFolder, self.mainStyleFile)
        projCustomStyles = os.path.join(self.project.processFolder, self.customStyleFile)
        # We will start with a very simple copy operation. Once we get going
        # we will need to make this more sophisticated.
        if os.path.isfile(ptStyles) :
            shutil.copy(ptStyles, projStyles)
        if os.path.isfile(ptCustomStyles) :
            shutil.copy(ptCustomStyles, projCustomStyles)




