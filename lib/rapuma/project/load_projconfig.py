#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will load a project configuration file and return a ConfigObj.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for this process

import os
from configobj                          import ConfigObj

# Load the local classes
from rapuma.core.tools                  import Tools, ToolsPath
from rapuma.core.user_config            import UserConfig
from rapuma.core.proj_local             import ProjLocal

###############################################################################
################################## Begin Class ################################
###############################################################################

class LoadProjConfig (object) :

    def __init__(self, pid) :
        '''Do the primary initialization for this class.'''

        userConfig                     = UserConfig().userConfig
        mType                          = userConfig['Projects'][pid]['projectMediaIDCode']
        local                          = ProjLocal(pid)
        tools                          = Tools()
        # File names
        projConfFileName               = 'project.conf'
        progConfXmlFileName            = mType + '.xml'
        # Paths
        projConfFolder                 = local.projConfFolder
        rapumaConfigFolder             = local.rapumaConfigFolder
        # Files with paths
        projConfFile                   = os.path.join(projConfFolder, projConfFileName)
        projConfXmlFile                = os.path.join(rapumaConfigFolder, progConfXmlFileName)
        # The proj config obj is really the only thing we want
        self.projConfig                = tools.initConfig(local.projConfFile, projConfXmlFile)

###############################################################################
############################ Manager Level Functions ##########################
###############################################################################
####################### Error Code Block Series = 1000 ########################
###############################################################################

# Do we need to put anything here?


