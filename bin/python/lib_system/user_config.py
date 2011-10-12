#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110823
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle user configuration operations.

# History:
# 20110823 - djd - Started with intial file from RPM project


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
        
        self.userHome       = userHome
        self.rpmHome       = rpmHome
        self.userConfFile   = os.path.join(userHome, 'rpm.conf')
        self.userResources  = os.path.join(userHome, 'resources')
        self.createUserConfig()


    def createUserConfig (self) :
        '''Create a user config object based on the system defaults and the
        overrides in the user config file, if it exsits.  If it does not, make
        one.'''

        # Check to see if the file is there, then read it in and break it into
        # sections. If it fails, scream really loud!
        rpmXML = os.path.join(self.rpmHome, 'bin', 'rpm.xml')
        if os.path.exists(rpmXML) :
            sysXmlConfig = xml_to_section(rpmXML)
        else :
            raise IOError, "Can't open " + rpmXML

        # Now get the settings from the users rpm.conf file
        if not os.path.exists(self.userConfFile) :
            self.initUserHome()

        # Load the conf file into an object
        rpmConfig = ConfigObj(self.userConfFile)

        # Look for any projects that might be registered and copy the data out
        try :
            rpmProjs = rpmConfig['Projects']
        except :
            rpmProjs = None

        # Create a new conf object based on all the XML default settings
        # Then override them with any exsiting user settings.
        self.userConfig = ConfigObj(sysXmlConfig.dict()).override(rpmConfig)

        # Put back the copied data of any project information that we might have
        # lost from the XML/conf file merging.
        if rpmProjs :
            self.userConfig['Projects'] = rpmProjs
            
        return self.userConfig


    def initUserHome (self) :
        '''Initialize a user config file on a new install or system re-init.'''
    
        # Create home folders
        if not os.path.isdir(self.userHome) :
            os.mkdir(self.userHome)

        if not os.path.isdir(self.userResources) :
            os.mkdir(self.userResources)

        # Make the default global rpm.conf for custom environment settings
        if not os.path.isfile(self.userConfFile) :
            date_time = tStamp()
            rpm = ConfigObj()
            rpm.filename = self.userConfFile
            rpm['System'] = {}
            rpm['Folders'] = {}
            rpm['System']['userName'] = 'Default User'
            rpm['System']['initDate'] = date_time
            # Folder list
            folders = ['auxiliaryTypes', 'compTypes', 'projTypes', 'share']
            # System folders
            for f in folders :
                rpm['Folders']['rpm' + f] = os.path.join(self.rpmHome, 'resources', 'lib_' + f)
            # User (home) folders
            for f in folders :
                thisFolder = os.path.join(self.userHome, 'resources', 'lib_' + f)
                rpm['Folders']['user' + f] = thisFolder
                if not os.path.isdir(thisFolder) :
                    os.mkdir(thisFolder)

            # Write out the user config file
            rpm.write()


