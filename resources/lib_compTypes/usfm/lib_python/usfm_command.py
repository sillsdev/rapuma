#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110823
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle USFM component process commands.  This relys a lot on
# the optparse lib.  Documentation can be found here:
# http://docs.python.org/library/optparse.html

# History:
# 20110823 - djd - Started with intial file from RPM project


###############################################################################
################################# Command Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os
from optparse import OptionParser
from sys_command import Command

###############################################################################
########################### Command Classes Go Here ###########################
###############################################################################
# Insert the commands you want visable to the system here in the order you want
# them to appear when listed.

class Render (Command) :
    '''Render a single component.'''
    
    type = "component_render"
    
    def run (self, args, aProject, userConfig) :
        super(Render, self).run(args, aProject, userConfig)
        comp = aProject.getComponent(self.options.component)
        comp.render()

    def setupOptions (self, parser) :
        self.parser.add_option("-c", "--component", type="string", action="store", help="Render a single project component. (Required)")




