#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110823
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle mostly housekeeping processes at the component level.

# History:
# 20110823 - djd - Started with intial file from RPM project


###############################################################################
################################### Shell Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import shutil

# Load the local classes
from tools import *

componentTypes = {}

class MetaCommand(type) :

    def __init__(cls, namestring, t, d) :
        global componentTypes
        super(MetaCommand, cls).__init__(namestring, t, d)
        if cls.type :
            componentTypes[cls.type] = cls


class Component (object) :
    __metaclass__ = MetaCommand
    type = None

    initialized = False

    def __init__(self, aProject, compConfig, typeConfig, cid) :
        '''Initiate the entire class here'''
        self.project = aProject
        self.compConfig = compConfig
        self.initialized = False
        self.cid = cid
        if not self.initialized : self.__class__.initType(aProject, typeConfig)


    def initClass(self) :
        '''Ensures everything is in place for components of this type to do their thing'''
        self.__class__.initialized = True


    @classmethod
    def initType(cls, aProject, typeConfig) :
        '''Internal housekeeping for the component type when it first wakes up'''
        cls.typeConfig = typeConfig


###############################################################################
########################### Component Init Functions ##########################
###############################################################################

    def initComponent(self) :
        '''A dummy function to avoid errors.  Any real initilization of any
        component should happen in the component itself.'''

        pass


    def render(self) :
        '''A dummy function to avoid errors.  Any real rendering of any
        component should happen in the component itself.'''

        self.project.writeToLog('ERR', 'Rendering function not found for: ' + self.type + ' component type', 'component.render()')


    def initCompFiles (self, initInfo) :
        '''Get the files for this project according to the init specs. of the
        component.'''

        # Before we init the files we need to do the folders
        self.initCompFolders(initInfo)

        fls = initInfo['Files'].__iter__()
        for fs in fls :
            fileName = ''; parentFolder = ''
            fGroup = initInfo['Files'][fs]
            for key, value in fGroup.iteritems() :
                if key == 'name' :
                    fileName = value
                elif key == 'location' :
                    if value :
                        parentFolder = value
                else :
                    pass

            if parentFolder :
                thisFile = os.path.join(self.project.projHome, parentFolder, fileName)
            else :
                thisFile = os.path.join(self.project.projHome, fileName)

            # Create source file name
            sourceFile = os.path.join(self.project.rpmHome, 'resources', 'lib_compTypes', self.type, 'lib_files', fileName)
            # Make the file if it is not already there
            if not os.path.isfile(thisFile) :
                if os.path.isfile(sourceFile) :
                    shutil.copy(sourceFile, thisFile)
                else :
                    open(thisFile, 'w').close()
                    if self.debugging == 'True' :
                        terminal('Created file: ' + thisFile)


    def initCompFolders (self, initInfo) :
        '''Get the folders for this project according to the init specs. of the
        component.'''

        fldrs = initInfo['Folders'].__iter__()
        for f in fldrs :
            folderName = ''; parentFolder = ''
            fGroup = initInfo['Folders'][f]
            for key, value in fGroup.iteritems() :
                if key == 'name' :

                    folderName = value
                elif key == 'location' :
                    if value != 'None' :
                        parentFolder = value
                else :
                    pass

            if parentFolder :
                thisFolder = os.path.join(self.project.projHome, parentFolder, folderName)
            else :
                thisFolder = os.path.join(self.project.projHome, folderName)

            # Create a source folder name in case there is one
            sourceFolder = os.path.join(self.project.rpmHome, 'resources', 'lib_compTypes', self.type, 'lib_folders', folderName)

            if not os.path.isdir(thisFolder) :
                if os.path.isdir(sourceFolder) :
                    shutil.copytree(sourceFolder, thisFolder)
                else :
                    os.mkdir(thisFolder)
                    if self.project.debugging == 'True' :
                        terminal('Created folder: ' + folderName)



# Depricated
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



