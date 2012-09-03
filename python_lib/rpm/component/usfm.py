#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project tasks.

# History:
# 20111222 - djd - Started with intial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os

# Load the local classes
from tools import *
from pt_tools import *
from component import Component


###############################################################################
################################## Begin Class ################################
###############################################################################

# As we load the module we will bring in all the common information about all the
# components this type will handle.



class Usfm (Component) :
    '''This class contains information about a type of component 
    used in a type of project.'''

    def __init__(self, project, config) :
        super(Usfm, self).__init__(project, config)

        self.project = project
        self.cid = ''
        # Check to see if this component type has been added to the 
        # proj config already
        self.project.addComponentType('Usfm')
        self.compSettings = self.project.projConfig['CompTypes']['Usfm']

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)

        self.usfmManagers = ['text', 'style', 'font', 'layout', 'illustration', self.renderer]

        # Init the general managers
        for mType in self.usfmManagers :
            self.project.createManager('usfm', mType)

       # Update default font if needed, usfm_Font manager will figure out which
       # font to use or it will die there.
        if not self.primaryFont or self.primaryFont == 'None' :
            self.project.managers['usfm_Font'].setPrimaryFont('', 'Usfm')
        else :
            # This will double check that all the fonts are installed
            self.project.managers['usfm_Font'].installFont('Usfm')

        # To better facilitate rendering that might be happening on this run, we
        # will update source file names and other settings used in the usfm_Text
        # manager (It might be better to do this elsewhere, but where?)
        self.project.managers['usfm_Text'].updateManagerSettings()


###############################################################################
############################ Functions Begin Here #############################
###############################################################################

    def render(self, force) :
        '''Does USFM specific rendering of a USFM component'''
            # useful variables: self.project, self.cfg

        self.cid = self.cfg['name']

        def preProcessComponent (cid) :
            '''This will prepare a component for rendering by checking for
            and/or creating any subcomponents it needs to render properly.'''

            # First see if this is a valid component. This is a little
            # redundant as this is done in project.py as well. It should
            # be caught there first but just in case we'll do it here too.
            if not isValidCID(self.project.projConfig, cid) :
                self.project.log.writeToLog('COMP-010', ['cid'])
                return False

            # See if the working text is present, quite if it is not
            if not self.project.managers['usfm_Text'].installUsfmWorkingText(cid) :
                return False

            # Check on the component styles
            self.project.managers['usfm_Style'].installCompTypeGlobalStyles()
            self.project.managers['usfm_Style'].installCompTypeOverrideStyles()

            # Run any preprocess checks or conversions
            
            # Run any illustration processes needed
            
            # Run any hyphenation or word break routines

            return True

        # If this is a meta component, preprocess all subcomponents
        # Stop if it breaks at any point
        if testForSetting(self.cfg, 'list') :
            for c in self.cfg['list'] :
                if not preProcessComponent(c) :
                    return False
        else :
            if not preProcessComponent(self.cid) :
                return False

        # With everything in place we can render the component and we pass-through
        # the force (render/view) command so the renderer will do the right thing.
        self.project.managers['usfm_' + self.renderer.capitalize()].run(self.cid, force)

        return True

