#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110907
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle page composition set process commands.  This relys a
# lot on the optparse lib.  Documentation can be found here:
# http://docs.python.org/library/optparse.html

# History:
# 20111013 - djd - Intial draft


###############################################################################
################################# Command Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os
from optparse import OptionParser
from sys_command import Command, commands

###############################################################################
########################### Command Classes Go Here ###########################
###############################################################################

class SetPageComp (Command) :
    '''Specify the composition set (format) for a type of content.'''

    type = "set_pagecomp"

    def run (self, args, aProject, userConfig) :
        super(SetPageComp, self).run(args, aProject, userConfig)
        if not self.options.component :
            self.options.component = list(aProject.getComponents('pageCompSets'))[0]
        if self.options.component and self.options.pagecomp :
            aProject.getComponent(self.options.component).setPageComp(self.options.component, self.options.pagecomp)
        else :
            raise SyntaxError, "Error: Missing required arguments!"

    def setupOptions (self, parser) :
        self.parser.add_option("-c", "--component", type="string", action="store", help="Specify the font component. (Required)")
        self.parser.add_option("-p", "--pagecomp", type="string", action="store", help="Specify the page composition for this component. (Required)")



