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
#from rapuma.component.usfm import PT_Tools
from rapuma.project.manager import Manager

###############################################################################
################################## Begin Class ################################
###############################################################################

class Illustration (Manager) :

    def __init__(self, project, cfg, cType) :
        '''Initialize the Illustration manager.'''

        '''Do the primary initialization for this manager.'''

        super(Illustration, self).__init__(project, cfg)

        # Set values for this manager
#        self.pt_tools                   = PT_Tools(project)
        self.project                    = project
        self.cfg                        = cfg
        self.cType                      = cType
        self.Ctype                      = cType.capitalize()
        self.manager                    = self.cType + '_Illustration'
        self.managers                   = project.managers
        self.backgroundTypes            = ['watermark', 'lines']
        # Bring in some manager objects we will need
        self.layout                     = self.managers[self.cType + '_Layout']
        # Get config objs
        self.projConfig                 = project.projConfig
        self.layoutConfig               = self.layout.layoutConfig
        self.userConfig                 = project.userConfig
        # Get some config settings
        self.userIllustrationsLibName   = self.projConfig['Managers'][cType + '_Illustration']['userIllustrationsLibName']

        # File names
        self.illustrationConfFileName   = self.project.projectMediaIDCode + '_illustration.conf'
        self.defaultXmlConfFileName     = 'illustration.xml'
        self.projWatermarkFileName      = self.layoutConfig['PageLayout']['watermarkFile']
        self.rpmDefWatermarkFileName    = 'watermark_default.pdf'
        self.projLinesFileName          = self.layoutConfig['PageLayout']['linesFile']
        self.rpmDefLinesFileName        = 'lines_default.pdf'
        self.boxBoarderFileName         = self.layoutConfig['PageLayout']['boxBoarderFile']
        self.rpmBoxBoarderFileName      = 'box_background.pdf'
        # Folder paths
        self.projIllustrationsFolder    = self.project.local.projIllustrationsFolder
        self.userIllustrationsLibFolder = self.userConfig['Resources']['illustrations']
        self.userIllustrationsLib       = os.path.join(self.userIllustrationsLibFolder, self.userIllustrationsLibName)
        self.rpmIllustrationsFolder     = self.project.local.rapumaIllustrationsFolder
        self.projConfFolder             = self.project.local.projConfFolder
        self.rpmRapumaConfigFolder      = self.project.local.rapumaConfigFolder
        # File names with folder paths
        self.illustrationConfFile       = os.path.join(self.projConfFolder, self.illustrationConfFileName)
        self.defaultXmlConfFile         = os.path.join(self.rpmRapumaConfigFolder, self.defaultXmlConfFileName)
        self.projWatermarkFile          = os.path.join(self.projIllustrationsFolder, self.projWatermarkFileName)
        self.rpmDefWatermarkFile        = os.path.join(self.rpmIllustrationsFolder, self.rpmDefWatermarkFileName)
        self.projLinesFile              = os.path.join(self.projIllustrationsFolder, self.projLinesFileName)
        self.rpmDefLinesFile            = os.path.join(self.rpmIllustrationsFolder, self.rpmDefLinesFileName)
        self.boxBoarderFile             = os.path.join(self.projIllustrationsFolder, self.boxBoarderFileName)
        self.rpmBoxBoarderFile          = os.path.join(self.rpmIllustrationsFolder, self.rpmBoxBoarderFileName)

        # If we have nothing in the project for pointing to an illustrations
        # lib, put the default in here
        if not self.userIllustrationsLibName :
            self.userIllustrationsLibName = self.userConfig['Resources']['defaultIllustrationsLibraryName']
            self.projConfig['Managers'][cType + '_Illustration']['userIllustrationsLibName'] = self.userIllustrationsLibName
            writeConfFile(self.projConfig)

        # Load the config object
        self.illustrationConfig = initConfig(self.illustrationConfFile, self.defaultXmlConfFile)
        # Load settings from the manager config
        for k, v in self.projConfig['Managers'][self.manager].iteritems() :
            setattr(self, k, v)

###############################################################################
############################ Manager Level Functions ##########################
###############################################################################




## FIXME: Working here!

#    def hasBackgroundFile (self, bType) :
#        '''Return True if this project has a valid background file installed.'''

#        if bType in self.backgroundTypes :
#            if testForSetting(self.layoutConfig['PageLayout'], bType + 'File') :
#                if self.layoutConfig['PageLayout'][bType + 'File'] != '' :
#                    backgroundFileName = self.layoutConfig['PageLayout'][bType + 'File']
#                    backgroundFile = os.path.join(self.project.local.projIllustrationsFolder, backgroundFileName)
#                    if os.path.isfile(backgroundFile) :
#                        return True
#        else :
#            self.project.log.writeToLog('ILUS-100', [bType])
#            dieNow()


    def changeWatermarkFile (self) :
        '''Change the current watermark file.'''

