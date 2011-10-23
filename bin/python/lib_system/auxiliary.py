#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111014
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle mostly housekeeping processes at the component level.

# History:
# 20111014 - djd - Started with intial file from RPM project


###############################################################################
################################### Shell Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

# import codecs, os

# Load the local classes

auxiliaryTypes = {}

class MetaAuxiliary(type) :

    def __init__(cls, namestring, t, d) :
        global auxiliaryTypes
        super(MetaAuxiliary, cls).__init__(namestring, t, d)
        if cls.type :
            auxiliaryTypes[cls.type] = cls


class Auxiliary (object) :
    __metaclass__ = MetaAuxiliary
    type = None

    initialized = False

    def __init__(self, aProject, auxConfig, typeConfig) :
        '''Initiate the entire class here'''
        self.project = aProject
        self.auxConfig = auxConfig
        self.typeConfig = typeConfig
        if not self.initialized : self.__class__.initType(aProject, typeConfig)

    def initClass(self) :
        '''Ensures everything is in place for components of this type to do their thing'''
        self.__class__.initialized = True
        
        
    @classmethod
    def initType(cls, aProject, typeConfig) :
        '''Internal housekeeping for the component type when it first wakes up'''
        cls.typeConfig = typeConfig


###############################################################################
########################### Auxiliary Init Functions ##########################
###############################################################################

    def initAuxiliary (self) :
        '''A dummy function to avoid errors.  Any real initilization of any
        auxiliary component should happen in the auxiliary itself.'''
        
        pass


    def initAuxFiles (self, atype, initInfo) :
        '''Get the files for this auxilary according to the init specs. of the
        component.'''

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
                thisFile = os.path.join(self.projHome, parentFolder, fileName)
            else :
                thisFile = os.path.join(self.projHome, fileName)

            # Create source file name
            sourceFile = os.path.join(self.rpmHome, 'resources', 'lib_compTypes', atype, 'lib_files', fileName)
            # Make the file if it is not already there
            if not os.path.isfile(thisFile) :
                if os.path.isfile(sourceFile) :
                    shutil.copy(sourceFile, thisFile)
                else :
                    open(thisFile, 'w').close()
                    if self.debugging == 'True' :
                        terminal('Created file: ' + thisFile)


    def initAuxFolders (self, atype, initInfo) :
        '''Get the folders for this auxiliary according to the init specs. of
        the component.'''

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
                thisFolder = os.path.join(self.projHome, parentFolder, folderName)
            else :
                thisFolder = os.path.join(self.projHome, folderName)

            # Create a source folder name in case there is one
            sourceFolder = os.path.join(self.rpmHome, 'resources', 'lib_compTypes', atype, 'lib_folders', folderName)

            if not os.path.isdir(thisFolder) :
                if os.path.isdir(sourceFolder) :
                    shutil.copytree(sourceFolder, thisFolder)
                else :
                    os.mkdir(thisFolder)
                    if self.debugging == 'True' :
                        terminal('Created folder: ' + folderName)


    def initAuxShared (self, initInfo) :
        '''Get the shared resources for this project according to the init

        specs. of the component.'''
        
        try :
            fldrs = initInfo['SharedResources'].__iter__()
            for f in fldrs :
                folderName = ''; parentFolder = ''
                fGroup = initInfo['SharedResources'][f]
                for key, value in fGroup.iteritems() :
                    if key == 'name' :
                        folderName = value
                    elif key == 'location' :
                        if value != 'None' :
                            parentFolder = value

                    elif key == 'shareLibPath' :
                        sharePath = value

                    else :
                        pass

                if parentFolder :
                    thisFolder = os.path.join(self.projHome, parentFolder, folderName)
                else :
                    thisFolder = os.path.join(self.projHome, folderName)

                # Create a source folder name
                sourceFolder = os.path.join(self.rpmHome, 'resources', 'lib_share', sharePath)
                # Create and copy the source stuff to the project
                if not os.path.isdir(thisFolder) :
                    if os.path.isdir(sourceFolder) :
                        shutil.copytree(sourceFolder, thisFolder)
        except :
            pass

