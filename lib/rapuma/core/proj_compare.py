#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110823
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
from rapuma.core.tools          import *
from rapuma.core.proj_config    import ProjConfig
from rapuma.core.user_config    import UserConfig
from rapuma.core.proj_local     import ProjLocal
from rapuma.core.proj_log       import ProjLog


class Compare (object) :

    def __init__(self, pid) :
        '''Intitate the whole class and create the object.'''

        self.rapumaHome         = os.environ.get('RAPUMA_BASE')
        self.userHome           = os.environ.get('RAPUMA_USER')
        self.user               = UserConfig(self.rapumaHome, self.userHome)
        self.userConfig         = self.user.userConfig
        self.pid                = pid
        self.projHome           = None
        self.projectMediaIDCode = None
        self.local              = None
        self.projConfig         = None
        self.finishInit()


    def finishInit (self, projHome = None) :
        '''Finishing collecting settings that would be needed for most
        functions in this module.'''

        try :
            self.projHome           = self.userConfig['Projects'][self.pid]['projectPath']
            self.projectMediaIDCode = self.userConfig['Projects'][self.pid]['projectMediaIDCode']
            self.local              = ProjLocal(self.rapumaHome, self.userHome, self.projHome)
            self.projConfig         = ProjConfig(self.local).projConfig
            self.log                = ProjLog(self.local, self.user)
        except :
            pass


###############################################################################
############################## Compare Functions ##############################
###############################################################################

    def compareComponent (self, gid, cid, test) :
        '''Compare a component with its source which was copied into the project
        when the component was created. This will pull up the user's differential
        viewer and compare the two files.'''

        # What kind of test is this
        cType       = self.projConfig['Groups'][gid]['cType']
        csid        = self.projConfig['Groups'][gid]['csid']
        fileWork    = cid + '_' + csid + '.' + cType
        fileCv1     = cid + '_' + csid + '.' + cType + '.cv1'
        if test == 'working' :
            new = os.path.join(self.local.projComponentsFolder, cid, fileWork)
            old = os.path.join(self.local.projComponentsFolder, cid, fileCv1)
        elif test == 'source' :
            for f in os.listdir(os.path.join(self.local.projComponentsFolder, cid)) :
                if f.find('.source') > 0 :
                    new = os.path.join(self.local.projComponentsFolder, cid, fileWork)
                    old = os.path.join(self.local.projComponentsFolder, cid, f)
                    break
        else :
            self.log.writeToLog('COMP-190', [test])

        # Turn it over to the generic compare tool
        self.compare(new, old)


    def isDifferent (self, new, old) :
        '''Return True if the contents of the files are different.'''

        # Inside of diffl() open both files with universial line endings then
        # check each line for differences.
        diff = difflib.ndiff(open(new, 'rU').readlines(), open(old, 'rU').readlines())
        comp = False
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
                self.log.writeToLog('COMP-195', [fName(new),fName(old)])
                subprocess.call([diffViewer, new, old])
            except Exception as e :
                # If we don't succeed, we should probably quite here
                self.log.writeToLog('COMP-180', [str(e)])
                dieNow()
        else :
            self.log.writeToLog('COMP-198')



