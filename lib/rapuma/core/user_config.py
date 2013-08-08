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

import codecs, os, sys
from configobj import ConfigObj

# Load the local classes
from rapuma.core.tools          import Tools


class UserConfig (object) :

    def __init__(self) :
        '''Intitate the whole class and create the object.'''

        self.rapumaHome         = os.environ.get('RAPUMA_BASE')
        self.userHome           = os.environ.get('RAPUMA_USER')
        self.userConfFile       = os.path.join(self.userHome, 'rapuma.conf')
        self.tools              = Tools()

        # Check to see if the file is there, then read it in and break it into
        # sections. If it fails, scream really loud!
        rapumaXMLDefaults = os.path.join(self.rapumaHome, 'config', 'rapuma.xml')
        if os.path.exists(rapumaXMLDefaults) :
            self.tools.sysXmlConfig = self.tools.xml_to_section(rapumaXMLDefaults)
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
        newConfig = ConfigObj(self.tools.sysXmlConfig.dict(), encoding='utf-8').override(self.userConfig)

        # Put back the copied data of any project information that we might have
        # lost from the XML/conf file merging.
        if userProjs :
            newConfig['Projects'] = userProjs

        # Do not bother writing if nothing has changed
        if not self.userConfig.__eq__(newConfig) :
            self.userConfig = newConfig
            self.userConfig.filename = self.userConfFile
            self.userConfig.write()

        # Log messages for this module
        self.errorCodes     = {
            '0000' : ['MSG', 'Placeholder message'],
        }

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
            self.userConfig['System']['initDate'] = self.tools.tStamp()
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

        self.tools.buildConfSection(self.userConfig, 'Projects')
        self.tools.buildConfSection(self.userConfig['Projects'], pid)

        # Now add the project data
        self.userConfig['Projects'][pid]['projectName']         = pname
        self.userConfig['Projects'][pid]['projectMediaIDCode']  = pmid
        self.userConfig['Projects'][pid]['projectPath']         = projHome
        self.userConfig['Projects'][pid]['projectCreateDate']   = self.tools.tStamp()

        self.userConfig.write()
        return True


    def unregisterProject (self, pid) :
        '''Remove a project from the user config file.'''
        
#        import pdb; pdb.set_trace()
        
        del self.userConfig['Projects'][pid]
        self.userConfig.write()
        
        # Check to see if we were succeful
        if not self.userConfig['Projects'].has_key(pid) :
            return True


    def setSystemSettings (self, section, key, value) :
        '''Function to make system settings.'''

        oldValue = self.userConfig[section][key]
        if oldValue != value :
            self.userConfig[section][key] = value
            # Write out the results
            self.userConfig.write()
            self.tools.terminal('\nRapuma user name setting changed from [' + oldValue + '] to [' + value + '].\n\n')
        else :
            self.tools.terminal('\nSame value given, nothing to changed.\n\n')


    def makeDefaultFolders (self) :
        '''Setup the default Rapuma resource folders.'''

        # Get the user config project folder location
        if not os.path.exists(self.tools.resolvePath(self.userConfig['Resources']['projects'])) :
            sys.exit('\nERROR: Invalid projects folder path: ' + self.userConfig['Resources']['projects'] + '\n\nProcess halted.\n')
        else :
            projects = self.tools.resolvePath(self.userConfig['Resources']['projects'])
            self.userConfig['Resources']['projects'] = projects

        # Get the user config Rapuma resouce folder location
        if self.userConfig['Resources']['rapumaResouce'] == '' :
            rapumaResouce = os.path.join(projects, 'Rapuma')
            self.userConfig['Resources']['rapumaResouce'] = rapumaResouce
        elif not os.path.exists(self.tools.resolvePath(self.userConfig['Resources']['rapumaResouce'])) :
            sys.exit('\nERROR: Invalid Rapuma resource folder path: ' + self.userConfig['Resources']['rapumaResouce'] + '\n\nProcess halted.\n')
        else :
            rapumaResouce = self.tools.resolvePath(self.userConfig['Resources']['rapumaResouce'])
            self.userConfig['Resources']['rapumaResouce'] = rapumaResouce
     
        # Make a list of sub-folders to make in the Rapuma resourcs folder
        resourceFolders = ['archive', 'backup', 'cloud', 'font', 'illustration', \
                            'macro','script', 'template']
        for r in resourceFolders :
            thisPath = os.path.join(rapumaResouce, r)
            if self.userConfig['Resources'].has_key(r) and self.userConfig['Resources'][r] != '' :
                if os.path.exists(self.userConfig['Resources'][r]) :
                    self.tools.terminal('Warning: Cannot create, ' + r + ' folder already exists at: ' + self.userConfig['Resources'][r])
            else :
                # Create the folder if needed
                if not os.path.isdir(thisPath) :
                    os.makedirs(thisPath)

                # Record the path
                self.userConfig['Resources'][r] = thisPath

        # Write out the results
        self.userConfig.write()
        self.tools.terminal('\nRapuma resource folder setting created/updated.\n\n')




