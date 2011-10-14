#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110907
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle font set process commands.  This relys a lot on the
# optparse lib.  Documentation can be found here:
# http://docs.python.org/library/optparse.html

# History:
# 20110907 - djd - Intial draft


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
 
class SetFont (Command) :
    '''Specify the font for a font set type.'''

    type = "set_font"

    def run (self, args, aProject, userConfig) :
        super(SetFont, self).run(args, aProject, userConfig)
        if not self.options.auxiliary :
            self.options.auxiliary = list(aProject.getAuxiliary('fontSets'))[0]
        if self.options.auxiliary and self.options.font :
            aProject.getAuxiliary(self.options.auxiliary).setFont(self.options.auxiliary, self.options.font)
        else :
            raise SyntaxError, "Error: Missing required arguments!"

    def setupOptions (self, parser) :
        self.parser.add_option("-a", "--auxiliary", type="string", action="store", help="Specify the font auxiliary component ID. (Required)")
        self.parser.add_option("-f", "--font", type="string", action="store", help="Specify the font for this actual font component. This font needs to be specified in the font lib. (Required)")



