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

import os, shutil
from configobj                      import ConfigObj

# Load the local classes
from rapuma.core.tools              import Tools, ToolsPath, ToolsGroup
from rapuma.core.user_config        import UserConfig
from rapuma.core.proj_local         import ProjLocal
from rapuma.core.proj_log           import ProjLog


###############################################################################
################################## Begin Class ################################
###############################################################################

class ProjConfig (object) :

    def __init__(self, pid, gid = None) :
        '''Do the primary initialization for this class.'''

        self.pid                            = pid
        self.gid                            = gid
        self.user                           = UserConfig()
        self.userConfig                     = self.user.userConfig
        self.projHome                       = self.userConfig['Projects'][self.pid]['projectPath']
        self.mType                          = self.userConfig['Projects'][self.pid]['projectMediaIDCode']
        self.local                          = ProjLocal(self.pid)
        self.tools                          = Tools()
        self.log                            = ProjLog(self.pid)
        # File names
        self.projConfFileName               = 'project.conf'
        self.progConfXmlFileName            = self.mType + '.xml'
        self.layoutConfFileName             = 'layout.conf'
        self.layoutXmlConfFileName          = self.mType + '_layout.xml'
        self.fontConfFileName               = 'font.conf'
        self.fontXmlConfFileName            = 'font.xml'
        self.hyphenConfFileName             = 'hyphenation.conf'
        self.hyphenXmlConfFileName          = 'hyphenation.xml'
        self.illustrationConfFileName       = 'illustration.conf'
        self.illustrationXmlConfFileName    = 'illustration.xml'
        # Paths
        self.projConfFolder                 = self.local.projConfFolder
        self.rapumaConfigFolder             = self.local.rapumaConfigFolder
        # Files with paths
        self.projConfFile                   = os.path.join(self.projConfFolder, self.projConfFileName)
        self.projConfXmlFile                = os.path.join(self.rapumaConfigFolder, self.progConfXmlFileName)
        self.layoutConfFile                 = os.path.join(self.projConfFolder, self.layoutConfFileName)
        self.layoutXmlConfFile              = os.path.join(self.rapumaConfigFolder, self.layoutXmlConfFileName)
        self.fontConfFile                   = os.path.join(self.projConfFolder, self.fontConfFileName)
        self.fontXmlConfFile                = os.path.join(self.rapumaConfigFolder, self.fontXmlConfFileName)
        self.hyphenConfFile                 = os.path.join(self.projConfFolder, self.hyphenConfFileName)
        self.hyphenXmlConfFile              = os.path.join(self.rapumaConfigFolder, self.hyphenXmlConfFileName)
        self.illustrationConfFile           = os.path.join(self.projConfFolder, self.illustrationConfFileName)
        self.illustrationXmlConfFile        = os.path.join(self.rapumaConfigFolder, self.illustrationXmlConfFileName)
        # Load the config objects
        self.layoutConfig                   = self.tools.initConfig(self.layoutConfFile, self.layoutXmlConfFile)
        self.fontConfig                     = self.tools.initConfig(self.fontConfFile, self.fontXmlConfFile)
        self.projConfig                     = self.tools.initConfig(self.local.projConfFile, self.projConfXmlFile)
        self.hyphenConfig                   = self.tools.initConfig(self.hyphenConfFile, self.hyphenXmlConfFile)
        self.illustrationConfig             = self.tools.initConfig(self.illustrationConfFile, self.illustrationXmlConfFile)

        self.tools_path                     = ToolsPath(self.local, self.projConfig, self.userConfig)
        self.tools_group                    = ToolsGroup(self.local, self.projConfig, self.userConfig)

        # For a cleaner init we will test for gid
        if gid :
            self.finishInit()
        else :
            self.cType                      = ''
            self.Ctype                      = ''
            self.macPack                    = ''

        # Log messages for this module
        self.errorCodes     = {
            'LYOT-000' : ['MSG', 'Layout module messages'],
            'LYOT-010' : ['LOG', 'Wrote out new layout configuration file. (layout.__init__())'],
            'LYOT-020' : ['LOG', 'Loaded exsisting layout configuration file. (layout.__init__())'],
            'LYOT-030' : ['LOG', 'Changes found in the default layout config model. These were merged into the exsisting layout configuration file. (layout.__init__())'],

            '0000' : ['MSG', 'Placeholder message'],
        }


    def finishInit (self) :
        '''Finishing collecting settings that would be needed for most
        functions in this module.'''

