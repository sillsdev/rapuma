#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle specific commands for this manager.  General
# project commands can be found in the proj_command.py module.  This relys a lot
# on the optparse lib.  Documentation can be found here:
# http://docs.python.org/library/optparse.html

# History:
# 20111207 - djd - Started with intial file from RPM project


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


class MakeTexHyphen (Command) :
    '''Add a font to a project.'''

    type = "hyphenation_tex"

    def run (self, args, aProject, userConfig) :
        super(MakeTexHyphen, self).run(args, aProject, userConfig)
        if self.options.component and self.options.type :
            aProject.addNewComponent(self.options.component, self.options.type)
        else :
            raise SyntaxError, "Error: Missing required arguments!"

    def setupOptions (self, parser) :
        self.parser.add_option("-c", "--component", type="string", action="store", help="Add a component to the project. (Required)")
        self.parser.add_option("-t", "--type", type="string", action="store", help="Specify the component type. It needs to be valid but not present in the project. (Required)")