# FIXME: This is a place holder function

        terminal('This does not work yet.')


    def installDefaultWatermarkFile (self) :
        '''Install a default Rapuma watermark file into the project.'''

        if not os.path.exists(self.projWatermarkFile) :
            try :
                shutil.copy(self.rpmDefWatermarkFile, self.projWatermarkFile)
                self.project.log.writeToLog('ILUS-080', [fName(self.projWatermarkFile)])
            except Exception as e :
                # If this doesn't work, we should probably quite here
                dieNow('Error: Failed to install default watermark background file with this error: ' + str(e) + '\n')


    def installLinesFile (self) :
        '''Install a background lines file into the project.'''

        if not os.path.exists(self.projLinesFile) :
            try :
                shutil.copy(self.rpmDefLinesFile, self.projLinesFile)
                self.project.log.writeToLog('ILUS-080', [fName(self.projLinesFile)])
            except Exception as e :

                # If this doesn't work, we should probably quite here
                dieNow('Error: Failed to install lines background file with this error: ' + str(e) + '\n')


    def installBoxBoarderFile (self) :
        '''Install a background lines file into the project.'''

        if not os.path.exists(self.boxBoarderFile) :
            try :
                shutil.copy(self.rpmBoxBoarderFile, self.boxBoarderFile)
                self.project.log.writeToLog('ILUS-080', [fName(self.boxBoarderFile)])
            except Exception as e :

                # If this doesn't work, we should probably quite here
                dieNow('Error: Failed to install lines background file with this error: ' + str(e) + '\n')


    def installIllustrationFile (self, fileName, path = None, force = False) :
        '''Install into the project the specified illustration file. If
        force is not set to True and no path has been specified, this 
        function will look into the project Illustrations folder first.
        Failing that, it will look in the user resources illustrations
        folder, and if found, copy it into the project. If a path is
        specified it will look there first and use that file.'''

#        import pdb; pdb.set_trace()

        # Set some file names/paths
        places = []
        if path :
            places.append(os.path.join(path, fileName))
        places.append(os.path.join(self.userIllustrationsLib, fileName))
        target = os.path.join(self.projIllustrationsFolder, fileName)
        # See if the file is there or not
        for p in places :
            if os.path.isfile(p) :
                if force :
                    if not shutil.copy(p, target) :
                        self.project.log.writeToLog('ILUS-020', [fName(p),'True'])
                        return True
                else :
                    if not os.path.isfile(target) :
                        if not shutil.copy(p, target) :
                            self.project.log.writeToLog('ILUS-020', [fName(p),'False'])
                            return True
                    else :
                        self.project.log.writeToLog('ILUS-030', [fName(p)])
                        return True

        # No joy, we're hosed
        self.project.log.writeToLog('ILUS-040', [fName(p)])
        dieNow()


    def getPics (self, cid) :
        '''Figure out what pics/illustrations we need for a given
        component and install them. It is assumed that this was 
        called because the user wants illustrations. Therefore, 
        this will kill the current session if it fails.'''

        for i in self.illustrationConfig['Illustrations'].keys() :
            if self.illustrationConfig['Illustrations'][i]['bid'] == cid :
                fileName = self.illustrationConfig['Illustrations'][i]['fileName']
                if not os.path.isfile(os.path.join(self.projIllustrationsFolder, fileName)) :
                    self.installIllustrationFile (fileName, '', False)


    def removeIllustrationFile (self, fileName) :
        '''Remove an Illustration file from the project and conf file.'''

        # Remove the file
        projIll = os.path.join(self.projIllustrationsFolder, fileName)
        if os.path.isfile(projIll) :
            os.remove(projIll)
            self.project.log.writeToLog('ILUS-050', [fileName])

        # Check to see if this is a watermark file, if it is, remove config setting
        if testForSetting(self.projConfig['CompTypes'][self.Ctype], 'pageWatermarkFile') :
            org = self.projConfig['CompTypes'][self.Ctype]['pageWatermarkFile']
            if org == fileName :
                self.projConfig['CompTypes'][self.Ctype]['pageWatermarkFile'] = ''
                writeConfFile(self.projConfig)


    def hasIllustrations (self, cName) :
        '''Return True if this component as any illustrations associated with it.'''

        thisBid = self.project.components[cName].getUsfmCid(cName)
        for i in self.illustrationConfig['Illustrations'].keys() :
            if self.illustrationConfig['Illustrations'][i]['bid'] == thisBid :
                return True


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
                    # Is a caption going to be used on this illustration?
                    caption = ''
                    if self.illustrationConfig['Illustrations'][i]['bid'] == cid.lower() :
                        if str2bool(self.layoutConfig['Illustrations']['useCaptions']) \
                            and str2bool(self.illustrationConfig['Illustrations'][i]['useThisCaption']) :
                            if obj['caption'] :
                                caption = obj['caption']
                    # Work out if we want a caption reference or not for this illustration
                    if self.illustrationConfig['Illustrations'][i]['bid'] == cid.lower() :
                        if str2bool(self.layoutConfig['Illustrations']['useCaptionReferences']) \
                            and str2bool(self.illustrationConfig['Illustrations'][i]['useThisCaptionRef']) :
                            if obj['location'] :
                                thisRef = obj['location']
                            else :
                                thisRef = obj['chapter'] + cvSep + obj['verse']
                        # If we made it this far we can output the line
                        writeObject.write(obj['bid'] + ' ' + obj['chapter'] + '.' + obj['verse'] + \
                            ' |' + obj['fileName'] + '|' + obj['width'] + '|' + obj['position'] + \
                                '|' + obj['scale'] + '|' + obj['copyright'] + '|' + caption + '|' + thisRef + ' \n')
            # Report to log
            self.project.log.writeToLog('ILUS-065', [cid])
            return True
        except Exception as e :
            # If this doesn't work, we should probably quite here
            dieNow('Error: Create piclist file failed with this error: ' + str(e))



