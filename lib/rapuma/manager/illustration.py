#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project tasks.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, codecs
from configobj                      import ConfigObj

# Load the local classes
from rapuma.core.tools              import Tools
from rapuma.project.manager         import Manager

###############################################################################
################################## Begin Class ################################
###############################################################################

class Illustration (Manager) :

    def __init__(self, project, cfg, cType) :
        '''Initialize the Illustration manager.'''

        '''Do the primary initialization for this manager.'''

        super(Illustration, self).__init__(project, cfg)

        # Set values for this manager
        self.tools                      = Tools()
        self.project                    = project
        self.cfg                        = cfg
        self.cType                      = cType
        self.Ctype                      = cType.capitalize()
        self.manager                    = self.cType + '_Illustration'
        self.managers                   = project.managers
        self.log                        = project.log
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
        # Folder paths
        self.projIllustrationsFolder    = self.project.local.projIllustrationsFolder
        self.userIllustrationsLibFolder = self.userConfig['Resources']['illustrations']
        self.userIllustrationsLib       = os.path.join(self.userIllustrationsLibFolder, self.userIllustrationsLibName)
        self.projConfFolder             = self.project.local.projConfFolder
        self.rpmRapumaConfigFolder      = self.project.local.rapumaConfigFolder
        # File names with folder paths
        self.illustrationConfFile       = os.path.join(self.projConfFolder, self.illustrationConfFileName)
        self.defaultXmlConfFile         = os.path.join(self.rpmRapumaConfigFolder, self.defaultXmlConfFileName)

        # If we have nothing in the project for pointing to an illustrations
        # lib, put the default in here
        if not self.userIllustrationsLibName :
            self.userIllustrationsLibName = self.userConfig['Resources']['defaultIllustrationsLibraryName']
            self.projConfig['Managers'][cType + '_Illustration']['userIllustrationsLibName'] = self.userIllustrationsLibName
            self.tools.writeConfFile(self.projConfig)

        # Load the config object
#        self.illustrationConfig = self.tools.initConfig(self.illustrationConfFile, self.defaultXmlConfFile)
        self.illustrationConfig         = ConfigObj(self.illustrationConfFile, encoding='utf-8')
        # Load settings from the manager config
        for k, v in self.projConfig['Managers'][self.manager].iteritems() :
            setattr(self, k, v)

        # Log messages for this module
        self.errorCodes     = {
            '0000' : ['MSG', 'Placeholder message'],
            '0240' : ['ERR', 'Failed to copy [<<1>>] into the project illustrations folder.'],
            '0220' : ['LOG', 'Copied [<<1>>] into the project illustrations folder. Force was set to [<<2>>].'],
            '0230' : ['LOG', 'Did not copy [<<1>>] into the project illustrations folder. File already exsits.'],
            '0265' : ['LOG', 'Piclist file for [<<1>>] has been created.'],

            'ILUS-000' : ['MSG', 'Illustration module messages'],
            'ILUS-010' : ['LOG', 'Wrote out new illustration configuration file. (illustration.__init__())'],
            'ILUS-050' : ['LOG', 'Removed [<<1>>] from the project illustrations folder.'],
            'ILUS-055' : ['LOG', 'Illustrations not being used. The piclist file has been removed from the [<<1>>] component folder.'],
            'ILUS-060' : ['LOG', 'Piclist file for [<<1>>] already exsits. File not created.'],
            'ILUS-070' : ['WRN', 'Watermark file [<<1>>] not found in illustrations folder. Will try to revert to default watermark.'],
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
        function will look into the project Illustrations folder first.
        Failing that, it will look in the user resources illustrations
        folder, and if found, copy it into the project. If a path is
        specified it will look there first and use that file.'''

#        import pdb; pdb.set_trace()

        # Set some file names/paths
        places = []
        if path :
            places.append(os.path.join(path, fileName))
        places.append(os.path.join(self.tools.resolvePath(self.userIllustrationsLib), fileName))
        target = os.path.join(self.projIllustrationsFolder, fileName)
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
        '''Figure out what pics/illustrations we need for a given
        component and install them. It is assumed that this was 
        called because the user wants illustrations. Therefore, 
        this will kill the current session if it fails.'''

        for i in self.illustrationConfig[gid].keys() :
            if self.illustrationConfig[gid][i]['bid'] == cid :
                fileName = self.illustrationConfig[gid][i]['fileName']
                if not os.path.isfile(os.path.join(self.projIllustrationsFolder, fileName)) :
                    self.installIllustrationFile (fileName, '', False)


    def removeIllustrationFile (self, fileName) :
        '''Remove an Illustration file from the project and conf file.'''

        # Remove the file
        projIll = os.path.join(self.projIllustrationsFolder, fileName)
        if os.path.isfile(projIll) :
            os.remove(projIll)
            self.log.writeToLog('ILUS-050', [fileName])

        # Check to see if this is a watermark file, if it is, remove config setting
        if self.tools.testForSetting(self.projConfig['CompTypes'][self.Ctype], 'pageWatermarkFile') :
            org = self.projConfig['CompTypes'][self.Ctype]['pageWatermarkFile']
            if org == fileName :
                self.projConfig['CompTypes'][self.Ctype]['pageWatermarkFile'] = ''
                self.tools.writeConfFile(self.projConfig)


    def hasIllustrations (self, gid, bid) :
        '''Return True if this component as any illustrations associated with it.'''

        for i in self.illustrationConfig[gid].keys() :
            if self.illustrationConfig[gid][i]['bid'] == bid :
                return True


    def createPiclistFile (self, gid, cid) :
        '''Look in the cid for \fig data. Extract it from the cid and
        use it to create a piclist file for this specific cid. If
        there is no \fig data no piclist file will be made.'''

        # Check for a .piclist file
        piclistFile = self.project.groups[gid].getCidPiclistPath(cid)
        cvSep = self.layoutConfig['Illustrations']['chapterVerseSeperator']
        thisRef = ''
        obj = {}

        try :
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
                    if self.illustrationConfig[gid][i]['bid'] == cid.lower() :
                        if self.tools.str2bool(self.layoutConfig['Illustrations']['useCaptions']) \
                            and self.tools.str2bool(self.illustrationConfig[gid][i]['useThisCaption']) :
                            if obj['caption'] :
                                caption = obj['caption']
                    # Work out if we want a caption reference or not for this illustration
                    if self.illustrationConfig[gid][i]['bid'] == cid.lower() :
                        if self.tools.str2bool(self.layoutConfig['Illustrations']['useCaptionReferences']) \
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
            self.log.writeToLog(self.errorCodes['0265'], [cid])
            return True
        except Exception as e :
            # If this doesn't work, we should probably quite here
            self.tools.dieNow('Error: Create piclist file failed with this error: ' + str(e))



