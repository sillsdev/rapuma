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


# FIXME: This should not be PT-centric

    def addStyleFile (self, sFile = None, force = False) :
        '''Add a style file for a specified component type. It should be as
        generlized as possible. If a style file already exsists, end the 
        process. There should only be one default style file for component type.
        Specific overrides can be added with a custom style file.
        
        If a path to a specific style file was passed via sFile, that file gets
        priority but it must be valid. If it is not, the operation will fail
        even if force is True.
        
        Otherwise, if nothing is specified, it will call on other routines to
        obtain a valid style file.
        
        If force is set to True, it will overwrite any config settings of the
        exsisting style file and remove the exsisting file. It will also force
        validation by copying in, if necessary, a "clean" valid copy of the
        necessary style sheet if anything is found wrong with the proposed
        style file or the one provided in the project.
        
        The sFile setting can work in two ways. With a full path and file
        name, it can Point to a new style file that will be copied into the
        project. Or, if only a file name is specified, with no specified path,
        RPM will then re-install an existing publishing project style file 
        already in the Styles folder. If it doesn't find it, then it will
        copy in a new one.'''

        def sSet (target) :
            # Double check other proceedures, record if good, die if not
            if os.path.isfile(target) :
                self.project.projConfig['CompTypes'][self.Ctype]['styleFile'] = fName(target)
                self.project.projConfig['Managers']['usfm_Style']['mainStyleFile'] = fName(target)
                writeConfFile(self.project.projConfig)
                self.project.log.writeToLog('STYL-090', [fName(target),self.cType])
                return True
            else :
                self.project.log.writeToLog('STYL-100', [target])
                dieNow()

        # If force is not set, the first thing we want to do is see
        # if the file exsists, quite here.
        target = os.path.join(self.project.local.projStylesFolder, self.project.projConfig['CompTypes'][self.Ctype]['styleFile'])
        if not force :
            if os.path.isfile(target) :
                self.project.log.writeToLog('STYL-010', [fName(target),self.cType])
                return False

        # Get/make the custom style file name.
        if sFile :
            # Good, we're done!
            if os.path.isfile(sFile) :
                if styleFileIsValid(source) :
                    # Force validate the source before we copy it into the project
                    if force :
                        # If shutil returns something, there is a problem
                        # Problems with failed style file copying are fatal
                        if not shutil.copy(sFile, os.path.join(self.project.local.projStylesFolder, fName(sFile))) :
                            self.project.log.writeToLog('STYL-070', [fName(source)])
                    else :
                        # Copy if the file is not there
                        if not os.path.isfile(target) :
                            shutil.copy(source, target)
                            self.project.log.writeToLog('STYL-080', [fName(source)])
                else :
                    self.project.log.writeToLog('STYL-140', [fName(source)])
                    return False

                if sSet(target) :
                    return True
            else :
                # Hopefully this is already there, just needs 
                # to be set in the config
                if os.path.isfile(os.path.join(self.project.local.projStylesFolder, sFile)) :
                    sSet(os.path.join(self.project.local.projStylesFolder, sFile))
                    return True
                else :
                    # Failed, do tell why
                    self.project.log.writeToLog('STYL-020', [sFile])
                    dieNow()
        else :
            if self.cType.lower() == 'usfm' :
                # If no sFile was specified, try installng a PT project style file
                # or a backup system style file
                sFile = self.installCompTypeStyleFile(force)
                if sFile and os.path.isfile(sFile) :
                    sSet(sFile)
                    if not force :
                        self.project.log.writeToLog('STYL-030', [fName(sFile)])
                    else :
                        self.project.log.writeToLog('STYL-035', [fName(sFile)])
                    return True
                else :
                    # If we havn't got it yet, we are hosed'
                    self.project.log.writeToLog('STYL-050')
                    dieNow()
            else :
                # We don't know how to work with this type is so we shouldn't process it
                self.project.log.writeToLog('STYL-060')
                dieNow()


    def installCompTypeStyleFile (self, force) :
        '''If the source is from a PT project, check to see if there is a
        (project-wide) stylesheet to install. If not, we will make one.
        This file is required as a minimum for components of this type to
        render. This function must succeed.'''

        if self.sourceEditor.lower() == 'paratext' :
            ptConf = getPTSettings(self.project.local.projHome)
            # Override default styleFile name if we found something in the PT conf
            try :
                self.mainStyleFile = ptConf['ScriptureText']['StyleSheet']
            except :
                pass
            target = os.path.join(self.project.local.projStylesFolder, self.mainStyleFile)
            # To force, simply get rid of the current target and reinstall
            if force :
                try :
                    os.remove(target)
                except :
                    pass

            # The way this is handled is specific to the editor
            if not os.path.isfile(target) :
                return self.installUsfmStyle(force)
            else :
                return None
        else :
            sys.exit('Error: Editor [' + self.sourceEditor + '] not recognized')


    def installUsfmStyle (self, force = False) :
        '''Go get the style sheet from the local PT project this is in
        and install it into the project where and how it needs to be. If it
        doesn't find it there go to the [My Paratext Projects] folder and
        look there. If none is found a default file will come be copied in
        from the RPM system.'''

        # As this is call is for a PT based project, it is certain the style
        # file should be found in the parent or grandparent folder. If that
        # exact file is not found in either place, a substitute will be
        # copied in from RPM and given the designated name.
        altSourcePath               = resolvePath(self.project.projConfig['CompTypes'][self.Ctype]['altSourcePath'])
        (parent, grandparent)       = ancestorsPath(self.project.local.projHome)
        targetStyle                 = os.path.join(self.project.local.projStylesFolder, self.mainStyleFile)
        altSourceStyle              = os.path.join(altSourcePath, self.mainStyleFile)
        ptProjStyle                 = os.path.join(parent, self.mainStyleFile)
        ptStyle                     = os.path.join(grandparent, self.mainStyleFile)
        rpmStyle                    = os.path.join(self.project.local.rpmCompTypeFolder, 'usfm', 'usfm.sty')
        searchOrder                 = [altSourceStyle, ptProjStyle, ptStyle, rpmStyle]

        # We will start by searching in order from the inside out and stop
        # as soon as we find one.
        if not os.path.isfile(targetStyle) or force :
            for sFile in searchOrder :
                if os.path.isfile(sFile) :
                    if styleFileIsValid(sFile) :
                        if not shutil.copy(sFile, targetStyle) :
                            return targetStyle
                    else :
                        self.project.log.writeToLog('STYL-130', [sFile,self.cType])
                else : 
                    self.project.log.writeToLog('STYL-105', [sFile])


    def removeStyleFile (self, force) :
        '''This would be useful for a style reset. Remove a style setting
        from the config for a component type and if force is used, remove
        the file from the project as well.'''

        # Make sure there is something to do
        try :
            oldStyle = self.project.projConfig['CompTypes'][self.Ctype]['styleFile']
            if oldStyle == 'None' :
                self.project.log.writeToLog('STYL-110', [self.cType])
                return
        except :
            self.project.log.writeToLog('STYL-110', [self.cType])
            return

        self.project.projConfig['CompTypes'][self.Ctype]['styleFile'] = None
        self.project.projConfig['Managers']['usfm_Style']['mainStyleFile'] = None
        writeConfFile(self.project.projConfig)

        if force :
            target = os.path.join(self.project.local.projStylesFolder, oldStyle)
            try :
                os.remove(target)
            except :
                pass
            self.project.log.writeToLog('STYL-120', [fName(oldStyle),self.cType])
        else :
            self.project.log.writeToLog('STYL-130', [fName(oldStyle),self.cType])

        return True


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






