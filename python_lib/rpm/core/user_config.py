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


    def initUserHome (self) :
        '''Initialize a user config file on a new install or system re-init.'''

        # Create home folders
        if not os.path.isdir(self.userHome) :
            os.mkdir(self.userHome)

        # Make the default global rpm.conf for custom environment settings
        if not os.path.isfile(self.userConfFile) :
            date_time = tStamp()
            self._userConfig = ConfigObj()
            self._userConfig.filename = self.userConfFile
            self._userConfig['System'] = {}
            self._userConfig['System']['userName'] = 'Default User'
            self._userConfig['System']['initDate'] = date_time
            writeConfFile(self._userConfig, self.userConfFile)


def isRegisteredProject (userConfig, pid) :
    '''Check to see if this project is recorded in the user's config'''

    try :
        return pid in userConfig['Projects']
    except :
        pass


def registerProject (userConfig, projConfig, projHome) :
    '''If it is already not there, add information about this project to the
    user's rpm.conf located in the user's config folder.'''

    pid     = projConfig['ProjectInfo']['projectIDCode']
    pname   = projConfig['ProjectInfo']['projectName']
    ptype   = projConfig['ProjectInfo']['projectType']
    date    = projConfig['ProjectInfo']['projectCreateDate']
    if not isRegisteredProject(userConfig, pid) :

        # FIXME: Before we create a project entry we want to be sure that
        # the projects section already exsists.  There might be a better way
        # of doing this.
        try :
            userConfig['Projects'][pid] = {}
        except :
            userConfig['Projects'] = {}
            userConfig['Projects'][pid] = {}

        # Now add the project data
        userConfig['Projects'][pid]['projectName']          = pname
        userConfig['Projects'][pid]['projectType']          = ptype
        userConfig['Projects'][pid]['projectPath']          = projHome
        userConfig['Projects'][pid]['projectCreateDate']    = date
        return True
    else :
        return False

