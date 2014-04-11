#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110823
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle GUI interface configuration operations.

###############################################################################
############################# Component Class #################################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, sys, site
from configobj import ConfigObj

# Load the local classes
from rapuma.core.tools          import Tools


class GuiConfig (object) :

    def __init__(self) :
        '''Intitate the whole class and create the object.'''

        self.rapumaHome         = os.environ.get('RAPUMA_BASE')
        self.defaultUserHome    = os.environ.get('RAPUMA_USER')
        self.guiConfFileName    = 'rapuma_gui.conf'
        self.guiConfFile        = os.path.join(self.defaultUserHome, self.guiConfFileName)
        self.tools              = Tools()

        # Check to see if the file is there, then read it in and break it into
        # sections. If it fails, scream really loud!
        rapumaXMLDefaults = os.path.join(self.rapumaHome, 'config', 'rapuma_gui.xml')
        if os.path.exists(rapumaXMLDefaults) :
            self.tools.sysXmlConfig = self.tools.xml_to_section(rapumaXMLDefaults)
        else :
            raise IOError, "Can't open " + rapumaXMLDefaults

#        import pdb; pdb.set_trace()

        # Load the Rapuma conf file into an object
        self.guiConfig = ConfigObj(self.guiConfFile, encoding='utf-8')

        # Create a new conf object based on all the XML default settings
        # Then override them with any exsiting user settings.
        newConfig = ConfigObj(self.tools.sysXmlConfig.dict(), encoding='utf-8').override(self.guiConfig)

        # Do not bother writing if nothing has changed
        if not self.guiConfig.__eq__(newConfig) :
            self.guiConfig = newConfig
            self.guiConfig.filename = self.guiConfFile
            self.guiConfig.write()

        # Grab the module settings
        self.currentPid     = self.guiConfig['ProjectBookmark']['currentPid']
        self.currentGid     = self.guiConfig['ProjectBookmark']['currentGid']
        self.currentCid     = self.guiConfig['ProjectBookmark']['currentCid']
        self.lastPage       = self.guiConfig['ProjectBookmark']['lastPage']

        # Log messages for this module
        self.errorCodes     = {
            '0000' : ['MSG', 'Placeholder message'],
        }

###############################################################################
############################# GUI Config Functions ############################
###############################################################################

    def resetBookmarks (self) :
        '''This will set all the bookmarks to nothing in one pass.'''

        self.guiConfig['ProjectBookmark']['currentPid'] = ''
        self.guiConfig['ProjectBookmark']['currentGid'] = ''
        self.guiConfig['ProjectBookmark']['currentCid'] = ''
        self.currentPid = ''
        self.currentGid = ''
        self.currentCid = ''
        self.tools.writeConfFile(self.guiConfig)


    def setBookmarks (self) :
        '''This will set all the bookmarks in one pass to the current settings.'''

        self.guiConfig['ProjectBookmark']['currentPid'] = self.currentPid
        self.guiConfig['ProjectBookmark']['currentGid'] = self.currentGid
        self.guiConfig['ProjectBookmark']['currentCid'] = self.currentCid
        self.tools.writeConfFile(self.guiConfig)


    def setLastPage (self, page) :
        '''Set the current page number for a last page bookmarking reference.'''

        self.lastPage = page
        self.guiConfig['ProjectBookmark']['lastPage'] = page
        self.tools.writeConfFile(self.guiConfig)


    def setPidCurrent (self, pid = None) :
        '''Compare pid with the current recored pid in rapuma_gui.conf.
        If it is different change to the new pid. If not, leave it alone.'''

        if pid != self.currentPid :
            self.currentPid = pid
            self.guiConfig['ProjectBookmark']['currentPid'] = pid
            self.tools.writeConfFile(self.guiConfig)


    def setGidCurrent (self, gid = None) :
        '''Compare gid with the current recored gid in rapuma_gui.conf. 
        If it is different change to the new gid. If not, leave it alone.'''

        if gid != self.currentGid :
            self.currentGid = gid
            self.guiConfig['ProjectBookmark']['currentGid'] = gid
            self.tools.writeConfFile(self.guiConfig)


    def setCidCurrent (self, cid = None) :
        '''Compare cid with the current recored cid in rapuma_gui.conf. 
        If it is different change to the new cid. If not, leave it alone.'''

        if gid != self.currentCid :
            self.currentCid = cid
            self.guiConfig['ProjectBookmark']['currentCid'] = cid
            self.tools.writeConfFile(self.guiConfig)








