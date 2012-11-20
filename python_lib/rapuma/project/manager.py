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

    def __init__(self, project, cfg) :
        self.project = project
        self.cfg = cfg

# FIXME: Start here with building the manager init file name
# we need to insert into the project config all the known managers that can be used
# we may need to find a better way to manage this as it may not be too scalable, we'll see


#        if self.xmlInitFile :
#            self.initInfo = getXMLSettings(os.path.join(project.rapumaConfigFolder, self.xmlInitFile))


#    def initManager(self) :
#        '''Do a basic (generic) initialisation according to the settings 
#        in the manager's init file, if it has one.'''

#        # Skip this is there is not an XML init file for this manager
#        if not self.xmlInitFile :
#            return True

#        files = self.initInfo['Files'].keys()
#        for f in files :
#            fn = self.initInfo['Files'][f]['name']
#            path = fn.split('/')[:-1]
#            fileName = fn.split('/')[-1:][0]

#            # Check for path defaults in the projConfFile If they are not there,
#            # we will create a path override section and add the default that we
#            # get from the init file.  If an override is found then we will use
#            # that value.
#            folderPath = ''
#            buildConfSection(self.project.projConfig, 'FolderNameOverride')
#            for f in path :
#                if f[0] == '%' :
#                    f = f.strip('%')
#                    try :
#                        folderPath = os.path.join(folderPath, self.projConfig['FolderNameOverride'][f])
#                    except :
#                        self.project.projConfig['FolderNameOverride'][f] = f
#                        writeConfFile(self.project.projConfig, self.project.projConfFile)
#                        folderPath = os.path.join(folderPath, f)
#                else :
#                    folderPath = os.path.join(folderPath, f)
#            
#            folderPath = os.path.join(self.project.projHome, folderPath)
#            
#            # Create the path if it is needed
#            if not os.path.exists(folderPath) :
#                os.makedirs(folderPath)

#            thisFile = os.path.join(folderPath, fileName)

#            # Create source file name
#            sourceFile = os.path.join(self.project.rapumaHome, 'resources', 'Files', fileName)
#            # Make the file if it is not already there
#            if not os.path.isfile(thisFile) :
#                if os.path.isfile(sourceFile) :
#                    shutil.copy(sourceFile, thisFile)
#                else :
#                    open(thisFile, 'w').close()
#                    if self.debugging == 'True' :
#                        terminal('Created file: ' + thisFile)



