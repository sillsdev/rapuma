#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project configuration operations.


###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os
from configobj import ConfigObj

# Load the local classes
from rapuma.core.tools import Tools


class ProjConfig (object) :

    def __init__(self, local) :
        '''Intitate the whole class and create the object.'''

        self.tools          = Tools()
        self.local          = local
        self.projConfig     = ConfigObj(encoding='utf-8')

        # Create a fresh projConfig object
        if os.path.isfile(self.local.projConfFile) :
            self.projConfig = ConfigObj(self.local.projConfFile, encoding='utf-8')
            self.projectMediaIDCode = self.projConfig['ProjectInfo']['projectMediaIDCode']
            self.projConfig.filename = self.local.projConfFile


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
        # Load the managers we will need
        if self.cType + '_Layout' not in self.managers :
            self.project.createManager('layout')
        self.layoutConfig           = self.managers[self.cType + '_Layout'].layoutConfig


###############################################################################
############################ Module Level Functions ###########################
###############################################################################

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





