#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110823
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will create an object that will hold all the general local info
# for a project.

# History:
# 20120228 - djd - Start with user_config.py as a model


###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os

# Load the local classes
from tools import *


class ProjLocal (object) :

    def __init__(self, projHome, userHome, rpmHome) :
        '''Intitate the whole class and create the object.'''
        
        self.projHome               = projHome
        self.userHome               = userHome
        self.rpmHome                = rpmHome

        # Bring in all the RPM default project location settings
        rpmXMLDefaults = os.path.join(self.rpmHome, 'config', 'proj_local.xml')
        if os.path.exists(rpmXMLDefaults) :
            lc = xml_to_section(rpmXMLDefaults)
        else :
            raise IOError, "Can't open " + rpmXMLDefaults
            
        # Do a loopy thingy and pull out all the known settings
        for key in lc['ProjFolderNames'] :
            if type(lc['ProjFolderNames'][key]) == list :
                setattr(self, key, os.path.join(self.projHome, *lc['ProjFolderNames'][key]))
            else :
                setattr(self, key, os.path.join(self.projHome, lc['ProjFolderNames'][key]))

        for key in lc['RpmFolderNames'] :
            if type(lc['RpmFolderNames'][key]) == list :
                setattr(self, key, os.path.join(self.projHome, *lc['RpmFolderNames'][key]))
            else :
                setattr(self, key, os.path.join(self.projHome, lc['RpmFolderNames'][key]))

        for key in lc['FileNames'] :
            setattr(self, key, lc['FileNames'][key])

        print dir(self)

