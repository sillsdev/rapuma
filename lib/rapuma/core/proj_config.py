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
from rapuma.core.tools import *


class ProjConfig (object) :

    def __init__(self, local) :
        '''Intitate the whole class and create the object.'''

        self.local          = local
        self.projConfig     = ConfigObj()
#        self.projHome       = ''

        # Create a fresh projConfig object
        if os.path.isfile(self.local.projConfFile) :
            self.projConfig = ConfigObj(self.local.projConfFile)
            self.projectMediaIDCode = self.projConfig['ProjectInfo']['projectMediaIDCode']
            self.projConfig.filename = self.local.projConfFile


    def makeNewProjConf (self, local, pid, pmid, pname, cVersion) :
        '''Create a new project configuration file for a new project.'''

        self.projConfig = ConfigObj(getXMLSettings(os.path.join(local.rapumaConfigFolder, pmid + '.xml')))
        # Insert intitial project settings
        self.projConfig['ProjectInfo']['projectMediaIDCode']        = pmid
        self.projConfig['ProjectInfo']['projectName']               = pname
        self.projConfig['ProjectInfo']['projectCreatorVersion']     = cVersion
        self.projConfig['ProjectInfo']['projectCreateDate']         = tStamp()
        self.projConfig['ProjectInfo']['projectIDCode']             = pid
        self.projConfig.filename                                    = local.projConfFile
        self.projConfig.write()







