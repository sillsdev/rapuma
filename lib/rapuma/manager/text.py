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
from functools import partial

# Load the local classes
from rapuma.core.tools import *
from rapuma.core.pt_tools import *
from rapuma.project.manager import Manager
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
        self.project                = project
        self.cfg                    = cfg
        self.cType                  = cType
        self.Ctype                  = cType.capitalize()
        self.manager                = self.cType + '_Text'
        self.managers               = project.managers
        self.rapumaXmlTextConfig    = os.path.join(self.project.local.rapumaConfigFolder, self.xmlConfFile)
        self.sourcePath             = getSourcePath(self.project.userConfig, self.project.projectIDCode, self.cType)
        self.sourceEditor           = getSourceEditor(self.project.projConfig, self.sourcePath, self.cType)
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


# REM: Changed getCompWorkingTextPath() -> usfm.getCidPath()
#    def getCompWorkingTextPath (self, cid) :
#        '''Return the full path of the cName working text file. This assumes
#        the cName is valid.'''

#        cName = getRapumaCName(cid)
#        cType = self.project.projConfig['Components'][cName]['type']
#        return os.path.join(self.project.local.projComponentsFolder, cName, cid + '.' + cType)


# REM: Changed getCompWorkingTextAdjPath() -> usfm.getCidAdjPath()
#    def getCompWorkingTextAdjPath (self, cid) :
#        '''Return the full path of the cName working text adjustments file. 
#        This assumes the cName is valid.'''

#        cName = getRapumaCName(cid)
#        cType = self.project.projConfig['Components'][cName]['type']
#        return os.path.join(self.project.local.projComponentsFolder, cName, cid + '.adj')

# REM: Changed getCompWorkingTextPiclistPath() -> usfm.getCidPiclistPath()
#    def  (self, cid) :
#        '''Return the full path of the cName working text illustrations file. 
#        This assumes the cName is valid.'''

#        cName = getRapumaCName(cid)
#        cType = self.project.projConfig['Components'][cName]['type']
#        return os.path.join(self.project.local.projComponentsFolder, cName, cid + '.piclist')


    def setSourceEditor (self, editor) :
        '''Set the source editor for the cType. It assumes the editor is valid.
        This cannot fail.'''

        se = ''
        if testForSetting(self.project.projConfig['CompTypes'][self.Ctype], 'sourceEditor') :
            se = self.project.projConfig['CompTypes'][self.Ctype]['sourceEditor']

        if se != editor :
            self.project.projConfig['CompTypes'][self.Ctype]['sourceEditor'] = editor
            writeConfFile(self.project.projConfig)


    def updateManagerSettings (self) :
        '''Update the settings for this manager if needed.'''

        # If the source editor is PT, then a lot of information can be
        # gleaned from the .ssf file. Otherwise we will go pretty much with
        # the defaults and hope for the best.
        if self.sourceEditor.lower() == 'paratext' :
            # Do a compare on the settings
            ptSet = getPTSettings(self.sourcePath)
            oldCompSet = self.compSettings.dict()
            # Don't overwrite manager settings (default sets reset to False) if
            # there already is a setting present on the nameFormID.
            if self.project.projConfig['Managers'][self.cType + '_Text']['nameFormID'] :
                newCompSet = mapPTTextSettings(self.compSettings.dict(), ptSet)
            else :
                newCompSet = mapPTTextSettings(self.compSettings.dict(), ptSet, True)

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


    def installUsfmWorkingText (self, cid, force = False) :
        '''Find the USFM source text and install it into the working text
        folder of the project with the proper name. If a USFM text file
        is not located in a PT project folder, the editor cannot be set
        to paratext, it must be set to generic. This assumes lock checking
        was done previous to the call.'''

