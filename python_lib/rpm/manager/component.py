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

class PubGroup (object) :
    pass

class PubComp (object) :
    pass

class Component (Manager) :


    def __init__(self, project) :
        '''Initialize this class.'''

        super(Component, self).__init__(project)

        terminal("Initializing Component Manager")

        # Add commands for this manager
        project.addCommand("component_add", cmpCmd.AddCompGroup(self))
        project.addCommand("component_remove", cmpCmd.RemoveCompGroup(self))

        self.defaultManagers = ['font', 'format', 'style', 'render']
        self.optionalManagers = ['illustration', 'hyphenation']

        for manager in self.defaultManagers :
            self.project.loadManager(manager)

        # Load any optional managers that are needed
# FIXME: We will want to load these here so we have to look through the comp groups to find the ones we need.
#        for manager in self.optionalManagers :
#            if str2bool(self._projConfig['ProjectInfo']['use' + manager.capitalize()]) :
#                self.loadManager(manager)

        # Now we will create an object for each component group as well as
        # each component in the project. These options will know everything
        # they need to know to process themselves.

        # First create the group objects
        buildConfSection(self.project._projConfig, 'ComponentGroups')
        for group in self.project._projConfig['ComponentGroups'] :
            cmpName = group
            group = PubGroup()
            group.name = cmpName
            group.compList = self.project._projConfig['ComponentGroups'][group.name]['compList']
            print 'Made ' + group.name + ' group object'
            
            # While we are here lets make the component objects too
            cmpObj = None
            for comp in group.compList :
                cmpName = comp
                comp = PubComp()
                self.initPubComp(comp, cmpName, group.name)
                print 'Made ' + comp.name + ' component object'


    def initPubComp (self, comp, cmpName, grpName) :
    
        comp.groupName = grpName
        comp.name = cmpName
        comp.fontList = self.project._projConfig['ComponentGroups'][grpName]['fontList']
        comp.compType = self.project._projConfig['ComponentGroups'][grpName]['compType']
        comp.rendering = self.project._projConfig['ComponentGroups'][grpName]['rendering']
        comp.useHyphenation = self.project._projConfig['ComponentGroups'][grpName]['useHyphenation']
        comp.useIllustration = self.project._projConfig['ComponentGroups'][grpName]['useIllustration']



###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def addComponentGroup (self, groupName, compList, fontList, compType, rendering, hyphenation, illustrations) :
        '''Add component group to the current project by adding all the necessary
        components and all the sub-components needed to render it.'''

        # Build the component group config section
        buildConfSection(self.project._projConfig, 'ComponentGroups')
        buildConfSection(self.project._projConfig['ComponentGroups'], groupName)

        # Try to find out what the ID of the file is.
        # At this point we are pretty much assuming USFM
        newCompList = []
        for comp in compList.split() :
            compID = ''
            if os.path.isfile(comp) :
                compObject = codecs.open(comp, "r", encoding='utf_8')
                for line in compObject :
                    if line.split()[0] == '\id' :
                        compID = line.split()[1].lower()
                        if compType == '' :
                            compType = 'usfm'
                        break
                compObject.close()
        
            if compID == '' :
                compID = os.path.split(comp)[1].split('.')[0]

            # Add the compID to the list
            newCompList.append(compID)

        # Record the components in this group
        self.project._projConfig['ComponentGroups'][groupName]['compList'] = newCompList

        # Assign the fonts to the group
        # The font manager will take care of setup later
        self.project._projConfig['ComponentGroups'][groupName]['fontList'] = fontList.split()

        # Assign the component type ID to the group
        self.project._projConfig['ComponentGroups'][groupName]['compType'] = compType.lower()

        # Assign the component rendering system type to the group
        self.project._projConfig['ComponentGroups'][groupName]['rendering'] = rendering.lower()

        # Add additional managers to this group if indicated (default is False)
        self.project._projConfig['ComponentGroups'][groupName]['useHyphenation'] = hyphenation.capitalize()
        self.project._projConfig['ComponentGroups'][groupName]['useIllustration'] = illustrations.capitalize()

        # Add the component group to the group order list
        newGroupOrderList = []
        try :
            newGroupOrderList = self._projConfig['ProjectInfo']['bindingOrder']
            newGroupOrderList.append(groupName)
        except :
            buildConfSection(self.project._projConfig, 'ProjectInfo')
            newGroupOrderList.append(groupName)

        self.project._projConfig['ProjectInfo']['bindingOrder'] = newGroupOrderList
        print self.project._projConfig['ProjectInfo']['bindingOrder']

        self.project.writeOutProjConfFile = True



    def removeComponent (self, comp) :
        '''Remove a component group from the current project.'''

        terminal('There is no way I am going to do this without some code to do it with!')
        pass

