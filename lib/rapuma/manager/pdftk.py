#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This manager class will handle PDF handling operations with pdftk.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, re, codecs, subprocess
from configobj                          import ConfigObj
from pyPdf                              import PdfFileReader

# Load the local classes
from rapuma.core.tools                  import Tools
from rapuma.manager.manager             import Manager
from rapuma.project.proj_config         import Config
from rapuma.project.proj_background     import ProjBackground
from rapuma.project.proj_diagnose       import ProjDiagnose


###############################################################################
################################## Begin Class ################################
###############################################################################

class Pdftk (Manager) :

    # Shared values
    xmlConfFile     = 'pdftk.xml'

    def __init__(self, project, cfg, cType) :
        '''Do the primary initialization for this manager.'''

        super(Pdftk, self).__init__(project, cfg)

#        import pdb; pdb.set_trace()

        # Create all the values we can right now for this manager.
        # Others will be created at run time when we know the cid.
        self.tools                  = Tools()
        self.project                = project
        self.local                  = project.local
        self.log                    = project.log
        self.cfg                    = cfg
        self.pid                    = project.projectIDCode
        self.gid                    = project.gid
        self.cType                  = cType
        self.Ctype                  = cType.capitalize()
        self.mType                  = project.projectMediaIDCode
        self.renderer               = 'pdftk'
        self.manager                = self.cType + '_' + self.renderer.capitalize()
        self.managers               = project.managers
        self.pg_back                = ProjBackground(self.pid, self.gid)
        self.fmt_diagnose           = ProjDiagnose(self.pid, self.gid)
        self.proj_config            = Config(self.pid, self.gid)
        self.proj_config.getProjectConfig()
        self.proj_config.getLayoutConfig()
        # Get config objs
        self.projectConfig          = self.proj_config.projectConfig
        self.layoutConfig           = self.proj_config.layoutConfig
        self.userConfig             = self.project.userConfig
        # Some config settings
        self.pdfViewerCmd           = self.project.userConfig['System']['pdfViewerCommand']
        self.pdfUtilityCmd          = self.project.userConfig['System']['pdfUtilityCommand']
        self.useBackground          = self.tools.str2bool(self.layoutConfig['DocumentFeatures']['useBackground'])
        self.useDiagnostic          = self.tools.str2bool(self.layoutConfig['DocumentFeatures']['useDiagnostic'])
        self.useDocInfo             = self.tools.str2bool(self.layoutConfig['DocumentFeatures']['useDocInfo'])

        # Get settings for this component
        self.managerSettings = self.projectConfig['Managers'][self.manager]
        for k, v in self.managerSettings.iteritems() :
            if v == 'True' or v == 'False' :
                setattr(self, k, self.tools.str2bool(v))
            else :
                setattr(self, k, v)

        # Make any dependent folders if needed
        if not os.path.isdir(self.local.projGidFolder) :
            os.makedirs(self.local.projGidFolder)


        # Log messages for this module
        self.errorCodes     = {

            '0000' : ['MSG', 'Messages for the pdftk module.'],

        }


###############################################################################
############################ Manager Level Functions ##########################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################


###############################################################################
################################# Main Function ###############################
###############################################################################
######################## Error Code Block Series = 5000 #######################
###############################################################################

    def run (self, gid, cidList, pgRange, override, save) :
        '''This will check all the dependencies for a group and then
        use pdftk to "render" the whole group or a subset of components
        and even a page range in a single component.'''

#        import pdb; pdb.set_trace()

        # There must be a cidList. If one was not passed, default to
        # the group list
        cidListSubFileName      = ''
        saveFile                = ''
        saveFileName            = ''
        if not cidList :
            cidList = self.projectConfig['Groups'][gid]['cidList']
        else :
            # We need to handle custom IDs of any size
            pass
            
        return True



