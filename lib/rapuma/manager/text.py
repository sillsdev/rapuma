#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project text tasks.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, codecs, re, subprocess

# Load the local classes
from rapuma.core.tools              import Tools
from rapuma.manager.manager         import Manager
from rapuma.core.paratext           import Paratext


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
        self.gid                    = project.gid
        self.pid                    = project.projectIDCode
        self.tools                  = Tools()
        self.pt_tools               = Paratext(project.projectIDCode, project.gid)
        self.project                = project
        self.projConfig             = project.projConfig
        self.cfg                    = cfg
        self.cType                  = cType
        self.Ctype                  = cType.capitalize()
        self.csid                   = project.projConfig['Groups'][self.gid]['csid']
        self.log                    = project.log
        self.manager                = self.cType + '_Text'
        self.managers               = project.managers
        self.rapumaXmlTextConfig    = os.path.join(self.project.local.rapumaConfigFolder, self.xmlConfFile)

#        import pdb; pdb.set_trace()

        # Get persistant values from the config if there are any
        newSectionSettings = self.tools.getPersistantSettings(self.project.projConfig['Managers'][self.manager], self.rapumaXmlTextConfig)
        if newSectionSettings != self.project.projConfig['Managers'][self.manager] :
            self.project.projConfig['Managers'][self.manager] = newSectionSettings
            self.tools.writeConfFile(self.project.projConfig)

        self.compSettings = self.project.projConfig['Managers'][self.manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)

        # Log messages for this module
        self.errorCodes     = {

            'TEXT-000' : ['MSG', 'Text module messages'],
            'TEXT-005' : ['ERR', 'Component type [<<1>>] is not supported by the text manager.'],
            'TEXT-015' : ['MSG', 'TEXT-015 - Unassigned error message ID.'],
            'TEXT-030' : ['LOG', 'Copied [<<1>>] to [<<2>>] in project.'],
            'TEXT-040' : ['WRN', 'The [<<1>>] component is locked. It must be unlocked before any modifications can be made.'],
            'TEXT-050' : ['LOG', 'Working text file for [<<1>>] has been completed.'],
            'TEXT-055' : ['ERR', 'TEXT-055 - Unassigned error message ID.'],
            'TEXT-080' : ['LOG', 'Validating text using the [<<1>>] style file.'],
            'TEXT-150' : ['MSG', 'USFM file: [<<1>>] is valid.'],
            'TEXT-160' : ['ERR', 'Unable to complete working text installation for [<<1>>]. May require \"force\" (-f).'],

            '0000' : ['MSG', 'Placeholder message'],

        }

###############################################################################
############################ Project Level Functions ##########################
###############################################################################


#    def setSourceEditor (self, editor) :
#        '''Set the source editor for the cType. It assumes the editor is valid.
#        This cannot fail.'''

#        se = ''
#        if self.project.projConfig['CompTypes'][self.Ctype].has_key('sourceEditor') :
#            se = self.project.projConfig['CompTypes'][self.Ctype]['sourceEditor']

#        if se != editor :
#            self.project.projConfig['CompTypes'][self.Ctype]['sourceEditor'] = editor
#            self.tools.writeConfFile(self.project.projConfig)


    def updateManagerSettings (self, gid) :
        '''Update the settings for this manager if needed.'''

#        import pdb; pdb.set_trace()

        sourceEditor = self.pt_tools.getSourceEditor()

        # If the source editor is PT, then a lot of information can be
        # gleaned from the .ssf file. Otherwise we will go pretty much with
        # the defaults and hope for the best.
        if sourceEditor.lower() == 'paratext' :
            # Do a compare on the settings
            ptSet = self.pt_tools.getPTSettings()
            oldCompSet = self.compSettings.dict()
            # Don't overwrite manager settings (default sets reset to False) if
            # there already is a setting present on the nameFormID.
            if self.project.projConfig['Managers'][self.cType + '_Text']['nameFormID'] :
                newCompSet = self.pt_tools.mapPTTextSettings(self.compSettings.dict(), ptSet)
            else :
                newCompSet = self.pt_tools.mapPTTextSettings(self.compSettings.dict(), ptSet, True)

            if not newCompSet == oldCompSet :
                self.compSettings.merge(newCompSet)
                self.tools.writeConfFile(self.project.projConfig)
                # Be sure to update the current session settings
                for k, v in self.compSettings.iteritems() :
                    setattr(self, k, v)
        # A generic editor means we really do not know where the text came
        # from. In that case, we just do the best we can.
        elif sourceEditor.lower() == 'generic' :
            if not self.project.projConfig['Managers'][self.cType + '_Text']['nameFormID'] or \
                not self.project.projConfig['Managers'][self.cType + '_Text']['postPart'] :
                self.project.projConfig['Managers'][self.cType + '_Text']['nameFormID'] = 'USFM'
                self.project.projConfig['Managers'][self.cType + '_Text']['postPart'] = 'usfm'

                self.tools.writeConfFile(self.project.projConfig)
        else :
            self.project.log.writeToLog('TEXT-010', [sourceEditor])
            self.tools.dieNow()

        return True


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
            self.tools.dieNow()


