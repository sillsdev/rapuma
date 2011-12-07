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

import os


# Load the local classes
from tools import *
from project import Project
import book_command


###############################################################################
################################## Begin Class ################################
###############################################################################

class Book (Project) :

###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def initProject (self) :
        '''Initialize a book project.'''

        # Some things this project type needs to know about
        # Valid Component Types: usfm, admin, maps, notes
        # Project Managers: font, format, style, illustration, hyphenation, render

        print "Initializing Book project"
        super(Book, self).initProject()
        pass


    def addNewComponent (self, cid, ctype) :
        '''Add component to the current project by adding them to the component
        binding list and inserting component info into the project conf file.

        All supplied arguments need to be valid.  This function will fail if the
        type, source or ID are not valid or if the component already exsists in
        the binding order list.'''

        # Test for this component and bail if it is there
        try :
            at = self._projConfig['Components'][cid]['compType']
            self.writeToLog('ERR', 'ID: [' + cid + '] cannot be added again.', 'project.addNewComponent()')
            return False

        except :
            # Add main Auxiliary sections if necessary
            buildConfSection(self._projConfig, 'ComponentTypes')
            buildConfSection(self._projConfig, 'Components')

            # First we add the type if it is not already in the project
            if ctype in self.validCompTypes :
                if not ctype in self._projConfig['ComponentTypes'] :
                    self.addNewComponentType(ctype)
            else :
                self.writeToLog('ERR', 'ID: [' + ctype + '] not valid component ID to use in [' + self.projectType + '] project type', 'project.addNewAuxiliary()')

            if not cid in self._projConfig['ComponentTypes'][ctype]['validIdCodes'] :
                self.writeToLog('ERR', 'ID: [' + cid + '] not valid ID for [' + ctype + '] component type', 'project.addNewComponents()')
                return False

            # Add to the installed components list for this type
            compList = []
            compList = self._projConfig['ComponentTypes'][ctype]['installedComponents']
            compList.append(cid)
            self._projConfig['ComponentTypes'][ctype]['installedComponents'] = compList

            # Read in the main settings file for this comp
            compSettings = getCompSettings(self.userHome, self.rpmHome, ctype)

            # Build a section for this aux and merge in the default settings
            buildConfSection(self._projConfig['Components'], cid)
            self._projConfig['Components'][cid].merge(compSettings['ComponentTypes']['ComponentInformation'])

            # Add component code to components list
            listOrder = []
            listOrder = self._projConfig['ProjectInfo']['componentList']
            listOrder.append(cid)
            self._projConfig['ProjectInfo']['componentList'] = listOrder

            # Add component code to binding order list
            if self._projConfig['ComponentTypes'][ctype]['inBindingList'] == 'True' :
                listOrder = []
                listOrder = self._projConfig['ProjectInfo']['projectComponentBindingOrder']
                listOrder.append(cid)
                self._projConfig['ProjectInfo']['projectComponentBindingOrder'] = listOrder

            self.writeOutProjConfFile = True
            self.writeToLog('MSG', 'Component added: ' + str(cid), 'project.addNewComponents()')

            return True


    def removeComponent (self, comp) :
        '''Remove a component from the current project by removing them from the

        component binding list and from their type information section.'''

        # Find out what kind of component type this is
        ctype = self._projConfig['Components'][comp]['compType']

        # Remove from components list first
        orderList = []
        orderList = self._projConfig['ProjectInfo']['componentList']
        if comp in orderList :
            orderList.remove(comp)
            self._projConfig['ProjectInfo']['componentList'] = orderList
            self.writeOutProjConfFile = True
        else :
            self.writeToLog('WRN', 'Component [' + comp + '] not found in component list', 'project.removeComponents()')

        # Remove from Binding order list
        orderList = []
        orderList = self._projConfig['ProjectInfo']['projectComponentBindingOrder']
        if comp in orderList :
            orderList.remove(comp)
            self._projConfig['ProjectInfo']['projectComponentBindingOrder'] = orderList
            self.writeOutProjConfFile = True
        else :
            self.writeToLog('WRN', 'Component [' + comp + '] not found in binding order list', 'project.removeComponents()')
        
        # Remove from the components installed list
        compList = self._projConfig['ComponentTypes'][ctype]['installedComponents']
        if comp in compList :
            compList.remove(comp)
            self._projConfig['ComponentTypes'][ctype]['installedComponents'] = compList
            self.writeOutProjConfFile = True
        
        # Remove the component's section from components
        if comp in self._projConfig['Components'] :
            del self._projConfig['Components'][comp]
            self.writeOutProjConfFile = True
            
        # Remove references in the ComponentTypes section if this is the last
        # component of its kind to be removed. 
        if len(self._projConfig['ComponentTypes'][ctype]['installedComponents']) == 0 :
            self.removeComponentType(ctype)

        # I guess if at least one of the above succeded we removed it
        if self.writeOutProjConfFile :
            self.writeToLog('MSG', 'Removed component: [' + comp + '] from project.', 'project.removeComponents()')


