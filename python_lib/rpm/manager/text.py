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

import os, shutil, codecs, unicodedata
from configobj import ConfigObj, Section

# Load the local classes
from tools import *
from pt_tools import *
from manager import Manager
import palaso.sfm as sfm
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
        if testForSetting(self.project.projConfig['CompTypes'][self.Ctype], 'altSourcePath') :
            self.altSourcePath   = self.project.projConfig['CompTypes'][self.Ctype]['altSourcePath']
            if self.altSourcePath :
                self.altSourcePath = resolvePath(self.altSourcePath)
        else :
            self.altSourcePath = ''

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
            ptSet = getPTSettings(self.project.local.projHome, self.altSourcePath)
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

        # Check to see if settings need updating
        self.updateManagerSettings()
        # Check if there is a font installed
        
        
# FIXME: How do you work with ptDefaultFont when it isn't there?
        
#        import pdb; pdb.set_trace()
        
        if not self.project.managers[self.cType + '_Font'].varifyFont() :
            font = self.project.projConfig['Managers'][self.cType + '_Font']['ptDefaultFont']
            self.project.managers[self.cType + '_Font'].installFont(font)

        thisFile = formPTName(self.project.projConfig, cid)
        # Test, no name = no success
        if not thisFile :
            self.project.log.writeToLog('TEXT-020')
            dieNow()

        # Will need the stylesheet for copy if that has not been added
        # to the project yet, we will do that now
        projStyName = self.project.projConfig['Managers'][self.cType + '_Style']['mainStyleFile']
        # If for some reason the name isn't there yet, assign the default name for a USFM style file
        if not projStyName :
            projStyName = 'usfm.sty'
        projSty = os.path.join(self.project.local.projStylesFolder, projStyName)
        if not os.path.isfile(projSty) :
            # Forcing style file creation possible if -f was used for component creation
            self.project.managers[self.cType + '_Style'].addStyleFile('', force)

        # Start the process by building paths and file names, if we made it this far.
        # Note the file name for the preprocess is hard coded. This will become a part
        # of the total system and this file will be copied in when the user requests to
        # preprocessing.
        
        # Current assuption is that source text is located in a directory above the
        # that is the default. In case that is not the case, we can override that and
        # specify a path to the source. If that exists, then we will use that instead.
        if self.altSourcePath :
            source      = os.path.join(self.altSourcePath, thisFile)
        else :
            source      = os.path.join(os.path.dirname(self.project.local.projHome), thisFile)

        targetFolder    = os.path.join(self.project.local.projComponentsFolder, cid)
        target          = os.path.join(targetFolder, cid + '.' + self.cType)

        # Copy the source to the working text folder. We do not want to do
        # this if the there already is a target and it is newer than the 
        # source text, that would indicate some edits have been done and we
        # do not want to loose the work. However, if it is older that would
        # indicate the source has been updated so unless the folder is locked
        # we will want to update the target.
        

# FIXME: The locking needs to be reimplemented
#        # First check for a general lock on all components of this type.
#        if os.path.isfile(typeLock) :
#            self.project.log.writeToLog('TEXT-040', [self.cType])
#            return False

#        # Now look for a lock on this specific component
#        if os.path.isfile(compLock) :
#            self.project.log.writeToLog('TEXT-045', [cid])
#            return False

#        import pdb; pdb.set_trace()
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
                if self.usfmCopy(source, target, projSty) :
                    return True
                else :
                    self.project.log.writeToLog('TEXT-070', [source,fName(target)])
                    return False
#            else :
#                return True
#        else :
#            return True

        # If the text is there, we should return True so do a last check to see
        if os.path.isfile(target) :
            return True


    def usfmCopy (self, source, target, projSty = None, errLevel = sfm.level.Content) :
        '''Use the Palaso USFM parser to bring in the text and clean it up if 
        needed. If projSty (path + file name) is not used, the sfm parser
        will use a default style file to drive the process which may lead to
        undesirable results. A style file should normally be used to avoid this.
        
        Error level reporting is possible with the usfm.parser. The following
        are the error it can report:
        Note            = -1    Just give output warning, do not stop
        Marker          =  0    Stop on any out of place marker
        Content         =  1    Stop on mal-formed content
        Structure       =  2    Stop on ???
        Unrecoverable   =  100  Stop on most anything that is wrong
        
        The default is Content. To change this the calling function must pass
        another level like "sfm.level.Note" or one of the other levels.'''

        # Load in the source text
        fh = codecs.open(source, 'rt', 'utf_8_sig')
        # Create the object
        if projSty :
            stylesheet = usfm.default_stylesheet.copy()
            stylesheet_extra = style.parse(open(os.path.expanduser(projSty),'r'))
            stylesheet.update(stylesheet_extra)
            doc = usfm.parser(fh, stylesheet, error_level=errLevel)
            self.project.log.writeToLog('TEXT-080', [fName(projSty)])
        else :
            doc = usfm.parser(fh, error_level=errLevel)

        # Check/Clean up the text
        tidy = sfm.pprint(doc)
        self.project.log.writeToLog('TEXT-090')

        # Normalize the text according to the usfm_Text config setting 
        normal = unicodedata.normalize(self.unicodeNormalForm, tidy)
        self.project.log.writeToLog('TEXT-100', [self.unicodeNormalForm])

        # Write to the target
        writeout = codecs.open(target, "wt", "utf_8_sig")
        writeout.write(normal)
        writeout.close
        return True

