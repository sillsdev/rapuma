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

    def addStyleFile (self, cType, sFile = None, force = False) :
        '''Add a style file for a specified component type. It should be as
        generlized as possible. If a style file already exsists, end the 
        process. There should only be one style file for component type.
        Specific overrides can be added at the component level.
        
        If force is set to True, overwrite any config settings for exsisting
        style file but do not remove the exsisting file.
        
        The sFile setting can work in two ways. With a full path and file
        name, it can Point to a new style file that will be copied into the
        project. Or, if only a file name is specified, with no specified path,
        RPM will then re-install an existing publishing project style file 
        already in the Components folder. If it doesn't find it, then it will
        auto-generate and install a new one and then use the specified
        sFile name.'''

    # FIXME: add sFile behavior
    # FIXME: add force behavior
    # FIXME: add auto-generate style file

        # Get/make the custom style file name.
        if sFile :
            # Good, we're done!
            if os.path.isfile(sFile) :
                target = os.path.join(self.project.local.projStylesFolder, fName(sFile))
                # Copy and set
                if not shutil.copy(sFile, target) :
                    self.project.projConfig['CompTypes'][Ctype]['styleFile'] = fName(sFile)
                    self.project.projConfig['Managers']['usfm_Style']['mainStyleFile'] = fName(sFile)
                    writeConfFile(self.project.projConfig)
                    self.project.log.writeToLog('STYL-000', [fName(sFile)])
                    return True
                else :
                    # Failed, do tell why
                    self.project.log.writeToLog('STYL-000', [sFile])
                    return False
            else :
                # Hopefully this is already there, just needs 
                # to be set in the config
                target = os.path.join(self.project.local.projStylesFolder, sFile)
                if os.path.isfile(target) :
                    self.project.projConfig['CompTypes'][Ctype]['styleFile'] = sFile
                    writeConfFile(self.project.projConfig)
                    self.project.log.writeToLog('STYL-000', [sFile])
                    return True
                else :
                    # Failed, do tell why
                    self.project.log.writeToLog('STYL-000', [sFile])
                    return False
        else :
            if cType.lower() == 'usfm' :
                # If no sFile was specified, try installng a PT project style file
                if self.installCompTypeGlobalStyles() :
                    self.project.log.writeToLog('STYL-000')
                    return True
                else :
                    # None was specified, none found, lets make one
                    if self.autoGenSty(cType) :
                        self.project.log.writeToLog('STYL-000')
                        return True
                    else :
                        # If we havn't figured it out by now we are hosed'
                        self.project.log.writeToLog('STYL-000')
                        dieNow()
            else :
                # We don't know what this type is so we shouldn't process it
                self.project.log.writeToLog('STYL-000')
                dieNow()


    def removeStyleFile (self, cType, force) :
        '''Remove a style file from a specified component type. However, if
        the type is locked, bow out gracefully, unless force is set to True.'''

    # FIXME: This is not even close to working

        def removeFile () :
            if os.path.isfile(styleFile) :
                os.remove(styleFile)
                self.project.log.writeToLog('STYL-000')
            else :
                self.project.log.writeToLog('STYL-000')

        # Set some vars
        styleFile = os.path.join(self.project.local.projComponentsFolder, cType + '.sty')

        if force :
            removeFile()
        else :
            if self.project.isLocked(cType) :
                self.project.log.writeToLog('STYL-000')
            else :
                removeFile()
                self.project.log.writeToLog('STYL-000')



    def autoGenSty (self, cType, sName = None) :
        '''Auto-generate a style file based on project data.'''

    # FIXME: add real auto-generation of sfm style files

        if sName :
            target = os.path.join(self.project.local.projStylesFolder, sName)
        else :
            target = os.path.join(self.project.local.projStylesFolder, cType + '.sty')

        # Here some real profound stuff should happen with the 
        # fancy sfm parser. However, for now we'll just copy in 
        # a default sty file.
        source = os.path.join(self.project.local.rpmCompTypeFolder, cType,  cType + '.sty')
        if not shutil.copy(source, target) :
            return True
        else :
            return False


    def installCompTypeGlobalStyles (self) :
        '''If the source is from a PT project, check to see if there is a
        (project-wide) stylesheet to install. If not, we will make one.
        This file is required as a minimum for components of this type to
        render. This function must succeed.'''

        ptConf = getPTSettings(self.project.local.projHome)
        globalStyFile = os.path.join(self.project.local.projStylesFolder, self.mainStyleFile)
        if not os.path.isfile(globalStyFile) :
            if self.sourceEditor.lower() == 'paratext' :
                # Build paths and names we need
                parent = os.path.dirname(self.project.local.projHome)
                gather = os.path.join(parent, 'gather')
                if os.path.isdir(gather) :
                    parent = gather

                # Override default styleFile name with what we find in the PT conf
                self.mainStyleFile = ptConf['ScriptureText']['StyleSheet']
                print self.mainStyleFile
                source = os.path.join(parent, self.mainStyleFile)
                target = os.path.join(self.project.local.projStylesFolder, self.mainStyleFile)
                if not os.path.isfile(target) :
                    installPTStyles(self.project.local, self.mainStyleFile)
                    # Change, if necessary, the main style file name
                    self.project.projConfig['Managers']['usfm_Style']['mainStyleFile'] = self.mainStyleFile
                    self.project.projConfig['CompTypes'][self.Ctype]['styleFile'] = self.mainStyleFile
                    if writeConfFile(self.project.projConfig) :
                        return True
            else :
                # Quite here
                return False


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






