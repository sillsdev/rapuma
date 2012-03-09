#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project text tasks.

# History:
# 20120121 - djd - Started with intial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil
from configobj import ConfigObj, Section

# Load the local classes
from tools import *
from pt_tools import *
from manager import Manager


###############################################################################
################################## Begin Class ################################
###############################################################################

class Text (Manager) :

    # Shared values
    xmlConfFile     = 'text.xml'

    def __init__(self, project, cfg, cType) :
        '''Do the primary initialization for this manager.'''

        super(Text, self).__init__(project, cfg)

        # Set values for this manager
        self.project            = project
        self.cfg                = cfg
        self.cType              = cType
        self.rpmXmlFontConfig   = os.path.join(self.project.local.rpmConfigFolder, self.xmlConfFile)

        # Get persistant values from the config if there are any
        manager = self.cType + '_Text'
        newSectionSettings = getPersistantSettings(self.project.projConfig['Managers'][manager], os.path.join(self.project.local.rpmConfigFolder, self.xmlConfFile))
        if newSectionSettings != self.project.projConfig['Managers'][manager] :
            self.project.projConfig['Managers'][manager] = newSectionSettings

        self.compSettings = self.project.projConfig['Managers'][manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)


###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def installPTWorkingText (self, ptConf, cid, cType, compPrefix) :
        '''Find the source text in the local PT project and install it into
        the working text folder of the project with the proper name.'''

        # Build up the source and working file names based on what we find
        # in the PT project SSF file
        if ptConf['ScriptureText']['FileNameBookNameForm'] == '41MAT' :
            thisFile = compPrefix + cid.upper() + ptConf['ScriptureText']['FileNamePostPart']
        else :
            writeToLog(self.project.local, self.project.userConfig, 'ERR', 'The PT Book Name Form: [' + ptConf['ScriptureText']['FileNameBookNameForm'] + '] is not supported yet.')
            return

        ptSource = os.path.join(os.path.dirname(self.project.local.projHome), thisFile)
        target = os.path.join(self.project.local.projTextFolder, cid + '.' + cType.lower())

        # Copy the source to the working text folder
        if os.path.isfile(ptSource) :
            shutil.copy(ptSource, target)






