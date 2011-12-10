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


###############################################################################
################################## Begin Class ################################
###############################################################################

class Book (Project) :


###############################################################################
############################## Book Level Functions ###########################
###############################################################################


    def initProject (self) :
        '''Initialize a book project.'''

        # Some things this project type needs to know about
        # Valid Component Types: usfm, admin, maps, notes
        # Project Managers: illustration, hyphenation, render

        terminal("Initializing Book project")
        super(Book, self).initProject()

        # Do the Book type initializing here
        self.defaultManagers = ['component', 'font', 'format', 'style', 'render']
        self.optionalManagers = ['illustration', 'hyphenation', 'map']
        self.managers = {}

        # Update the config file if it is needed
        newConf = mergeConfig(self._projConfig, os.path.join(self.rpmConfigFolder, 'book.xml'))
        if newConf != self._projConfig :
            self._projConfig = newConf
            self.writeOutProjConfFile = True

        # Load up default managers
        for manager in self.defaultManagers :
            self.loadManager(manager)

        # Load any optional managers that are needed
        for manager in self.optionalManagers :
            if str2bool(self._projConfig['ProjectInfo']['use' + manager.capitalize()]) :
                self.loadManager(manager)


    def loadManager(self, manager) :
        module = __import__(manager)
        manobj = getattr(module, manager.capitalize())(self)
        self.managers[manager] = manobj
#        manobj.initManager()



