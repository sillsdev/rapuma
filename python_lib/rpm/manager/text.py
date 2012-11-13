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
from palaso.sfm import usfm, style, element, text


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
        if testForSetting(self.project.projConfig['CompTypes'][self.Ctype], 'sourcePath') :
            self.sourcePath   = self.project.projConfig['CompTypes'][self.Ctype]['sourcePath']
            if self.sourcePath :
                self.sourcePath = resolvePath(self.sourcePath)
        else :
            self.sourcePath = ''

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
            sourcePath = self.project.projConfig['CompTypes'][self.Ctype]['sourcePath']
            ptSet = getPTSettings(sourcePath)
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

#        import pdb; pdb.set_trace()

        # Check to see if settings need updating
        self.updateManagerSettings()
        # Check if there is a font installed
        self.project.createManager(self.cType, 'font')
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
        self.project.createManager(self.cType, 'style')
        projStyName = self.project.projConfig['Managers'][self.cType + '_Style']['mainStyleFile']
        if projStyName == '' :
            self.project.managers[self.cType + '_Style'].addStyleFile('main', '', force)
            projStyName = self.project.projConfig['Managers'][self.cType + '_Style']['mainStyleFile']
        # If for some reason the name isn't there yet, assign the default
        # name for a USFM style file
        if not projStyName :
            projStyName = 'usfm.sty'
        projSty = os.path.join(self.project.local.projStylesFolder, projStyName)
        if not os.path.isfile(projSty) :
            # Forcing style file creation possible if -f was used for component creation
            self.project.managers[self.cType + '_Style'].addStyleFile('main', '', force)

        # Start the process by building paths and file names, if we made it this far.
        # Note the file name for the preprocess is hard coded. This will become a part
        # of the total system and this file will be copied in when the user requests to
        # preprocessing.
        
        # Current assuption is that source text is located in a directory above the
        # that is the default. In case that is not the case, we can override that and
        # specify a path to the source. If that exists, then we will use that instead.
        if self.sourcePath :
            source      = os.path.join(self.sourcePath, thisFile)
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
                    # If the text is there, we should return True so do a last check to see
                    if os.path.isfile(target) :
                        self.project.log.writeToLog('TEXT-060', [cid])
                        return True
                else :
                    self.project.log.writeToLog('TEXT-070', [source,fName(target)])
                    return False



    def usfmCopy (self, source, target, projSty = None, errLevel = sfm.level.Content) :
        '''Use the Palaso USFM parser to bring in the text and clean it up if 
        needed. If projSty (path + file name) is not used, the sfm parser
        will use a default style file to drive the process which may lead to
        undesirable results. A style file should normally be used to avoid this.
        
        The sfm.pprint() is not being used at this point because of a bug that
        takes out \ft markers in footnotes. When this is fix, we might use this
        function again. For now, we will just use the sfm parser to validate the
        text that is being copied into a project.'''

        # For future reference, the sfm parser will fail if TeX style
        # comment markers "%" are used to comment text rather than "#".

# FIXME: Validation does not work right now, usfmTextFileIsValid() defaults to True

        # Validate the text first thing
        if not self.usfmTextFileIsValid(source, projSty) :
            self.project.log.writeToLog('TEXT-155', [source])
            return False

        # We may want to expand the validation and cleaning of incoming
        # text but for now, we will just open the target and normalize
        # it 
        contents = codecs.open(source, 'rt', 'utf_8_sig')
        lines = contents.read()
        normal = unicodedata.normalize(self.unicodeNormalForm, lines)
        self.project.log.writeToLog('TEXT-100', [self.unicodeNormalForm])
        writeout = codecs.open(target, "wt", "utf_8_sig")
        writeout.write(normal)
        writeout.close

        return True

# FIXME: Preserve the following if we decide to use the sfm parser
#        fh = codecs.open(source, 'rt', 'utf_8_sig')
#        # Create the object
#        if projSty :
#            stylesheet = usfm.default_stylesheet.copy()
#            stylesheet_extra = style.parse(open(os.path.expanduser(projSty),'r'))
#            stylesheet.update(stylesheet_extra)
#            doc = usfm.parser(fh, stylesheet, error_level=errLevel)
#            self.project.log.writeToLog('TEXT-080', [fName(projSty)])
#        else :
#            doc = usfm.parser(fh, error_level=errLevel)


    def testCompTextFile (self, source, projSty = None) :
        '''This will direct a request to the proper validater for
        testing the source of a component text file.'''

        if self.cType == 'usfm' :
            # Note: Error level reporting is possible with the usfm.parser.
            # The following are the errors it can report:
            # Note            = -1    Just give output warning, do not stop
            # Marker          =  0    Stop on any out of place marker
            # Content         =  1    Stop on mal-formed content
            # Structure       =  2    Stop on ???
            # Unrecoverable   =  100  Stop on most anything that is wrong'''
            if self.usfmTextFileIsValid(source, projSty) :
                self.project.log.writeToLog('TEXT-150', [source])
                return True
            else :
                # If it is not valid we want to report errors found
                fh = codecs.open(source, 'rt', 'utf_8_sig')
                stylesheet = usfm.default_stylesheet.copy()
                if projSty :
                    stylesheet_extra = style.parse(open(os.path.expanduser(projSty),'r'))
                    stylesheet.update(stylesheet_extra)
                doc = usfm.parser(fh, stylesheet, sfm.level.Content)

# FIXME: This does not work yet.

                self.project.log.writeToLog('TEXT-155', [source])
                return False
        else :
            self.project.log.writeToLog('TEXT-005', [self.cType])
            dieNow()


    def usfmTextFileIsValid (self, source, projSty) :
        '''Use the USFM parser to validate a style file. This is meant to
        be just a simple test so only return True or False.'''

# FIXME: Inserted over-ride, this does not work now
        return True

        try :
            fh = codecs.open(source, 'rt', 'utf_8_sig')
            stylesheet = usfm.default_stylesheet.copy()
            if projSty :
                stylesheet_extra = style.parse(open(os.path.expanduser(projSty),'r'))
                stylesheet.update(stylesheet_extra)
            doc = usfm.parser(fh, stylesheet, sfm.level.Structure)

            return True
        except Exception as e :
            return False



