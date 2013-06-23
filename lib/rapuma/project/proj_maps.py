
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
from configobj                          import ConfigObj, Section
from functools                          import partial

# Load the local classes
from rapuma.core.tools                  import Tools, ToolsPath, ToolsGroup
from rapuma.core.user_config            import UserConfig
from rapuma.core.proj_local             import ProjLocal
from rapuma.core.proj_log               import ProjLog
from rapuma.core.paratext               import Paratext
from rapuma.manager.project             import Project
from rapuma.project.proj_config         import ProjConfig


###############################################################################
################################## Begin Class ################################
###############################################################################

class ProjMaps (object) :

    def __init__(self, pid, gid) :
        '''Do the primary initialization for this class.'''

        self.pid                        = pid
        self.gid                        = gid
        self.tools                      = Tools()
        self.user                       = UserConfig()
        self.userConfig                 = self.user.userConfig
        self.projHome                   = self.userConfig['Projects'][self.pid]['projectPath']
        self.mType                      = self.userConfig['Projects'][self.pid]['projectMediaIDCode']
        self.local                      = ProjLocal(pid)
        self.projConfig                 = ProjConfig(pid).projConfig
        self.log                        = ProjLog(pid)
        self.tools_path                 = ToolsPath(self.local, self.projConfig, self.userConfig)
        self.tools_group                = ToolsGroup(self.local, self.projConfig, self.userConfig)
        self.paratext                   = Paratext(pid)
        # File names
        self.illustrationConfFileName   = 'illustration.conf'
        self.gidTexFileName             = self.gid + '.tex'
        # Folder paths
        self.projConfFolder             = self.local.projConfFolder
        self.projComponentsFolder       = self.local.projComponentsFolder
        self.projIllustrationsFolder    = self.local.projIllustrationsFolder
        self.gidFolder                  = os.path.join(self.projComponentsFolder, gid)
        # File names with paths
        self.illustrationConfFile       = os.path.join(self.projConfFolder, self.illustrationConfFileName)
        self.gidTexFile                 = os.path.join(self.gidFolder, self.gidTexFileName)

        # Load the maps settings config object
        self.illustrationConfig         = ConfigObj(self.illustrationConfFile, encoding='utf-8')

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

            '0825' : ['MSG', 'Rendering of [<<1>>] successful.'],
            '0830' : ['ERR', 'Rendering [<<1>>] was unsuccessful. <<2>> (<<3>>)'],
            '0835' : ['ERR', 'XeTeX error code [<<1>>] not understood by Rapuma.'],
            '0840' : ['MSG', 'Rendered the project maps for group: [<<1>>].'],
            '0860' : ['ERR', 'Invalid map component ID: [<<1>>].'],

        }

        # A source path is often important, try to get that now
        try :
            self.csid                   = self.projConfig['Groups'][self.gid]['csid']
            self.cType                  = self.projConfig['Groups'][self.gid]['cType']
            self.sourcePath             = self.userConfig['Projects'][self.pid][self.csid + '_sourcePath']
        except :
            pass


###############################################################################
################################ Add Functions ################################
###############################################################################
######################## Error Code Block Series = 0200 #######################
###############################################################################

# FIXME? This is a duplicate of a function of the same name in proj_setup but
# because this changes the config obj I copied it here to save on confusion
    def addComponentType (self, cType) :
        '''Add (register) a component type to the config if it 
        is not there already.'''

        Ctype = cType.capitalize()
        # Build the comp type config section
        self.tools.buildConfSection(self.projConfig, 'CompTypes')
        self.tools.buildConfSection(self.projConfig['CompTypes'], Ctype)

        # Get persistant values from the config if there are any
        newSectionSettings = self.tools.getPersistantSettings(self.projConfig['CompTypes'][Ctype], os.path.join(self.local.rapumaConfigFolder, cType + '.xml'))
        if newSectionSettings != self.projConfig['CompTypes'][Ctype] :
            self.projConfig['CompTypes'][Ctype] = newSectionSettings
            # Save the setting rightaway
            self.tools.writeConfFile(self.projConfig)


    def addGroup (self, mapFileList, csid, csidPath, force = False) :
        '''Add maps to the project.'''

        # First be sure the component type exists in the conf
        self.projConfig = self.tools.addComponentType(self.projConfig, self.local, 'map')

