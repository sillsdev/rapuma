#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project backup/archive operations.

###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, difflib, subprocess
from configobj import ConfigObj

# Load the local classes
from rapuma.core.tools              import Tools
from rapuma.core.user_config        import UserConfig
from rapuma.core.proj_log           import ProjLog


class ProjCompare (object) :

    def __init__(self, pid) :
        '''Intitate the whole class and create the object.'''

        self.pid                            = pid
        self.log                            = ProjLog(self.pid)
        self.tools                          = Tools()
        self.user                           = UserConfig()
        self.userConfig                     = self.user.userConfig
        self.projectMediaIDCode = self.userConfig['Projects'][self.pid]['projectMediaIDCode']
        self.diffViewCmd                    = self.userConfig['System']['textDifferentialViewerCommand']

        # Make sure the diff view command is a list
        if type(self.diffViewCmd) != list :
            self.diffViewCmd = [self.userConfig['System']['textDifferentialViewerCommand']]

        # Log messages for this module
        self.errorCodes     = {
            '0210' : ['WRN', 'File does not exist: [<<1>>] compare cannot be done.'],
            '0280' : ['ERR', 'Failed to compare files with error: [<<1>>]'],
            '0285' : ['ERR', 'Cannot compare component [<<1>>] because a coresponding subcomponent could not be found.'],
            '0290' : ['ERR', 'Compare test type: [<<1>>] is not valid.'],
            '0295' : ['MSG', 'Comparing: [<<1>>] with [<<2>>] Close the viewer to return to the terminal prompt.'],
            '0220' : ['MSG', 'Comparison not needed, files seem to be the same.'],
        }


###############################################################################
############################## Compare Functions ##############################
###############################################################################
######################## Error Code Block Series = 0200 ########################
###############################################################################

    def compareComponent (self, gid, cid, test) :
        '''Compare a component with its source which was copied into the project
        when the component was created. This will pull up the user's differential
        viewer and compare the two files.'''

        print 'ERROR: proj_compare.compareComponent() needs to be rewritten!'


    def isDifferent (self, new, old) :
        '''Return True if the contents of the files are different.'''

        # If one file is missing, return True
        if not os.path.exists(new) or not os.path.exists(old) :
            return True

        # Inside of diffl() open both files with universial line endings then
        # check each line for differences.
        diff = difflib.ndiff(open(new, 'rU').readlines(), open(old, 'rU').readlines())
        for d in diff :
            if d[:1] == '+' or d[:1] == '-' :
                return True
        # FIXME: Is returning False better than None?
        return False


    def compare (self, new, old) :
        '''Run a compare on two files. Do not open in viewer unless it is different.'''

#        import pdb; pdb.set_trace()

        # If there are any differences, open the diff viewer
        if self.isDifferent(new, old) :
            # To prevent file names being pushed back to the list ref
            # we need to use extend() rather than append()
            cmd = []
            cmd.extend(self.diffViewCmd)
            cmd.extend([new, old])
            try :
                self.log.writeToLog(self.errorCodes['0295'], [self.tools.fName(new),self.tools.fName(old)])
                subprocess.call(cmd)
            except Exception as e :
                # If we don't succeed, we should probably quite here
                self.log.writeToLog(self.errorCodes['0280'], [str(e)])
        else :
            self.log.writeToLog(self.errorCodes['0220'])



