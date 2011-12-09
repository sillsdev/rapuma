#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111209
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This is the manager super class.

# History:
# 20111209 - djd - New file


###############################################################################
################################# Project Class ###############################
###############################################################################

# Firstly, import all the standard Python modules we need for
# this process
import os, shutil

# Load the local classes
from tools import *


class Manager(object) :

    def __init__(self, project) :
        self.project = project

    def initManager(self) :
        pass
        
        
    def runBasicManagerInit (self, initInfo) :
        '''Do a basic initialisation according to the settings in an init file.'''

        files = initInfo['Files'].keys()
        for f in files :
            fn = initInfo['Files'][f]['name']
            path = fn.split('/')[:-1]
            fileName = fn.split('/')[-1:][0]

            # Check for path defaults in the projConfFile If they are not there,
            # we will create a path override section and add the default that we
            # get from the init file.  If an override is found then we will use
            # that value.
            folderPath = ''
            buildConfSection(self.project._projConfig, 'FolderNameOverride')
            for f in path :
                if f[0] == '%' :
                    f = f.strip('%')
                    try :
                        folderPath = os.path.join(folderPath, self._projConfig['FolderNameOverride'][f])
                    except :
                        self.project._projConfig['FolderNameOverride'][f] = f
                        writeConfFile(self.project._projConfig, self.project.projConfFile)
                        folderPath = os.path.join(folderPath, f)
                else :
                    folderPath = os.path.join(folderPath, f)
            
            folderPath = os.path.join(self.project.projHome, folderPath)
            
            # Create the path if it is needed
            if not os.path.exists(folderPath) :
                os.makedirs(folderPath)

            thisFile = os.path.join(folderPath, fileName)

            # Create source file name
            sourceFile = os.path.join(self.project.rpmHome, 'resources', 'Files', fileName)
            # Make the file if it is not already there
            if not os.path.isfile(thisFile) :
                if os.path.isfile(sourceFile) :
                    shutil.copy(sourceFile, thisFile)
                else :
                    open(thisFile, 'w').close()
                    if self.debugging == 'True' :
                        terminal('Created file: ' + thisFile)



