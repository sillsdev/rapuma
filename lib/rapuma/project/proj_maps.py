
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
        self.projConfFolder             = self.local.projConfFolder
        self.projMapsFolder             = os.path.join(self.local.projIllustrationsFolder, 'Maps')
        self.rpmRapumaConfigFolder      = self.local.rapumaConfigFolder
        # File names with paths
        self.mapsConfFile               = os.path.join(self.projConfFolder, self.mapsConfFileName)
        self.defaultXmlConfFile         = os.path.join(self.rpmRapumaConfigFolder, self.defaultXmlConfFileName)

        # Load the config object
        self.mapsConfig                 = self.tools.initConfig(self.mapsConfFile, self.defaultXmlConfFile)
#        # Load settings from the manager config
#        for k, v in self.mapsConfig['Maps'][self.manager].iteritems() :
#            setattr(self, k, v)


        # Log messages for this module
        self.errorCodes     = {

            '0205' : ['ERR', 'Cannot find: [<<1>>]'],
            '0210' : ['LOG', 'Wrote out map settings to the project configuration file.'],
            '0215' : ['ERR', 'Failed to write out project map settings to the project configuration file.'],
            '0220' : ['MSG', 'Added maps to project.'],
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

    def addMapGroup (self, gid, mapFileList, sourceId, path, force = False) :
        '''Add maps to the project.'''

        print gid, mapFileList, sourceId, path, force

        mapInfo = {}
        mapInfo['MapFiles'] = {}

        # First test for the files
        for m in mapFileList :
            mp = os.path.join(path, m)
            if not os.path.exists(mp) :
                self.log.writeToLog(self.errorCodes['0205'], [mp])
            else :
                mapInfo['MapFiles'][os.urandom(8)] = {}
                
        print mapInfo
        


#        self.createMapsFolder()
#        self.mapsConfig['ProjMapInfo']['mapFileList'] = mapList
#        self.tools.writeConfFile(self.mapsConfig)
#        self.log.writeToLog(self.errorCodes['0220'])


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






