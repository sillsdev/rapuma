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
#from rapuma.component.usfm import PT_Tools
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
#        self.pt_tools                       = PT_Tools(project)
        self.cType                          = cType
        self.Ctype                          = cType.capitalize()
        self.manager                        = self.cType + '_Layout'
        self.project                        = project
        self.managers                       = project.managers
        self.projConfig                     = self.project.projConfig
        self.projMediaType                  = self.project.projectMediaIDCode
        # File names
        self.layoutDefaultXmlConfFileName   = self.project.projectMediaIDCode + '_layout.xml'
        self.layoutDefaultConfFileName   = self.project.projectMediaIDCode + '_layout.conf'
        self.layoutConfFile                 = os.path.join(self.project.local.projConfFolder, self.layoutDefaultConfFileName)
        # Set local var and override in project object (if needed)
        self.project.local.layoutConfFile   = self.layoutConfFile
        self.layoutDefaultXmlConfFile       = os.path.join(self.project.local.rapumaConfigFolder, self.layoutDefaultXmlConfFileName)
        # Grab the projConfig settings for this manager
        self.compSettings = self.project.projConfig['Managers'][self.manager]
        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)

        # Load the layoutConfFile
        # At this point, on a new project, only default settings will be
        # in the layoutConfFile. The renderer manager my have more settings
        # to add when it gets there
        if not os.path.isfile(self.layoutConfFile) :
            self.layoutConfig           = ConfigObj(getXMLSettings(self.layoutDefaultXmlConfFile), encoding='utf-8')
            self.layoutConfig.filename  = self.layoutConfFile
            writeConfFile(self.layoutConfig)
            self.project.log.writeToLog('LYOT-010')
        else :
            # But check against the default for possible new settings
            self.layoutConfig           = ConfigObj(encoding='utf-8')
            orgLayoutConfig             = ConfigObj(self.layoutConfFile, encoding='utf-8')
            orgFileName                 = orgLayoutConfig.filename
            layoutDefault               = ConfigObj(getXMLSettings(self.layoutDefaultXmlConfFile), encoding='utf-8')
            layoutDefault.merge(orgLayoutConfig)
            # A key comparison should be enough to tell if it is the same or not
            if orgLayoutConfig.keys() == layoutDefault.keys() :
                self.layoutConfig = orgLayoutConfig
                self.layoutConfig.filename = orgFileName
# Probably not needed to report as it should be normal
#                self.project.log.writeToLog('LYOT-020')
            else :
                self.layoutConfig = layoutDefault
                self.layoutConfig.filename = orgFileName
                writeConfFile(self.layoutConfig)
                self.project.log.writeToLog('LYOT-030')


###############################################################################
############################ Manager Level Functions ##########################
###############################################################################


# FIXME: We may want to move to this manager some more general functions
# from other managers


