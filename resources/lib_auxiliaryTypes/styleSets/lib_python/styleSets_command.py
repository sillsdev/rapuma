#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111013
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle style type set process commands.  This relys a
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

class SetStyle (Command) :
    '''Specify the style set (format) for a type of content.'''

    type = "set_style"

    def run (self, args, aProject, userConfig) :
        super(SetStyle, self).run(args, aProject, userConfig)
        if not self.options.auxiliary :
            self.options.auxiliary = list(aProject.getAuxiliary('styleSets'))[0]
        if self.options.auxiliary and self.options.style :
            aProject.getAuxiliary(self.options.auxiliary).setStyle(self.options.auxiliary, self.options.style)
        else :
            raise SyntaxError, "Error: Missing required arguments!"

    def setupOptions (self, parser) :
        self.parser.add_option("-a", "--auxiliary", type="string", action="store", help="Specify the style auxiliary component. (Required)")
        self.parser.add_option("-s", "--style", type="string", action="store", help="Specify the style for this actual auxiliary component. (Required)")



