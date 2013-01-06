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
        self.illustrationConfig         = ConfigObj()
        self.project                    = project
        self.projIllustrationsFolder    = self.project.local.projIllustrationsFolder
        self.rapumaIllustrationsFolder  = self.project.local.rapumaIllustrationsFolder

        # Create an empty default Illustration config file if needed
        if not os.path.isfile(self.project.local.illustrationConfFile) :
            self.illustrationConfig.filename = self.project.local.illustrationConfFile
            writeConfFile(self.illustrationConfig)
            self.project.log.writeToLog('ILUS-010')
        else :
            self.fontConfig = ConfigObj(self.project.local.illustrationConfFile)

        # Get persistant values from the config if there are any
        manager = self.cType + '_Illustration'
        newSectionSettings = getPersistantSettings(self.project.projConfig['Managers'][manager], os.path.join(self.project.local.rapumaConfigFolder, self.xmlConfFile))
        if newSectionSettings != self.project.projConfig['Managers'][manager] :
            self.project.projConfig['Managers'][manager] = newSectionSettings

        self.compSettings = self.project.projConfig['Managers'][manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)


    def installWatermarkFile (self, fileName, path = None, force = False) :
        '''Install into the project the specified watermark file.
        It will use installIllustrationFile() to do the heavy lifting.
        Then it will register the file with the conf as the watermark file.'''

        # Resolve path
        if not path :
            path = self.rapumaIllustrationsFolder

        watermarkFile = os.path.join(path, fileName)
        if os.path.isfile(watermarkFile) :
            if self.installIllustrationFile(fileName, path, force) :
                self.project.projConfig['CompTypes'][self.Ctype]['pageWatermarkFile'] = fileName
                writeConfFile(self.project.projConfig)


    def installIllustrationFile (self, fileName, path = None, force = False) :
        '''Install into the project the specified illustration file. If
        force is not set to True and no path has been specified, this 
        function will look into the project Illustrations folder first.
        Failing that, it will look in the user resources illustrations
        folder, and if found, copy it into the project. If a path is
        specified it will look there first and use that file.'''

        # Set some file names/paths
        pathIll = os.path.join(path, fileName)
        projIll = os.path.join(self.projIllustrationsFolder, fileName)
        userIll = os.path.join(self.project.local.libIllustrations, fileName)
        places = [pathIll, projIll, userIll]
        # See if the file is there or not
        for p in places :
            if os.path.isfile(p) :
                if force :
                    if not shutil.copy(p, self.projIllustrationsFolder) :
                        self.project.log.writeToLog('ILUS-020', [fName(p),'True'])
                    else :
                        self.project.log.writeToLog('ILUS-040', [fName(p)])
                else :
                    if not os.path.isfile(projIll) :
                        if not shutil.copy(p, self.projIllustrationsFolder) :
                            self.project.log.writeToLog('ILUS-020', [fName(p),'False'])
                        else :
                            self.project.log.writeToLog('ILUS-040', [fName(p)])
                    else :
                        self.project.log.writeToLog('ILUS-030', [fName(p)])
                        return True
            break
        return True


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






# FIXME: Do we want this moved to the usfm module?




    def createPiclistFile (self, cid) :
        '''Look in the cid for \fig data. Extract it from the cid and
        use it to create a piclist file for this specific cid. If
        there is no \fig data no piclist file will be made.'''

        # Check for a .piclist file
        print dir(self)
# FIXME: How do I call on usfm module to get the piclist path?
        
        piclistFile = self.project.managers[self.cType + '_Text'].getCompWorkingTextPiclistPath(cid)
        if not os.path.isfile(piclistFile) :
            with codecs.open(piclistFile, "w", encoding='utf_8') as writeObject :
                writeObject.write('% Illustration placement file for: ' + cid + '\n\n')
                writeObject.write('%' + cid.upper() + ' 3.1 |<file name>|col|tl|1.0|Copyright info|Vernacular caption| \n')




