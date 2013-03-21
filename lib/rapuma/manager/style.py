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
from rapuma.core.tools import *
from rapuma.project.manager import Manager
from rapuma.group.usfm import PT_Tools


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
        self.pt_tools               = PT_Tools(project)
        self.project                = project
        self.local                  = project.local
        self.cfg                    = cfg
        self.cType                  = cType
        self.Ctype                  = cType.capitalize()
        self.gid                    = project.gid
        # Config objects we need
        self.projConfig             = project.projConfig
        self.userConfig             = project.userConfig
        # Misc settings
        self.rapumaXmlStyleConfig   = os.path.join(self.local.rapumaConfigFolder, self.xmlConfFile)
        self.renderer               = self.projConfig['CompTypes'][self.Ctype]['renderer']
        self.sourceEditor           = self.projConfig['CompTypes'][self.Ctype]['sourceEditor']
        # File names
        self.defaultStyFileName     = self.cType + '.sty'
        self.defaultExtStyFileName  = self.cType + '-ext.sty'
        self.grpExtStyFileName      = self.gid + '-ext.sty'
        self.rapumaCmpStyFileName   = self.cType + '.sty'
        # Folder paths
        self.projComponentsFolder   = self.local.projComponentsFolder
        self.gidFolder              = os.path.join(self.projComponentsFolder, self.gid)
        self.projStylesFolder       = self.local.projStylesFolder
        self.rapumaStyFolder        = self.local.rapumaStylesFolder
        self.rapumaCmpStyFolder     = os.path.join(self.rapumaStyFolder, self.cType)
        # Files with paths
        self.defaultStyFile         = os.path.join(self.projStylesFolder, self.defaultStyFileName)
        self.defaultExtStyFile      = os.path.join(self.projStylesFolder, self.defaultExtStyFileName)
        self.grpExtStyFile          = os.path.join(self.gidFolder, self.grpExtStyFileName)
        self.usrDefaultExtStyFile   = os.path.join(self.project.userConfig['Resources']['styles'], self.defaultExtStyFileName)
        self.rapumaCmpStyFile       = os.path.join(self.rapumaCmpStyFolder, self.rapumaCmpStyFileName)
        # Get persistant values from the config if there are any
        manager = self.cType + '_Style'
        newSectionSettings = getPersistantSettings(self.projConfig['Managers'][manager], self.rapumaXmlStyleConfig)
        if newSectionSettings != self.projConfig['Managers'][manager] :
            self.projConfig['Managers'][manager] = newSectionSettings

        self.compSettings = self.projConfig['Managers'][manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)

###############################################################################
########################## External Manager Functions #########################
###############################################################################




