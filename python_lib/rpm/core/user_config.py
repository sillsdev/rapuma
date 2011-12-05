#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110823
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle user configuration operations.

# History:
# 20111202 - djd - Start over with manager-centric model


###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os
from configobj import ConfigObj

# Load the local classes
from tools import *


class UserConfig (object) :

    def __init__(self, userHome, rpmHome) :
        '''Intitate the whole class'''
        
        self.userHome               = userHome
        self.rpmHome                = rpmHome
        self.userConfFile           = os.path.join(userHome, 'rpm.conf')
        self._defaultConfig         = {}
        self._userConfig            = {}
        self.writeOutUserConfFile   = False
        self.createUserConfig()


    def createUserConfig (self) :
        '''Create a user config object based on the system defaults and the
        overrides in the user config file, if it exsits.  If it does not, make
        one.'''

        # Check to see if the file is there, then read it in and break it into
        # sections. If it fails, scream really loud!
        rpmXML = os.path.join(self.rpmHome, 'config', 'rpm.xml')
        if os.path.exists(rpmXML) :
            sysXmlConfig = xml_to_section(rpmXML)
        else :
            raise IOError, "Can't open " + rpmXML

        # Now make the users local rpm.conf file if it isn't there
        if not os.path.exists(self.userConfFile) :
            self.initUserHome()

        # Load the RPM conf file into an object
        self._userConfig = ConfigObj(self.userConfFile)

        # Look for any projects that might be registered and copy the data out
        try :
            userProjs = self._userConfig['Projects']
        except :
            userProjs = None

        # Create a new conf object based on all the XML default settings
        # Then override them with any exsiting user settings.
        newConfig = ConfigObj(sysXmlConfig.dict()).override(self._userConfig)

        # Put back the copied data of any project information that we might have
        # lost from the XML/conf file merging.
        if userProjs :
            newConfig['Projects'] = userProjs
            
        self._userConfig = newConfig
        self._userConfig.filename = self.userConfFile
        self._userConfig.write()


    def initUserHome (self) :
        '''Initialize a user config file on a new install or system re-init.'''
    
        # Create home folders
        if not os.path.isdir(self.userHome) :
            os.mkdir(self.userHome)

        # Make the default global rpm.conf for custom environment settings
        if not os.path.isfile(self.userConfFile) :
            date_time = tStamp()
            rpm = ConfigObj()
            rpm.filename = self.userConfFile
            rpm['System'] = {}
            rpm['System']['userName'] = 'Default User'
            rpm['System']['initDate'] = date_time

            # Write out the user config file
            rpm.write()


