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

# Load the local classes
from rapuma.core.tools              import Tools
from rapuma.manager.manager         import Manager
from rapuma.project.proj_config     import Config
from rapuma.project.proj_macro      import Macro
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
        self.proj_macro                 = Macro(pid, gid)
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
            self.proj_macro.getMacPackConfig(self.macPack)
            self.macPackConfig          = self.proj_macro.macPackConfig
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
            '0210' : ['WRN', 'Cannot copy [<<1>>] into the project Illustration folder. File already exists. Please use remove or update commands if the file needs to be replaced.'],
            '0220' : ['MSG', 'Copied [<<1>>] into the project Illustration folder.'],
            '0230' : ['ERR', 'Failed to Copy [<<1>>] into the project Illustration folder.'],
            '0240' : ['MSG', 'Illustration add operation complete!'],
            '0265' : ['LOG', 'Piclist file for [<<1>>] has been created.'],
            '0270' : ['WRN', 'Illustration file [<<1>>] not found in Illustration folder.'],

            '1010' : ['MSG', 'Removed illustration file [<<1>>] from project Illustration folder.'],
            '1020' : ['LOG', 'Request to removed illustration file [<<1>>] from project Illustration folder. File not found. Operation not complete'],
            '1030' : ['MSG', 'Illustration remove operation complete!'],

            '2010' : ['MSG', 'Updated illustration file [<<1>>] in project Illustration folder.'],
            '2020' : ['ERR', 'Update failed, file [<<1>>] not found in project Illustration folder. Use add illustration command to install the illustration.'],
            '2030' : ['ERR', 'Update failed on file [<<1>>]. Copy proceedure failed.'],
            '2040' : ['MSG', 'Illustration update operation complete!']

        }

###############################################################################
############################ Illustration Functions ###########################
###############################################################################
######################## Error Code Block Series = 0200 #######################
###############################################################################


    def addIllustrationFiles (self, path) :
        '''Import all the illustrations for a group that are found in
        the given path. This assumes illustrations are being used in
        one or more components in this group. Assumes valid path. Will
        fail if a copy doesn't succeed. If the file is already there,
        give a warning and do not copy.'''

        for i in self.illustrationConfig[self.gid].keys() :
            cid = self.illustrationConfig[self.gid][i]['bid']
            fileName = self.illustrationConfig[self.gid][i]['fileName']
            target = os.path.join(self.projIllustrationFolder, fileName)
            # Check to see if the target exists
            if not os.path.isfile(target) :
                source = os.path.join(path, fileName)
                if os.path.isfile(source) :
                    # Make sure we have a target dir
                    if not os.path.isdir(self.projIllustrationFolder) :
                        os.makedirs(self.projIllustrationFolder)
                    # Copy in the source to the project
                    if not shutil.copy(source, target) :
                        self.log.writeToLog(self.errorCodes['0220'], [self.tools.fName(source)])
                    # Double check that it happened
                    if not os.path.isfile(target) :
                        self.log.writeToLog(self.errorCodes['0230'], [self.tools.fName(source)])
            else :
                self.log.writeToLog(self.errorCodes['0210'], [self.tools.fName(target)])

        # If nothing above failed, we can return True now
        self.log.writeToLog(self.errorCodes['0240'])
        return True


    def missingIllustrations (self, bid) :
        '''Check for any missing illustration files for this component and
        report them. The assumption is that this component is supposed to
        have one or more illustrations in it so it should be used under
        hasIllustrations().'''
        
        missing = 0
        for i in self.illustrationConfig[self.gid].keys() :
            if self.illustrationConfig[self.gid][i]['bid'] == bid :
                fileName = self.illustrationConfig[self.gid][i]['fileName']
                target = os.path.join(self.local.projIllustrationFolder, fileName)
                if not os.path.exists(target) :
                    self.log.writeToLog(self.errorCodes['0270'], [fileName])
                    missing +=1

        # Returning True if something was missing
        if missing > 0 :
            return True


    def hasIllustrations (self, bid) :
        '''Return True if this component as any illustration associated with it.'''

        # Adjustment for Map cType
        if self.cType == 'map' :
            bid = 'map'

        # If we are missing the bid we fail (gracefully)
        try :
            for i in self.illustrationConfig[self.gid].keys() :
                if self.illustrationConfig[self.gid][i]['bid'] == bid :
                    return True
        except :
            return False


    def getCidPiclistFile (self, cid) :
        '''Return the full path of the cName working text illustration file. 
        This assumes the cName is valid.'''

        return os.path.join(self.local.projComponentFolder, cid, cid + '_base.' + self.cType + '.piclist')


    def createPiclistFile (self, cid) :
        '''Look in the cid for \fig data. Extract it from the cid and
        use it to create a piclist file for this specific cid. If
        there is no \fig data no piclist file will be made.'''

