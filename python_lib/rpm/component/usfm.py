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
from pprint import pprint


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

#        self.usfmManagers = ['preprocess', 'illustration', 'hyphenation']
        self.usfmManagers = ['text', 'style', 'font', 'layout', 'illustration', self.renderer]

        # Init the general managers
        for mType in self.usfmManagers :
            self.project.createManager('usfm', mType)

       # Update default font if needed, font manager will figure out which
       # font to use or it will die there.
        if not self.primaryFont or self.primaryFont == 'None' :
            self.project.managers['usfm_Font'].setPrimaryFont('', 'Usfm')
        else :
            # This will double check that all the fonts are installed
            self.project.managers['usfm_Font'].installFont('Usfm')

# FIXME: Start here, how can we get text file info into the proj conf for when we need it.

        # Check to see what the source editor is and adjust settings if needed
        sourceEditor = self.project.projConfig['CompTypes']['Usfm']['sourceEditor']
        if sourceEditor.lower() == 'paratext' :
            ptSet = getPTSettings(self.project.local.projHome)
            # In this situation we don't want to make any changes to exsiting
            # settings so the reset is set to False
            oldCompSet = self.compSettings.dict()
            newCompSet = mapPTTextSettings(self.compSettings.dict(), ptSet, False)
            if not newCompSet == oldCompSet :
                self.compSettings.merge(newCompSet)
                writeConfFile(self.project.projConfig)
        else :
            writeToLog(self.project, 'ERR', 'Source file editor [' + sourceEditor + '] is not recognized by this system. Please double check the name used for the source text editor setting.')
            dieNow()


###############################################################################
############################ Functions Begin Here #############################
###############################################################################

    def render(self) :
        '''Does USFM specific rendering of a USFM component'''
            # useful variables: self.project, self.cfg

        self.cid = self.cfg['name']

        def preProcessComponent (cid) :
            '''This will prepare a component for rendering by checking for
            and/or creating any subcomponents it needs to render properly.'''

            # First see if this is a valid component
            if hasUsfmCidInfo(self.cid) :
                terminal("Preprocessing: " + getUsfmCidInfo(self.cid)[0])

                # See if the working text is present
                self.project.managers['usfm_Text'].installUsfmWorkingText(cid)

                # Check on the component styles
                self.project.managers['usfm_Style'].installCompTypeGlobalStyles()
                self.project.managers['usfm_Style'].installCompTypeOverrideStyles()

                # Run any preprocess checks or conversions
                
                # Run any illustration processes needed
                
                # Run any hyphenation or word break routines

            else :
                writeToLog(self.project, 'ERR', 'Invalid component ID: [' + cid + '], cannot be preprocessed.')
                return

        # If this is a meta component, preprocess all subcomponents
        if testForSetting(self.cfg, 'list') :
            for c in self.cfg['list'] :
                preProcessComponent(c)
        else :
            preProcessComponent(self.cid)

        # With everything in place we can render the component
        self.project.managers['usfm_' + self.renderer.capitalize()].run(self.cid)