#        import pdb; pdb.set_trace()
        
        # First test for the map component files
        pgOrder = 0
        for fileName in mapFileList :
            pgOrder +=1
            filePath = os.path.join(csidPath, fileName)
            if not os.path.exists(filePath) :
                self.log.writeToLog(self.errorCodes['0205'], [filePath])
            else :
                self.addIllustration(fileName, csidPath, pgOrder, force)

        # Having made it this far we can output information to the project config
        cidList = self.illustrationConfig[self.gid].keys()
        self.createGroupFolder()
        self.createMapGroupStyleFile(force)
        self.tools.buildConfSection(self.projConfig, 'Groups')
        self.projConfig['Groups'][self.gid] = {}
#        self.projConfig['Groups'][self.gid]['cidList'] = cidList
        self.projConfig['Groups'][self.gid]['cidList'] = [self.gid]
        self.projConfig['Groups'][self.gid]['startPageNumber'] = 1
        self.projConfig['Groups'][self.gid]['cType'] = 'map'
        self.projConfig['Groups'][self.gid]['isLocked'] = True
        self.projConfig['Groups'][self.gid]['csid'] = csid
        self.projConfig['Groups'][self.gid]['totalPages'] = pgOrder
        self.projConfig['Groups'][self.gid]['precedingGroup'] = None
        self.projConfig['Groups'][self.gid]['bindingOrder'] = 0
        self.tools.buildConfSection(self.projConfig, 'Managers')
        self.tools.buildConfSection(self.projConfig['Managers'], 'map_Xetex')
        self.projConfig['Managers']['map_Xetex']['draftBackground'] = ['draftWatermark']
        self.tools.writeConfFile(self.projConfig)

        # Make a container file for the images
        self.createComponentContainerFile(cidList, force)

        # Add map group source path to userConfig
        self.userConfig['Projects'][self.pid][csid + '_sourcePath'] = csidPath
        self.tools.writeConfFile(self.userConfig)

        self.log.writeToLog(self.errorCodes['0220'], [self.gid])


    def addIllustration (self, fileName, filePath, pgOrder, force) :
        '''Add a single map component to a group.'''

#        import pdb; pdb.set_trace()

        # Because we use are using the paratext.logFigure()
        # function we need to format the figConts manually
        # so it gets what it expects
        cid = os.path.splitext(fileName)[0]
        figConts = 'some text\\fig Map file for: ' + self.gid + '|' + fileName + '|span|b|SIL International 2013|None|MAP 1:1 \\fig* some more text'
        # Put the map (illustration) into the config file
        # This is a really dumb way to do this but this is how
        # logFigure() is expecting to see the data
        re.sub(r'\\fig\s(.+?)\\fig\*', partial(self.paratext.logFigure, self.gid, cid), figConts)

        # Reload the illustrationConfFile
        self.illustrationConfig         = ConfigObj(self.illustrationConfFile, encoding='utf-8')

        # Modify this entry in the illustration config file
#        self.illustrationConfig[self.gid][cid]['pageOrder'] = pgOrder
        self.illustrationConfig[self.gid][cid]['bid'] = 'map'
        self.illustrationConfig[self.gid][cid]['location'] = ''
        self.illustrationConfig[self.gid][cid]['position'] = 'b'
        self.illustrationConfig[self.gid][cid]['scale'] = '0.75'
        self.illustrationConfig[self.gid][cid]['chapter'] = pgOrder
        self.tools.writeConfFile(self.illustrationConfig)
        # Copy the file into the project illustration folder
        if not os.path.exists(self.projIllustrationsFolder) :
            os.makedirs(self.projIllustrationsFolder)
        shutil.copy(os.path.join(filePath, fileName), os.path.join(self.projIllustrationsFolder, fileName))

         # Create a component folder and its contents
#        self.createComponentFolder(cid)
#        self.createComponentContainerFile(cid, force)

        self.log.writeToLog(self.errorCodes['0225'], [cid,self.gid])


    def createGroupFolder (self) :
        '''Create a project maps folder if one is not there.'''

        folder = os.path.join(self.projComponentsFolder, self.gid)
        if not os.path.exists(folder) :
            os.makedirs(folder)
            self.log.writeToLog(self.errorCodes['0250'], [self.gid])


#    def createComponentFolder (self, cid) :
#        '''Create a project maps folder if one is not there.'''

