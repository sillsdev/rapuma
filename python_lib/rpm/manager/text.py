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
import palaso.sfm as sfm
#import palaso.sfm.usfm as usfm
from palaso.sfm import usfm, style, pprint, element, text


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

    def updateManagerSettings (self) :
        '''Update the settings for this manager if needed.'''

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
                # Be sure to update the current session settings
                for k, v in self.compSettings.iteritems() :
                    setattr(self, k, v)
        else :
            writeToLog(self.project, 'ERR', 'Source file editor [' + sourceEditor + '] is not recognized by this system. Please double check the name used for the source text editor setting.')
            dieNow()

        return True


    def installUsfmWorkingText (self, cid) :
        '''Find the USFM source text and installs it into the working text
        folder of the project with the proper name.'''

        # Check to see if settings need updating
        self.updateManagerSettings()
        if self.nameFormID == '41MAT' :
            mainName = getUsfmCidInfo(cid)[1] + cid.upper()
            if self.prePart and self.prePart != 'None' :
                thisFile = self.prePart + mainName + self.postPart
            else :
                thisFile = mainName + self.postPart
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
        target = os.path.join(targetFolder, cid + '.usfm')

        # Copy the source to the working text folder
        if not isOlder(target, source) :
            if not os.path.isfile(target) :
                if os.path.isfile(source) :
                    # Use the Palaso USFM parser to bring in the text and
                    # clean it up if needed
                    fh = codecs.open(source, 'r', 'utf_8_sig')
                    doc = usfm.parser(fh)
                    tidy = sfm.pprint(doc)
                    writeout = codecs.open(target, "w", "utf-8")
                    writeout.write(tidy)
                    writeout.close
                    # FIXME: Add a hook here for custom post processing here
                    # for things like encoding and word changes.
                    writeToLog(self.project, 'LOG', 'Copied [' + fName(source) + '] to [' + fName(target) + '] in project.')
                else :
                    writeToLog(self.project, 'LOG', 'Source file: [' + source + '] not found! Cannot copy to project.')





