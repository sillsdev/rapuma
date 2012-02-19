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
        renderers = ['Xetex']
        self.cType                      = cType
        self.manager                    = None

        # Search for renderer to create a layout conf for
        for m in self.project._projConfig['Managers'].keys() :
            for r in renderers :
                if m == cType + '_' + r :
                    self.manager = m

        if not self.manager :
            self.project.writeToLog('ERR', 'Renderering manager not found: ' + self.manager)

        # Set values for this manager
        self._layoutConfig              = {}
        self.macroPackage               = self.project._projConfig['Managers'][self.manager]['macroPackage']
        self.projMacrosFolder           = os.path.join(self.project.macrosFolder, self.macroPackage)
        self.rpmMacrosFolder            = os.path.join(self.project.rpmMacrosFolder, self.macroPackage)
        self.layoutConfFile             = os.path.join(self.project.projConfFolder, 'layout.conf')
        self.layoutDefaultValuesFile    = os.path.join(self.project.rpmConfigFolder, 'layout_default.xml')
        self.macroLayoutValuesFile      = os.path.join(self.project.rpmConfigFolder, 'layout_' + self.macroPackage + '.xml')

        # Create a layout settings file for this specific component type.if needed
        if len(self.project._layoutConfig) == 0 :
            self._layoutConfig = mergeConfig(getXMLSettings(self.layoutDefaultValuesFile), self.macroLayoutValuesFile)
            writeConfFile(self._layoutConfig, self.layoutConfFile)

        # Copy in to the project the macro package for this component
        if not os.path.isdir(self.projMacrosFolder) :
            os.makedirs(self.projMacrosFolder)

        for root, dirs, files in os.walk(self.rpmMacrosFolder) :
            for f in files :
                if not os.path.isfile(os.path.join(self.projMacrosFolder, f)) :
                    shutil.copy(os.path.join(self.rpmMacrosFolder, f), os.path.join(self.projMacrosFolder, f))



###############################################################################
############################ Project Level Functions ##########################
###############################################################################





