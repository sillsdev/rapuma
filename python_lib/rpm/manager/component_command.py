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


class AddFont (Command) :
    '''Add a font set to the project.'''

    type = "font_add"

    def __init__(self, man) :
        super(AddFont, self).__init__()
        self.manager = man

    def run (self, args, aProject, userConfig) :
        super(AddFont, self).run(args, aProject, userConfig)

class AddCompGroup (Command) :
    '''Add a component to a project.'''

    type = "component_add"

    def __init__(self, man) :
        super(AddCompGroup, self).__init__()
        self.manager = man

    def run (self, args, aProject, userConfig) :
        super(AddCompGroup, self).run(args, aProject, userConfig)

        if self.options.components :
            self.manager.addComponentGroup(self.options.name, self.options.components)
        else :
            raise SyntaxError, "Error: Missing required arguments!"

    def setupOptions (self, parser) :
        self.parser.add_option("-n", "--name", type="string", action="store", default="contents", help="Give a name to this component group. (Required)")
        self.parser.add_option("-c", "--components", type="string", action="store", help="Add a component group to the project. A group is one or more component. Enter a file name with complete path. (Required)")


class RemoveCompGroup (Command) :
    '''Remove a component from a project.'''

    type = "component_remove"

    def __init__(self, man) :
        super(RemoveCompGroup, self).__init__()
        self.manager = man

    def run (self, args, aProject, userConfig) :
        super(RemoveCompGroup, self).run(args, aProject, userConfig)

        if self.options.component :
            self.manager.removeComponent(self.options.component)
        else :
            raise SyntaxError, "Error: Missing required arguments!"

    def setupOptions (self, parser) :
        self.parser.add_option("-c", "--component", type="string", action="store", help="Remove a component from the project. (Required)")


