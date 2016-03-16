#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (sparkycbr at gmail dot com)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project infrastructure tasks.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, sys, shutil, imp, subprocess, zipfile, StringIO, filecmp
from configobj                      import ConfigObj, Section


# Load the local classes
from rapuma.core.tools              import Tools
from importlib                      import import_module
from rapuma.core.user_config        import UserConfig
from rapuma.core.proj_local         import ProjLocal
from rapuma.core.proj_log           import ProjLog
from rapuma.project.proj_config     import Config

###############################################################################
################################## Begin Class ################################
###############################################################################

class Project (object) :

    def __init__(self, pid, gid) :
        '''Instantiate this class.'''

        self.pid                    = pid
        self.gid                    = gid
        self.user                   = UserConfig()
        self.userConfig             = self.user.userConfig
        self.projHome               = os.path.join(self.userConfig['Resources']['projects'], self.pid)
        self.config                 = Config(self.pid)
        self.config.getProjectConfig()
        self.projectConfig          = self.config.projectConfig
        self.cType                  = self.projectConfig['Groups'][self.gid]['cType']
        self.Ctype                  = self.cType.capitalize()
        self.local                  = ProjLocal(pid, gid, self.cType)
        self.log                    = ProjLog(self.pid)
        self.tools                  = Tools()
        self.groups                 = {}
        self.components             = {}
        self.managers               = {}
        self.projectMediaIDCode     = self.projectConfig['ProjectInfo']['projectMediaIDCode']
        self.projectIDCode          = self.projectConfig['ProjectInfo']['projectIDCode']
        self.projectName            = self.projectConfig['ProjectInfo']['projectTitle']
        self.plid                   = self.projectConfig['ProjectInfo']['languageCode']
        self.psid                   = self.projectConfig['ProjectInfo']['scriptCode']
        
        # The gid cannot generally be set yet but we will make a placeholder
        # for it here and the functions below will set it. (I'm just say'n)

#        import pdb; pdb.set_trace()

        m = import_module('rapuma.manager.' + self.projectMediaIDCode)
        self.__class__ = getattr(m, self.projectMediaIDCode[0].upper() + self.projectMediaIDCode[1:])

        # Update the existing config file with the project type XML file
        # if needed
        newXmlDefaults = os.path.join(self.local.rapumaConfigFolder, self.projectMediaIDCode + '.xml')
        xmlConfig = self.tools.getXMLSettings(newXmlDefaults)
        newConf = ConfigObj(xmlConfig.dict(), encoding='utf-8').override(self.projectConfig)
        for s,v in self.projectConfig.items() :
            if s not in newConf :
                newConf[s] = v

        # Replace with new conf if new is different from old
        # Rem new conf doesn't have a filename, give it one
        if self.projectConfig != newConf :
            self.projectConfig = newConf
            self.projectConfig.filename = self.local.projectConfFile

        # Log messages for this module
        self.errorCodes     = {
            'PROJ-000' : ['MSG', 'Project module messages'],
            'PROJ-030' : ['MSG', 'Changed  [<<1>>][<<2>>][<<3>>] setting from \"<<4>>\" to \"<<5>>\".'],
            'PROJ-040' : ['ERR', 'Problem making setting change. Section [<<1>>] missing from configuration file.'],
            'PROJ-050' : ['ERR', 'Component [<<1>>] working text file was not found in the project configuration.'],
            'PROJ-060' : ['ERR', 'Component [<<1>>] was not found in the project configuration.'],
            'PROJ-070' : ['ERR', 'Source file not found: [<<1>>].'],
            'PROJ-080' : ['MSG', 'Successful copy of [<<1>>] to [<<2>>].'],
            'PROJ-090' : ['ERR', 'Target file [<<1>>] already exists. Use force (-f) to overwrite.'],

            '0205' : ['LOG', 'Created the [<<1>>] manager object.'],
            '0210' : ['LOG', 'Wrote out [<<1>>] settings to the project configuration file.'],
            '0211' : ['ERR', 'Failed to write out project [<<1>>] settings to the project configuration file.'],

            '0660' : ['ERR', 'Invalid component ID: [<<1>>].'],

        }

