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


    def addStyleFile (self, sType, sFile = '', force = False) :
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
        exsisting style file and remove the exsisting file. It will, however,
        fail if the incoming style sheet doesn't validate. This could leave
        the project in a situation where it will not render because the style
        file is missing.
        
        The sFile setting points to a new style file that will be copied into
        the project. That style file will need to be validated as well.'''

        def sSet (sType, target) :
            # Double check other proceedures, record if good, die if not
            if os.path.isfile(target) :
                if sType.lower() == 'main' :
                        self.project.projConfig['Managers'][self.cType + '_Style']['mainStyleFile'] = fName(target)
                elif sType.lower() == 'custom' :
                    self.project.projConfig['Managers'][self.cType + '_Style']['customStyleFile'] = fName(target)

                writeConfFile(self.project.projConfig)
                self.project.log.writeToLog('STYL-010', [fName(target),self.cType])
                return True
            else :
                self.project.log.writeToLog('STYL-020', [target])
                dieNow()

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

        # If force is set, the first thing we want to do is remove the old file and settings
        # Otherwise, check to see if style file matched the settings, if it does, quite
        if force :
            self.removeStyleFile(sType, force)
        else :
            if sType.lower() == 'main' :
                if self.project.projConfig['Managers'][self.cType + '_Style']['mainStyleFile'] == fName(target) :
                    self.project.log.writeToLog('STYL-040', [fName(target),self.cType])
                    dieNow()
            elif sType.lower() == 'custom' :
                if self.project.projConfig['Managers'][self.cType + '_Style']['customStyleFile'] == fName(target) :
                    self.project.log.writeToLog('STYL-040', [fName(target),self.cType])
                    dieNow()

        # Get/make a style file with a specific name (main or custom) if a name was given in sFile.
        if sFile :


#            import pdb; pdb.set_trace()


            sFile = resolvePath(sFile)
            target = os.path.join(self.project.local.projStylesFolder, fName(sFile))
            # Good, we're done!
            if os.path.isfile(sFile) :
                # If this is not an RPM custom style file we will validate it
                if sType.lower() == 'main' :
                    if not styleFileIsValid(sFile) :
                        self.project.log.writeToLog('STYL-070', [fName(sFile)])
                        return False



                # Copy it into the project
                if force :
                    # If shutil returns something, there is a problem
                    # Problems with failed style file copying are fatal
                    if not shutil.copy(sFile, target) :
                        self.project.log.writeToLog('STYL-050', [fName(sFile)])
                else :
                    # Copy if the file is not there
                    if not os.path.isfile(target) :
                        shutil.copy(sFile, target)
                        self.project.log.writeToLog('STYL-060', [fName(sFile)])

                if sSet(sType, target) :
                    return True
            else :
                # Hopefully this is already there, just needs 
                # to be set in the config
                if os.path.isfile(target) :
                    sSet(sType, target)
                    return True
                else :
                    # Failed, do tell why
                    self.project.log.writeToLog('STYL-080', [sFile])
                    dieNow()
        else :
            if sType.lower() == 'main' :
                if self.cType.lower() == 'usfm' :
                    # If no sFile was specified, try installng a PT project style file
                    # or a backup system style file
                        # FIXME: We will want to provide support for PT custom styles which
                        # will be merged into the style file that is copied/created for the
                        # project. This is because "custom" styles in RPM are only for rendering
                        # and need to be hanled separate from any PT source styles.
                    if self.sourceEditor.lower() == 'paratext' :
                        ptConf = getPTSettings(self.project.local.projHome)
                        # Override default styleFile name if we found something in the PT conf
                        if ptConf :
                            self.mainStyleFile = ptConf['ScriptureText']['StyleSheet']
                        else :
                            if not self.mainStyleFile :
                                self.mainStyleFile = 'usfm.sty'

                        target = os.path.join(self.project.local.projStylesFolder, self.mainStyleFile)
                        # The way this is handled is specific to the editor
                        if os.path.isfile(target) :
                            if not self.project.projConfig['Managers'][self.cType + '_Style']['mainStyleFile'] :
                                sSet(sType, target)
                        else :
                            # As this is call is for a PT based project, it is certain the style
                            # file should be found in the parent or grandparent folder. If that
                            # exact file is not found in either place, a substitute will be
                            # copied in from RPM and given the designated name.
                            altSourceStyle              = ''
                            if self.project.projConfig['CompTypes'][self.Ctype]['altSourcePath'] :
                                altSourcePath           = resolvePath(self.project.projConfig['CompTypes'][self.Ctype]['altSourcePath'])
                                altSourceStyle          = os.path.join(altSourcePath, self.mainStyleFile)
                            (parent, grandparent)       = ancestorsPath(self.project.local.projHome)
                            ptProjStyle                 = os.path.join(parent, self.mainStyleFile)
                            ptStyle                     = os.path.join(grandparent, self.mainStyleFile)
                            rpmStyle                    = os.path.join(self.project.local.rpmCompTypeFolder, 'usfm', 'usfm.sty')
                            searchOrder                 = [altSourceStyle, ptProjStyle, ptStyle, rpmStyle]

                            # We will start by searching in order from the inside out and stop
                            # as soon as we find one.
                            for sFile in searchOrder :
                                if os.path.isfile(sFile) :

# FIXME: Something not right here with the validation

                                    if styleFileIsValid(sFile) :
                                        if not shutil.copy(sFile, target) :
                                            sSet(sType, target)
                                    else :
                                        self.project.log.writeToLog('STYL-075', [sFile,self.cType])
                                else : 
                                    self.project.log.writeToLog('STYL-090', [sFile])
                    else :
                        sys.exit('\nError: Editor [' + self.sourceEditor + '] not recognized.\n')

            # As this is a custom RPM style file, we will just make an empty one if there is not one already
            elif sType.lower() == 'custom' :
                target = os.path.join(self.project.local.projStylesFolder, self.customStyleFile)
                # The way this is handled is specific to the editor
                if os.path.isfile(target) :
                    if not self.project.projConfig['Managers'][self.cType + '_Style']['customStyleFile'] :
                        sSet(sType, target)
                else :
                    with codecs.open(target, "wt", encoding="utf_8_sig") as output:
                        output.write('\# Custom RPM style file\nThis file contains custom rendering styles for this publishing project\n\n')

            
#        elif sType == 'custom' :
#        else :
#            sys.exit('\nError: Style file type [' + sType + '] not recognized.\n')


    def removeStyleFile (self, sType, force = False) :
        '''This would be useful for a style reset. Remove a style setting
        from the config for a component type and if force is used, remove
        the file from the project as well.'''

        # Make sure there is something to do
        if sType.lower() == 'main' :
            oldStyle = self.project.projConfig['Managers'][self.cType + '_Style']['mainStyleFile']
        elif sType.lower() == 'custom' :
            oldStyle = self.project.projConfig['Managers'][self.cType + '_Style']['customStyleFile']

        if not oldStyle :
            self.project.log.writeToLog('STYL-100', [self.cType])
            return
        else :
            if sType.lower() == 'main' :
                self.project.projConfig['Managers'][self.cType + '_Style']['mainStyleFile'] = ''
                self.mainStyleFile = ''
            elif sType.lower() == 'custom' :
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






