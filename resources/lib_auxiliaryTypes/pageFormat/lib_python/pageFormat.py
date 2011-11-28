#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110907
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle the configuration of page composition elements for
# publication projects.

# History:
# 20111013 - djd - Intial draft


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, sys

# Load the local classes
from pageCompTex_command import Command
from auxiliary import Auxiliary


###############################################################################
############################ Define Global Functions ##########################
###############################################################################

# These root level functions work at a fundamental level of the system


###############################################################################
################################## Begin Class ################################
###############################################################################

class PageFormat (Auxiliary) :

    type = "pageFormat"
    
    def __init__(self, aProject, auxConfig, typeConfig, aid) :
        '''Initialize this class.'''
        
        # Make it available to the Project Class with this
        super(PageFormat, self).__init__(aProject, auxConfig, typeConfig, aid)
        # no file system work to be done in this method!

        self._formatConfig      = {}

        # Make a format file if it isn't there already then
        # load the project's format configuration
        if not os.path.isfile(aProject.formatConfFile) :
            self.createProjFormatFile()
        else :
            self._formatConfig = ConfigObj(self.formatConfFile)




###############################################################################
############################# Begin Main Functions ############################
###############################################################################

    @classmethod
    def initType (cls, aProject, typeConfig) :
        '''Initialize a component in this project.  This will put all the files
        in place for this type of component so it can be rendered.'''
        super(PageCompTex, cls).initType(aProject, typeConfig)
        

#    def initAuxiliary (self, aux) :
#        '''Initialize this component.  This is a generic named function that
#        will be called from the project initialisation process.'''
#        
#        self.project.writeToLog('LOG', "Initialized [" + aux + "] for the PageCompTex auxiliary component type.")     
#        return True


    def setPageCompTex (self, ctype, pctype) :
        '''Setup a page composition type for a specific TeX component.'''
        
        print "Setting up page composition auxiliary for this TeX component"
        


    def createProjFormatFile (self) :
        '''Create the project's format conf file.'''

        # Create a master format file for this project if there is not already
        # one there. This will contain all the formating for this project.
        if not os.path.isfile(self.formatConfFile) :
            aProject._formatConfig = getXMLSettings(os.path.join(aProject.rpmAuxTypes, 'pageFormat', 'pageFormat_values.xml'))
            writeProjFormatConfFile(self._formatConfig, aProject.projHome)

            return True