###############################################################################
############################ Manager Level Functions ##########################
###############################################################################
######################## Error Code Block Series = 200 ########################
###############################################################################

    def createManager (self, mType) :
        '''Check to see if a manager is listed in the config and load it if
        it is not already.'''

        fullName = self.cType + '_' + mType.capitalize()
        if fullName not in self.managers :
            self.addManager(mType)
            self.loadManager(mType)
            self.log.writeToLog(self.errorCodes['0205'], [fullName])


    def loadManager (self, mType) :
        '''Do basic load on a manager.'''

        fullName = self.cType + '_' + mType.capitalize()
        cfg = self.projectConfig['Managers'][fullName]
        module = import_module('rapuma.manager.' + mType)
        ManagerClass = getattr(module, mType.capitalize())
        manobj = ManagerClass(self, cfg, self.cType)
        self.managers[fullName] = manobj


    def addManager (self, mType) :
        '''Create a manager reference in the project config that components
        will point to.'''

#        import pdb; pdb.set_trace()

        fullName = self.cType + '_' + mType.capitalize()
        managerDefaults = None
        # Insert the Manager section if it is not already there
        self.tools.buildConfSection(self.projectConfig, 'Managers')
        if not self.projectConfig['Managers'].has_key(fullName) :
            self.tools.buildConfSection(self.projectConfig['Managers'], fullName)

        # Update settings if needed
        update = False
        managerDefaults = self.tools.getXMLSettings(os.path.join(self.local.rapumaConfigFolder, mType + '.xml'))
        for k, v, in managerDefaults.iteritems() :
            # Do not overwrite if a value is already there
            if not self.projectConfig['Managers'][fullName].has_key(k) :
                self.projectConfig['Managers'][fullName][k] = v
                # If we are dealing with an empty string, don't bother writing out
                # Trying to avoid needless conf updating here. Just in case we are
                # working with a list, we'll use len()
                if len(v) > 0 :
                    update = True
        # Update the conf if one or more settings were changed
        if update :
            if self.tools.writeConfFile(self.projectConfig) :
                self.log.writeToLog(self.errorCodes['0210'],[fullName])
            else :
                self.log.writeToLog(self.errorCodes['0211'],[fullName])


###############################################################################
############################ Group Level Functions ############################
###############################################################################
####################### Error Code Block Series = 0600 ########################
###############################################################################


    def renderGroup (self, cidList = '', pages = '', override = '', save = False) :
        '''Render a group of subcomponents or any number of components
        in the group specified in the cidList.'''

#        import pdb; pdb.set_trace()

        # If there are any cids listed we need to test them
        if cidList :
            self.isValidCidList(cidList)

        # Otherwise, do a basic test for exsistance and move on
        if self.projectConfig['Groups'].has_key(self.gid) :
            # Now create the group and pass the params on
            self.createGroup().render(self.gid, cidList, pages, override, save)
            return True


    def createGroup (self) :
        '''Create a group object that can be acted on. It is assumed
        this only happens for one group per session. This group
        will contain one or more compoenents. The information for
        each one will be contained in the group object.'''

#        import pdb; pdb.set_trace()

        # If the object already exists just return it
        if self.gid in self.groups: 
            return self.groups[self.gid]

        cType = self.projectConfig['Groups'][self.gid]['cType']
        # Create a special component object if called
        cfg = self.projectConfig['Groups'][self.gid]
        module = import_module('rapuma.group.' + cType)
        ManagerClass = getattr(module, cType.capitalize())
        groupObj = ManagerClass(self, cfg)
        self.groups[self.gid] = groupObj

        return groupObj


    def isValidCidList (self, thisCidlist) :
        '''Check to see if all the components in the list are in the group.'''

        cidList = self.projectConfig['Groups'][self.gid]['cidList']
        for cid in thisCidlist :
            # If this is not a usfm type we do not need to validate
            if self.cType == 'usfm' :
                if not cid in cidList :
                    self.log.writeToLog(self.errorCodes['0660'],[cid])


    def listAllComponents (self, cType) :
        '''Generate a list of valid component IDs and cNames for this cType.'''

        # Create the component object now with a special component caller ID
        self.createComponent('usfm_internal_caller')
        # Get the component info dictionary
        comps = self.components['usfm_internal_caller'].usfmCidInfo()
        # List and sort
        cList = list(comps.keys())
        cList.sort()
        # For now we'll output to terminal but may want to change this later.
        for c in cList :
            if c != '_z_' :
                print c, comps[c][1]


###############################################################################
############################ System Level Functions ###########################
###############################################################################

    def run (self, command, opts, userConfig) :
        '''Run a command'''

        if command in self.commands :
            self.commands[command].run(opts, self, userConfig)
        else :
            self.tools.terminalError('The command: [' + command + '] failed to run with these options: ' + str(opts))


