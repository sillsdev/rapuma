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
from pt_tools import *
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
        self.Ctype              = cType.capitalize()
        self.rpmXmlStyleConfig  = os.path.join(self.project.local.rpmConfigFolder, self.xmlConfFile)
        self.renderer           = self.project.projConfig['CompTypes'][self.Ctype]['renderer']
        self.sourceEditor       = self.project.projConfig['CompTypes'][self.Ctype]['sourceEditor']

        # Get persistant values from the config if there are any
        manager = self.cType + '_Style'
        newSectionSettings = getPersistantSettings(self.project.projConfig['Managers'][manager], self.rpmXmlStyleConfig)
        if newSectionSettings != self.project.projConfig['Managers'][manager] :
            self.project.projConfig['Managers'][manager] = newSectionSettings

        self.compSettings = self.project.projConfig['Managers'][manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)

###############################################################################
############################ Project Level Functions ##########################
###############################################################################

    def installCompTypeGlobalStyles (self) :
        '''If the source is from a PT project, check to see if there is a
        (project-wide) stylesheet to install. If not, we will make one.
        This file is required as a minimum for components of this type to
        render. This function must succeed.'''

        ptConf = getPTSettings(self.project.local.projHome)
        globalStyFile = os.path.join(self.project.local.projProcessFolder, self.mainStyleFile)
        if not os.path.isfile(globalStyFile) :
            if self.sourceEditor.lower() == 'paratext' :
                # Override default styleFile name with what we find in the PT conf
                self.mainStyleFile = ptConf['ScriptureText']['StyleSheet']
                globalStyFile = os.path.join(self.project.local.projProcessFolder, self.mainStyleFile)
                if not os.path.isfile(globalStyFile) :
                    installPTStyles(self.project.local, self.mainStyleFile)
                    self.project.log.writeToLog('STYL-010')
            else :
                # Quite here
                self.project.log.writeToLog('STYL-015')
                dieNow()


    def installCompTypeOverrideStyles (self) :
        '''If the source is from a PT project, check to see if there is a
        (project-wide) custom stylesheet to install. If not, we are done.
        This style file is not required.'''
        cusStyFile = os.path.join(self.project.local.projProcessFolder, self.customStyleFile)
        if not os.path.isfile(cusStyFile) :
            if self.sourceEditor.lower() == 'paratext' :
                if not installPTCustomStyles(self.project.local, self.customStyleFile) :
                    self.project.log.writeToLog('STYL-020')
                    self.createCustomUsfmStyles()
            else :
                self.createCustomUsfmStyles()


    def createCustomUsfmStyles (self) :
        '''Create a custom project-wide USFM style file for this project.
        This USFM style file will override the main component type styles.'''

        self.project.log.writeToLog('STYL-030')


    def createCompOverrideUsfmStyles (self, cid) :
        '''Create a component override style file for a single component.
        This file will override specific styles from preceeding style
        files loaded before it.'''

        self.project.log.writeToLog('STYL-040')






