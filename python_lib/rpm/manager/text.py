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

import os, shutil
from configobj import ConfigObj, Section

# Load the local classes
from tools import *
from pt_tools import *
from manager import Manager


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
        self.project            = project
        self.cfg                = cfg
        self.cType              = cType
        self.Ctype              = cType.capitalize()
        self.rpmXmlTextConfig   = os.path.join(self.project.local.rpmConfigFolder, self.xmlConfFile)

        # Get persistant values from the config if there are any
        manager = self.cType + '_Text'
        newSectionSettings = getPersistantSettings(self.project.projConfig['Managers'][manager], self.rpmXmlTextConfig)
        if newSectionSettings != self.project.projConfig['Managers'][manager] :
            self.project.projConfig['Managers'][manager] = newSectionSettings

        self.compSettings = self.project.projConfig['Managers'][manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)


###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def installUsfmWorkingText (self, cid) :
        '''Find the USFM source text and installs it into the working text
        folder of the project with the proper name.'''

        # Check to see what the source editor is and adjust settings if needed
        sourceEditor = self.project.projConfig['CompTypes']['Usfm']['sourceEditor']
        if sourceEditor.lower() == 'paratext' :
            ptSet = getPTSettings(self.project.local.projHome)
            # In this situation we don't want to make any changes to exsiting
            # settings so the reset is set to False
            oldCompSet = self.compSettings.dict()
            newCompSet = mapPTTextSettings(self.compSettings.dict(), ptSet, False)
            if not newCompSet == oldCompSet :
                self.compSettings.merge(newCompSet)
                writeConfFile(self.project.projConfig)
        else :
            writeToLog(self.project, 'ERR', 'Source file editor [' + sourceEditor + '] is not recognized by this system. Please double check the name used for the source text editor setting.')
            dieNow()

        compNum     = '00'
        if self.nameFormID == '41MAT' :
        
# FIXME: Start here - Build the source main file name part in a consistant/intelligent way

            compNum = getUsfmCidInfo(cid)[1]

            if self.prePart :
                thisFile = self.prePart + compNum + cid.upper() + self.postPart
            else :
                thisFile = compNum + cid.upper() + postPart
        else :
            if not self.nameFormID :
                writeToLog(self.project, 'ERR', 'Source file name could not be built because the Name Form ID is missing. Double check to see which editor created the source text.')
            else :
                writeToLog(self.project, 'ERR', 'Source file name could not be built because the Name Form ID [' + self.nameFormID + '] is not recognized by this system. Please contact the system developer about this problem.')

            # Both of the above are bad news so we need to take down the system now
            dieNow()

        # Make target folder if needed
        targetFolder = os.path.join(self.project.local.projProcessFolder, cid)
        if not os.path.isdir(targetFolder) :
            os.makedirs(targetFolder)

        source = os.path.join(os.path.dirname(self.project.local.projHome), thisFile)
        print source
        target = os.path.join(targetFolder, cid + '.usfm')

        # Copy the source to the working text folder
        # FIXME: At some point dependency checking might need to be done
        if not os.path.isfile(target) :
            if os.path.isfile(source) :
            
# Here we want to use the usfm parser to do the copy opperation.
                shutil.copy(source, target)
                writeToLog(self.project, 'LOG', 'Copied [' + fName(source) + '] to [' + fName(target) + '] in project.')
            else :
                writeToLog(self.project, 'LOG', 'Source file: [' + source + '] not found! Cannot copy to project.')