#        import pdb; pdb.set_trace()

        cType = self.projectConfig['Groups'][self.gid]['cType']
        if cType == 'usfm' :
            piclistFile = self.getCidPiclistFile(cid)
        elif cType == 'map' :
            piclistFile = self.getCidPiclistFile(self.gid)
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

            for i in self.illustrationConfig[self.gid].keys() :
                obj = self.illustrationConfig[self.gid][i]
                thisRef = ''
                # Filter out if needed with this
                if not self.tools.str2bool(obj['useThisIllustration']) :
                    continue
                # Is a caption going to be used on this illustration?
                caption = ''
                if self.illustrationConfig[self.gid][i]['bid'] == cid :
                    if self.tools.str2bool(self.layoutConfig['DocumentFeatures']['useCaptions']) \
                        and self.tools.str2bool(self.illustrationConfig[self.gid][i]['useThisCaption']) :
                        if obj['caption'] :
                            caption = obj['caption']
                # Work out if we want a caption reference or not for this illustration
                if self.illustrationConfig[self.gid][i]['bid'] == cid :
                    if self.tools.str2bool(self.layoutConfig['DocumentFeatures']['useCaptionReferences']) \
                        and self.tools.str2bool(self.illustrationConfig[self.gid][i]['useThisCaptionRef']) :
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


###############################################################################
######################## Illustration Remove Functions ########################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################

    def removeIllustrationFiles (self) :
        '''Remove all the illustration files from the illustration folder for
        a group. This does not affect the illustration.conf file.'''

        for i in self.illustrationConfig[self.gid].keys() :
            cid = self.illustrationConfig[self.gid][i]['bid']
            fileName = self.illustrationConfig[self.gid][i]['fileName']
            target = os.path.join(self.projIllustrationFolder, fileName)
            # Check to see if the target exists, then delete, skip if not there
            if os.path.exists(target) :
                os.remove(target)
                self.log.writeToLog(self.errorCodes['1010'], [self.tools.fName(target)])
            else :
                self.log.writeToLog(self.errorCodes['1020'], [self.tools.fName(target)])

        # Report and return
        self.log.writeToLog(self.errorCodes['1030'])
        return True


###############################################################################
######################## Illustration Update Functions ########################
###############################################################################
######################## Error Code Block Series = 2000 #######################
###############################################################################

    def updateIllustrationFiles (self, path) :
        '''Update all the illustrations in a group from path as referenced in
        the illustration.conf file. Skip any referenced but not in path.'''

        for i in self.illustrationConfig[self.gid].keys() :
            cid = self.illustrationConfig[self.gid][i]['bid']
            fileName = self.illustrationConfig[self.gid][i]['fileName']
            target = os.path.join(self.projIllustrationFolder, fileName)
            source = os.path.join(path, fileName)
            # Check to see if the source exists, proceed if it does
            if os.path.isfile(source) :
                if os.path.isfile(target) :
                    # Copy the source to the project
                    if not shutil.copy(source, target) :
                        self.log.writeToLog(self.errorCodes['2010'], [self.tools.fName(source)])
                    else :
                        self.log.writeToLog(self.errorCodes['2030'], [self.tools.fName(source)])
                else :
                    self.log.writeToLog(self.errorCodes['2020'], [self.tools.fName(source)])

        # Report and return
        self.log.writeToLog(self.errorCodes['2040'])
        return True



