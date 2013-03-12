#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project text tasks.

# History:
# 20120121 - djd - Started with intial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, codecs, re
#from configobj import ConfigObj, Section

# Load the local classes
from rapuma.core.tools import *
from rapuma.project.manager import Manager
from rapuma.group.usfm import PT_Tools


###############################################################################
################################## Begin Class ################################
###############################################################################

class Text (Manager) :

    # Shared values
    xmlConfFile     = 'text.xml'

    def __init__(self, project, cfg, cType) :
        '''Do the primary initialization for this manager.'''

        super(Text, self).__init__(project, cfg)

        # Set values for this manager
        self.pt_tools               = PT_Tools(project)
        self.project                = project
        self.cfg                    = cfg
        self.cType                  = cType
        self.Ctype                  = cType.capitalize()
        self.manager                = self.cType + '_Text'
        self.managers               = project.managers
        self.rapumaXmlTextConfig    = os.path.join(self.project.local.rapumaConfigFolder, self.xmlConfFile)
        self.sourceEditor           = self.pt_tools.getSourceEditor()
        self.setSourceEditor(self.sourceEditor)

        # Get persistant values from the config if there are any
        manager = self.cType + '_Text'
        newSectionSettings = getPersistantSettings(self.project.projConfig['Managers'][manager], self.rapumaXmlTextConfig)
        if newSectionSettings != self.project.projConfig['Managers'][manager] :
            self.project.projConfig['Managers'][manager] = newSectionSettings
            writeConfFile(self.project.projConfig)

        self.compSettings = self.project.projConfig['Managers'][manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)


###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def setSourceEditor (self, editor) :
        '''Set the source editor for the cType. It assumes the editor is valid.
        This cannot fail.'''

        se = ''
        if testForSetting(self.project.projConfig['CompTypes'][self.Ctype], 'sourceEditor') :
            se = self.project.projConfig['CompTypes'][self.Ctype]['sourceEditor']

        if se != editor :
            self.project.projConfig['CompTypes'][self.Ctype]['sourceEditor'] = editor
            writeConfFile(self.project.projConfig)


    def updateManagerSettings (self, gid) :
        '''Update the settings for this manager if needed.'''

        # If the source editor is PT, then a lot of information can be
        # gleaned from the .ssf file. Otherwise we will go pretty much with
        # the defaults and hope for the best.
        if self.sourceEditor.lower() == 'paratext' :
            # Do a compare on the settings
            ptSet = self.pt_tools.getPTSettings(gid)
            oldCompSet = self.compSettings.dict()
            # Don't overwrite manager settings (default sets reset to False) if
            # there already is a setting present on the nameFormID.
            if self.project.projConfig['Managers'][self.cType + '_Text']['nameFormID'] :
                newCompSet = self.pt_tools.mapPTTextSettings(self.compSettings.dict(), ptSet)
            else :
                newCompSet = self.pt_tools.mapPTTextSettings(self.compSettings.dict(), ptSet, True)

            if not newCompSet == oldCompSet :
                self.compSettings.merge(newCompSet)
                writeConfFile(self.project.projConfig)
                # Be sure to update the current session settings
                for k, v in self.compSettings.iteritems() :
                    setattr(self, k, v)
        # A generic editor means we really do not know where the text came
        # from. In that case, we just do the best we can.
        elif self.sourceEditor.lower() == 'generic' :
            if not self.project.projConfig['Managers'][self.cType + '_Text']['nameFormID'] or \
                not self.project.projConfig['Managers'][self.cType + '_Text']['postPart'] :
                self.project.projConfig['Managers'][self.cType + '_Text']['nameFormID'] = 'USFM'
                self.project.projConfig['Managers'][self.cType + '_Text']['postPart'] = 'usfm'

                writeConfFile(self.project.projConfig)
        else :
            self.project.log.writeToLog('TEXT-010', [self.sourceEditor])
            dieNow()

        return True


    def installWorkingText (self, cName, cid, force = False) :
        '''Call on the component type text install function.'''

        # Check to see if text manager settings need updating
        self.updateManagerSettings()

        if self.cType == 'usfm' :
            self.project.components[cName].installUsfmWorkingText(cName, cid, force)
        else :
            self.project.log.writeToLog('TEXT-005', [self.cType])


    def testCompTextFile (self, source, projSty = None) :
        '''This will direct a request to the proper validater for
        testing the source of a component text file.'''

        if self.cType == 'usfm' :
            # If this fails it will die at the validation process
            if self.project.components[cName].usfmTextFileIsValid(source, projSty) :
                self.project.log.writeToLog('TEXT-150', [source])
                return True
        else :
            self.project.log.writeToLog('TEXT-005', [self.cType])
            dieNow()


    def decodeText (self, fileName) :
        '''In case an encoding conversion is needed. This function will try
        to do that and if it fails, it should return a meaningful error msg.'''

        # First, test so see if we can even read the file
        try:
            fileObj = open(fileName, 'r').read()
        except Exception as e :
            terminal('decodeText() failed with the following error: ' + str(e))
            dieNow()
        # Now try to run the decode() function
        try:
            return fileObj.decode(self.sourceEncode)

        except Exception:
            terminal('decodeText() could not decode: [' + fileName + ']\n')
            dieNow()



