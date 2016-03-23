#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (sparkycbr at gmail dot com)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle user configuration operations.

###############################################################################
############################# Component Class #################################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, sys, site
from configobj import ConfigObj

# Load the local classes
from rapuma.core.tools          import Tools


class UserConfig (object) :

    def __init__(self) :
        '''Intitate the whole class and create the object.'''

#        import pdb; pdb.set_trace()

        self.rapumaHome         = os.environ.get('RAPUMA_BASE')
        self.defaultUserHome    = os.environ.get('RAPUMA_USER')
        self.userConfFileName   = 'rapuma.conf'
        self.tools              = Tools()

        # Point to the right user config
        # Look for a web installation first, if not go to default
        # Note that a slash is put before var as it is off of root
        # That kind of stops this from being cross-platform
        rapumaWebConfig         = os.path.join('/var', 'lib', 'rapuma', 'config', self.userConfFileName)
        defaultConfig           = os.path.join(self.defaultUserHome, self.userConfFileName)
        if os.path.exists(rapumaWebConfig) :
            self.userConfFile   = rapumaWebConfig
        else :
            self.userConfFile   = defaultConfig

        # Check to see if the file is there, then read it in and break it into
        # sections. If it fails, scream really loud!
        rapumaXMLDefaults = os.path.join(self.rapumaHome, 'config', 'rapuma.xml')
        if os.path.exists(rapumaXMLDefaults) :
            self.tools.sysXmlConfig = self.tools.xml_to_section(rapumaXMLDefaults)
        else :
            raise IOError, "Can't open " + rapumaXMLDefaults

        # Now make the users local rapuma.conf file if it isn't there
        if not os.path.exists(self.userConfFile) :
            self.initUserHome()

        # Load the system.conf file into an object
        self.userConfig = ConfigObj(self.userConfFile, encoding='utf-8')

        # Log messages for this module
        self.errorCodes     = {
            '0000' : ['MSG', 'Placeholder message'],
        }

###############################################################################
############################ User Config Functions ############################
###############################################################################

    def initUserHome (self) :
        '''Initialize a user config file on a new install or system re-init.'''

        # Create home folders
        if not os.path.isdir(self.defaultUserHome) :
            os.mkdir(self.defaultUserHome)

        # Make the default global rapuma.conf for custom environment settings
        if not os.path.isfile(self.userConfFile) :
            self.userConfig = ConfigObj(self.tools.sysXmlConfig.dict(), encoding='utf-8')
            self.userConfig.filename = self.userConfFile
            self.userConfig['System']['initDate'] = self.tools.tStamp()
            self.userConfig.write()


    def setSystemSettings (self, section, key, value) :
        '''Function to make system settings.'''

        oldValue = self.userConfig[section][key]
        if oldValue != value :
            self.userConfig[section][key] = value
            # Write out the results
            self.userConfig.write()
            self.tools.terminal('\nRapuma user name setting changed from [' + oldValue + '] to [' + value + '].\n\n')
        else :
            self.tools.terminal('\nSame value given, nothing to changed.\n\n')




