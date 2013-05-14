
#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle map groups in book projects.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, codecs, re, subprocess, tempfile
from configobj                      import ConfigObj, Section

# Load the local classes
from rapuma.core.tools              import Tools
from rapuma.core.proj_config        import ProjConfig
from rapuma.core.user_config        import UserConfig
from rapuma.core.proj_local         import ProjLocal
from rapuma.core.proj_log           import ProjLog
from rapuma.project.project         import Project


###############################################################################
################################## Begin Class ################################
###############################################################################

class Maps (object) :

    def __init__(self, pid) :
        '''Do the primary initialization for this manager.'''

        self.pid                        = pid
        self.tools                      = Tools()
        self.user                       = UserConfig()
        self.userConfig                 = self.user.userConfig
        self.projHome                   = self.userConfig['Projects'][self.pid]['projectPath']
        self.projectMediaIDCode         = self.userConfig['Projects'][self.pid]['projectMediaIDCode']
        self.local                      = ProjLocal(self.pid)
        self.projConfig                 = ProjConfig(self.local).projConfig
        self.log                        = ProjLog(self.pid)
        # File names
        self.defaultXmlConfFileName     = 'proj_maps.xml'
        self.mapsConfFileName           = 'maps.conf'
        # Paths
        self.projMapsFolder             = os.path.join(self.local.projIllustrationsFolder, 'Maps')
        self.rpmRapumaConfigFolder      = self.local.rapumaConfigFolder
        # File names with paths
        self.projMapXmlFile             = os.path.join(self.rpmRapumaConfigFolder, self.defaultXmlConfFileName)
        self.mapsConfFile               = os.path.join(self.projConfFolder, self.mapsConfFileName)

        # Load the config object
        self.mapsConfig                 = self.tools.initConfig(self.mapsConfFile, self.defaultXmlConfFile)
        # Load settings from the manager config
        for k, v in self.projConfig['Managers'][self.manager].iteritems() :
            setattr(self, k, v)


        # Log messages for this module
        self.errorCodes     = {

            '0205' : ['MSG', 'Unassigned message.'],
            '0210' : ['LOG', 'Wrote out map settings to the project configuration file.'],
            '0215' : ['ERR', 'Failed to write out project map settings to the project configuration file.'],
            '0220' : ['LOG', 'Added maps to project.'],
            '0230' : ['MSG', 'Maps have been removed from the project configuration.'],
            '0240' : ['MSG', 'Rendered the project maps.'],
            '0250' : ['LOG', 'Created project maps folder.'],

        }


###############################################################################
################################ Map Functions ################################
###############################################################################
######################## Error Code Block Series = 200 ########################
###############################################################################

#        import pdb; pdb.set_trace()

    def addMaps (self, mapList) :
        '''Add maps to the project.'''

        self.createMapSettings()
        self.projConfig['Groups']['Maps']['mapFileList'] = mapList
        if self.tools.writeConfFile(self.projConfig) :
            self.log.writeToLog(self.errorCodes['0220'])


    def removeMaps (self) :
        '''Remove the maps from a project.'''

        self.log.writeToLog(self.errorCodes['0230'])


    def renderMaps (self, mapFiles = None, force = False) :
        '''Render a map or a set of maps.'''

        self.log.writeToLog(self.errorCodes['0240'])


    def createMapsFolder (self) :
        '''Create a project maps folder if one is not there.'''

        if not os.path.exists(self.projMapsFolder) :
            os.makedirs(self.projMapsFolder)
            self.log.writeToLog(self.errorCodes['0250'])


    def createMapSettings (self) :
        '''Create a map group and settings in the project config file.'''

        # At this point we are under the assumption that only one map group is needed
        if not self.tools.isConfSection(self.projConfig['Groups'], 'Maps') :
            self.tools.buildConfSection(self.projConfig['Groups'], 'Maps')

        # Update settings if needed
        update = False
        mapDefaults = self.tools.getXMLSettings(self.projMapXmlFile)
        for k, v, in maps.iteritems() :
            # Do not overwrite if a value is already there
            if not self.tools.testForSetting(self.projConfig['Groups']['Maps'], k) :
                self.projConfig['Groups']['Maps'][k] = v
                # If we are dealing with an empty string, don't bother writing out
                # Trying to avoid needless conf updating here. Just in case we are
                # working with a list, we'll use len()
                if len(v) > 0 :
                    update = True
        # Update the conf if one or more settings were changed
        if update :
            if self.tools.writeConfFile(self.projConfig) :
                self.log.writeToLog(self.errorCodes['0210'])
            else :
                self.log.writeToLog(self.errorCodes['0215'])