#        folder = os.path.join(self.projComponentsFolder, cid)
#        if not os.path.exists(folder) :
#            os.makedirs(folder)
#            self.log.writeToLog(self.errorCodes['0260'], [cid])


    def getGidContainerFileName (self) :
        '''Create the gid container file name. '''

        return 'map' + '_' + self.projConfig['Groups'][self.gid]['csid'] + '.map'


    def getGidContainerFile (self) :
        '''Create the gid container file name. '''

        return os.path.join(self.projComponentsFolder, self.gid, self.getGidContainerFileName())


    def createComponentContainerFile (self, cidList, force) :
        '''Create the map component container file. This is a usfm-like
        file that will guide the rendering process. Because we look at
        map processing different than text, this file is auto-generated.'''

        gidFile = self.getGidContainerFile()
        if not os.path.exists(gidFile) or force :
            contents = codecs.open(gidFile, "w", encoding="utf_8_sig")
            contents.write('\\id map - ' + self.tools.fName(gidFile) + '\n')
            contents.write('\\rem Auto-generated map rendering file. Edit as needed.\n')
            contents.write('\\rem Generated on: ' + self.tools.tStamp() + '\n\n')
            pgCount = 1
            for cid in cidList :
                title = self.illustrationConfig[self.gid][cid]['caption']
                contents.write('\\mt1 ' + title + '\n')
                contents.write('\\c ' + str(pgCount) + '\n')
                contents.write('\\p\n')
                contents.write('\\v 1 \\nbsp\n')
                contents.write('\\eject\n\n')
                pgCount +=1


    def createMapGroupStyleFile (self, force) :
        '''Create the map component container file. This is a usfm-like
        file that will guide the rendering process. Because we look at
        map processing different than text, this file is auto-generated.'''

        styFileName     = 'usfm-grp-ext.sty'
        styFile         = os.path.join(self.projComponentsFolder, self.gid, styFileName)

        # Lets start with just a simple file and go from there
        # This should go in before any other auto-generated sty
        # file so we should be good to go
        if not os.path.exists(styFile) or force :
            contents = codecs.open(styFile, "w", encoding="utf_8_sig")
            contents.write('# Auto-generated style file for map rendering. Edit as needed.\n')
            contents.write('# ' + styFileName + ' Generated on: ' + self.tools.tStamp() + '\n\n')
            contents.write('\\Marker v\n')
            contents.write('\\FontSize 0.2\n\n')
            contents.write('\\Marker mt1\n')
            contents.write('\\FontSize 14\n')
            contents.write('\\SpaceAfter 0\n')
            contents.write('\\SpaceBefore 0\n\n')
            contents.write('\\Marker p\n')
            contents.write('\\FontSize 0.2\n\n')


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
        if self.projConfig['Groups'].has_key(gid) :
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
            if self.userConfig['Projects'][self.pid].has_key(csid + '_sourcePath') :
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

    def renderMapGroup (self, mode, cidList = None, force = False) :
        '''Render a map or a set of maps.'''

        # Sort out the cid list
        if cidList :
            self.isValidCidList(cidList)
        else :
            cidList = self.projConfig['Groups'][self.gid]['cidList']

        # Be sure all the images are preprocessed
#        for cid in cidList :
#            self.preprocessImage(cid, force)

        # TeX rendering
        Project(self.pid, self.gid).renderGroup(mode, cidList, True)


        self.log.writeToLog(self.errorCodes['0840'], [self.gid])


    def isValidCidList (self, thisCidlist) :
        '''Check to see if all the components in the list are in the group.'''

        cidList = self.projConfig['Groups'][self.gid]['cidList']
        for cid in thisCidlist :
            if not cid in cidList :
                self.log.writeToLog(self.errorCodes['0860'],[cid])


    def preprocessImage (self, cid, force) :
        '''Use ImageMagick to preprocess a map image.'''
        
        # Create the file names we will need
        fileName = self.mapsConfig['Groups'][self.gid][cid]['mapFileName']
        inFile = os.path.join(self.projComponentsFolder, cid, fileName)
        outOne = os.path.join(self.projComponentsFolder, cid, fileName.replace('.png', '-1.png'))
        outTwo = os.path.join(self.projComponentsFolder, cid, fileName.replace('.png', '-2.png'))
        outThree = os.path.join(self.projComponentsFolder, cid, fileName.replace('.png', '.pdf'))

        # Create the ImageMagick rendering commands
        cmdOne = ['convert', '-border', '5', '-bordercolor', 'black', inFile, '-density', '150', '-rotate', '-90', outOne]
        cmdTwo = ['convert', outOne, '-border', '100', '-bordercolor', 'white', outTwo]
        cmdThree = ['convert', outTwo, '-format', 'pdf', outThree]

        # Run the processes
        processes = [cmdOne, cmdTwo, cmdThree]
        if not os.path.exists(outThree) or force :
            for cmd in processes :
                subprocess.call(cmd)



