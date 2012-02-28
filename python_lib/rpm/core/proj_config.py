#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110823
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project configuration operations.

# History:
# 20120228 - djd - Start with user_config.py as a model


###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os
from configobj import ConfigObj

# Load the local classes
from tools import *


class ProjConfig (object) :

    def __init__(self, userHome, rpmHome) :
        '''Intitate the whole class and create the object.'''
        
        self.userHome               = userHome
        self.rpmHome                = rpmHome
        self.userConfFile           = os.path.join(userHome, 'rpm.conf')
        self.userConfig            = {}

# Here we do all the stuff that it takes to initiate a project config file

#        # Check to see if the file is there, then read it in and break it into
#        # sections. If it fails, scream really loud!
#        rpmXMLDefaults = os.path.join(self.rpmHome, 'config', 'rpm.xml')
#        if os.path.exists(rpmXMLDefaults) :
#            sysXmlConfig = xml_to_section(rpmXMLDefaults)
#        else :
#            raise IOError, "Can't open " + rpmXMLDefaults

#        # Now make the users local rpm.conf file if it isn't there
#        if not os.path.exists(self.userConfFile) :
#            self.initUserHome()

#        # Load the RPM conf file into an object
#        self.userConfig = ConfigObj(self.userConfFile)

#        # Look for any projects that might be registered and copy the data out
#        try :
#            userProjs = self.userConfig['Projects']
#        except :
#            userProjs = None

#        # Create a new conf object based on all the XML default settings
#        # Then override them with any exsiting user settings.
#        newConfig = ConfigObj(sysXmlConfig.dict()).override(self.userConfig)

#        # Put back the copied data of any project information that we might have
#        # lost from the XML/conf file merging.
#        if userProjs :
#            newConfig['Projects'] = userProjs

#        # Do not bother writing if nothing has changed
#        if not self.userConfig.__eq__(newConfig) :
#            self.userConfig = newConfig
#            self.userConfig.filename = self.userConfFile
#            self.userConfig.write()


