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
from configobj                  import ConfigObj, Section

# Load the local classes
from rapuma.core.tools          import Tools
from rapuma.core.proj_config    import ProjConfig
from rapuma.core.user_config    import UserConfig
from rapuma.core.proj_local     import ProjLocal
from rapuma.core.proj_log       import ProjLog


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
                if self.tools.testForSetting(self.projConfig['Binding'], bgID) :
                    del self.projConfig['Binding'][bgID]
            except :
                pass

        try :
            # Add the info to the components section
            if not self.tools.testForSetting(self.projConfig, 'Binding') :
                self.tools.buildConfSection(self.projConfig, 'Binding')
            if not self.tools.testForSetting(self.projConfig['Binding'], bgID) :
                self.tools.buildConfSection(self.projConfig['Binding'], bgID)
                self.projConfig['Binding'][bgID]['gidList'] = gIDs.split()
                self.tools.writeConfFile(self.projConfig)
                self.log.writeToLog(self.errorCodes['0210'], [bgID])
            else :
                self.log.writeToLog(self.errorCodes['0212'], [bgID])
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.log.writeToLog(self.errorCodes['0215'], [bgID,str(e)])


    def removeBindingGroup (self, bgID) :
        '''Remove a binding group from the project config.'''

        if self.tools.testForSetting(self.projConfig['Binding'], bgID) :
            del self.projConfig['Binding'][bgID]
            self.tools.writeConfFile(self.projConfig)
            self.log.writeToLog(self.errorCodes['0220'], [bgID])
        else :
            self.log.writeToLog(self.errorCodes['0225'], [bgID])


    def bindComponents (self, bgID) :
        '''Bind a project binding group. Right now this is hard-wired to only work
        with pdftk.'''

        # Build the command
        confCommand = ['pdftk']
        outputPath = os.path.join(self.local.projComponentsFolder, bgID)
        if not os.path.exists(outputPath) :
            os.makedirs(outputPath)
        # Append each of the input files
        for f in self.projConfig['Binding'][bgID]['gidList'] :
            f = os.path.join(self.local.projComponentsFolder, f, f + '.pdf')
            confCommand.append(f)
        # Now the rest of the commands and output file
        confCommand.append('cat')
        confCommand.append('output')
        output = os.path.join(outputPath, bgID + '.pdf')
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
        if self.tools.testForSetting(self.projConfig['Binding'][bgID], 'totalPages') :
            oldPages = int(self.projConfig['Binding'][bgID]['totalPages'])
            if oldPages != newPages or oldPages == 'None' :
                self.projConfig['Binding'][bgID]['totalPages'] = newPages
                self.tools.writeConfFile(self.projConfig)
                self.log.writeToLog(self.errorCodes['0240'], [str(newPages),bgID])
        else :
            self.projConfig['Binding'][bgID]['totalPages'] = newPages
            self.tools.writeConfFile(self.projConfig)
            self.log.writeToLog(self.errorCodes['0240'], [str(newPages),bgID])





# FIXME: Add a view feature here once the viewer can be moved to the reworked tools module








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




