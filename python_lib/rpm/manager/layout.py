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
from tools import *
from manager import Manager


###############################################################################
################################## Begin Class ################################
###############################################################################

class Layout (Manager) :

    def __init__(self, project, cfg, cType) :
        '''Do the primary initialization for this manager.'''

        super(Layout, self).__init__(project, cfg)

        # List the renderers this manager supports
        renderers                       = ['Xetex']
        self.cType                      = cType
        self.manager                    = None
        self.layoutConfig               = ConfigObj()
        self.project                    = project

        # Bring in default layout config information
        if not os.path.isfile(self.project.local.layoutConfFile) :
            self.layoutConfig  = ConfigObj(getXMLSettings(self.project.local.rpmLayoutDefaultFile))
            self.layoutConfig.filename = self.project.local.layoutConfFile
            self.layoutConfig.write()
            writeToLog(self.project.local, self.project.userConfig, 'LOG', 'Write out new layout config: layout.__init__()')
        else :
            self.layoutConfig = ConfigObj(self.project.local.layoutConfFile)

        # Search for renderer to create a layout conf for
        for m in self.project.projConfig['Managers'].keys() :
            for r in renderers :
                if m == cType + '_' + r :
                    self.manager = m

        if not self.manager :
            writeToLog(self.project.local, self.project.userConfig, 'ERR', 'Renderering manager not found: ' + self.manager)

        # Set values for this manager
        self.macroPackage               = self.project.projConfig['Managers'][self.manager]['macroPackage']
        self.macrosTarget               = os.path.join(self.project.local.projMacrosFolder, self.macroPackage)
        self.macrosSource               = os.path.join(self.project.local.rpmMacrosFolder, self.macroPackage)

        # Copy in to the process folder the macro package for this component
        if not os.path.isdir(self.macrosTarget) :
            os.makedirs(self.macrosTarget)

        for root, dirs, files in os.walk(self.macrosSource) :
            for f in files :
                if not os.path.isfile(os.path.join(self.macrosTarget, f)) :
                    shutil.copy(os.path.join(self.macrosSource, f), os.path.join(self.project.local.projMacrosFolder, f))

# FIXME: May need to move this stuff out to xetex.py and deprecate this mod

###############################################################################
############################ Project Level Functions ##########################
###############################################################################





