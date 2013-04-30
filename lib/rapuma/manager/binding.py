#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project tasks.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil

# Load the local classes
from rapuma.core.tools          import Tools
from rapuma.project.manager     import Manager


###############################################################################
################################## Begin Class ################################
###############################################################################

class Binding (Manager) :

    def __init__(self, project, cfg, cType) :
        '''Do the primary initialization for this manager.'''

        super(Binding, self).__init__(project, cfg)

        # List the renderers this manager supports
        self.tools                          = Tools()
        self.cType                          = cType
        self.Ctype                          = cType.capitalize()
        self.manager                        = 'usfm_Binding'
        self.project                        = project
        self.local                          = project.local
        self.managers                       = project.managers
        self.projConfig                     = self.project.projConfig
        self.projMediaType                  = self.project.projectMediaIDCode
        self.rapumaXmlBindConfig            = os.path.join(self.local.rapumaConfigFolder, 'binding.xml')
        # File names

        # Paths

        # Files with paths

        # Get persistant values from the config if there are any
        newSectionSettings = self.tools.getPersistantSettings(self.project.projConfig['Managers'][self.manager], self.rapumaXmlBindConfig)
        if newSectionSettings != self.project.projConfig['Managers'][self.manager] :
            self.project.projConfig['Managers'][self.manager] = newSectionSettings
            self.tools.writeConfFile(self.project.projConfig)

        self.compSettings = self.project.projConfig['Managers'][self.manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)



        # Log messages for this module
        self.errorCodes     = {

            '0000' : ['MSG', 'Placeholder message'],

        }

###############################################################################
############################ Manager Level Functions ##########################
###############################################################################


# FIXME: We may want to move to this manager some more general functions
# from other managers