# FIXME: Log messages need to be transfered over to this module



    def checkDefaultStyFile (self) :
        '''Check for the exsistance of the Global Sty file. Make it if it
        is not there.'''

        if not os.path.exists(self.defaultStyFile) :
            if not self.makeDefaultStyFile() :
                self.project.log.writeToLog('XTEX-120', [fName(self.defaultStyFile)])
                return False
        else :
            return True


    def checkDefaultExtStyFile (self) :
        '''Check for the exsistance of the component extention Sty file. We need
        to throw a stern warning if it is not there and create a blank one.'''

        if not os.path.isfile(self.defaultExtStyFile) :
            if not self.makeDefaultExtStyFile() :
                self.project.log.writeToLog('XTEX-120', [fName(self.defaultExtStyFile)])
                return False
        else :
            return True


    def checkGrpExtStyFile (self) :
        '''Check for the exsistance of the group extention Sty file. We need
        to throw a stern warning if it is not there and create a blank one.'''

        if not os.path.isfile(self.grpExtStyFile) :
            if not self.makeGrpExtStyFile() :
                self.project.log.writeToLog('XTEX-120', [fName(self.grpExtStyFile)])
                return False
        else :
            return True


    def makeDefaultStyFile (self) :
        '''Create or copy in a default global style file for the current component type.'''

        if os.path.isfile(self.rapumaCmpStyFile) :
            # No news is good news
            if not shutil.copy(self.rapumaCmpStyFile, self.defaultStyFile) :
                return True


    def makeDefaultExtStyFile (self) :
        '''Create/copy a component Style extentions file to the project for specified group.'''

        description = 'This is the component extention style file which overrides settings in \
        the main default component style settings file.'

        # First look for a user file, if not, then make a blank one
        if not os.path.isfile(self.defaultExtStyFile) :
            if os.path.isfile(self.usrDefaultExtStyFile) :
                shutil.copy(self.usrDefaultExtStyFile, self.defaultExtStyFile)
            else :
                # Create a blank file
                with codecs.open(self.defaultExtStyFile, "w", encoding='utf_8') as writeObject :
                    writeObject.write(makeFileHeader(fName(self.defaultExtStyFile), description, False))
                self.project.log.writeToLog('XTEX-040', [fName(self.defaultExtStyFile)])

        # Need to return true here even if nothing was done
        return True


    def makeGrpExtStyFile (self) :
        '''Create/copy a group Style extentions file to a specified group.'''

        description = 'This is the group style extention file which overrides settings in \
        the main default component extentions settings style file.'

        # Create a blank file
        with codecs.open(self.grpExtStyFile, "w", encoding='utf_8') as writeObject :
            writeObject.write(makeFileHeader(fName(self.grpExtStyFile), description, False))
        self.project.log.writeToLog('XTEX-040', [fName(self.grpExtStyFile)])

        # Need to return true here even if nothing was done
        return True



###############################################################################
############################ General Style Functions ##########################
###############################################################################

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

###############################################################################
########################### ParaTExt Style Functions ##########################
###############################################################################

    def usfmStyleFileIsValid (self, path) :
        '''Use the USFM parser to validate a style file. This is meant to
        be just a simple test so only return True or False.'''

        try :
            stylesheet = usfm.default_stylesheet.copy()
            stylesheet_extra = usfm.style.parse(open(os.path.expanduser(path),'r'), usfm.style.level.Content)
            return True
        except Exception as e :
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


    def addExsitingUsfmStyFile (self, sFile, sType, force) :
        '''Add a specific style file that is on the local system.'''

        sFile = resolvePath(sFile)
        target = os.path.join(self.project.local.projStylesFolder, fName(sFile))

        if not force and os.path.isfile(target) :
            self.project.log.writeToLog('STYL-030', [fName(sFile)])
            return False
        elif os.path.isfile(sFile) :
            # It's there? Good, we're done!
            # If this is not an Rapuma custom style file we will validate it
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


    def addPtUsfmStyFile (self) :
        '''Install a PT project style file. Merg in any custom
        project styles too.'''

        # First pick up our PT settings
        ptConf = self.pt_tools.getPTSettings(self.gid)
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
        # copied in from Rapuma and given the designated name.
        sourceStyle             = os.path.join(self.sourcePath, self.mainStyleFile)
        parent                  = os.path.dirname(self.sourcePath)
        # If there is a "gather" folder, assume the style file is there
        if os.path.isdir(os.path.join(self.sourcePath, 'gather')) :
            ptProjStyle             = os.path.join(self.sourcePath, 'gather', self.mainStyleFile)
        else :
            ptProjStyle             = os.path.join(self.sourcePath, self.mainStyleFile)
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


#    def installUSFMCustom (self) :
#        '''Install the custom style file from the Rapuma system. This contains
#        special style code to help with implementing special features'''

#        sFile = os.path.join(self.project.local.rapumaCompTypeFolder, 'usfm', 'custom.sty')
#        target = os.path.join(self.project.local.projStylesFolder, fName(sFile))
#        if os.path.isfile(sFile) :
#            # No news is good news
#            if not shutil.copy(sFile, target) :
#                return sFile


