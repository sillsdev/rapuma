#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project tasks.

# History:
# 20111207 - djd - Started with intial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil


# Load the local classes
from rapuma.core.tools import *
from rapuma.core.pt_tools import *
from rapuma.project.manager import Manager

###############################################################################
################################## Begin Class ################################
###############################################################################

class Illustration (Manager) :

    # Shared values
    xmlConfFile     = 'illustration.xml'

###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def __init__(self, project, cfg, cType) :
        '''Initialize the Illustration manager.'''

        '''Do the primary initialization for this manager.'''

        super(Illustration, self).__init__(project, cfg)

        # Set values for this manager
        self.project                    = project
        self.cfg                        = cfg
        self.cType                      = cType
        self.Ctype                      = cType.capitalize()
        self.illustrationConfig         = ConfigObj(encoding='utf-8')
        self.project                    = project
        self.projIllustrationsFolder    = self.project.local.projIllustrationsFolder
        self.illustrationsLib           = self.project.projConfig['Managers'][cType + '_Illustration']['illustrationsLib']
        self.illustrationsLibFolder     = self.project.userConfig['Resources']['illustrations']
        self.rapumaIllustrationsFolder  = self.project.local.rapumaIllustrationsFolder
        self.sourcePath                 = getattr(self.project, self.cType + '_sourcePath')
        self.layoutConfig               = self.project.managers[self.cType + '_Layout'].layoutConfig
        self.backgroundTypes            = ['watermark', 'lines']

        # Create an empty default Illustration config file if needed
        if not os.path.isfile(self.project.local.illustrationConfFile) :
            self.illustrationConfig.filename = self.project.local.illustrationConfFile
            writeConfFile(self.illustrationConfig)
            self.project.log.writeToLog('ILUS-010')
        else :
            self.illustrationConfig = ConfigObj(self.project.local.illustrationConfFile, encoding='utf-8')

        # Get persistant values from the config if there are any
        manager = self.cType + '_Illustration'
        newSectionSettings = getPersistantSettings(self.project.projConfig['Managers'][manager], os.path.join(self.project.local.rapumaConfigFolder, self.xmlConfFile))
        if newSectionSettings != self.project.projConfig['Managers'][manager] :
            self.project.projConfig['Managers'][manager] = newSectionSettings

        self.compSettings = self.project.projConfig['Managers'][manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)


