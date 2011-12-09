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

#        if self.options.component and self.options.type :
#            aProject.addNewComponent(self.options.component, self.options.type)
#        else :
#            raise SyntaxError, "Error: Missing required arguments!"

#        if self.options.auxiliary and self.options.font :
        print dir(aProject)
        if self.options.font :
            self.manager.addFont(self.options.font)
        else :
            raise SyntaxError, "Error: Missing required arguments!"

    def setupOptions (self, parser) :
        self.parser.add_option("-f", "--font", type = "string", action = "store", help = "Specify the font for this actual font component. This font needs to be specified in the font lib. (Required)")



