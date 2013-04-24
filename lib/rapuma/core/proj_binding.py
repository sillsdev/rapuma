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
            '0250' : ['MSG', 'Binding component [<<1>>] not found. Will create/recreate it now.'],
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

    def addBindingGroup (self, bgID, gIDs, force = False) :
        '''Add a binding group to the project.'''

        if force :
            try :
                if self.tools.testForSetting(self.projConfig['Groups'], bgID) :
                    del self.projConfig['Groups'][bgID]
            except :
                pass

        try :
            # Add the info to the components section
            if not self.tools.testForSetting(self.projConfig['Groups'], bgID) :
                self.tools.buildConfSection(self.projConfig['Groups'], bgID)
                self.projConfig['Groups'][bgID]['gidList'] = gIDs.split()
                self.projConfig['Groups'][bgID]['cType'] = 'bind'
                self.tools.writeConfFile(self.projConfig)
                self.log.writeToLog(self.errorCodes['0210'], [bgID])
            else :
                self.log.writeToLog(self.errorCodes['0212'], [bgID])
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.log.writeToLog(self.errorCodes['0215'], [bgID,str(e)])


    def removeBindingGroup (self, bgID) :
        '''Remove a binding group from the project config.'''

        if self.tools.testForSetting(self.projConfig['Groups'], bgID) :
            del self.projConfig['Groups'][bgID]
            self.tools.writeConfFile(self.projConfig)
            self.log.writeToLog(self.errorCodes['0220'], [bgID])
        else :
            self.log.writeToLog(self.errorCodes['0225'], [bgID])


    def bindComponents (self, bgID) :
        '''Bind a project binding group. Right now this is hard-wired to only work
        with pdftk.'''

#        import pdb; pdb.set_trace()

        # Check for components and render any that do not exist
        for gid in self.projConfig['Groups'][bgID]['gidList'] :
            gidPdf = os.path.join(self.local.projDeliverablesFolder, gid + '.pdf')
            cType = self.projConfig['Groups'][gid]['cType']
            renderer = self.projConfig['CompTypes'][cType.capitalize()]['renderer']
            manager = cType + '_' + renderer.capitalize()
            if not os.path.exists(gidPdf) :
                self.log.writeToLog(self.errorCodes['0250'], [self.tools.fName(gidPdf)])
                # Seriously!, a bind command should not be called when components
                # have not been created. However, if that's the case, then we'll
                # do it this way even though it is not the most efficient.
                # Suspend the PDF viewer for this operation if needed
                orgPdfViewerSettings = self.projConfig['Managers'][manager]['usePdfViewer']
                if orgPdfViewerSettings == 'True' :
                    self.projConfig['Managers'][manager]['usePdfViewer'] = False
                    self.tools.writeConfFile(self.projConfig)
                # Render the group
                Project(self.pid, gid).renderGroup(gid, '', '')
                # Turn on the PDF viewer if needed
                if self.projConfig['Managers'][manager]['usePdfViewer'] != orgPdfViewerSettings :
                    self.projConfig['Managers'][manager]['usePdfViewer'] = orgPdfViewerSettings
                    self.tools.writeConfFile(self.projConfig)

        # Build the command
        confCommand = ['pdftk']
        # Append each of the input files
        for gid in self.projConfig['Groups'][bgID]['gidList'] :
            gidPdf = os.path.join(self.local.projDeliverablesFolder, gid + '.pdf')
            confCommand.append(gidPdf)
        # Now the rest of the commands and output file
        confCommand.append('cat')
        confCommand.append('output')
        output = os.path.join(self.local.projDeliverablesFolder, bgID + '.pdf')
        confCommand.append(output)
        # Run the binding command
        rCode = subprocess.call(confCommand)
        # Analyse the return code
        if rCode == int(0) :
            self.log.writeToLog(self.errorCodes['0230'], [bgID])
        else :
            self.log.writeToLog(self.errorCodes['0235'], [bgID])

        # Collect the page count and record in group
        newPages = self.getPdfPages(output)
        if self.tools.testForSetting(self.projConfig['Groups'][bgID], 'totalPages') :
            oldPages = int(self.projConfig['Groups'][bgID]['totalPages'])
            if oldPages != newPages or oldPages == 'None' :
                self.projConfig['Groups'][bgID]['totalPages'] = newPages
                self.tools.writeConfFile(self.projConfig)
                self.log.writeToLog(self.errorCodes['0240'], [str(newPages),bgID])
        else :
            self.projConfig['Groups'][bgID]['totalPages'] = newPages
            self.tools.writeConfFile(self.projConfig)
            self.log.writeToLog(self.errorCodes['0240'], [str(newPages),bgID])

        # Build the viewer command
        pdfViewer = self.projConfig['Managers'][manager]['pdfViewerCommand']
        pdfViewer.append(output)
        # Run the viewer and collect the return code for analysis
        try :
            subprocess.Popen(pdfViewer)
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.log.writeToLog(self.errorCodes['0260'], [str(e)])


    def getPdfPages (self, pdfFile) :
        '''Get the total number of pages in a PDF file.'''

        # Create a temporary file that we will use to hold data.
        # It should be deleted after the function is done.
        rptData = tempfile.NamedTemporaryFile()
        rCode = subprocess.call(['pdftk', pdfFile, 'dump_data', 'output', rptData.name])
        with codecs.open(rptData.name, 'rt', 'utf_8_sig') as contents :
            for line in contents :
                if line.split(':')[0] == 'NumberOfPages' :
                    return int(line.split(':')[1].strip())




