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
        self.config.getLayoutConfig()
        self.projectConfig      = self.config.projectConfig
        self.layoutConfig       = self.config.layoutConfig
        self.useBackground      = self.tools.str2bool(self.layoutConfig['DocumentFeatures']['useBackground'])
        self.useDocInfo         = self.tools.str2bool(self.layoutConfig['DocumentFeatures']['useDocInfo'])
        self.projHome           = os.path.join(self.userConfig['Resources']['projects'], self.pid)
        self.local              = ProjLocal(self.pid)
        self.log                = ProjLog(self.pid)

        # Log messages for this module
        self.errorCodes     = {
            '0205' : ['MSG', 'Unassigned message.'],
            '0210' : ['MSG', 'No contents are specified for binding.'],
            '0215' : ['ERR', 'Failed to bind contents into the [<<1>>] fille. Got error: [<<2>>]'],
            '0220' : ['ERR', 'Could not copy [<<1>>] temp file to [<<2>>] saved binding file.'],
            '0230' : ['MSG', 'Completed proccessing on the [<<1>>] binding file.'],
            '0235' : ['ERR', 'Failed to complete proccessing on the [<<1>>] binding file.'],
            '0240' : ['LOG', 'Recorded [<<1>>] rendered pages in the [<<2>>] binding file.'],
            '0260' : ['ERR', 'PDF viewer failed with this error: [<<1>>]'],
            '0280' : ['ERR', 'GS PDF file merge failed with this error: [<<1>>]'],
            '0300' : ['MSG', 'File binding operation in process, please wait...']
        }


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

        # Get the order of the groups to be bound.
        bindOrder = {}
        # Put a safty in here in case there are no groups yet
        if not self.projectConfig.has_key('Groups') :
            return False

        # Build the bindOrder dict with ord num as key and file name as value
        for gid in self.projectConfig['Groups'].keys() :
            if not self.projectConfig['Groups'][gid].has_key('bindingOrder') :
                self.projectConfig['Groups'][gid]['bindingOrder'] = 0
                self.tools.writeConfFile(self.projectConfig)
            if int(self.projectConfig['Groups'][gid]['bindingOrder']) > 0 :
                gidPdfFile = os.path.join(self.local.projComponentFolder, gid, gid + '.pdf')
#                bindOrder[self.projectConfig['Groups'][gid]['bindingOrder']] = self.projectConfig['Groups'][gid]['bindingFile']
                bindOrder[self.projectConfig['Groups'][gid]['bindingOrder']] = gidPdfFile
        bindGrpNum = len(bindOrder)
        # Need not keep going if nothing was found
        if bindGrpNum == 0 :
            self.log.writeToLog(self.errorCodes['0210'])
            return False

        # Make an ordered key list
        keyList = bindOrder.keys()
        keyList.sort()

        # Output the bind files in order according to the list we made
        fileList = []
        for key in keyList :
            fileList.append(bindOrder[key])

        # First merge the master pages together
        tempFile = self.mergePdfFilesGs(fileList)

        # Now add background and doc info if requested
        bgFile = ''
        if self.useBackground :
            bgFile = self.pg_back.addBackground(tempFile)
        if self.useDocInfo :
            if bgFile :
                bgFile = self.pg_back.addDocInfo(bgFile)
            else :
                bgFile = self.pg_back.addDocInfo(tempFile)

        # If we are saving this make a name for it
        if save :
            bindFileName = self.pid + '_contents_' + self.tools.ymd()
            # Save this to the Deliverable folder (Make sure there is one)
            if not os.path.isdir(self.local.projDeliverableFolder) :
                os.makedirs(self.local.projDeliverableFolder)
            bindFile = os.path.join(self.local.projDeliverableFolder, bindFileName + '.pdf')
            if os.path.exists(bgFile) :
                if shutil.copy(bgFile, bindFile) :
                    self.log.writeToLog(self.errorCodes['0220'], [bgFile,bindFile])
            else :
                if shutil.copy(tempFile, bindFile) :
                    self.log.writeToLog(self.errorCodes['0220'], [tempFile,bindFile])
            # Direct to viewFile
            viewFile = bindFile
                
        else :
            if os.path.exists(bgFile) :
                viewFile = bgFile
            else :
                viewFile = tempFile

        # Build the viewer command (fall back to default if needed)
        # FIXME: For now, we need to hard-code the manager name (usfm_Xetex)
        pdfViewerCmd = self.projectConfig['Managers']['usfm_Xetex']['pdfViewerCommand']
        if not pdfViewerCmd :
            pdfViewerCmd = self.userConfig['System']['pdfViewerCommand']

        pdfViewerCmd.append(viewFile)
        # Run the XeTeX and collect the return code for analysis
        try :
            subprocess.Popen(pdfViewerCmd)
            return True
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.log.writeToLog(self.errorCodes['0260'], [str(e)])


    def mergePdfFilesGs (self, sourceList) :
        '''Using GS, merge multiple PDF files into one. The advantage of
        using Gs is that the index will be maintained. pdftk strips out
        the index, which is bad...'''

        # This is our working file for this operation
        tempFile = tempfile.NamedTemporaryFile().name + '.pdf'


        cmd = ['gs', '-dBATCH', '-dNOPAUSE', '-q', '-sDEVICE=pdfwrite', '-dPDFSETTINGS=/prepress', '-sOutputFile=' + tempFile]
        cmd = cmd + sourceList

        try :
            self.log.writeToLog(self.errorCodes['0300'])
            subprocess.call(cmd)
            # Return our file name for further processing
            return tempFile
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.log.writeToLog(self.errorCodes['0280'], [str(e)])




