#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111210
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project tasks.

# History:
# 20111210 - djd - Started with intial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, codecs


# Load the local classes
from tools import *
from manager import Manager
import component_command as cmpCmd


###############################################################################
################################## Begin Class ################################
###############################################################################

class Component (Manager) :


    def __init__(self, project) :
        super(Component, self).__init__(project)

        terminal("Initializing Component Manager")

        # Add commands for this manager
        project.addCommand("component_add", cmpCmd.AddCompGroup(self))
        project.addCommand("component_remove", cmpCmd.RemoveCompGroup(self))


###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def addComponentGroup (self, groupName, compList) :
        '''Add component group to the current project by adding all the necessary
        components and all the sub-components needed to render it.'''
        print compList
        # Build the component group config section
        buildConfSection(self.project._projConfig, 'ComponentGroups')
        buildConfSection(self.project._projConfig['ComponentGroups'], groupName)

        # Try to find out what the ID of the file is.
        # At this point we are pretty much assuming USFM
        c = 0
        newCompList = []
        compList = compList.split()
        for comp in compList :
            compID = ''
            if os.path.isfile(comp) :
                print comp
                compObject = codecs.open(comp, "r", encoding='utf_8')
                for line in compObject :
                    if line.split()[0] == '\id' :
                        compID = line.split()[1].lower()
                        break
                compObject.close()
        
            if compID == '' :
                compID = os.path.split(comp)[1].split('.')[0]

            newCompList.append(compID)
            print newCompList

        self.project._projConfig['ComponentGroups'][groupName]['compList'] = newCompList

        self.project.writeOutProjConfFile = True



    def removeComponent (self, comp) :
        '''Remove a component group from the current project.'''

        pass

