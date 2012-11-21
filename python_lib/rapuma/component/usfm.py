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
from rapuma.core.tools import *
from rapuma.core.pt_tools import *
from rapuma.component.component import Component


###############################################################################
################################## Begin Class ################################
###############################################################################

# As we load the module we will bring in all the common information about all the
# components this type will handle.



class Usfm (Component) :
    '''This class contains information about a type of component 
    used in a type of project.'''

    def __init__(self, project, cfg) :
        super(Usfm, self).__init__(project, cfg)

        # Set values for this manager
        self.project            = project
        self.cid                = ''
        self.cfg                = cfg
        self.cType              = 'usfm'
        self.Ctype              = self.cType.capitalize()

        # Check to see if this component type has been added to the 
        # proj config already
        self.project.addComponentType(self.Ctype)
        self.compSettings = self.project.projConfig['CompTypes']['Usfm']

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)

        self.usfmManagers = ['text', 'style', 'font', 'layout', 'hyphenation', 'illustration', self.renderer]
#        self.usfmManagers = ['text', 'style', 'font', 'layout', 'illustration', self.renderer]

        # Init the general managers
        for mType in self.usfmManagers :
            self.project.createManager(self.cType, mType)

#        # Update default font if needed, usfm_Font manager will figure out which
#        if not self.project.managers[self.cType + '_Font'].varifyFont() :
#            font = self.project.projConfig['Managers'][self.cType + '_Font']['ptDefaultFont']
#            self.project.managers[self.cType + '_Font'].installFont(font)

        # Check if there is a font installed
        self.project.createManager(self.cType, 'font')
        if not self.project.managers[self.cType + '_Font'].varifyFont() :
            # If a PT project, use that font, otherwise, install default
            if self.sourceEditor.lower() == 'paratext' :
                font = self.project.projConfig['Managers'][self.cType + '_Font']['ptDefaultFont']
            else :
                font = 'DefaultFont'

            self.project.managers[self.cType + '_Font'].installFont(font)




        # To better facilitate rendering that might be happening on this run, we
        # will update source file names and other settings used in the usfm_Text
        # manager (It might be better to do this elsewhere, but where?)
        self.project.managers[self.cType + '_Text'].updateManagerSettings()


###############################################################################
############################ Functions Begin Here #############################
###############################################################################

    def render(self, force) :
        '''Does USFM specific rendering of a USFM component'''
            # useful variables: self.project, self.cfg

        self.cid = self.cfg['name']

#        import pdb; pdb.set_trace()

        def preProcessComponent (cid) :
            '''This will prepare a component for rendering by checking for
            and/or creating any subcomponents it needs to render properly.'''

            # First see if this is a valid component. This is a little
            # redundant as this is done in project.py as well. It should
            # be caught there first but just in case we'll do it here too.
            if not self.project.isComponent(cid) :
                self.project.log.writeToLog('COMP-010', ['cid'])
                return False

            # See if the working text is present, quite if it is not
#            if not self.project.managers['usfm_Text'].isUsfmWorkingText(cid) :
#                return False

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



