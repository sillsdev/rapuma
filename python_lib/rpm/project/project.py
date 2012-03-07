#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111203
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project infrastructure tasks.

# History:
# 20110823 - djd - Started with intial file from RPM project
# 20111203 - djd - Begin changing over to new manager model


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, sys, fileinput, shutil, imp
#from configobj import ConfigObj, Section


# Load the local classes
from tools import *
import manager as mngr
import component as cmpt
import command as projCmd
import user_config as userConfig

###############################################################################
################################## Begin Class ################################
###############################################################################

class Project (object) :

    def __init__(self, userConfig, projConfig, local) :
        '''Instantiate this class.'''

        self.local                  = local
        self.userConfig             = userConfig
        self.projConfig             = projConfig
        self.layoutConfig           = ConfigObj()
        self.confFileList           = ['userConfig', 'projConfig', 'layoutConfig']
        self.components             = {}
        self.componentType          = {}
        self.projectType            = None
        self.projectIDCode          = None


###############################################################################
############################ Project Level Functions ##########################
###############################################################################

    def initProject (self) :
        '''Initialize the project object and load the project type class.'''

        # Initialize the managers dictionary here
        self.managers = {}

        # Do some cleanup like getting rid of the last sessions error log file.
        try :
            if os.path.isfile(self.local.projErrorLogFile) :
                os.remove(self.local.projErrorLogFile)
        except :
            pass

        # Initialize the project type
        m = __import__(self.projectType)
        self.__class__ = getattr(m, self.projectType[0].upper() + self.projectType[1:])

        # Update the existing config file with the project type XML file
        # if needed
        newXmlDefaults = os.path.join(self.local.rpmConfigFolder, self.projectType + '.xml')
        xmlConfig = getXMLSettings(newXmlDefaults)
        newConf = ConfigObj(xmlConfig.dict()).override(self.projConfig)
        for s,v in self.projConfig.items() :
            if s not in newConf :
                newConf[s] = v

        if self.projConfig != newConf :
            self.projConfig = newConf

        # Bring in default layout config information
        if not os.path.isfile(self.local.layoutConfFile) :
            self.layoutConfig  = ConfigObj(getXMLSettings(self.local.rpmLayoutDefaultFile))
#            self.layoutConfig.filename = self.local.layoutConfFile
        else :
            self.layoutConfig = ConfigObj(self.local.layoutConfFile)

        # Create some common folders used in every project (if needed)
        if not os.path.isdir(self.local.processFolder) :
            os.mkdir(self.local.processFolder)
        if not os.path.isdir(self.local.textFolder) :
            os.mkdir(self.local.textFolder)
        if not os.path.isdir(self.local.fontsFolder) :
            os.mkdir(self.local.fontsFolder)


###############################################################################
############################ Manager Level Functions ##########################
###############################################################################

    def createManager (self, cType, mType) :
        '''Check to see if a manager is listed in the config and load it if
        it is not already.'''

        fullName = cType + '_' + mType.capitalize()
        if fullName not in self.managers :
            self.addManager(cType, mType)
            self.loadManager(cType, mType)

        writeToLog('LOG', 'Created the [' + fullName + '] manager object.')
        return self.managers[fullName]


    def loadManager (self, cType, mType) :
        '''Do basic load on a manager.'''

        fullName = cType + '_' + mType.capitalize()
        cfg = self.projConfig['Managers'][fullName]
        module = __import__(mType)
        manobj = getattr(module, mType.capitalize())(self, cfg, cType)
        self.managers[fullName] = manobj


    def addManager (self, cType, mType) :
        '''Create a manager reference in the project config that components will point to.'''

        fullName = cType + '_' + mType.capitalize()
        # Insert the Manager section if it is not already there
        buildConfSection(self.projConfig, 'Managers')
        if not testForSetting(self.projConfig['Managers'], fullName) :
            buildConfSection(self.projConfig['Managers'], fullName)
            managerDefaults = getXMLSettings(os.path.join(self.local.rpmConfigFolder, mType + '.xml'))
            for k, v, in managerDefaults.iteritems() :
                # Do not overwrite if a value is already there
                if not testForSetting(self.projConfig['Managers'][fullName], k) :
                    self.projConfig['Managers'][fullName][k] = v
                    writeOutProjConfFile = True


###############################################################################
########################## Component Level Functions ##########################
###############################################################################

    def renderComponent (self, cid) :
        '''Render a single component. This will ensure there is a component
        object, then render it.'''

        self.createComponent(cid).render()


    def createComponent (self, cid) :
        '''Create a component object that can be acted on.'''

        # If the object already exists just return it
        if cid in self.components : return self.components[cid]
        
        # Otherwise, create a new one and return it
        cfg = self.projConfig['Components'][cid]
        ctype = cfg['type']
        module = __import__(ctype)
        compobj = getattr(module, ctype.capitalize())(self, cfg)
        self.components[cid] = compobj

        return compobj


    def addComponent (self, cid, ctype) :
        '''This will add a component to the object we created 
        above in createComponent().'''

        try :
            x = self.projConfig['Components'][cid]
            writeToLog('MSG', 'The [' + cid + '] component already exists in this project.')
        except :
            buildConfSection(self.projConfig, 'Components')
            buildConfSection(self.projConfig['Components'], cid)
            self.projConfig['Components'][cid]['name'] = cid
            self.projConfig['Components'][cid]['type'] = ctype
            writeConfFile(self.projConfig)
            writeToLog('MSG', 'Added the [' + cid + '] component to the project')


###############################################################################
############################ System Level Functions ###########################
###############################################################################


    def run(self, command, opts, userConfig) :
        '''Run a command'''

        if command in self.commands :
            self.commands[command].run(opts, self, userConfig)
        else :
            terminalError('The command: [' + command + '] failed to run with these options: ' + str(opts))


    def changeSystemSetting (self, key, value) :
        '''Change global default setting (key, value) in the System section of
        the RPM user settings file.  This will write out changes
        immediately.'''

        pass



