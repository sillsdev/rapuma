#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project illustration tasks.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, codecs
from configobj                      import ConfigObj

# Load the local classes
from rapuma.core.tools              import Tools
from rapuma.manager.manager         import Manager
from rapuma.project.proj_config     import Config
from rapuma.core.proj_local         import ProjLocal
from rapuma.core.proj_log           import ProjLog
from rapuma.core.user_config        import UserConfig

###############################################################################
################################## Begin Class ################################
###############################################################################

class ProjIllustration (object) :

    def __init__(self, pid, gid) :
        '''Do the primary initialization for this class.'''

        self.pid                        = pid
        self.gid                        = gid
        self.tools                      = Tools()
        self.local                      = ProjLocal(pid)
        self.user                       = UserConfig()
        self.userConfig                 = self.user.userConfig
        self.proj_config                = Config(pid, gid)
        self.proj_config.getProjectConfig()
        self.proj_config.getLayoutConfig()
        self.proj_config.getIllustrationConfig()
        self.projectConfig              = self.proj_config.projectConfig
        self.layoutConfig               = self.proj_config.layoutConfig
        self.illustrationConfig         = self.proj_config.illustrationConfig
        self.cType                      = self.projectConfig['Groups'][gid]['cType']
        self.Ctype                      = self.cType.capitalize()
        self.macPack                    = None
        self.macPackConfig              = None
        if self.projectConfig['CompTypes'][self.Ctype].has_key('macroPackage') and self.projectConfig['CompTypes'][self.Ctype]['macroPackage'] != '' :
            self.macPack                = self.projectConfig['CompTypes'][self.Ctype]['macroPackage']
            self.proj_config.getMacPackConfig(self.macPack)
            self.macPackConfig          = self.proj_config.macPackConfig
        self.log                        = ProjLog(pid)
        self.backgroundTypes            = ['watermark', 'lines']
        # Get some config settings
        self.userIllustrationLibName    = self.illustrationConfig['GeneralSettings'].get('userIllustrationLibName')
        # If we have nothing in the project for pointing to an illustration
        # lib, put the default in here
        if not self.userIllustrationLibName :
            self.userIllustrationLibName = self.userConfig['Resources']['defaultIllustrationLibraryName']
            self.illustrationConfig['GeneralSettings']['userIllustrationLibName'] = self.userIllustrationLibName
            self.tools.writeConfFile(self.projectConfig)

        # File names

        # Folder paths
        self.projComponentFolder        = self.local.projComponentFolder
        self.projIllustrationFolder     = self.local.projIllustrationFolder
        self.userIllustrationLibFolder  = self.userConfig['Resources']['illustration']
        self.userIllustrationLib        = os.path.join(self.userIllustrationLibFolder, self.userIllustrationLibName)
        self.projConfFolder             = self.local.projConfFolder
        # File names with folder paths


        # Log messages for this module
        self.errorCodes     = {
            '0000' : ['MSG', 'Placeholder message'],
            '0010' : ['ERR', 'Component type [<<1>>] not recognized!'],
            '0240' : ['ERR', 'Failed to copy [<<1>>] into the project illustration folder.'],
            '0220' : ['LOG', 'Copied [<<1>>] into the project illustration folder. Force was set to [<<2>>].'],
            '0230' : ['LOG', 'Did not copy [<<1>>] into the project illustration folder. File already exsits.'],
            '0265' : ['LOG', 'Piclist file for [<<1>>] has been created.'],

            'ILUS-000' : ['MSG', 'Illustration module messages'],
            'ILUS-010' : ['LOG', 'Wrote out new illustration configuration file. (illustration.__init__())'],
            'ILUS-050' : ['LOG', 'Removed [<<1>>] from the project illustration folder.'],
            'ILUS-055' : ['LOG', 'Illustration not being used. The piclist file has been removed from the [<<1>>] component folder.'],
            'ILUS-060' : ['LOG', 'Piclist file for [<<1>>] already exsits. File not created.'],
            'ILUS-070' : ['WRN', 'Watermark file [<<1>>] not found in illustration folder. Will try to revert to default watermark.'],
            'ILUS-080' : ['LOG', 'Installed watermark file [<<1>>] into the project.'],
            'ILUS-090' : ['LOG', 'Changed watermark config file name to [<<1>>].'],
            'ILUS-100' : ['ERR', 'Unknown background file type: [<<1>>]'],
        }

###############################################################################
############################ Illustration Functions ###########################
###############################################################################
######################## Error Code Block Series = 0200 #######################
###############################################################################


    def installIllustrationFile (self, fileName, path = None, force = False) :
        '''Install into the project the specified illustration file. If
        force is not set to True and no path has been specified, this 
        function will look into the project Illustration folder first.
        Failing that, it will look in the user resources illustration
        folder, and if found, copy it into the project. If a path is
        specified it will look there first and use that file.'''

