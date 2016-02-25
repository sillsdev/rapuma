#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (sparkycbr at gmail dot com)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class handles PDF component type tasks for book projects.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, codecs, re
from configobj import ConfigObj, Section
#from functools import partial

# Load the local classes
from rapuma.core.tools                  import Tools
from rapuma.group.group                 import Group
from rapuma.project.proj_config         import Config
from rapuma.project.proj_background     import ProjBackground


###############################################################################
################################## Begin Class ################################
###############################################################################

# As we load the module we will bring in all the common information about all the
# components this type will handle.

class Pdf (Group) :
    '''This class contains information about a type of component 
    used in a type of project.'''

    # Shared values
    xmlConfFile     = 'pdf.xml'

    def __init__(self, project, cfg) :
        super(Pdf, self).__init__(project, cfg)

#        import pdb; pdb.set_trace()

        # Set values for this manager
        self.pid                    = project.projectIDCode
        self.gid                    = project.gid
        self.cType                  = 'pdf'
        self.Ctype                  = self.cType.capitalize()
        self.project                = project
        self.local                  = project.local
        self.tools                  = Tools()
        self.proj_config            = Config(self.pid, self.gid)
        self.proj_config.getProjectConfig()
        self.proj_config.getAdjustmentConfig()
        self.projectConfig          = self.proj_config.projectConfig
        self.log                    = project.log
        self.cfg                    = cfg
        self.mType                  = project.projectMediaIDCode
        self.renderer               = project.projectConfig['CompTypes'][self.Ctype]['renderer']
        self.compSource             = project.projectConfig['CompTypes'][self.Ctype]['compSource']

        # Get the comp settings
        self.compSettings           = project.projectConfig['CompTypes'][self.Ctype]

        # Build a tuple of managers this component type needs to use
        self.pdfManagers = ('fixed', self.renderer)

        # Init the general managers
        for self.mType in self.pdfManagers :
            self.project.createManager(self.mType)

        # Create the internal ref names we use in this module
        self.text                   = self.project.managers[self.cType + '_Fixed']
        # File names

        # Folder paths
        self.projScriptFolder       = self.local.projScriptFolder
        self.projComponentFolder    = self.local.projComponentFolder
        self.gidFolder              = os.path.join(self.projComponentFolder, self.gid)
        # File names with folder paths
        self.rapumaXmlCompConfig    = os.path.join(self.project.local.rapumaConfigFolder, self.xmlConfFile)

        # Get persistant values from the config if there are any
        newSectionSettings = self.tools.getPersistantSettings(self.projectConfig['CompTypes'][self.Ctype], self.rapumaXmlCompConfig)
        if newSectionSettings != self.projectConfig['CompTypes'][self.Ctype] :
            self.projectConfig['CompTypes'][self.Ctype] = newSectionSettings
        # Set them here
        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)

        # Module Error Codes
        self.errorCodes     = {

            '0000' : ['MSG', 'Messages for the PDF module.'],

        }


###############################################################################
############################ Functions Begin Here #############################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################



    def makeFileNameWithExt(self, cid) :
        '''From what we know, return the full file name.'''

        return self.makeFileName(cid) + '.' + self.cType


    def getCidPath (self, cid) :
        '''Return the full path of the cName working text file. This assumes
        the cid is valid.'''

        return os.path.join(self.local.projComponentFolder, cid, self.makeFileNameWithExt(cid))


    def render(self, gid, cidList, pages, override, save) :
        '''This will join together PDF files in a group. Though we call
        it render, it is more of a merging operation.'''

#        import pdb; pdb.set_trace()

        # If the whole group is being rendered, we need to preprocess it
        cids = []
        if not cidList :
            cids = self.projectConfig['Groups'][gid]['cidList']
        else :
            cids = cidList

        # Preprocess all subcomponents (one or more)
        # Stop if it breaks at any point
        for cid in cids :
            if not self.preProcessGroup(gid, [cid]) :
                return False

        # With everything in place we can render the component.
        # Note: We pass the cidList straight through
        self.project.managers['pdf_' + self.renderer.capitalize()].run(gid, cidList, pages, override, save)

        return True


    def preProcessGroup (self, gid, cidList) :
        '''This will prepare a PDF component group for a merging
        operation. Right now, I'm not sure what that means so this
        is just a place holder function incase something needs
        to be done at this point.'''

#        import pdb; pdb.set_trace()

        return True


