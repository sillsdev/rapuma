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

    def __init__(self, rpmHome) :
        '''Intitate the whole class and create the object.'''

        self.rpmHome = rpmHome

        # Set the user environment path
        self.userHome = os.environ.get('RPM_USER')
        if not self.userHome :
            sysHome = os.environ.get('HOME')
            self.userHome = os.path.join(sysHome, '.config', 'rpm')
            os.environ['RPM_USER'] = self.userHome

        # Set the (potential) project home
        self.projHome = os.getcwd()

        # Bring in all the RPM default project location settings
        rpmXMLDefaults = os.path.join(self.rpmHome, 'config', 'proj_local.xml')
        if os.path.exists(rpmXMLDefaults) :
            lc = xml_to_section(rpmXMLDefaults)
        else :
            raise IOError, "Can't open " + rpmXMLDefaults
            
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
                if type(lc[t][key]) == list :
                    setattr(self, key, os.path.join(home, *lc[t][key]))
                else :
                    setattr(self, key, os.path.join(home, lc[t][key]))
                print getattr(self, key)
        
        
        
#        for key in lc['ProjFolders'] :
#            if type(lc['ProjFolders'][key]) == list :
#                setattr(self, key, os.path.join(self.projHome, *lc['ProjFolders'][key]))
#            else :
#                setattr(self, key, os.path.join(self.projHome, lc['ProjFolders'][key]))

#        for key in lc['UserFolders'] :
#            if type(lc['UserFolders'][key]) == list :
#                setattr(self, key, os.path.join(self.userHome, *lc['ProjFolders'][key]))
#            else :
#                setattr(self, key, os.path.join(self.userHome, lc['ProjFolders'][key]))

#        for key in lc['RpmFolders'] :
#            if type(lc['RpmFolders'][key]) == list :
#                setattr(self, key, os.path.join(self.rpmHome, *lc['RpmFolders'][key]))
#            else :
#                setattr(self, key, os.path.join(self.rpmHome, lc['RpmFolders'][key]))

#        for key in lc['ProjFiles'] :
#            if type(lc['ProjFiles']) == list :
#                setattr(self, key, os.path.join(self.userHome, *lc['ProjFiles'][key]))
#            else :
#                setattr(self, key, os.path.join(self.userHome, lc['ProjFiles'][key]))

#        for key in lc['UserFiles'] :
#            if type(lc['UserFiles']) == list :
#                setattr(self, key, os.path.join(self.userHome, *lc['UserFiles'][key]))
#            else :
#                setattr(self, key, os.path.join(self.userHome, lc['UserFiles'][key]))

#        for key in lc['RpmFiles'] :
#            if type(lc['RpmFiles']) == list :
#                setattr(self, key, os.path.join(self.userHome, *lc['RpmFiles'][key]))
#            else :
#                setattr(self, key, os.path.join(self.userHome, lc['RpmFiles'][key]))

        print dir(self)

