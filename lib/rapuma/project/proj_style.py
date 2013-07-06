#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project tasks.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, warnings, codecs

# Load the local classes
from rapuma.core.tools              import Tools
from rapuma.core.paratext           import Paratext
from rapuma.project.proj_config     import ProjConfig, ConfigTools
from rapuma.core.user_config        import UserConfig
from rapuma.core.proj_local         import ProjLocal
from rapuma.core.proj_log           import ProjLog


###############################################################################
################################## Begin Class ################################
###############################################################################

class ProjStyle (object) :

    def __init__(self, pid, gid) :
        '''Do the primary initialization for this class.'''

        # Set values for this class
        self.pid                        = pid
        self.gid                        = gid
        self.tools                      = Tools()
        self.pt_tools                   = Paratext(pid, gid)
        self.user                       = UserConfig()
        self.userConfig                 = self.user.userConfig
        self.projHome                   = self.userConfig['Projects'][pid]['projectPath']
        self.projectMediaIDCode         = self.userConfig['Projects'][pid]['projectMediaIDCode']
        self.local                      = ProjLocal(pid)
        self.proj_config                = ProjConfig(pid, gid)
        self.configTools                = ConfigTools(pid, gid)
        self.projConfig                 = self.proj_config.projConfig
        self.macPackConfig              = self.proj_config.macPackConfig
        self.log                        = ProjLog(pid)
        self.cType                      = self.projConfig['Groups'][gid]['cType']
        self.Ctype                      = self.cType.capitalize()
        # Misc settings
        self.renderer                   = self.projConfig['CompTypes'][self.Ctype]['renderer']
        self.sourceEditor               = self.projConfig['CompTypes'][self.Ctype]['sourceEditor']
        # File names
        # Folder paths
        self.projComponentsFolder       = self.local.projComponentsFolder
        self.gidFolder                  = os.path.join(self.projComponentsFolder, gid)
        self.rapumaStyFolder            = self.local.rapumaStylesFolder
        self.rapumaCmpStyFolder         = os.path.join(self.rapumaStyFolder, self.cType)
        # Files with paths
        self.defaultStyFile             = self.configTools.processNestedPlaceholders(self.macPackConfig['ProjectStyles']['defaultStyFile'])
        self.glbExtStyFile              = self.configTools.processNestedPlaceholders(self.macPackConfig['ProjectStyles']['glbExtStyFile'])
        self.grpExtStyFile              = self.configTools.processNestedPlaceholders(self.macPackConfig['ProjectStyles']['grpExtStyFile'])

        # Log messages for this module
        self.errorCodes     = {

            '2010' : ['ERR', 'Style file [<<1>>] could not be created.'],
            '2020' : ['LOG', 'Default style file already exists in the project. Will not replace with a new copy.'],
            '2040' : ['LOG', 'Created: [<<1>>]'],

        }


###############################################################################
########################## External Manager Functions #########################
###############################################################################



#    def checkDefaultStyFile (self) :
#        '''Check for the exsistance of the Global Sty file. Make it if it
#        is not there.'''

#        if not os.path.exists(self.defaultStyFile) :
#            if not self.makeDefaultStyFile() :
#                self.log.writeToLog(self.errorCodes['2010'], [self.tools.fName(self.defaultStyFile)], 'style.checkDefaultStyFile():0010')
#                return False
#        else :
#            return True


#    def checkGlbExtStyFile (self) :
#        '''Check for the exsistance of the component extention Sty file. We need
#        to throw a stern warning if it is not there and create a blank one.'''

#        if not os.path.isfile(self.glbExtStyFile) :
#            if not self.makeGlbExtStyFile() :
#                self.log.writeToLog(self.errorCodes['2010'], [self.tools.fName(self.glbExtStyFile)], 'style.checkGlbExtStyFile():0010')
#                return False
#        else :
#            return True


    def checkGrpExtStyFile (self) :
        '''Check for the exsistance of the group extention Sty file. We need
        to throw a stern warning if it is not there and create a blank one.'''

        if not os.path.isfile(self.grpExtStyFile) :
            if not self.makeGrpExtStyFile() :
                self.log.writeToLog(self.errorCodes['2010'], [self.tools.fName(self.grpExtStyFile)], 'style.checkGrpExtStyFile():0010')
                return False
        else :
            return True


#    def makeDefaultStyFile (self) :
#        '''Create or copy in a default global style file for the current component type.
#        And while we are at it, make it read-only. But do not do it if one is already there.'''

#        if not os.path.exists(self.defaultStyFile) :
#            if os.path.exists(self.rapumaDefaultStyFile) :
#                # No news is good news
#                if not shutil.copy(self.rapumaDefaultStyFile, self.defaultStyFile) :
#                    self.tools.makeReadOnly(self.defaultStyFile)
#                    self.log.writeToLog(self.errorCodes['2040'], [self.tools.fName(self.defaultStyFile)])
#                    return True
#                else :
#                    return False
#        else :
#            self.log.writeToLog(self.errorCodes['2020'])
#            return True


#    def makeGlbExtStyFile (self) :
#        '''Create/copy a component Style extentions file to the project for specified group.'''

#        description = 'This is the component extention style file which overrides settings in \
#        the main default component style settings file.'

#        # First look for a user file, if not, then make a blank one
#        if not os.path.isfile(self.glbExtStyFile) :
#            if os.path.isfile(self.usrGlbExtStyFile) :
#                shutil.copy(self.usrGlbExtStyFile, self.glbExtStyFile)
#            else :
#                # Create a blank file
#                with codecs.open(self.glbExtStyFile, "w", encoding='utf_8') as writeObject :
#                    writeObject.write(self.tools.makeFileHeader(self.tools.fName(self.glbExtStyFile), description, False))
#                self.log.writeToLog(self.errorCodes['2040'], [self.tools.fName(self.glbExtStyFile)])

#        # Need to return true here even if nothing was done
#        return True


    def makeGrpExtStyFile (self) :
        '''Create a group Style extentions file to a specified group.'''

        description = 'This is the group style extention file which overrides settings in \
        the main default component extentions settings style file.'

        # Create a blank file (only if there is none)
        if not os.path.exists(self.grpExtStyFile) :
            with codecs.open(self.grpExtStyFile, "w", encoding='utf_8') as writeObject :
                writeObject.write(self.tools.makeFileHeader(self.tools.fName(self.grpExtStyFile), description, False))
            self.log.writeToLog(self.errorCodes['2040'], [self.tools.fName(self.grpExtStyFile)])

        # Need to return true here even if nothing was done
        return True



