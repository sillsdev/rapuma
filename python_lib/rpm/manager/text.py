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
        self.axSourcePath       = self.project.projConfig['CompTypes'][self.Ctype]['axillarySourcePath']
        if self.axSourcePath and self.axSourcePath != 'None' :
            self.axSourcePath = resolvePath(self.axSourcePath)
        else :
            self.axSourcePath = None

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
            # Do a compare on the settings
            ptSet = getPTSettings(self.project.local.projHome)
            oldCompSet = self.compSettings.dict()
            # Don't overwrite manager settings (default sets reset to False) if
            # there already is a setting present on the nameFormID.
            if self.project.projConfig['Managers']['usfm_Text']['nameFormID'] :
                newCompSet = mapPTTextSettings(self.compSettings.dict(), ptSet)
            else :
                newCompSet = mapPTTextSettings(self.compSettings.dict(), ptSet, True)

            if not newCompSet == oldCompSet :
                self.compSettings.merge(newCompSet)
                writeConfFile(self.project.projConfig)
                # Be sure to update the current session settings
                for k, v in self.compSettings.iteritems() :
                    setattr(self, k, v)
        else :
            self.project.log.writeToLog('TEXT-010', [sourceEditor])
            dieNow()

        return True


    def installUsfmWorkingText (self, cid, force = False) :
        '''Find the USFM source text and install it into the working text
        folder of the project with the proper name.'''

        def copyAndClean (source, target) :
            # Use the Palaso USFM parser to bring in the text and
            # clean it up if needed
            fh = codecs.open(source, 'r', 'utf_8_sig')
            doc = usfm.parser(fh)
            tidy = sfm.pprint(doc)
            writeout = codecs.open(target, "w", "utf-8")
            writeout.write(tidy)
            writeout.close
            self.project.log.writeToLog('TEXT-030', [fName(source), fName(target)])

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
                self.project.log.writeToLog('TEXT-020')
            else :
                self.project.log.writeToLog('TEXT-025', [self.nameFormID])

            # Both of the above are bad news so we need to take down the system now
            dieNow()

        # Start the process by building paths and file names, if we made it this far.
        # Note the file name for the preprocess is hard coded. This will become a part
        # of the total system and this file will be copied in when the user requests to
        # preprocessing.
        
        # Current assuption is that source text is located in a directory above the
        # that is the default. In case that is not the case, we can override that and
        # specify a path to the source. If that exists, then we will use that instead.
        if self.axSourcePath :
            source      = os.path.join(self.axSourcePath, thisFile)
        else :
            source      = os.path.join(os.path.dirname(self.project.local.projHome), thisFile)

        targetFolder    = os.path.join(self.project.local.projProcessFolder, cid)
        target          = os.path.join(targetFolder, cid + '.usfm')
        compLock        = os.path.join(targetFolder, '.lock')
        typeLock        = os.path.join(os.path.dirname(targetFolder), '.' + self.cType + '-lock')
        preprocess     = os.path.join(self.project.local.projProcessFolder, self.cType + '-preprocess.py')

        # Copy the source to the working text folder. We do not want to do
        # this if the there already is a target and it is newer than the 
        # source text, that would indicate some edits have been done and we
        # do not want to loose the work. However, if it is older that would
        # indicate the source has been updated so unless the folder is locked
        # we will want to update the target.
        
#        import pdb; pdb.set_trace()

        # First check for a general lock on all components of this type.
        if os.path.isfile(typeLock) :
            self.project.log.writeToLog('TEXT-040', [self.cType])
            return False

        # Now look for a lock on this specific component
        if os.path.isfile(compLock) :
            self.project.log.writeToLog('TEXT-045', [cid])
            return False

        # Look for the source now
        if not os.path.isfile(source) :
            self.project.log.writeToLog('TEXT-035', [source])
            return False

        # Make target folder if needed
        if not os.path.isdir(targetFolder) :
            os.makedirs(targetFolder)

        # Now do the age checks and copy if source is newer than target
        if not isOlder(target, source) or force :
            if not os.path.isfile(target) or force :
                copyAndClean(source, target)
                return True

        # If the text is there, we should return True so do a last check to see
        if os.path.isfile(target) :
            return True