#        import pdb; pdb.set_trace()

        # Set some file names/paths
        places = []
        if path :
            places.append(os.path.join(path, fileName))
        places.append(os.path.join(self.tools.resolvePath(self.userIllustrationLib), fileName))
        target = os.path.join(self.projIllustrationFolder, fileName)
        # See if the file is there or not
        for p in places :
            if os.path.isfile(p) :
                if force :
                    if not shutil.copy(p, target) :
                        self.log.writeToLog(self.errorCodes['0220'], [self.tools.fName(p),'True'])
                        return True
                else :
                    if not os.path.isfile(target) :
                        if not shutil.copy(p, target) :
                            self.log.writeToLog(self.errorCodes['0220'], [self.tools.fName(p),'False'])
                            return True
                    else :
                        self.log.writeToLog(self.errorCodes['0230'], [self.tools.fName(p)])
                        return True

        # No joy, we're hosed
        self.log.writeToLog(self.errorCodes['0240'], [self.tools.fName(p)])


    def getPics (self, gid, cid) :
        '''Figure out what pics/illustration we need for a given
        component and install them. It is assumed that this was 
        called because the user wants illustration. Therefore, 
        this will kill the current session if it fails.'''

        for i in self.illustrationConfig[gid].keys() :
            if self.illustrationConfig[gid][i]['bid'] == cid :
                fileName = self.illustrationConfig[gid][i]['fileName']
                if not os.path.isfile(os.path.join(self.projIllustrationFolder, fileName)) :
                    self.installIllustrationFile (fileName, '', False)


    def removeIllustrationFile (self, fileName) :
        '''Remove an Illustration file from the project and conf file.'''

        # Remove the file
        projIll = os.path.join(self.projIllustrationFolder, fileName)
        if os.path.isfile(projIll) :
            os.remove(projIll)
            self.log.writeToLog('ILUS-050', [fileName])

        # Check to see if this is a watermark file, if it is, remove config setting
        if self.projectConfig['CompTypes'][self.Ctype].has_key('pageWatermarkFile') :
            org = self.projectConfig['CompTypes'][self.Ctype]['pageWatermarkFile']
            if org == fileName :
                self.projectConfig['CompTypes'][self.Ctype]['pageWatermarkFile'] = ''
                self.tools.writeConfFile(self.projectConfig)


    def hasIllustrations (self, gid, bid) :
        '''Return True if this component as any illustration associated with it.'''

        # Adjustment for Map cType
        if self.cType == 'map' :
            bid = 'map'

        # If we are missing the bid we fail (gracefully)
        try :
            for i in self.illustrationConfig[gid].keys() :
                if self.illustrationConfig[gid][i]['bid'] == bid :
                    return True
        except :
            return False


    def getCidPiclistFile (self, cid) :
        '''Return the full path of the cName working text illustration file. 
        This assumes the cName is valid.'''

        return os.path.join(self.local.projComponentFolder, cid, cid + '_base.' + self.cType + '.piclist')


    def createPiclistFile (self, gid, cid) :
        '''Look in the cid for \fig data. Extract it from the cid and
        use it to create a piclist file for this specific cid. If
        there is no \fig data no piclist file will be made.'''

#        import pdb; pdb.set_trace()

        cType = self.projectConfig['Groups'][gid]['cType']
        if cType == 'usfm' :
            piclistFile = self.getCidPiclistFile(cid)
        elif cType == 'map' :
            piclistFile = self.getCidPiclistFile(gid)
        else :
            self.log.writeToLog(self.errorCodes['0010'], [cType])
        
        cvSep = self.macPackConfig['Illustrations']['chapterVerseSeperator']
        thisRef = ''
        trueCid = cid
        obj = {}

        # Change cid for map cType
        # Note: The piclist IDs must be three characters long but need not be recognized USFM
        # file IDs. As such, we adjust the code to recognize 'map' as our ID for map rendering
        # operations. This seems to work for now.
#        if self.cType == 'map' :
#            cid = 'map'

        with codecs.open(piclistFile, "w", encoding='utf_8') as writeObject :
            writeObject.write('% This is an auto-generated usfmTex piclist file for this project.\n')
            writeObject.write('% Do not bother editing this file.\n\n')

            for i in self.illustrationConfig[gid].keys() :
                obj = self.illustrationConfig[gid][i]
                thisRef = ''
                # Filter out if needed with this
                if not self.tools.str2bool(obj['useThisIllustration']) :
                    continue
                # Is a caption going to be used on this illustration?
                caption = ''
                if self.illustrationConfig[gid][i]['bid'] == cid :
                    if self.tools.str2bool(self.layoutConfig['DocumentFeatures']['useCaptions']) \
                        and self.tools.str2bool(self.illustrationConfig[gid][i]['useThisCaption']) :
                        if obj['caption'] :
                            caption = obj['caption']
                # Work out if we want a caption reference or not for this illustration
                if self.illustrationConfig[gid][i]['bid'] == cid :
                    if self.tools.str2bool(self.layoutConfig['DocumentFeatures']['useCaptionReferences']) \
                        and self.tools.str2bool(self.illustrationConfig[gid][i]['useThisCaptionRef']) :
                        if obj['location'] :
                            thisRef = obj['location']
                        else :
                            thisRef = obj['chapter'] + cvSep + obj['verse']

                    # If we made it this far we can output the line
                    writeObject.write(obj['bid'] + ' ' + obj['chapter'] + '.' + obj['verse'] + \
                        ' |' + obj['fileName'] + '|' + obj['width'] + '|' + obj['position'] + \
                            '|' + obj['scale'] + '|' + obj['copyright'] + '|' + caption + '|' + thisRef + ' \n')
        # Report to log
        self.log.writeToLog(self.errorCodes['0265'], [trueCid])
        return True



