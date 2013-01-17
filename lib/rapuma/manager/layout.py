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
    xmlConfDefaultFile     = 'layout_default.xml'

    def __init__(self, project, cfg, cType) :
        '''Do the primary initialization for this manager.'''

        super(Layout, self).__init__(project, cfg)

        # List the renderers this manager supports
        self.cType                          = cType
        self.manager                        = self.cType + '_Layout'
        self.layoutConfig                   = ConfigObj(encoding='utf-8')
        self.project                        = project
        self.sourcePath                     = getSourcePath(self.project.userConfig, self.project.projectIDCode, self.cType)
        # Overrides
        self.project.local.layoutConfFile   = os.path.join(self.project.local.projConfFolder, self.manager + '.conf')

# FIXME: we need to be able to run persistant values on both the default and the cType configs
# This is very different from the other managers, do it with something like this:


#        # Get persistant values from the config if there are any
#        manager = self.cType + '_Illustration'
#        newSectionSettings = getPersistantSettings(self.project.projConfig['Managers'][manager], os.path.join(self.project.local.rapumaConfigFolder, self.xmlConfFile))
#        if newSectionSettings != self.project.projConfig['Managers'][manager] :
#            self.project.projConfig['Managers'][manager] = newSectionSettings

#        self.compSettings = self.project.projConfig['Managers'][manager]

#        for k, v in self.compSettings.iteritems() :
#            setattr(self, k, v)

# It might be the best way will be to split the current conf back out to the 2 source forms
# check and update each one, then merge them back together. A copy will need to be taken
# first before the process is started so the results can be compared with the orginal. If
# there is no difference, nothing will be written out.



# This needs to be reworked:

        # Create a new default layout config file if needed
        if not os.path.isfile(self.project.local.layoutConfFile) :
            self.layoutConfig  = ConfigObj(getXMLSettings(self.project.local.rapumaLayoutDefaultFile), encoding='utf-8')
            self.layoutConfig.filename = self.project.local.layoutConfFile
            writeConfFile(self.layoutConfig)
            self.project.log.writeToLog('LYOT-010')
        else :
            self.layoutConfig = ConfigObj(self.project.local.layoutConfFile, encoding='utf-8')


###############################################################################
############################ Manager Level Functions ##########################
###############################################################################





