
#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle map groups in book projects.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, codecs, re, subprocess, tempfile
from configobj                      import ConfigObj, Section

# Load the local classes
from rapuma.core.tools              import Tools, ToolsPath, ToolsGroup
from rapuma.core.proj_config        import ProjConfig
from rapuma.core.user_config        import UserConfig
from rapuma.core.proj_local         import ProjLocal
from rapuma.core.proj_log           import ProjLog
from rapuma.project.project         import Project


###############################################################################
################################## Begin Class ################################
###############################################################################

class Maps (object) :

    def __init__(self, pid) :
        '''Do the primary initialization for this manager.'''

        self.pid                        = pid
        self.tools                      = Tools()
        self.user                       = UserConfig()
        self.userConfig                 = self.user.userConfig
        self.projHome                   = self.userConfig['Projects'][self.pid]['projectPath']
        self.projectMediaIDCode         = self.userConfig['Projects'][self.pid]['projectMediaIDCode']
        self.local                      = ProjLocal(self.pid)
        self.projConfig                 = ProjConfig(self.local).projConfig
        self.log                        = ProjLog(self.pid)
        self.tools_path                 = ToolsPath(self.local, self.projConfig, self.userConfig)
        self.tools_group                = ToolsGroup(self.local, self.projConfig, self.userConfig)
        # File names
        self.mapsConfFileName           = 'maps.conf'
        # Paths
        self.projConfFolder             = self.local.projConfFolder
        self.projComponentsFolder       = self.local.projComponentsFolder
        # File names with paths
        self.mapsConfFile               = os.path.join(self.projConfFolder, self.mapsConfFileName)

        # Load the maps settings config object
        self.mapsConfig                 = ConfigObj(self.mapsConfFile, encoding='utf-8')

        # Log messages for this module
        self.errorCodes     = {

            '0050' : ['ERR', 'Map group [<<1>>] is locked, no action can be taken. Use force (-f) to override.'],

            '0205' : ['ERR', 'Cannot find: [<<1>>]'],
            '0210' : ['LOG', 'Wrote out map settings to the project configuration file.'],
            '0220' : ['MSG', 'Added map group [<<1>>] to project.'],
            '0225' : ['LOG', 'Added map component [<<1>>] to group [<<2>>].'],
            '0230' : ['MSG', 'Map group [<<1>>] has been removed from the project configuration.'],
            '0250' : ['LOG', 'Created map group folder: [<<1>>]'],
            '0260' : ['LOG', 'Created map component folder: [<<2>>]'],

            '0420' : ['MSG', 'Removed map group: [<<1>>]'],
            '0430' : ['WRN', 'Cannot removed map group: [<<1>>]'],
            '0460' : ['MSG', 'Map component [<<1>>] has been removed from the project.'],

            '0610' : ['ERR', 'No valid source path for this map group.'],
            '0620' : ['LOG', 'Reset source path for this map group: [<<1>>]'],
            '0630' : ['ERR', 'Component [<<1>>] is not a part of the [<<2>>] map group.'],
            '0640' : ['MSG', 'Component [<<1>>] part of the [<<2>>] map group has been updated.'],

            '0840' : ['MSG', 'Rendered the project maps.'],

        }


###############################################################################
################################ Add Functions ################################
###############################################################################
######################## Error Code Block Series = 0200 #######################
###############################################################################

#        import pdb; pdb.set_trace()

    def addGroup (self, gid, mapFileList, csid, csidPath, force = False) :
        '''Add maps to the project.'''

        # First test for the map component files
        pgOrder = 0
        for fileName in mapFileList :
            pgOrder +=1
            filePath = os.path.join(csidPath, fileName)
            if not os.path.exists(filePath) :
                self.log.writeToLog(self.errorCodes['0205'], [filePath])
            else :
                self.addComponent(gid, fileName, filePath, pgOrder)

        # Having made it this far we can output information to the project config
        self.createGroupFolder(gid)
        self.projConfig['Groups'][gid] = {}
        self.projConfig['Groups'][gid]['cidList'] = self.mapsConfig['Groups'][gid].keys()
        self.projConfig['Groups'][gid]['startPageNumber'] = 1
        self.projConfig['Groups'][gid]['cType'] = 'map'
        self.projConfig['Groups'][gid]['isLocked'] = True
        self.projConfig['Groups'][gid]['csid'] = csid
        self.projConfig['Groups'][gid]['totalPages'] = pgOrder
        self.projConfig['Groups'][gid]['precedingGroup'] = None
        self.projConfig['Groups'][gid]['bindingOrder'] = 0
        self.tools.writeConfFile(self.projConfig)
        # Add map group source path to userConfig
        self.userConfig['Projects'][self.pid][csid + '_sourcePath'] = csidPath
        self.tools.writeConfFile(self.userConfig)

        self.log.writeToLog(self.errorCodes['0220'], [gid])


    def addComponent (self, gid, fileName, filePath, pgOrder) :
        '''Add a single map component to a group.'''

        # Build a map file info dictionary
        mapInfo = {}
        mapInfo['Groups'] = {}
        mapInfo['Groups'][gid] = {}
        cid = os.path.splitext(fileName)[0].upper()
        mapInfo['Groups'][gid][cid] = {}
        mapInfo['Groups'][gid][cid]['mapFileName'] = fileName
        mapInfo['Groups'][gid][cid]['mapFileType'] = os.path.splitext(fileName)[1][1:].lower()
        mapInfo['Groups'][gid][cid]['pageTitle'] = 'Title: ' + cid
        mapInfo['Groups'][gid][cid]['usePageTitle'] = True
        mapInfo['Groups'][gid][cid]['pageOrder'] = pgOrder
        # Merge the info into the existing maps config file
        self.mapsConfig.merge(mapInfo)
        self.tools.writeConfFile(self.mapsConfig)
        # Create a component folder and copy the source into it
        self.createComponentFolder(cid)
        shutil.copy(os.path.join(filePath, fileName), os.path.join(self.projComponentsFolder, cid, fileName))
        self.log.writeToLog(self.errorCodes['0225'], [cid,gid])


    def createGroupFolder (self, gid) :
        '''Create a project maps folder if one is not there.'''

        folder = os.path.join(self.projComponentsFolder, gid)
        if not os.path.exists(folder) :
            os.makedirs(folder)
            self.log.writeToLog(self.errorCodes['0250'], [gid])


    def createComponentFolder (self, cid) :
        '''Create a project maps folder if one is not there.'''

        folder = os.path.join(self.projComponentsFolder, cid)
        if not os.path.exists(folder) :
            os.makedirs(folder)
            self.log.writeToLog(self.errorCodes['0260'], [cid])


