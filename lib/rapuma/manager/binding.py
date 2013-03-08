#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle binding component groups in book projects.

# Created: Fri Mar 08 10:34:34 2013 

###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, codecs, re, subprocess
from configobj import ConfigObj, Section

# Load the local classes
from rapuma.core.tools import *
from rapuma.project.manager import Manager


###############################################################################
################################## Begin Class ################################
###############################################################################

class Binding (Manager) :

    # Shared values
    xmlConfFile     = 'binding.xml'

    def __init__(self, project, cfg, cType) :
        '''Do the primary initialization for this manager.'''

        super(Binding, self).__init__(project, cfg)

        # Set values for this manager
        self.project                = project
        self.projConfig             = project.projConfig
        self.local                  = project.local
        self.cfg                    = cfg
        self.cType                  = cType
        self.Ctype                  = cType.capitalize()
        self.mType                  = self.project.projectMediaIDCode
        self.manager                = self.mType + '_Binding'
        self.managers               = project.managers
        self.rapumaXmlBindConfig    = os.path.join(self.local.rapumaConfigFolder, self.xmlConfFile)
        self.projComponentsFolder   = self.local.projComponentsFolder

        # Get persistant values from the config if there are any
        manager = self.mType + '_Binding'
        newSectionSettings = getPersistantSettings(self.projConfig['Managers'][manager], self.rapumaXmlBindConfig)
        if newSectionSettings != self.projConfig['Managers'][manager] :
            self.projConfig['Managers'][manager] = newSectionSettings
            writeConfFile(self.projConfig)

        self.compSettings = self.projConfig['Managers'][manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)


###############################################################################
############################ Project Level Functions ##########################
###############################################################################

    def addBindingGroup (self, bgID, cgIDs, force = False) :
        '''Add a binding group to the project.'''

        if force and testForSetting(self.projConfig['Components'], bgID) :
            del self.projConfig['Components'][bgID]

        try :
            # Add the info to the components section
            buildConfSection(self.projConfig, 'Components')
            if not testForSetting(self.projConfig['Components'], bgID) :
                buildConfSection(self.projConfig['Components'], bgID)
                self.projConfig['Components'][bgID]['type'] = self.mType
                self.projConfig['Components'][bgID]['cidList'] = cgIDs.split()
                writeConfFile(self.projConfig)
                self.project.log.writeToLog('BIND-010', [bgID])
            else :
                self.project.log.writeToLog('BIND-012', [bgID])
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.project.log.writeToLog('BIND-015', [bgID,str(e)])
            dieNow()


    def removeBindingGroup (self, bgID) :
        '''Remove a binding group from the project config.'''

        if testForSetting(self.projConfig['Components'], bgID) :
            del self.projConfig['Components'][bgID]
            writeConfFile(self.projConfig)
            self.project.log.writeToLog('BIND-020', [bgID])
        else :
            self.project.log.writeToLog('BIND-025', [bgID])


    def bindComponents (self, bgID) :
        '''Bind a project binding group. Right now this is only working
        with pdftk.'''

        # Build the command
        confCommand = self.projConfig['Managers'][self.manager]['simpleBind']
        outputPath = os.path.join(self.projComponentsFolder, bgID)
        if not os.path.exists(outputPath) :
            os.makedirs(outputPath)
        # Append each of the input files
        for f in self.projConfig['Components'][bgID]['cidList'] :
            f = os.path.join(self.projComponentsFolder, f, f + '.pdf')
            confCommand.append(f)
        # Now the rest of the commands and output file
        confCommand.append('cat')
        confCommand.append('output')
        output = os.path.join(outputPath, bgID + '.pdf')
        confCommand.append(output)
        # Run the binding command
        rCode = subprocess.call(confCommand)
        # Analyse the return code
        if rCode == int(0) :
            self.project.log.writeToLog('BIND-030', [bgID])
        else :
            self.project.log.writeToLog('BIND-035', [bgID])
            dieNow()






