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

import os, shutil

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


    def aquireStyleTarget (self, sType) :
        '''Get the style file target file name and path. If no useful project
        information can be found, create a default name according to the type.'''

        # Set a default target file name

        if sType.lower() == 'main' :
            if self.project.projConfig['Managers'][self.cType + '_Style']['mainStyleFile'] :
                target = os.path.join(self.project.local.projStylesFolder, self.project.projConfig['Managers'][self.cType + '_Style']['mainStyleFile'])
            else :
                target = os.path.join(self.project.local.projStylesFolder, 'usfm.sty')
                self.project.log.writeToLog('STYL-030', [fName(target)])
        elif sType.lower() == 'custom' :
            if self.project.projConfig['Managers'][self.cType + '_Style']['customStyleFile'] :
                target = os.path.join(self.project.local.projStylesFolder, self.project.projConfig['Managers'][self.cType + '_Style']['customStyleFile'])
            else :
                target = os.path.join(self.project.local.projStylesFolder, 'custom.sty')
                self.project.log.writeToLog('STYL-030', [fName(target)])

        return target


    def addStyleFile (self, sType, sFile, force = False) :
        ''' This is a generalized function to direct a request 
        to install a style file into the project.'''


# Working here


        print 'cccccccccccccccccccccc', sType, sFile, force

        if self.cType == 'usfm' :
            # If this is a force, then remove exsiting file and meta data
            if force :
                self.removeUsfmStyFile(sType, force)
            if sFile :
                if self.addExsitingUsfmStyFile(sFile, sType) :
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
                        sFile = self.installUSFMFallback()
                        if sFile :
                            self.recordStyleFile(sFile, sType)
                            return True
                        else :
                            dieNow('RPM USFM fallback style file not found.')
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

        self.project.projConfig['Managers'][self.cType + '_Style'][sType + 'StyleFile'] = fileName
        writeConfFile(self.project.projConfig)
# FIXME: What's wrong with this?
#        self.project.log.writeToLog('STYL-010', [fileName,sType,self.cType])
        return True


    def addPtUsfmStyFile (self) :
        '''Install a PT project style file. Merg in any custom
        project styles too.'''

        # First pick up our PT settings
        ptConf = getPTSettings(self.project.local.projHome)
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
        # file should be found in the parent or grandparent folder. If that
        # exact file is not found in either place, a substitute will be
        # copied in from RPM and given the designated name.
        altSourceStyle              = ''
        altSourcePath               = ''
        if self.project.projConfig['CompTypes'][self.Ctype]['altSourcePath'] :
            altSourcePath           = resolvePath(self.project.projConfig['CompTypes'][self.Ctype]['altSourcePath'])
            altSourceStyle          = os.path.join(altSourcePath, self.mainStyleFile)
        (parent, grandparent)       = ancestorsPath(self.project.local.projHome)
        # If there is a "gather" folder, assume the style file is there
        if os.path.isdir(os.path.join(parent, 'gather')) :
            ptProjStyle             = os.path.join(parent, 'gather', self.mainStyleFile)
        else :
            ptProjStyle             = os.path.join(parent, self.mainStyleFile)
        ptStyle                     = os.path.join(grandparent, self.mainStyleFile)
        searchOrder                 = [altSourceStyle, ptProjStyle, ptStyle]
        # We will start by searching in order from the inside out and stop
        # as soon as we find one.
        for sFile in searchOrder :
            if os.path.isfile(sFile) :
                if styleFileIsValid(sFile) :
                    if not shutil.copy(sFile, target) :
                        return True
                else :
                    self.project.log.writeToLog('STYL-075', [sFile,self.cType])
            else : 
                self.project.log.writeToLog('STYL-090', [sFile])


    def installUSFMFallback (self) :
        '''Install the fallback style file from the RPM system.'''

        sFile = os.path.join(self.project.local.rpmCompTypeFolder, 'usfm', 'usfm.sty')
        target = os.path.join(self.project.local.projStylesFolder, fName(sFile))
        if os.path.isfile(sFile) :
            # No news is good news
            if not shutil.copy(sFile, target) :
                return fName(target)


    def addExsitingUsfmStyFile (self, sFile, sType) :
        '''Add a specific style file that is on the local system.'''

        sFile = resolvePath(sFile)
        target = os.path.join(self.project.local.projStylesFolder, fName(sFile))

        # It's there? Good, we're done!
        if os.path.isfile(sFile) :
            # If this is not an RPM custom style file we will validate it
            if sType.lower() == 'main' :
                if styleFileIsValid(sFile) :
                    shutil.copy(sFile, target)
                    self.project.log.writeToLog('STYL-060', [fName(sFile)])
                    return True
                else :
                    # We die if it does not validate
                    self.project.log.writeToLog('STYL-070', [fName(sFile)])
                    dieNow()
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


    def validateStyleFile (self, path, errStop = False) :
        '''Use the USFM parser to validate a style file.'''

        if styleFileIsValid(path, errStop) :
            self.project.log.writeToLog('STYL-150', [path])
        else :
            self.project.log.writeToLog('STYL-155', [path])



#    def installCompTypeOverrideStyles (self) :
#        '''If the source is from a PT project, check to see if there is a
#        (project-wide) custom stylesheet to install. If not, we are done.
#        This style file is not required.'''

#        target = os.path.join(self.project.local.projComponentsFolder, self.customStyleFile)
#        if not os.path.isfile(target) :
#            if self.sourceEditor.lower() == 'paratext' :
#                # Build paths and names we need
#                parent = os.path.dirname(self.project.local.projHome)
#                gather = os.path.join(parent, 'gather')
#                if os.path.isdir(gather) :
#                    parent = gather

#                source = os.path.join(parent, self.customStyleFile)
#                if os.path.isfile(source) :
#                    shutil.copy(source, target)
#                    self.project.log.writeToLog('STYL-025', [fName(target)])
#                else :
#                    if not installPTCustomStyles(self.project.local, self.customStyleFile) :
#                        self.project.log.writeToLog('STYL-020')
#                        self.createCustomUsfmStyles()
#            else :
#                self.createCustomUsfmStyles()


#    def createCompOverrideUsfmStyles (self, cid) :
#        '''Create a component override style file for a single component.
#        This file will override specific styles from preceeding style
#        files loaded before it.'''

#        self.project.log.writeToLog('STYL-040')






