#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110823
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project configuration operations.

# History:
# 20120228 - djd - Start with user_config.py as a model


###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os
from configobj import ConfigObj

# Load the local classes
from tools import *


class ProjConfig (object) :

    def __init__(self, local) :
        '''Intitate the whole class and create the object.'''

        self.local          = local
        self.projConfig     = ConfigObj()
#        self.projHome       = ''

        # Create a fresh projConfig object
        if os.path.isfile(self.local.projConfFile) :
            self.projConfig = ConfigObj(self.local.projConfFile)
            self.projectType = self.projConfig['ProjectInfo']['projectType']
            self.projConfig.filename = self.local.projConfFile


    def makeNewProjConf (self, local, pid, ptype, pname) :
        '''Create a new project configuration file for a new project.'''

        self.projConfig = ConfigObj(getXMLSettings(os.path.join(local.rpmConfigFolder, ptype + '.xml')))
        # Insert intitial project settings
        self.projConfig['ProjectInfo']['projectType']              = ptype
        self.projConfig['ProjectInfo']['projectName']              = pname
        self.projConfig['ProjectInfo']['projectCreateDate']        = tStamp()
        self.projConfig['ProjectInfo']['projectIDCode']            = pid
        self.projConfig.filename = local.projConfFile
        self.projConfig.write()


