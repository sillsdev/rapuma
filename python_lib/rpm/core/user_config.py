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

    def __init__(self, local) :
        '''Intitate the whole class and create the object.'''
        

        self.local  = local
        # Check to see if the file is there, then read it in and break it into
        # sections. If it fails, scream really loud!
        rpmXMLDefaults = os.path.join(self.local.rpmHome, 'config', 'rpm.xml')
        if os.path.exists(rpmXMLDefaults) :
            sysXmlConfig = xml_to_section(rpmXMLDefaults)
        else :
            raise IOError, "Can't open " + rpmXMLDefaults

        # Now make the users local rpm.conf file if it isn't there
        if not os.path.exists(self.local.userConfFile) :
            self.initUserHome()

        # Load the RPM conf file into an object
        self.userConfig = ConfigObj(self.local.userConfFile)

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

        # Do not bother writing if nothing has changed
        if not self.userConfig.__eq__(newConfig) :
            self.userConfig = newConfig
            self.userConfig.filename = self.local.userConfFile
            self.userConfig.write()


    def initUserHome (self) :
        '''Initialize a user config file on a new install or system re-init.'''

        # Create home folders
        if not os.path.isdir(self.local.userHome) :
            os.mkdir(self.local.userHome)

        # Make the default global rpm.conf for custom environment settings
        if not os.path.isfile(self.local.userConfFile) :
            self.userConfig = ConfigObj()
            self.userConfig.filename = self.local.userConfFile
            self.userConfig['System'] = {}
            self.userConfig['System']['userName'] = 'Default User'
            self.userConfig['System']['initDate'] = tStamp()
            self.userConfig.write()


    def isRegisteredProject (self, pid) :
        '''Check to see if this project is recorded in the user's config'''

        try :
            return pid in self.userConfig['Projects']
        except :
            pass


    def registerProject (self, pid, pname, ptype, projHome) :
        '''If it is already not there, add information about this project to the
        user's rpm.conf located in the user's config folder.'''

        if not self.isRegisteredProject(pid) :

            buildConfSection(self.userConfig, 'Projects')
            buildConfSection(self.userConfig['Projects'], pid)

            # Now add the project data
            self.userConfig['Projects'][pid]['projectName']          = pname
            self.userConfig['Projects'][pid]['projectType']          = ptype
            self.userConfig['Projects'][pid]['projectPath']          = projHome
            self.userConfig['Projects'][pid]['projectCreateDate']    = tStamp()
            self.userConfig.write()
            return True


    def unregisterProject (self, pid) :
        '''Remove a project from the user config file.'''
        
        del self.userConfig['Projects'][pid]
        self.userConfig.write()


