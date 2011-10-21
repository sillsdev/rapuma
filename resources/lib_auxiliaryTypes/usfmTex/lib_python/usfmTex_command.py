#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111019
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle USFM TeX macro process commands.  This relys a lot on
# the optparse lib.  Documentation can be found here:
# http://docs.python.org/library/optparse.html

# History:
# 20111019 - djd - Intial draft


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
 
class SetTexMacros (Command) :
    '''Specify the font for a font set type.'''

    type = "set_texmacros"

    def run (self, args, aProject, userConfig) :
        super(SetTexMacros, self).run(args, aProject, userConfig)
        if not self.options.auxiliary :
            self.options.auxiliary = list(aProject.getAuxiliary('usfmTex'))[0]
        if self.options.macros :
            aProject.getAuxiliary(self.options.auxiliary).setTexMacros(self.options.macros)
        else :
            raise SyntaxError, "Error: Missing required arguments!"

    def setupOptions (self, parser) :
        self.parser.add_option("-m", "--macros", type = "string", action = "store", default = "normal", help = "Indicate the type of TeX macro set you wish to use on this publication. The default is normal.")



