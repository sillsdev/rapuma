#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will create an object that will hold all the general local info
# for a project.


###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os
from configobj import ConfigObj

# Load the local classes
from rapuma.core.tools              import Tools
from rapuma.core.user_config        import UserConfig


class ProjLocal (object) :

    def __init__(self, pid) :
        '''Intitate a class object which contains all the project folder locations.'''

        self.pid                = pid
        self.rapumaHome         = os.environ.get('RAPUMA_BASE')
        self.userHome           = os.environ.get('RAPUMA_USER')
        self.user               = UserConfig()
        self.userConfig         = self.user.userConfig
        self.projHome           = ''
        if self.userConfig['Projects'].has_key(pid) :
            self.projHome       = self.userConfig['Projects'][pid]['projectPath']
        self.tools              = Tools()

# FIXME: Do we want to change the way we do this and add file names and
# more sophisticated XML?

        # Bring in all the Rapuma default project location settings
        rapumaXMLDefaults = os.path.join(self.rapumaHome, 'config', 'proj_local.xml')
        if os.path.exists(rapumaXMLDefaults) :
            lc = self.tools.xml_to_section(rapumaXMLDefaults)
        else :
            raise IOError, "Can't open " + rapumaXMLDefaults
            
        # Create a list of project folders for later processing
        self.projFolders = lc['ProjFolders'].keys()

        # Do a loopy thingy and pull out all the known folder names
        localTypes = ['ProjFolders', 'UserFolders', 'RapumaFolders']
        for t in localTypes :
            if t[:3].lower() == 'pro' :
                home = getattr(self, 'projHome')
            elif t[:3].lower() == 'use' :
                home = getattr(self, 'userHome')
            elif t[:3].lower() == 'rap' :
                home = getattr(self, 'rapumaHome')
            # Combine folder names with paths and set vars
            for key in lc[t] :
                setattr(self, key + 'Name', lc[t][key])
                if type(lc[t][key]) == list :
                    setattr(self, key, os.path.join(home, *lc[t][key]))
                else :
                    setattr(self, key, os.path.join(home, lc[t][key]))

                # Uncomment for testing
#                print key + ' = ', getattr(self, key)

        # Add some additional necessary params
        self.lockExt = '.lock'
        
        # Add necessary file names
        self.projConfFileName       = 'project.conf'
        self.projConfFile           = os.path.join(self.projConfFolder, self.projConfFileName)
        self.userConfFileName       = 'rapuma.conf'
        self.userConfFile           = os.path.join(self.userHome, self.userConfFileName)
        if self.projHome :
            self.projLogFileName        = 'rapuma.log'
            self.projLogFile            = os.path.join(self.projHome, self.projLogFileName)
            self.projErrorLogFileName   = 'error.log'
            self.projErrorLogFile       = os.path.join(self.projHome, self.projErrorLogFileName)

        # Do some cleanup like getting rid of the last sessions error log file.
        try :
            if os.path.isfile(self.projErrorLogFile) :
                os.remove(self.projErrorLogFile)
        except :
            pass

        # Load the Rapuma conf file into an object
        self.localUserConfig = ConfigObj(self.userConfFile, encoding='utf-8')

        # Create a fresh projConfig object
        if os.path.isfile(self.projConfFile) :
            self.localProjConfig = ConfigObj(self.projConfFile, encoding='utf-8')


###############################################################################
########################### Project Local Functions ###########################
###############################################################################

# Maybe we should try to put something here?


