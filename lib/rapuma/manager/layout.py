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






# FIXME: The problem here is that we can't load the renderer manager without
# loading the layout manager. We need to move the macroPackage related settings
# over to the renderer to be added in there, that is where it is needed anyway.

        self.renderer                       = self.projConfig['CompTypes'][self.Ctype]['renderer']
        self.rendererManager                = cType + '_' + self.renderer.capitalize()
        self.sourcePath                     = getSourcePath(self.project.userConfig, self.project.projectIDCode, self.cType)
        self.macroPackage                   = self.projConfig['Managers'][self.rendererManager]['macroPackage']



        # File names
        
# FIXME: Will this work right?
#        self.layoutDefaultXmlConfFileName   = 'layout_default.xml'
        self.layoutDefaultXmlConfFileName   = xmlConfFile
        
        
        self.layoutMacroXmlConfFileName     = 'layout_' + self.macroPackage + '.xml'
        self.layoutConfFile                 = os.path.join(self.project.local.projConfFolder, self.manager + '.conf')
        # Set local var and override in project object (if needed)
        self.project.local.layoutConfFile   = self.layoutConfFile
        self.layoutDefaultXmlConfFile       = os.path.join(self.project.local.rapumaConfigFolder, self.layoutDefaultXmlConfFileName)
        self.layoutMacroXmlConfFile         = os.path.join(self.project.local.rapumaConfigFolder, self.layoutMacroXmlConfFileName)
        # Grab the projConfig settings for this manager
        self.compSettings = self.project.projConfig['Managers'][self.manager]
        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)




# FIXME: This part will be moved out

        # Load up the layout config file which is dependent on 2 different
        # config source files, a default and a cType specific one
        # First, load up the default settings
        layoutMerged            = ConfigObj(encoding='utf-8')
        layoutDefault           = ConfigObj(getXMLSettings(self.layoutDefaultXmlConfFile), encoding='utf-8')
        layoutMacro             = ConfigObj(getXMLSettings(self.layoutMacroXmlConfFile), encoding='utf-8')
        layoutMacro.merge(layoutDefault)
        layoutMerged            = layoutMacro
        layoutMerged.filename   = self.layoutConfFile





# FIXME: This part will be simplified, only one defaul will be used

        # Create a new default layout config file if needed
        # Otherwise check if anything new is in the default
        # settings that need to be added to the project version
        if not os.path.isfile(self.layoutConfFile) :
            self.layoutConfig   = ConfigObj(encoding='utf-8')
            self.layoutConfig   = layoutMerged
            self.layoutConfig.filename = self.layoutConfFile
            writeConfFile(self.layoutConfig)
            self.project.log.writeToLog('LYOT-010')
        else :
            self.layoutConfig = ConfigObj(self.layoutConfFile, encoding='utf-8')
            self.layoutConfig.filename = self.layoutConfFile
            layoutMerged.merge(self.layoutConfig)
            if layoutMerged != self.layoutConfig :
                self.layoutConfig = layoutMerged
                writeConfFile(self.layoutConfig)
                self.project.log.writeToLog('LYOT-020')


###############################################################################
############################ Manager Level Functions ##########################
###############################################################################


# FIXME: We may want to move to this manager some more general functions
# from other managers


