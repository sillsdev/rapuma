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
from rapuma.core.tools          import Tools, ToolsPath
from rapuma.core.proj_config    import ProjConfig
from rapuma.core.user_config    import UserConfig
from rapuma.core.proj_local     import ProjLocal
from rapuma.core.proj_log       import ProjLog


class Compare (object) :

    def __init__(self, pid) :
        '''Intitate the whole class and create the object.'''

        self.pid                = pid
        self.tools              = Tools()
        self.user               = UserConfig()
        self.userConfig         = self.user.userConfig
        self.projHome           = None
        self.projectMediaIDCode = None
        self.local              = None
        self.projConfig         = None
        self.finishInit()

        # Log messages for this module
        self.errorCodes     = {
            '210' : ['WRN', 'File does not exist: [<<1>>] compare cannot be done.'],
            '280' : ['ERR', 'Failed to compare files with error: [<<1>>]'],
            '285' : ['ERR', 'Cannot compare component [<<1>>] because a coresponding subcomponent could not be found.'],
            '290' : ['ERR', 'Compare test type: [<<1>>] is not valid.'],
            '295' : ['MSG', 'Comparing: [<<1>>] with [<<2>>] Close the viewer to return to the terminal prompt.'],
            '220' : ['MSG', 'Comparison not needed, files seem to be the same.'],
        }

    def finishInit (self, projHome = None) :
        '''Finishing collecting settings that would be needed for most
        functions in this module.'''

        try :
            self.projHome           = self.userConfig['Projects'][self.pid]['projectPath']
            self.projectMediaIDCode = self.userConfig['Projects'][self.pid]['projectMediaIDCode']
            self.local              = ProjLocal(self.pid)
            self.projConfig         = ProjConfig(self.local).projConfig
            self.log                = ProjLog(self.pid)
            self.tools_path         = ToolsPath(self.local, self.projConfig, self.userConfig)
        except :
            pass


###############################################################################
############################## Compare Functions ##############################
###############################################################################
######################## Error Code Block Series = 200 ########################
###############################################################################

    def compareComponent (self, gid, cid, test) :
        '''Compare a component with its source which was copied into the project
        when the component was created. This will pull up the user's differential
        viewer and compare the two files.'''

        # Comare between real source and copied (backup) working source
        if test == 'source' :
            new = self.tools_path.getSourceFile(gid, cid)
            old = self.tools_path.getWorkingSourceFile(gid, cid)
        # Comare between working text and the last backup of that text
        elif test == 'working' :
            new = self.tools_path.getWorkingFile(gid, cid)
            old = self.tools_path.getWorkCompareFile(gid, cid)
        # Comare between working text and the copied (backup) source
        elif test == 'source-working' :
            new = self.tools_path.getWorkingFile(gid, cid)
            old = self.tools_path.getWorkingSourceFile(gid, cid)
        else :
            self.log.writeToLog(self.errorCodes['290'], [test])

        # Test to be sure the files are valid
        if not os.path.exists(new) :
            self.log.writeToLog(self.errorCodes['210'], [new])
        elif not os.path.exists(old) :
            self.log.writeToLog(self.errorCodes['210'], [old])
        else :
            # Turn it over to the generic compare tool
            self.compare(new, old)


    def isDifferent (self, new, old) :
        '''Return True if the contents of the files are different.'''

        # Inside of diffl() open both files with universial line endings then
        # check each line for differences.
        diff = difflib.ndiff(open(new, 'rU').readlines(), open(old, 'rU').readlines())
        for d in diff :
            if d[:1] == '+' or d[:1] == '-' :
                return True


    def compare (self, new, old) :
        '''Run a compare on two files. Do not open in viewer unless it is different.'''

        # If there are any differences, open the diff viewer
        if self.isDifferent(new, old) :
            # Get diff viewer
            diffViewer = self.userConfig['System']['textDifferentialViewerCommand']
            try :
                self.log.writeToLog(self.errorCodes['295'], [self.tools.fName(new),self.tools.fName(old)])
                subprocess.call([diffViewer, new, old])
            except Exception as e :
                # If we don't succeed, we should probably quite here
                self.log.writeToLog(self.errorCodes['280'], [str(e)])
        else :
            self.log.writeToLog(self.errorCodes['220'])