#        import pdb; pdb.set_trace()

        # Get the rapuma component name, this assumes the cid is valid
        cName = getUsfmCidInfo(cid)[1]

        # Check to see if text manager settings need updating
        self.updateManagerSettings()

        # Check if there is a font installed
        self.project.createManager(self.cType, 'font')
        if not self.project.managers[self.cType + '_Font'].varifyFont() :
            # If a PT project, use that font, otherwise, install default
            if self.sourceEditor.lower() == 'paratext' :
                font = self.project.projConfig['Managers'][self.cType + '_Font']['ptDefaultFont']
            else :
                font = 'DefaultFont'

            self.project.managers[self.cType + '_Font'].installFont(font)

        # Build the file name
        thisFile = ''
        if self.sourceEditor.lower() == 'paratext' :
            thisFile = formPTName(self.project.projConfig, cid)
        elif self.sourceEditor.lower() == 'generic' :
            thisFile = formGenericName(self.project.projConfig, cid)
        else :
            self.project.log.writeToLog('TEXT-010', [self.sourceEditor])

        # Test, no name = no success
        if not thisFile :
            self.project.log.writeToLog('TEXT-020', [cid])
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

        targetFolder    = os.path.join(self.project.local.projComponentsFolder, cName)
        target          = os.path.join(targetFolder, cid + '.' + self.cType)
        targetSource    = os.path.join(targetFolder, thisFile + '.source')

        # Copy the source to the working text folder. We do not want to do
        # this if the there already is a target and it is newer than the 
        # source text, that would indicate some edits have been done and we
        # do not want to loose the work. However, if it is older that would
        # indicate the source has been updated so unless the folder is locked
        # we will want to update the target.

        # Look for the source now, if not found, fallback on the targetSource
        # backup file. But if that isn't there die.
        if not os.path.isfile(source) :
            if os.path.isfile(targetSource) :
                source = targetSource
            else :
                self.project.log.writeToLog('TEXT-035', [source])
                dieNow()

        # Now do the age checks and copy if source is newer than target
        if not isOlder(target, source) or force :
            if not os.path.isfile(target) or force :

                # Make target folder if needed
                if not os.path.isdir(targetFolder) :
                    os.makedirs(targetFolder)

                # Always save an untouched copy of the source and set to
                # read only. We may need this to restore/reset later.
                if os.path.isfile(targetSource) :
                    # Don't bother if we copied from it in the first place
                    if targetSource != source :
                        # Reset permissions to overwrite
                        makeWriteable(targetSource)
                        shutil.copy(source, targetSource)
                        makeReadOnly(targetSource)
                else :
                    shutil.copy(source, targetSource)
                    makeReadOnly(targetSource)

                # To be sure nothing happens, copy from our project source
                # backup file.
                if self.usfmCopy(targetSource, target, projSty) :

                    # Run any working text preprocesses on the new component text
                    scriptFileName = self.project.projConfig['CompTypes'][self.cType.capitalize()]['preprocessScript']
                    preProScript = os.path.join(self.project.local.projScriptsFolder, scriptFileName)
                    if os.path.isfile(preProScript) :
#                        import pdb; pdb.set_trace()
                        if self.project.isLocked(cName) :
                            self.project.lockUnlock(cName, False, True)
                        if not self.project.runProcessScript(cName, preProScript) :
                            self.project.log.writeToLog('COMP-130', [cName])
                        if not self.project.isLocked(cName) :
                            self.project.lockUnlock(cName, True, True)

                    # If this is a USFM component type we need to remove any \fig markers,
                    # and record in the illustration.conf file
                    if self.cType == 'usfm' :
                        tempFile = target + '.tmp'
                        contents = codecs.open(target, "rt", encoding="utf_8_sig").read()
                        # logFigure() logs the fig data and strips it from the working text
                        # Note: Using partial() to allows the passing of the cid param 
                        # into logFigure()
                        contents = re.sub(r'\\fig\s(.+?)\\fig\*', partial(self.logFigure, cid), contents)
                        codecs.open(tempFile, "wt", encoding="utf_8_sig").write(contents)
                        # Finish by copying the tempFile to the source
                        if not shutil.copy(tempFile, target) :
                            # Take out the trash
                            os.remove(tempFile)

                    # If the text is there, we should return True so do a last check to see
                    if os.path.isfile(target) :
                        self.project.log.writeToLog('TEXT-060', [cName])
                        return True
                else :
                    self.project.log.writeToLog('TEXT-070', [source,fName(target)])
                    return False
            else :
                return True
        else :
            return True


    def logFigure (self, cid, figConts) :
        '''Log the figure data in the illustration.conf.'''
        
        fig = figConts.group(1).split('|')
        figKeys = ['description', 'fileName', 'position', 'refRange', 'copyright', 'caption', 'location']
        figDict = {}

        # Add all the figure info to the dictionary
        c = 0
        for v in fig :
            figDict[figKeys[c]] = v
            c +=1

        # Add additional information, get rid of stuff we don't need
        figDict['illustrationID'] = figDict['fileName'].split('.')[0]
        figDict['bid'] = cid.upper()
        figDict['chapter'] = figDict['location'].split(':')[0]
        figDict['verse'] = figDict['location'].split(':')[1]

        del figDict['location']

        illustrationConfig = self.managers[self.cType + '_Illustration'].illustrationConfig
        # Put the dictionary info into the illustration conf file
        if not testForSetting(illustrationConfig, figDict['illustrationID'].upper()) :
            buildConfSection(illustrationConfig, figDict['illustrationID'].upper())
        for k in figDict.keys() :