###############################################################################
############################## Remove Functions ###############################
###############################################################################
######################## Error Code Block Series = 0400 #######################
###############################################################################

    def removeGroup (self, gid, force = False) :
        '''Remove the maps from a project.'''

        cidList         = self.projConfig['Groups'][gid]['cidList']
        cType           = self.projConfig['Groups'][gid]['cType']
        csid            = self.projConfig['Groups'][gid]['csid']
        groupFolder     = os.path.join(self.local.projComponentsFolder, gid)

        # First test for lock
        if self.tools_group.isLocked(gid) and force == False :
            self.log.writeToLog(self.errorCodes['0050'], [gid])

        # Remove subcomponents from the target if there are any
        self.tools.buildConfSection(self.projConfig, 'Groups')
        if self.tools.isConfSection(self.projConfig['Groups'], gid) :
            for cid in cidList :
                self.uninstallGroupComponent(gid, cid)
            if os.path.exists(groupFolder) :
                shutil.rmtree(groupFolder)
            # Now remove the config entry
            del self.projConfig['Groups'][gid]
            if self.tools.writeConfFile(self.projConfig) :
                # Clean up the maps config file
                del self.mapsConfig['Groups'][gid]
                self.tools.writeConfFile(self.mapsConfig)
                # Clean up the Rapuma config file
                del self.userConfig['Projects'][self.pid][csid + '_sourcePath']
                self.tools.writeConfFile(self.userConfig)
                self.log.writeToLog(self.errorCodes['0420'], [gid])
        else :
            self.log.writeToLog(self.errorCodes['0430'], [gid])


    def uninstallGroupComponent (self, gid, cid) :
        '''This will remove component map files from a group in the project.
        This assumes that it is okay to do this as the lock and force issues
        were handled by the calling function.'''

#       import pdb; pdb.set_trace()

        # Remove the files by removing the entire component folder
        targetFolder    = os.path.join(self.local.projComponentsFolder, cid)
        if os.path.exists(targetFolder) :
            shutil.rmtree(targetFolder)
            self.log.writeToLog(self.errorCodes['0460'], [cid])


###############################################################################
############################## Update Functions ###############################
###############################################################################
######################## Error Code Block Series = 0600 #######################
###############################################################################

    def updateGroup (self, gid, cidList = None, sourcePath = None, force = False) :
        '''Update a map group, --source is optional but if given it will
        overwrite the current setting.'''

#        import pdb; pdb.set_trace()

        # Just in case there are any problems with the source path
        # resolve it here before going on.
        csid        = self.projConfig['Groups'][gid]['csid']
        if not self.tools.resolvePath(sourcePath) :
            if self.tools.testForSetting(self.userConfig['Projects'][self.pid], csid + '_sourcePath') :
                sourcePath = self.userConfig['Projects'][self.pid][csid + '_sourcePath']
                if not os.path.exists(sourcePath) :
                    self.log.writeToLog(self.errorCodes['0610'], [csid])
        else :
            # Reset the source path for this csid
            self.userConfig['Projects'][self.pid][csid + '_sourcePath'] = sourcePath
            self.tools.writeConfFile(self.userConfig)
            self.log.writeToLog(self.errorCodes['0620'], [csid])

        # Sort out the list
        if not cidList :
            cidList = self.projConfig['Groups'][gid]['cidList']
        else :
            if type(cidList) != list :
                 cidList = cidList.split()
                 # Do a quick validity test
                 for cid in cidList :
                    if not cid in self.projConfig['Groups'][gid]['cidList'] :
                        self.log.writeToLog(self.errorCodes['0630'], [cid,gid])

        # Process each cid
        pgOrder = 0
        for cid in cidList :
            pgOrder +=1
            targetFolder    = os.path.join(self.local.projComponentsFolder, cid)
            fileName        = self.mapsConfig['Groups'][gid][cid]['mapFileName']
            target          = os.path.join(targetFolder, fileName)
            source          = os.path.join(sourcePath, fileName)

            if force :
                self.tools_group.lockUnlock(gid, False)
                self.uninstallGroupComponent(gid, cid)
                self.addComponent(gid, fileName, sourcePath, pgOrder)
                self.log.writeToLog(self.errorCodes['0640'], [cid,gid])
            else :
                self.log.writeToLog(self.errorCodes['0050'], [cid])

        # Now be sure the group is locked down before we go
        if self.projConfig['Groups'][gid]['isLocked'] == 'False' :
            self.tools_group.lockUnlock(gid, True)






###############################################################################
############################## Render Functions ###############################
###############################################################################
######################## Error Code Block Series = 0800 #######################
###############################################################################

    def renderMaps (self, mapFiles = None, force = False) :
        '''Render a map or a set of maps.'''

        self.log.writeToLog(self.errorCodes['0640'])







