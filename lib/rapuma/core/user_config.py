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
        self.defaultUserHome    = os.getcwd()
        self.userConfFileName   = 'system.ini'
        self.tools              = Tools()

        # Regardless of what environment Rapuma is deployed, the user/system
        # config file is located with the program rather then the traditional
        # location of ~/.config/rapuma Doing it this way requires the user
        # to preconfigure the system.ini file before runing the setup.py
        # script to install Rapuma.
        self.userConfFile           = os.path.join(self.defaultUserHome, 'config', self.userConfFileName)

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




