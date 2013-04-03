#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project tasks.

# History:
# 20111207 - djd - Started with intial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, warnings

# Load the local classes
from rapuma.core.tools      import *
from rapuma.core.paratext   import Paratext
from rapuma.core.proj_setup import ProjSetup
from rapuma.project.manager import Manager


###############################################################################
################################## Begin Class ################################
###############################################################################

class Style (Manager) :

    def __init__(self, project, cfg, cType) :
        '''Do the primary initialization for this manager.'''

        super(Style, self).__init__(project, cfg)

        # Set values for this manager
        self.pt_tools               = Paratext(project.projectIDCode)
        self.setup                  = ProjSetup(project.projectIDCode)
        self.project                = project
        self.local                  = project.local
        self.cfg                    = cfg
        self.cType                  = cType
        self.Ctype                  = cType.capitalize()
        self.gid                    = project.gid
        manager                     = self.cType + '_Style'
        self.rapumaXmlStyleConfig   = os.path.join(self.local.rapumaConfigFolder, 'style.xml')
        # Config objects we need
        self.projConfig             = project.projConfig
        self.userConfig             = project.userConfig
        # Get persistant values from the config if there are any
        newSectionSettings = getPersistantSettings(self.projConfig['Managers'][manager], self.rapumaXmlStyleConfig)
        if newSectionSettings != self.projConfig['Managers'][manager] :
            self.projConfig['Managers'][manager] = newSectionSettings
        self.compSettings = self.projConfig['Managers'][manager]
        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)
        # Misc settings
        self.renderer               = self.projConfig['CompTypes'][self.Ctype]['renderer']
        self.sourceEditor           = self.projConfig['CompTypes'][self.Ctype]['sourceEditor']
        # File names
        self.defaultStyFileName     = self.projConfig['Managers'][manager]['defaultStyFile']
        self.defaultExtStyFileName  = self.projConfig['Managers'][manager]['defaultExtStyFile']
        self.grpExtStyFileName      = self.projConfig['Managers'][manager]['grpExtStyFile']
        # Folder paths
        self.projComponentsFolder   = self.local.projComponentsFolder
        self.gidFolder              = os.path.join(self.projComponentsFolder, self.gid)
        self.projStylesFolder       = self.local.projStylesFolder
        self.rapumaStyFolder        = self.local.rapumaStylesFolder
        self.rapumaCmpStyFolder     = os.path.join(self.rapumaStyFolder, self.cType)
        # Files with paths
        self.defaultStyFile         = os.path.join(self.projStylesFolder, self.defaultStyFileName)
        self.defaultExtStyFile      = os.path.join(self.projStylesFolder, self.defaultExtStyFileName)
        self.grpExtStyFile          = os.path.join(self.gidFolder, self.grpExtStyFileName)
        self.usrDefaultExtStyFile   = os.path.join(self.project.userConfig['Resources']['styles'], self.defaultExtStyFileName)

        # Log messages for this module
        self.errorCodes     = {
            'STYL-000' : ['MSG', 'Style module messages'],
            'STYL-005' : ['ERR', 'Component type [<<1>>] is not supported by the style manager.'],
            'STYL-007' : ['ERR', 'The [<<1>>] component type source text editor [<<2>>] is not supported by the style manager.'],
            'STYL-010' : ['MSG', 'The style file [<<1>>] was set as the [<<2>>] style file for the [<<3>>] component type.'],
            'STYL-020' : ['ERR', 'Style file: [<<1>>] was not found. Operation failed.'],
            'STYL-030' : ['WRN', 'Style file: [<<1>>] already exsits. Use (-f) force to replace it.'],
            'STYL-060' : ['LOG', 'The file [<<1>>] was validated and copied to the project styles folder.'],
            'STYL-065' : ['LOG', 'The file [<<1>>] was copied to the project styles folder.'],
            'STYL-070' : ['ERR', 'Style file: [<<1>>] is not valid. Copy operation failed!'],
            'STYL-075' : ['LOG', 'Style file: [<<1>>] is not valid. Will attempt to find a valid one from another source.'],
            'STYL-090' : ['LOG', 'Style file: [<<1>>] was not found.'],
            'STYL-100' : ['LOG', 'No style file setting was found for the [<<1>>] component type. Nothing has been done.'],
            'STYL-110' : ['MSG', 'Force switch was set (-f). Style file: [<<1>>] was removed from the project and references removed from the [<<2>>] settings.'],
            'STYL-120' : ['MSG', 'Style file: [<<1>>] was removed from the [<<2>>] settings.'],
            'STYL-150' : ['MSG', 'Style file: [<<1>>] is valid.'],
            'STYL-155' : ['ERR', 'Style file: [<<1>>] did NOT pass the validation test.'],

            '0010' : ['ERR', 'Style file [<<1>>] could not be created.'],

        }


###############################################################################
########################## External Manager Functions #########################
###############################################################################



    def checkDefaultStyFile (self) :
        '''Check for the exsistance of the Global Sty file. Make it if it
        is not there.'''

        if not os.path.exists(self.defaultStyFile) :
            if not self.setup.makeDefaultStyFile(self.gid) :
                self.project.log.writeToLog(self.errorCodes['0010'], [fName(self.defaultStyFile)], 'style.checkDefaultStyFile():0010')
                return False
        else :
            return True


    def checkDefaultExtStyFile (self) :
        '''Check for the exsistance of the component extention Sty file. We need
        to throw a stern warning if it is not there and create a blank one.'''

        if not os.path.isfile(self.defaultExtStyFile) :
            if not self.setup.makeDefaultExtStyFile(self.gid) :
                self.project.log.writeToLog(self.errorCodes['0010'], [fName(self.defaultExtStyFile)], 'style.checkDefaultExtStyFile():0010')
                return False
        else :
            return True


    def checkGrpExtStyFile (self) :
        '''Check for the exsistance of the group extention Sty file. We need
        to throw a stern warning if it is not there and create a blank one.'''

        if not os.path.isfile(self.grpExtStyFile) :
            if not self.setup.makeGrpExtStyFile(self.gid) :
                self.project.log.writeToLog(self.errorCodes['0010'], [fName(self.grpExtStyFile)], 'style.checkGrpExtStyFile():0010')
                return False
        else :
            return True