#            illustrationConfig[figDict['illustrationID'].upper()][k] = figDict[k].encode('utf-8')








# FIXME: Had a problem with this, does not always seem to store in Unicode, then fails
#            illustrationConfig[figDict['illustrationID'].upper()][k] = figDict[k].encode('utf-8')

            # For testing ['description', 'copyright', 'caption']
            if k in ['caption'] :
                illustrationConfig[figDict['illustrationID'].upper()][k] = ''
            else :
                illustrationConfig[figDict['illustrationID'].upper()][k] = figDict[k].encode('utf-8')

        writeConfFile(illustrationConfig)


    def usfmCopy (self, source, target, projSty = None) :
        '''Copy USFM text from source to target. Decode if necessary, then
        normalize. With the text in place, validate unless that is False.'''

        # Bring in our source text
        if self.sourceEncode == self.workEncode :
            contents = codecs.open(source, 'rt', 'utf_8_sig')
            lines = contents.read()
        else :
            # Lets try to change the encoding.
            lines = self.decodeText(source)

        # Normalize the text
        normal = unicodedata.normalize(self.unicodeNormalForm, lines)
        self.project.log.writeToLog('TEXT-100', [self.unicodeNormalForm])

        # Write out the text to the target
        writeout = codecs.open(target, "wt", "utf_8_sig")
        writeout.write(normal)
        writeout.close

        # Validate the target USFM text (Defalt is True)
        if str2bool(self.validateUsfm) :
            if not self.usfmTextFileIsValid(target, projSty) :
                self.project.log.writeToLog('TEXT-155', [source,fName(target)])
                return False
        else :
            self.project.log.writeToLog('TEXT-157', [fName(target)])

        return True


    def testCompTextFile (self, source, projSty = None) :
        '''This will direct a request to the proper validater for
        testing the source of a component text file.'''

        if self.cType == 'usfm' :
            # If this fails it will die at the validation process
            if self.usfmTextFileIsValid(source, projSty) :
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


    def usfmTextFileIsValid (self, source, projSty) :
        '''Use the USFM parser to validate a style file. For now,
        if a file fails, we'll just quite right away, otherwise,
        return True.'''

        # Note: Error level reporting is possible with the usfm.parser.
        # The following are the errors it can report:
        # Note            = -1    Just give output warning, do not stop
        # Marker          =  0    Stop on any out of place marker
        # Content         =  1    Stop on mal-formed content
        # Structure       =  2    Stop on ???
        # Unrecoverable   =  100  Stop on most anything that is wrong
        # For future reference, the sfm parser will fail if TeX style
        # comment markers "%" are used to comment text rather than "#".

        try :
            fh = codecs.open(source, 'rt', 'utf_8_sig')
            stylesheet = usfm.default_stylesheet.copy()
            if projSty :
                stylesheet_extra = style.parse(open(os.path.expanduser(projSty),'r'))
                stylesheet.update(stylesheet_extra)
            doc = usfm.parser(fh, stylesheet, error_level=sfm.level.Structure)
            # With the doc text loaded up, we run a list across it
            # so the parser will either pass or fail
            testlist = list(doc)
            # Good to go
            return True

        except Exception as e :
            # If the text is not good, I think we should die here an now.
            # We may want to rethink this later but for now, it feels right.
            self.project.log.writeToLog('TEXT-090', [source,str(e)])
            return False



