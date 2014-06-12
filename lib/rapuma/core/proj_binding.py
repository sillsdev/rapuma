#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle binding component groups in book projects.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, codecs, re, subprocess, tempfile
from configobj                      import ConfigObj, Section

# Load the local classes
from rapuma.core.tools                  import Tools
from rapuma.core.user_config            import UserConfig
from rapuma.core.proj_local             import ProjLocal
from rapuma.core.proj_log               import ProjLog
from rapuma.manager.project             import Project
from rapuma.project.proj_config         import Config
from rapuma.project.proj_background     import ProjBackground


###############################################################################
################################## Begin Class ################################
###############################################################################

class ProjBinding (object) :

    def __init__(self, pid) :
        '''Do the primary initialization for this manager.'''

        self.pid                = pid
        self.tools              = Tools()
        self.user               = UserConfig()
        self.userConfig         = self.user.userConfig
        self.config             = Config(pid)
        self.pg_back            = ProjBackground(self.pid)
        self.config.getProjectConfig()
        self.projectConfig      = self.config.projectConfig
        self.projHome           = None
        self.projectMediaIDCode = None
        self.local              = None
        self.finishInit()

        # Log messages for this module
        self.errorCodes     = {
            '0205' : ['MSG', 'Unassigned message.'],
            '0210' : ['MSG', 'No contents are specified for binding.'],
            '0215' : ['ERR', 'Failed to bind contents into the [<<1>>] fille. Got error: [<<2>>]'],
            '0230' : ['MSG', 'Completed proccessing on the [<<1>>] binding file.'],
            '0235' : ['ERR', 'Failed to complete proccessing on the [<<1>>] binding file.'],
            '0240' : ['LOG', 'Recorded [<<1>>] rendered pages in the [<<2>>] binding file.'],
            '0260' : ['ERR', 'PDF viewer failed with this error: [<<1>>]'],
        }


    def finishInit (self, projHome = None) :
        '''Finishing collecting settings that would be needed for most
        functions in this module.'''

#        import pdb; pdb.set_trace()
        try :
            self.projHome           = os.path.join(self.userConfig['Resources']['projects'], self.pid)
            self.local              = ProjLocal(self.pid)
            self.log                = ProjLog(self.pid)
        except :
            pass


###############################################################################
############################## Binding Functions ##############################
###############################################################################
######################## Error Code Block Series = 200 ########################
###############################################################################

#        import pdb; pdb.set_trace()


    def bind (self, save = False) :
        '''Bind all groups in the order they are indicated by group bindOrder
        settings. Note, because binding spans groups and the main body
        (project.py) mainly just works on one group at a time, this has to
        be called from outside project and project needs to be reinitialized
        each time a group is rendered from here.'''

#        import pdb; pdb.set_trace()

# FIXME: The problem with bind the way it is is that because the process creates 3
# separate files and joins them together with pdftk, we loose the index. What is 
# needed is to make one big control file that runs everything needed in the right order
# This has been reported in the Rapuma bugtracker.

        # Make a name if the file is to be saved
        if save :
            bindFileName = self.pid + '_contents_' + self.tools.ymd()
            # Save this to the Deliverable folder (Make sure there is one)
            if not os.path.isdir(self.local.projDeliverableFolder) :
                os.makedirs(self.local.projDeliverableFolder)
            bindFile = os.path.join(self.local.projDeliverableFolder, bindFileName + '.pdf')
        else :
            bindFile = tempfile.NamedTemporaryFile().name

        # Get the order of the groups to be bound.
        bindOrder = {}
        # Put a safty in here in case there are no groups yet
        if not self.projectConfig.has_key('Groups') :
            return False

        for grp in self.projectConfig['Groups'].keys() :
            if not self.projectConfig['Groups'][grp].has_key('bindingOrder') :
                self.projectConfig['Groups'][grp]['bindingOrder'] = 0
                self.tools.writeConfFile(self.projectConfig)
            if int(self.projectConfig['Groups'][grp]['bindingOrder']) > 0 :
                bindOrder[self.projectConfig['Groups'][grp]['bindingOrder']] = grp
        bindGrpNum = len(bindOrder)
        # Need not keep going if nothing was found
        if bindGrpNum == 0 :
            self.log.writeToLog(self.errorCodes['0210'])
            return False

        # Rerender the groups by bindingOrder value
        keyList = bindOrder.keys()
        keyList.sort()

        # Build the final bind command
        disposable = []
        confCommand = ['pdftk']
        # Append each of the input files
        for key in keyList :
            gidPdf = os.path.join(self.local.projComponentFolder, bindOrder[key], bindOrder[key] + '.pdf')
            confCommand.append(gidPdf)
            disposable.append(gidPdf)
        # Now the rest of the commands and output file
        confCommand.append('cat')
        confCommand.append('output')
        confCommand.append(bindFile)

        # Run the binding command
        rCode = subprocess.call(confCommand)
        # Analyse the return code
        if rCode == int(0) :
            self.log.writeToLog(self.errorCodes['0230'], [self.tools.fName(bindFile)])
        else :
            self.log.writeToLog(self.errorCodes['0235'], [self.tools.fName(bindFile)])

        # Collect the page count and record in group
        newPages = self.tools.pdftkTotalPages(bindFile)
        # FIXME: For now, we need to hard-code the manager name
        manager = 'usfm_Xetex'
        if self.projectConfig['Managers'][manager].has_key('totalBoundPages') :
            oldPages = int(self.projectConfig['Managers'][manager]['totalBoundPages'])
            if oldPages != newPages or oldPages == 'None' :
                self.projectConfig['Managers'][manager]['totalBoundPages'] = newPages
                self.tools.writeConfFile(self.projectConfig)
                self.log.writeToLog(self.errorCodes['0240'], [str(newPages),self.tools.fName(bindFileName)])
        else :
            self.projectConfig['Managers'][manager]['totalBoundPages'] = newPages
            self.tools.writeConfFile(self.projectConfig)
            self.log.writeToLog(self.errorCodes['0240'], [str(newPages),self.tools.fName(bindFileName)])

        # Build the viewer command
        pdfViewerCmd = self.projectConfig['Managers'][manager]['pdfViewerCommand']
        pdfViewerCmd.append(bindFile)
        # Run the XeTeX and collect the return code for analysis
        try :
            subprocess.Popen(pdfViewerCmd)
            return True
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.log.writeToLog(self.errorCodes['0260'], [str(e)])
