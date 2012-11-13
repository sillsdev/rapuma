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
from tools import *
from pt_tools import *
from manager import Manager


###############################################################################
################################## Begin Class ################################
###############################################################################

class Style (Manager) :

    # Shared values
    xmlConfFile     = 'style.xml'

    def __init__(self, project, cfg, cType) :
        '''Do the primary initialization for this manager.'''

        super(Style, self).__init__(project, cfg)

        # Set values for this manager
        self.project            = project
        self.cfg                = cfg
        self.cType              = cType
        self.Ctype              = cType.capitalize()
        self.rpmXmlStyleConfig  = os.path.join(self.project.local.rpmConfigFolder, self.xmlConfFile)
        self.renderer           = self.project.projConfig['CompTypes'][self.Ctype]['renderer']
        self.sourceEditor       = self.project.projConfig['CompTypes'][self.Ctype]['sourceEditor']

        # Get persistant values from the config if there are any
        manager = self.cType + '_Style'
        newSectionSettings = getPersistantSettings(self.project.projConfig['Managers'][manager], self.rpmXmlStyleConfig)
        if newSectionSettings != self.project.projConfig['Managers'][manager] :
            self.project.projConfig['Managers'][manager] = newSectionSettings

        self.compSettings = self.project.projConfig['Managers'][manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)

###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def addStyleFile (self, sType, sFile, force = False) :
        ''' This is a generalized function to direct a request 
        to install a style file into the project.'''