#        import pdb; pdb.set_trace()

        self.cType                          = self.projConfig['Groups'][self.gid]['cType']
        self.Ctype                          = self.cType.capitalize()
        self.macPack                        = self.projConfig['CompTypes'][self.Ctype]['macroPackage']


###############################################################################
############################ Manager Level Functions ##########################
###############################################################################


    def makeNewProjConf (self, local, pid, pmid, pname, cVersion) :
        '''Create a new project configuration file for a new project.'''

        self.projConfig = ConfigObj(self.tools.getXMLSettings(os.path.join(local.rapumaConfigFolder, pmid + '.xml')), encoding='utf-8')
        # Insert intitial project settings
        self.projConfig['ProjectInfo']['projectMediaIDCode']        = pmid
        self.projConfig['ProjectInfo']['projectName']               = pname
        self.projConfig['ProjectInfo']['projectCreatorVersion']     = cVersion
        self.projConfig['ProjectInfo']['projectCreateDate']         = self.tools.tStamp()
        self.projConfig['ProjectInfo']['projectIDCode']             = pid
        self.projConfig.filename                                    = local.projConfFile
        self.projConfig.write()


###############################################################################
########################## Config Handling Functions ##########################
###############################################################################

class ConfigTools (object) :
    '''Configuration handling functions.'''

    def __init__(self, project) :

        self.project                = project
        self.managers               = project.managers
        self.projConfig             = project.projConfig
        self.gid                    = project.gid
        self.pid                    = project.projectIDCode
        self.csid                   = self.projConfig['Groups'][self.gid]['csid']
        self.cType                  = self.projConfig['Groups'][self.gid]['cType']
        self.Ctype                  = self.cType.capitalize()
        self.layoutConfig           = ProjConfig(self.pid).layoutConfig


    def processLinePlaceholders (self, line, value) :
        '''Search a string (or line) for a type of Rapuma placeholder and
        insert the value. This is for building certain kinds of config values.'''

        # Allow for multiple placeholders with "while"
        while self.hasPlaceHolder(line) :
            (holderType, holderKey) = self.getPlaceHolder(line)
            # Insert the raw value
            if holderType == 'v' :
                line = self.insertValue(line, value)
            # Go get a value from another setting in the self.layoutConfig
            elif holderType in self.layoutConfig.keys() :
                holderValue = self.layoutConfig[holderType][holderKey]
                line = self.insertValue(line, holderValue)
            # A value that needs a measurement unit attached
            elif holderType == 'vm' :
                line = self.insertValue(line, self.addMeasureUnit(value))
            # A value that is a path
            elif holderType == 'path' :
                pth = getattr(self.project.local, holderKey)
                line = self.insertValue(line, pth)
            # A value that is a path separater character
            elif holderType == 'pathSep' :
                pathSep = os.sep
                line = self.insertValue(line, pathSep)
            # A value that contains a system delclaired value
            # Note this only works if the value we are looking for has
            # been declaired above in the module init
            elif holderType == 'self' :
                line = self.insertValue(line, getattr(self, holderKey))

        return line


    def insertValue (self, line, v) :
        '''Insert a value where a place holder is.'''

        # Handle empty values here
        if v == '[empty]' :
            v = ''
        begin = line.find('[')
        end = line.find(']') + 1
        ph = line[begin:end]

        return line.replace(ph, v)


    def hasPlaceHolder (self, line) :
        '''Return True if this line has a data place holder in it.'''

        # If things get more complicated we may need to beef this up a bit
        if line.find('[') > -1 and line.find(']') > -1 :
            return True


    def getPlaceHolder (self, line) :
        '''Return place holder type and a key if one exists from a TeX setting line.'''

        begin = line.find('[')
        end = line.find(']') + 1
        cnts = line[begin + 1:end - 1]
        if cnts.find(':') > -1 :
            return cnts.split(':')
        elif cnts.find('.') > -1 :
            return cnts.split('.')
        else :
            return cnts, ''


    def addMeasureUnit (self, val) :
        '''Return the value with the specified measurement unit attached.'''
        
        mu = self.layoutConfig['GeneralSettings']['measurementUnit']
        return val + mu





