#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110823
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle USFM component processing tasks.

# History:
# 20110823 - djd - Started with intial file from RPM project


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, sys, shutil

# Load the local classes
from tools import *
from usfm_command import Command
from component import Component


###############################################################################
############################ Define Global Functions ##########################
###############################################################################

# These root level functions work at a fundamental level of the system


###############################################################################
################################## Begin Class ################################
###############################################################################

class Usfm (Component) :
    type = "usfm"

    def __init__(self, aProject, compType, typeConfig, cid) :
        '''Initialize this class.'''
        
        # Make it available to the Project Class with this
        super(Usfm, self).__init__(aProject, compType, typeConfig, cid)
        # no file system work to be done in this method!


###############################################################################
############################# Begin Main Functions ############################
###############################################################################

    @classmethod
    def initType (cls, aProject, typeConfig) :
        '''Initialize a component in this project.  This will put all the files
        in place for this type of component so it can be rendered.'''
        super(Usfm, cls).initType(aProject, typeConfig)
        
        print "(usfm.initType) Initializing this component:", cls


#    def initComponent(self) :

#        # Pull the information from the project init xml file
#        initInfo = getCompInitSettings(self.project.userHome, self.project.rpmHome, self.type)

#        # Create all necessary (empty) folders
#        self.initCompFolders(initInfo)
#        # Bring in any known resources like macros, etc.
#        self.initCompShared(initInfo)
#        # Bring in any know files for this component
#        self.initCompFiles(initInfo)

#        return True   

#        
#    def initCompFiles (self, initInfo) :
#        '''Get the files for this project according to the init specs. of the
#        component.'''

#        fls = initInfo['Files'].__iter__()
#        for fs in fls :
#            print fs
#            fileName = ''; parentFolder = ''
#            fGroup = initInfo['Files'][fs]
#            for key, value in fGroup.iteritems() :
#                if key == 'name' :
#                    fileName = value
#                elif key == 'location' :
#                    if value :
#                        parentFolder = value
#                else :
#                    pass

#            if parentFolder :
#                thisFile = os.path.join(self.project.projHome, parentFolder, fileName)
#            else :
#                thisFile = os.path.join(self.project.projHome, fileName)

#            # Create source file name
#            sourceFile = os.path.join(self.project.rpmHome, 'resources', 'lib_compTypes', self.type, 'lib_files', fileName)
#            # Make the file if it is not already there
#            if not os.path.isfile(thisFile) :
#                if os.path.isfile(sourceFile) :
#                    shutil.copy(sourceFile, thisFile)
#                else :
#                    open(thisFile, 'w').close()
#                    if self.debugging == 'True' :
#                        terminal('Created file: ' + thisFile)


#    def initCompFolders (self, initInfo) :
#        '''Get the folders for this project according to the init specs. of the
#        component.'''

#        fldrs = initInfo['Folders'].__iter__()
#        for f in fldrs :
#            folderName = ''; parentFolder = ''
#            fGroup = initInfo['Folders'][f]
#            for key, value in fGroup.iteritems() :
#                if key == 'name' :

#                    folderName = value
#                elif key == 'location' :
#                    if value != 'None' :
#                        parentFolder = value
#                else :
#                    pass

#            if parentFolder :
#                thisFolder = os.path.join(self.project.projHome, parentFolder, folderName)
#            else :
#                thisFolder = os.path.join(self.project.projHome, folderName)

#            # Create a source folder name in case there is one
#            sourceFolder = os.path.join(self.project.rpmHome, 'resources', 'lib_compTypes', self.type, 'lib_folders', folderName)

#            if not os.path.isdir(thisFolder) :
#                if os.path.isdir(sourceFolder) :
#                    shutil.copytree(sourceFolder, thisFolder)
#                else :
#                    os.mkdir(thisFolder)
#                    if self.project.debugging == 'True' :
#                        terminal('Created folder: ' + folderName)


#    def initCompShared (self, initInfo) :
#        '''Get the shared resources for this project according to the init
#        specs. of the component.'''
#        
#        try :
#            fldrs = initInfo['SharedResources'].__iter__()
#            for f in fldrs :
#                folderName = ''; parentFolder = ''
#                fGroup = initInfo['SharedResources'][f]
#                for key, value in fGroup.iteritems() :
#                    if key == 'name' :
#                        folderName = value
#                    elif key == 'location' :
#                        if value != 'None' :
#                            parentFolder = value

#                    elif key == 'shareLibPath' :
#                        sharePath = value
#                    else :
#                        pass

#                if parentFolder :
#                    thisFolder = os.path.join(self.project.projHome, parentFolder, folderName)
#                else :
#                    thisFolder = os.path.join(self.project.projHome, folderName)

#                # Create a source folder name
#                sourceFolder = os.path.join(self.project.rpmHome, 'resources', 'lib_share', sharePath)
#                # Create and copy the source stuff to the project
#                if not os.path.isdir(thisFolder) :
#                    if os.path.isdir(sourceFolder) :
#                        shutil.copytree(sourceFolder, thisFolder)
#        except :
#            pass
        

    def render (self) :
        '''Render a single project component.  Before starting, make sure
        everything necessary has been initialized.'''

        self.project.writeToLog('MSG', 'Rendered: [' + self.cid + ']', 'project.renderComponent()')
        
        return True


        
        