###############################################################################
############################ Manager Level Functions ##########################
###############################################################################

    def hasBackgroundFile (self, bType) :
        '''Return True if this project has a valid background file installed.'''

        if bType in self.backgroundTypes :
            if testForSetting(self.layoutConfig['PageLayout'], bType + 'File') :
                if self.layoutConfig['PageLayout'][bType + 'File'] != '' :
                    backgroundFileName = self.layoutConfig['PageLayout'][bType + 'File']
                    backgroundFile = os.path.join(self.project.local.projIllustrationsFolder, backgroundFileName)
                    if os.path.isfile(backgroundFile) :
                        return True
        else :
            self.project.log.writeToLog('ILUS-100', [bType])
            dieNow()


    def installBackgroundFile (self, bType, fileName, path = None, force = False) :
        '''Install into the project the specified background file.
        It will use installIllustrationFile() to do the heavy lifting.
        Then it will register the file with the conf as the appropreate
        type of background file.'''

        if bType in self.backgroundTypes :
            # Resolve path
            if not path :
                path = self.rapumaIllustrationsFolder

            backgroundFile = os.path.join(path, fileName)
            if os.path.isfile(backgroundFile) :
                if not self.installIllustrationFile(fileName, path, force) :
                    self.project.log.writeToLog('ILUS-080', [fileName])

            if fileName != self.layoutConfig['PageLayout'][bType + 'File'] :
                self.layoutConfig['PageLayout'][bType + 'File'] = fileName
                writeConfFile(self.layoutConfig)
                self.project.log.writeToLog('ILUS-090', [fileName])
        else :
            self.project.log.writeToLog('ILUS-100', [bType])
            dieNow()


    def installIllustrationFile (self, fileName, path = None, force = False) :
        '''Install into the project the specified illustration file. If
        force is not set to True and no path has been specified, this 
        function will look into the project Illustrations folder first.
        Failing that, it will look in the user resources illustrations
        folder, and if found, copy it into the project. If a path is
        specified it will look there first and use that file.'''

        # Set some file names/paths
        places = []
        if path :
            places.append(os.path.join(path, fileName))
        places.append(os.path.join(self.illustrationsLibFolder, self.illustrationsLib, fileName))
        target = os.path.join(self.projIllustrationsFolder, fileName)
        # See if the file is there or not
        for p in places :
            if os.path.isfile(p) :
                if force :
                    if not shutil.copy(p, target) :
                        self.project.log.writeToLog('ILUS-020', [fName(p),'True'])
                    else :
                        self.project.log.writeToLog('ILUS-040', [fName(p)])
                else :
                    if not os.path.isfile(target) :
                        if not shutil.copy(p, target) :
                            self.project.log.writeToLog('ILUS-020', [fName(p),'False'])
                        else :
                            self.project.log.writeToLog('ILUS-040', [fName(p)])
                    else :
                        self.project.log.writeToLog('ILUS-030', [fName(p)])
                        return True
                break
        return True


    def getPics (self, cid) :
        '''Figure out what pics/illustrations we need for a given
        component and install them. It is assumed that this was 
        called because the user wants illustrations. Therefore, 
        this will kill the current session if it fails.'''

        for i in self.illustrationConfig['Illustrations'].keys() :
            if self.illustrationConfig['Illustrations'][i]['bid'] == cid :
                fileName = self.illustrationConfig['Illustrations'][i]['file']
                if not self.installIllustrationFile (fileName, '', False) :
                    dieNow()


    def removeIllustrationFile (self, fileName) :
        '''Remove an Illustration file from the project and conf file.'''

        # Remove the file
        projIll = os.path.join(self.projIllustrationsFolder, fileName)
        if os.path.isfile(projIll) :
            os.remove(projIll)
            self.project.log.writeToLog('ILUS-050', [fileName])

        # Check to see if this is a watermark file, if it is, remove config setting
        if testForSetting(self.project.projConfig['CompTypes'][self.Ctype], 'pageWatermarkFile') :
            org = self.project.projConfig['CompTypes'][self.Ctype]['pageWatermarkFile']
            if org == fileName :
                self.project.projConfig['CompTypes'][self.Ctype]['pageWatermarkFile'] = ''
                writeConfFile(self.project.projConfig)


    def createPiclistFile (self, cName, cid) :
        '''Look in the cid for \fig data. Extract it from the cid and
        use it to create a piclist file for this specific cid. If
        there is no \fig data no piclist file will be made.'''

        # Check for a .piclist file
        piclistFile = self.project.components[cName].getCidPiclistPath(cid)
        cvSep = self.layoutConfig['Illustrations']['chapterVerseSeperator']
        thisRef = ''
        obj = {}
        try :
            with codecs.open(piclistFile, "w", encoding='utf_8') as writeObject :
                writeObject.write('% This is an auto-generated usfmTex piclist file for this project.\n')
                writeObject.write('% Do not bother editing this file.\n\n')
                for i in self.illustrationConfig['Illustrations'].keys() :
                    obj = self.illustrationConfig['Illustrations'][i]
                    thisRef = ''
                    # Filter out if needed with this
                    if not str2bool(obj['useThisIllustration']) :
                        continue

                    if self.illustrationConfig['Illustrations'][i]['bid'] == cid.lower() :
                        if str2bool(self.layoutConfig['Illustrations']['useCaptionReferences']) \
                            and str2bool(self.illustrationConfig['Illustrations'][i]['useThisCaptionRef']) :
                            if obj['location'] :
                                thisRef = obj['location']
                            else :
                                thisRef = obj['chapter'] + cvSep + obj['verse']
                        # If we made it this far we can output the line
                        writeObject.write(obj['bid'] + ' ' + obj['chapter'] + '.' + obj['verse'] + \
                            ' |' + obj['file'] + '|' + obj['width'] + '|' + obj['position'] + \
                                '|' + obj['scale'] + '|' + obj['copyright'] + '|' + obj['caption'] + '|' + thisRef + ' \n')
            # Report to log
            self.project.log.writeToLog('ILUS-065', [cid])
        except Exception as e :
            # If this doesn't work, we should probably quite here
            dieNow('Error: Create piclist file failed with this error: ' + str(e))



