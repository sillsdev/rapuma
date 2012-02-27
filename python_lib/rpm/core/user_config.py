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
        self.userConfig            = {}
        self.createUserConfig()

# FIXME: merge with init
    def createUserConfig (self) :
        '''Create a user config object based on the system defaults and the
        overrides in the user config file, if it exsits.  If it does not, make
        one.'''

        # Check to see if the file is there, then read it in and break it into
        # sections. If it fails, scream really loud!
        rpmXMLDefaults = os.path.join(self.rpmHome, 'config', 'rpm.xml')
        if os.path.exists(rpmXMLDefaults) :
            sysXmlConfig = xml_to_section(rpmXMLDefaults)
        else :
            raise IOError, "Can't open " + rpmXMLDefaults

        # Now make the users local rpm.conf file if it isn't there
        if not os.path.exists(self.userConfFile) :
            self.initUserHome()

        # Load the RPM conf file into an object
        self.userConfig = ConfigObj(self.userConfFile)

        # Look for any projects that might be registered and copy the data out
        try :
            userProjs = self.userConfig['Projects']
        except :
            userProjs = None

        # Create a new conf object based on all the XML default settings
        # Then override them with any exsiting user settings.
        newConfig = ConfigObj(sysXmlConfig.dict()).override(self.userConfig)

        # Put back the copied data of any project information that we might have
        # lost from the XML/conf file merging.
        if userProjs :
            newConfig['Projects'] = userProjs
            
        self.userConfig = newConfig
        self.userConfig.filename = self.userConfFile
        writeConfFile(self.userConfig)


    def initUserHome (self) :
        '''Initialize a user config file on a new install or system re-init.'''

        # Create home folders
        if not os.path.isdir(self.userHome) :
            os.mkdir(self.userHome)

        # Make the default global rpm.conf for custom environment settings
        if not os.path.isfile(self.userConfFile) :
            self.userConfig = ConfigObj()
            self.userConfig.filename = self.userConfFile
            self.userConfig['System'] = {}
            self.userConfig['System']['userName'] = 'Default User'
            self.userConfig['System']['initDate'] = tStamp()
            writeConfFile(self.userConfig)


    def isRegisteredProject (self, pid) :
        '''Check to see if this project is recorded in the user's config'''

        try :
            return pid in self.userConfig['Projects']
        except :
            pass


    def registerProject (self, pid, pname, ptype, projHome) :
        '''If it is already not there, add information about this project to the
        user's rpm.conf located in the user's config folder.'''

        if not self.isRegisteredProject(self.userConfig, pid) :

            buildConfSection(self.userConfig, 'Projects')
            buildConfSection(self.userConfig['Projects'], pid)

            # Now add the project data
            self.userConfig['Projects'][pid]['projectName']          = pname
            self.userConfig['Projects'][pid]['projectType']          = ptype
            self.userConfig['Projects'][pid]['projectPath']          = projHome
            self.userConfig['Projects'][pid]['projectCreateDate']    = tStamp()
            writeConfFile(self.userConfig)
            return True

    def unregisterProject (self, pid) :
        '''Remove a project from the user config file.'''
        
        del self.userConfig['Projects'][pid]
        writeConfFile(self.userConfig)


