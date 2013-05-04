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
from rapuma.core.tools              import Tools
from rapuma.core.proj_config        import ProjConfig
from rapuma.core.user_config        import UserConfig
from rapuma.core.proj_local         import ProjLocal
from rapuma.core.proj_log           import ProjLog
from rapuma.project.project         import Project


###############################################################################
################################## Begin Class ################################
###############################################################################

class Binding (object) :

    def __init__(self, pid) :
        '''Do the primary initialization for this manager.'''

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
            '0000' : ['MSG', 'Placeholder message'],
            
            '0205' : ['MSG', 'Unassigned message.'],
            '0210' : ['MSG', 'Created the [<<1>>] binding group.'],
            '0212' : ['WRN', 'The [<<1>>] binding group already exists. Use force to replace.'],
            '0215' : ['ERR', 'Failed to create the [<<1>>] binding group. Got error: [<<2>>]'],
            '0220' : ['MSG', 'Removed the [<<1>>] binding group.'],
            '0225' : ['ERR', 'The [<<1>>] binding group was not found.'],
            '0230' : ['MSG', 'Completed proccessing on the [<<1>>] binding group.'],
            '0235' : ['ERR', 'Failed to complete proccessing on the [<<1>>] binding group.'],
            '0240' : ['LOG', 'Recorded [<<1>>] rendered pages in the [<<2>>] binding group.'],
            '0250' : ['MSG', 'Completed final render on Binding component [<<1>>].'],
            '0260' : ['ERR', 'PDF viewer failed with this error: [<<1>>]'],

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
        except :
            pass


###############################################################################
############################## Binding Functions ##############################
###############################################################################
######################## Error Code Block Series = 200 ########################
###############################################################################

#        import pdb; pdb.set_trace()

#    def initProject (self, pid, gid) :
#        '''Initialize an existing project according to the project ID given.
#        This is slightly different from the one in the main rapuma script.'''

#        local       = ProjLocal(pid)
#        pc          = ProjConfig(local)
#        log         = ProjLog(pid)
#        return        Project(pid, gid)


    def bind (self) :
        '''Bind all groups in the order they are indicated by group bindOrder
        settings. Note, because binding spans groups and the main body
        (project.py) mainly just works on one group at a time, this has to
        be called from outside project and project needs to be reinitialized
        each time a group is rendered from here.'''

        # Get the order of the groups to be bound.
        bindOrder = {}
        for grp in self.projConfig['Groups'].keys() :
            if not self.tools.testForSetting(self.projConfig['Groups'][grp], 'bindingOrder') :
                self.projConfig['Groups'][grp]['bindingOrder'] = 0
                self.tools.writeConfFile(self.projConfig)
            if int(self.projConfig['Groups'][grp]['bindingOrder']) > 0 :
                bindOrder[self.projConfig['Groups'][grp]['bindingOrder']] = grp
        bindGrpNum = len(bindOrder)
        # Need not keep going if nothing was found
        if bindGrpNum == 0 :
            self.log.writeToLog(self.errorCodes['0410'])
            return False




# FIXME: main work starts in here some place
# will also need to add back all the "self.gid" markers in all
# the project managers.




        # Rerender the groups by bindingOrder value
        keyList = bindOrder.keys()
        keyList.sort()
        for key in keyList :
            # Do a force render in the bind mode
            Project(self.pid, bindOrder[key]).renderGroup(bindOrder[key], 'bind', '', True)




        # Build the final bind command
        confCommand = ['pdftk']
        # Append each of the input files
        for key in keyList :
            gidPdf = os.path.join(self.local.projComponentsFolder, bindOrder[key], bindOrder[key] + '.pdf')
            confCommand.append(gidPdf)
        # Now the rest of the commands and output file
        confCommand.append('cat')
        confCommand.append('output')
        output = os.path.join(self.local.projDeliverablesFolder, self.pid + '_' + self.tools.ymd() + '.pdf')
        confCommand.append(output)
        # Run the binding command
        rCode = subprocess.call(confCommand)
        # Analyse the return code
        if rCode == int(0) :
            self.log.writeToLog(self.errorCodes['0230'], [self.tools.fName(output)])
        else :
            self.log.writeToLog(self.errorCodes['0235'], [self.tools.fName(output)])

        # Collect the page count and record in group
        newPages = self.tools.getPdfPages(output)
        # FIXME: For now, we need to hard-code the manager name
        manager = 'usfm_Xetex'
        if self.tools.testForSetting(self.projConfig['Managers'][manager], 'totalBoundPages') :
            oldPages = int(self.projConfig['Managers'][manager]['totalBoundPages'])
            if oldPages != newPages or oldPages == 'None' :
                self.projConfig['Managers'][manager]['totalBoundPages'] = newPages
                self.tools.writeConfFile(self.projConfig)
                self.log.writeToLog(self.errorCodes['0240'], [str(newPages),self.tools.fName(output)])
        else :
            self.projConfig['Managers'][manager]['totalBoundPages'] = newPages
            self.tools.writeConfFile(self.projConfig)
            self.log.writeToLog(self.errorCodes['0240'], [str(newPages),self.tools.fName(output)])

        # Build the viewer command
        pdfViewer = self.projConfig['Managers'][manager]['pdfViewerCommand']
        pdfViewer.append(output)
        # Run the viewer and collect the return code for analysis
        try :
            subprocess.Popen(pdfViewer)
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.log.writeToLog(self.errorCodes['0260'], [str(e)])