#        import pdb; pdb.set_trace()
        if self.cType == 'usfm' :
            # If this is a force, then remove exsiting file and meta data
            if force :
                self.removeUsfmStyFile(sType, force)
            if sFile :
                if self.addExsitingUsfmStyFile(sFile, sType, force) :
                    self.recordStyleFile(sFile, sType)
                    return True
            else :
                # Priority goes to any exsisting project style files
                if self.sourceEditor.lower() == 'paratext' :
                    sFile = self.addPtUsfmStyFile()
                    if sFile :
                        self.recordStyleFile(sFile, sType)
                        return True
                    else :
                        # If we get this far, install fallback style file
                        if sType.lower() == 'main' :
                            sFile = self.installUSFMFallback()
                        elif sType.lower() == 'custom' :
                            sFile = self.installUSFMCustom()

                        # Record in the config what we did
                        if sFile :
                            self.recordStyleFile(sFile, sType)
                            return True
                        else :
                            dieNow('RPM USFM [' + sType + '] style file not found.')
                else :
                    self.project.log.writeToLog('STYL-007', [self.cType,self.sourceEditor])
                    dieNow()
        else :
            self.project.log.writeToLog('STYL-005', [self.cType])
            dieNow()


    def removeStyleFile (self, sType, force = False) :
        '''Direct a request to remove a style file from a project.'''
        if self.cType == 'usfm' :
            self.removeUsfmStyFile(sType, force)
        else :
            self.project.log.writeToLog('STYL-005', [self.cType])
            dieNow()


    def recordStyleFile (self, fileName, sType) :
        '''Record in the project conf file the style file being used.'''

        self.project.projConfig['Managers'][self.cType + '_Style'][sType + 'StyleFile'] = fName(fileName)
        writeConfFile(self.project.projConfig)
        self.project.log.writeToLog('STYL-010', [fName(fileName),sType,self.cType])
        return True


    def addPtUsfmStyFile (self) :
        '''Install a PT project style file. Merg in any custom
        project styles too.'''

        # First pick up our PT settings
        sourcePath = resolvePath(self.project.projConfig['CompTypes'][self.Ctype]['sourcePath'])
        ptConf = getPTSettings(sourcePath)
        if not ptConf :
            return False

        # If nothing is set, give it a default to start off
        if not self.mainStyleFile :
            self.mainStyleFile = 'usfm.sty'
        # Now, override default styleFile name if we found something in the PT conf
        if ptConf['ScriptureText']['StyleSheet'] :
            self.mainStyleFile = ptConf['ScriptureText']['StyleSheet']

        # Set the target destination
        target = os.path.join(self.project.local.projStylesFolder, self.mainStyleFile)
        # As this is call is for a PT based project, it is certain the style
        # file should be found in the source or parent folder. If that
        # exact file is not found in either place, a substitute will be
        # copied in from RPM and given the designated name.
        sourceStyle             = os.path.join(sourcePath, self.mainStyleFile)
        parent                  = os.path.dirname(sourcePath)
        # If there is a "gather" folder, assume the style file is there
        if os.path.isdir(os.path.join(sourcePath, 'gather')) :
            ptProjStyle             = os.path.join(sourcePath, 'gather', self.mainStyleFile)
        else :
            ptProjStyle             = os.path.join(sourcePath, self.mainStyleFile)
        ptStyle                     = os.path.join(parent, self.mainStyleFile)
        searchOrder                 = [sourceStyle, ptProjStyle, ptStyle]
        # We will start by searching in order from the inside out and stop
        # as soon as we find one.
        for sFile in searchOrder :
            if os.path.isfile(sFile) :
                if self.usfmStyleFileIsValid(sFile) :
                    if not shutil.copy(sFile, target) :
                        return fName(target)
                else :
                    self.project.log.writeToLog('STYL-075', [sFile,self.cType])
            else : 
                self.project.log.writeToLog('STYL-090', [sFile])


    def installUSFMFallback (self) :
        '''Install the fallback style file from the RPM system. This is just
        a known good copy of the current USFM styles.'''

        sFile = os.path.join(self.project.local.rpmCompTypeFolder, 'usfm', 'usfm.sty')
        target = os.path.join(self.project.local.projStylesFolder, fName(sFile))
        if os.path.isfile(sFile) :
            # No news is good news
            if not shutil.copy(sFile, target) :
                return sFile


    def installUSFMCustom (self) :
        '''Install the custom style file from the RPM system. This contains
        special style code to help with implementing special features'''

        sFile = os.path.join(self.project.local.rpmCompTypeFolder, 'usfm', 'custom.sty')
        target = os.path.join(self.project.local.projStylesFolder, fName(sFile))
        if os.path.isfile(sFile) :
            # No news is good news
            if not shutil.copy(sFile, target) :
                return sFile


    def addExsitingUsfmStyFile (self, sFile, sType, force) :
        '''Add a specific style file that is on the local system.'''

        sFile = resolvePath(sFile)
        target = os.path.join(self.project.local.projStylesFolder, fName(sFile))

        if not force and os.path.isfile(target) :
            self.project.log.writeToLog('STYL-030', [fName(sFile)])
            return False
        elif os.path.isfile(sFile) :
            # It's there? Good, we're done!
            # If this is not an RPM custom style file we will validate it
            if sType.lower() == 'main' :
                if self.usfmStyleFileIsValid(sFile) :
                    shutil.copy(sFile, target)
                    self.project.log.writeToLog('STYL-060', [fName(sFile)])
                    return True
                else :
                    # We die if it does not validate
                    self.project.log.writeToLog('STYL-070', [fName(sFile)])
                    dieNow()
            else :
                # Assuming a custom style file we can grab most anything
                # without validating it
                shutil.copy(sFile, target)
                self.project.log.writeToLog('STYL-065', [fName(sFile)])
                return True
        else :
            # Not finding the file may not be the end of the world 
            self.project.log.writeToLog('STYL-020', [fName(sFile)])
            return False


    def removeUsfmStyFile (self, sType, force) :
        '''This would be useful for a style reset. Remove a style setting
        from the config for a component type and if force is used, remove
        the file from the project as well.'''

        sType = sType.lower()

        # Make sure there is something to do
        if sType == 'main' :
            oldStyle = self.project.projConfig['Managers'][self.cType + '_Style']['mainStyleFile']
        elif sType == 'custom' :
            oldStyle = self.project.projConfig['Managers'][self.cType + '_Style']['customStyleFile']

        if not oldStyle :
            self.project.log.writeToLog('STYL-100', [self.cType])
            return
        else :
            if sType == 'main' :
                self.project.projConfig['Managers'][self.cType + '_Style']['mainStyleFile'] = ''
                self.mainStyleFile = ''
            elif sType == 'custom' :
                self.project.projConfig['Managers'][self.cType + '_Style']['customStyleFile'] = ''
                self.customStyleFile = ''

            writeConfFile(self.project.projConfig)

            if force :
                target = os.path.join(self.project.local.projStylesFolder, oldStyle)
                if os.path.isfile(target) :
                    os.remove(target)

                self.project.log.writeToLog('STYL-110', [fName(oldStyle),self.cType])
            else :
                self.project.log.writeToLog('STYL-120', [fName(oldStyle),self.cType])

            return True


    def usfmStyleFileIsValid (self, path) :
        '''Use the USFM parser to validate a style file. This is meant to
        be just a simple test so only return True or False.'''

        try :
            stylesheet = usfm.default_stylesheet.copy()
            stylesheet_extra = usfm.style.parse(open(os.path.expanduser(path),'r'), usfm.style.level.Content)
            return True
        except Exception as e :
            return False


    def testStyleFile (self, path) :
        '''This is a basic validity test of a style file. If it
        does not validate the errors will be reported in the
        terminal for the user to examine.'''

        if self.cType == 'usfm' :
            if self.usfmStyleFileIsValid(path) :
                self.project.log.writeToLog('STYL-150', [path])
                return True
            else :
                stylesheet_extra = ''
                stylesheet = usfm.default_stylesheet.copy()
                stylesheet_extra = usfm.style.parse(open(os.path.expanduser(path),'r'), usfm.style.level.Unrecoverable)
                self.project.log.writeToLog('STYL-155', [path])
                return False
        else :
            self.project.log.writeToLog('STYL-005', [self.cType])
            dieNow()


