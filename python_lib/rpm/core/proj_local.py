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

    def __init__(self, rpmHome, userHome, projHome) :
        '''Intitate the whole class and create the object.'''

        self.rpmHome = rpmHome
        self.userHome = userHome
        self.projHome = projHome

        # Bring in all the RPM default project location settings
        rpmXMLDefaults = os.path.join(self.rpmHome, 'config', 'proj_local.xml')
        if os.path.exists(rpmXMLDefaults) :
            lc = xml_to_section(rpmXMLDefaults)
        else :
            raise IOError, "Can't open " + rpmXMLDefaults
            
        # Create a list of project folders for later processing
        self.projFolders = lc['ProjFolders'].keys()

        # Do a loopy thingy and pull out all the known settings
        localTypes = ['ProjFolders', 'UserFolders', 'RpmFolders', 'ProjFiles', 'UserFiles', 'RpmFiles']
        for t in localTypes :
            if t[:3].lower() == 'pro' :
                home = getattr(self, 'projHome')
            elif t[:3].lower() == 'use' :
                home = getattr(self, 'userHome')
            elif t[:3].lower() == 'rpm' :
                home = getattr(self, 'rpmHome')

            for key in lc[t] :
                # For extra credit, if we are looking at files, set the name here
                if t[-5:].lower() == 'files' :
                    if type(lc[t][key]) == list :
                        setattr(self, key + 'Name', lc[t][key][len(lc[t][key])-1])
                    else :
                        setattr(self, key + 'Name', lc[t][key])
                    # Uncomment for testing
#                    print key + 'Name = ', getattr(self, key + 'Name')

                if type(lc[t][key]) == list :
                    setattr(self, key, os.path.join(home, *lc[t][key]))
                else :
                    setattr(self, key, os.path.join(home, lc[t][key]))

                # Uncomment for testing
#                print key + ' = ', getattr(self, key)

        # Extract just the file names from these
        localTypes = ['ProjFiles', 'UserFiles', 'RpmFiles']

        # Add some additional necessary params
        self.lockExt = '.lock'

