#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110823
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle user configuration operations.

###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os
from configobj import ConfigObj

# Load the local classes
from rapuma.core.tools import *


class UserConfig (object) :

    def __init__(self, rapumaHome, userHome) :
        '''Intitate the whole class and create the object.'''

        self.rapumaHome     = rapumaHome
        self.userHome       = userHome
        self.userConfFile   = os.path.join(userHome, 'rapuma.conf')
        
        # Check to see if the file is there, then read it in and break it into
        # sections. If it fails, scream really loud!
        rapumaXMLDefaults = os.path.join(self.rapumaHome, 'config', 'rapuma.xml')
        if os.path.exists(rapumaXMLDefaults) :
            sysXmlConfig = xml_to_section(rapumaXMLDefaults)
        else :
            raise IOError, "Can't open " + rapumaXMLDefaults

        # Now make the users local rapuma.conf file if it isn't there
        if not os.path.exists(self.userConfFile) :
            self.initUserHome()

        # Load the Rapuma conf file into an object
        self.userConfig = ConfigObj(self.userConfFile, encoding='utf-8')

        # Look for any projects that might be registered and copy the data out
        try :
            userProjs = self.userConfig['Projects']
        except :
            userProjs = ''

        # Create a new conf object based on all the XML default settings
        # Then override them with any exsiting user settings.
        newConfig = ConfigObj(sysXmlConfig.dict(), encoding='utf-8').override(self.userConfig)

        # Put back the copied data of any project information that we might have
        # lost from the XML/conf file merging.
        if userProjs :
            newConfig['Projects'] = userProjs

        # Do not bother writing if nothing has changed
        if not self.userConfig.__eq__(newConfig) :
            self.userConfig = newConfig
            self.userConfig.filename = self.userConfFile
            self.userConfig.write()

###############################################################################
############################ User Config Functions ############################
###############################################################################


    def initUserHome (self) :
        '''Initialize a user config file on a new install or system re-init.'''

        # Create home folders
        if not os.path.isdir(self.userHome) :
            os.mkdir(self.userHome)

        # Make the default global rapuma.conf for custom environment settings
        if not os.path.isfile(self.userConfFile) :
            self.userConfig = ConfigObj(encoding='utf-8')
            self.userConfig.filename = self.userConfFile
            self.userConfig['System'] = {}
            self.userConfig['System']['userName'] = 'Default User'
            self.userConfig['System']['initDate'] = tStamp()
            self.userConfig.write()


    def isRegisteredProject (self, pid) :
        '''Check to see if this project is recorded in the user's config'''

        try :
            return pid in self.userConfig['Projects']
        except :
            pass


    def registerProject (self, pid, pname, pmid, projHome) :
        '''If it is not there, create an entry in the user's
        rapuma.conf located in the user's config folder.'''

        buildConfSection(self.userConfig, 'Projects')
        buildConfSection(self.userConfig['Projects'], pid)

        # Now add the project data
        self.userConfig['Projects'][pid]['projectName']         = pname
        self.userConfig['Projects'][pid]['projectMediaIDCode']  = pmid
        self.userConfig['Projects'][pid]['projectPath']         = projHome
        self.userConfig['Projects'][pid]['projectCreateDate']   = tStamp()
        # To hopefully prevent "Key not found" issues we will add a
        # blanked out source path setting for each component type
        # This may need to be changed at some point
        for cType in self.userConfig['System']['recognizedComponentTypes'] :
            self.userConfig['Projects'][pid][cType + '_sourcePath'] = None

        self.userConfig.write()
        return True


    def unregisterProject (self, pid) :
        '''Remove a project from the user config file.'''
        
        del self.userConfig['Projects'][pid]
        self.userConfig.write()
        
        # Check to see if we were succeful
        if not isConfSection(self.userConfig['Projects'], pid) :
            return True


    def setSystemSettings (self, cmdType, value) :
        '''Function to make system settings.'''

        if cmdType == 'userName' :
            oldName = self.userConfig['System']['userName']
            if oldName != value :
                self.userConfig['System']['userName'] = value
                # Write out the results
                self.userConfig.write()
                terminal('\nRapuma user name setting changed from [' + oldName + '] to [' + value + '].\n\n')
            else :
                terminal('\nSame name given, nothing to changed.\n\n')

        elif cmdType == 'resources' :
            # Before starting, check the path
            path = resolvePath(value)
            if not os.path.isdir(path) :
                sys.exit('\nERROR: Invalid path: '  + path + '\n\nProcess halted.\n')

            # Make a list of sub-folders to make in the Rapuma resources folder
            resources = ['archives', 'backups', 'fonts', 'examples', 'illustrations', 'macros', \
                            'scripts', 'templates']
            for r in resources :
                thisPath = os.path.join(path, 'Rapuma', r)
                # Create the folder if needed
                if not os.path.isdir(thisPath) :
                    os.makedirs(thisPath)

                # Copy in the Rapuma example zip files
                if r == 'examples' :
                    exampleFiles = os.listdir(self.local.rapumaExamplesFolder)
                    for f in exampleFiles :
                        try :
                            if f.split('.')[1].lower() == 'zip' :
                                shutil.copy(os.path.join(self.rapumaExamplesFolder, f), thisPath)
                        except :
                            pass
                    
                # Record the path
                self.userConfig['Resources'][r] = thisPath

            # Write out the results
            self.userConfig.write()
            terminal('\nRapuma resource folder setting created/updated.\n\n')




