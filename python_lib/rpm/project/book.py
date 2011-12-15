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

#    def __init__(self, project) :
#        super(Book, self).__init__(project)
#        self.project = project
#        terminal("Initializing Book project")
        
# FIXME: All the initializing should be done up here in a proper __init__
# How do we do that?

# Also, in the init a book object needs to be created. This object will have
# all the necessary knowlege and attributes to be able to process itself
# How do we do that?

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

        # Initialize the managers dictionary here
        self.managers = {}

        # Update the config file if it is needed
        newConf = mergeConfig(self._projConfig, os.path.join(self.rpmConfigFolder, 'book.xml'))
        if newConf != self._projConfig :
            self._projConfig = newConf
            self.writeOutProjConfFile = True

        # Load up the component manager, we only need this one here
        self.loadManager('component')


# FIXME: This needs to be moved to the manager module. How do we make that work?
    def loadManager(self, manager) :
        module = __import__(manager)
        manobj = getattr(module, manager.capitalize())(self)
        self.managers[manager] = manobj
#        manobj.initManager()



