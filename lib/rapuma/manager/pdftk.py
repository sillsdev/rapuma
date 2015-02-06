#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This manager class will handle PDF handling operations with pdftk.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, re, codecs, subprocess
from configobj                          import ConfigObj
from pyPdf                              import PdfFileReader

# Load the local classes
from rapuma.core.tools                  import Tools
from rapuma.manager.manager             import Manager
from rapuma.project.proj_config         import Config
from rapuma.project.proj_background     import ProjBackground
from rapuma.project.proj_diagnose       import ProjDiagnose


###############################################################################
################################## Begin Class ################################
###############################################################################

class Pdftk (Manager) :

    # Shared values
    xmlConfFile     = 'pdftk.xml'

    def __init__(self, project, cfg, cType) :
        '''Do the primary initialization for this manager.'''

        super(Pdftk, self).__init__(project, cfg)

#        import pdb; pdb.set_trace()

        # Create all the values we can right now for this manager.
        # Others will be created at run time when we know the cid.
        self.tools                  = Tools()
        self.project                = project
        self.local                  = project.local
        self.log                    = project.log
        self.cfg                    = cfg
        self.pid                    = project.projectIDCode
        self.gid                    = project.gid
        self.cType                  = cType
        self.Ctype                  = cType.capitalize()
        self.mType                  = project.projectMediaIDCode
        self.renderer               = 'pdftk'
        self.manager                = self.cType + '_' + self.renderer.capitalize()
        self.managers               = project.managers
        self.pg_back                = ProjBackground(self.pid, self.gid)
        self.fmt_diagnose           = ProjDiagnose(self.pid, self.gid)
        self.proj_config            = Config(self.pid, self.gid)
        self.proj_config.getProjectConfig()
        self.proj_config.getLayoutConfig()
        # Get config objs
        self.projectConfig          = self.proj_config.projectConfig
        self.layoutConfig           = self.proj_config.layoutConfig
        self.userConfig             = self.project.userConfig
        # Some config settings
        self.pdfViewerCmd           = self.project.userConfig['System']['pdfViewerCommand']
        self.pdfUtilityCmd          = self.project.userConfig['System']['pdfUtilityCommand']
        self.useBackground          = self.tools.str2bool(self.layoutConfig['DocumentFeatures']['useBackground'])
        self.useDocInfo             = self.tools.str2bool(self.layoutConfig['DocumentFeatures']['useDocInfo'])

        # Get settings for this component
        self.managerSettings = self.projectConfig['Managers'][self.manager]
        for k, v in self.managerSettings.iteritems() :
            if v == 'True' or v == 'False' :
                setattr(self, k, self.tools.str2bool(v))
            else :
                setattr(self, k, v)

        # Make any dependent folders if needed
        if not os.path.isdir(self.local.projGidFolder) :
            os.makedirs(self.local.projGidFolder)


        # Log messages for this module
        self.errorCodes     = {

            '0000' : ['MSG', 'Messages for the pdftk module.'],

            '5010' : ['ERR', 'Subprocess failed with this error: <<1>>'],
            '5020' : ['MSG', 'PDF merge was successful. Output = <<1>>'],
            '5200' : ['ERR', 'Rendered file not found: <<1>>'],
            '5210' : ['WRN', 'PDF viewing is disabled.'],
            '5720' : ['MSG', 'Saved rendered file to: [<<1>>]'],
            '5730' : ['ERR', 'Failed to save rendered file to: [<<1>>]']

        }


###############################################################################
############################ Manager Level Functions ##########################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################

    def sourceListFromCidList (self, cidList) :
        '''Return a sourceList derived from a given cidList.'''

        sourceList = []
        for cid in cidList :
            sourceList.append(self.sourceFromCid(cid))

        return sourceList

    def sourceFromCid (self, cid) :
        '''Return the full path with file name derived from a valid cid.'''
        
        return os.path.join(self.local.projComponentFolder, cid, cid + '.pdf')


###############################################################################
################################# Main Function ###############################
###############################################################################
######################## Error Code Block Series = 5000 #######################
###############################################################################

    def run (self, gid, cidList, pgRange, override, save) :
        '''This will check all the dependencies for a group and then
        use pdftk to "render" the whole group or a subset of components
        and even a page range in a single component.'''

#        import pdb; pdb.set_trace()

        # There must be a cidList. If one was not passed, default to
        # the group list
        cidListSubFileName      = ''
        saveFile                = ''
        saveFileName            = ''
        viewFile                = ''
        if not cidList :
            cidList = self.projectConfig['Groups'][gid]['cidList']

        # Make a list of files that pdftk will merge together
        sourceList = self.sourceListFromCidList(cidList)
                
        # Merge the files
        cmd = ['pdftk'] + sourceList + ['cat', 'output', self.local.gidPdfFile]

#        import pdb; pdb.set_trace()

        # No return from pdftk is good, we can continue on
        if not subprocess.call(cmd) : 
            # Collect the page count and record in group (Write out at the end of the opp.)
            self.projectConfig['Groups'][gid]['totalPages'] = str(PdfFileReader(open(self.local.gidPdfFile)).getNumPages())
            # Write out any changes made to the project.conf file that happened during this opp.
            self.tools.writeConfFile(self.projectConfig)

            # Pull out pages if requested (use the same file for output)
            if pgRange :
                self.tools.pdftkPullPages(self.local.gidPdfFile, self.local.gidPdfFile, pgRange)

            # The gidPdfFile is the residue of the last render and if approved, can be
            # used for the binding process. In regard to saving and file naming, the
            # gidPdfFile will be copied but never renamed. It must remain intact.

            # If the user wants to save this file or use a custom name, do that now
            if save and not override :
                saveFileName = self.pid + '_' + gid
                if cidListSubFileName :
                    saveFileName = saveFileName + '_' + cidListSubFileName
                if pgRange :
                    saveFileName = saveFileName + '_pg(' + pgRange + ')'
                # Add date stamp
                saveFileName = saveFileName + '_' + self.tools.ymd()
                # Add render file extention
                saveFileName = saveFileName + '.pdf'
                # Save this to the Deliverable folder (Make sure there is one)
                if not os.path.isdir(self.local.projDeliverableFolder) :
                    os.makedirs(self.local.projDeliverableFolder)
                # Final file name and path
                saveFile = os.path.join(self.local.projDeliverableFolder, saveFileName)
                # Copy, no news is good news
                if shutil.copy(self.local.gidPdfFile, saveFile) :
                    self.log.writeToLog(self.errorCodes['5730'], [saveFileName])
                else :
                    self.log.writeToLog(self.errorCodes['5720'], [saveFileName])            

            # If given, the override file name becomes the file name 
            if override :
                saveFile = override
                # With shutil.copy(), no news is good news
                if shutil.copy(self.local.gidPdfFile, saveFile) :
                    self.log.writeToLog(self.errorCodes['5730'], [saveFileName])
                else :
                    self.log.writeToLog(self.errorCodes['5720'], [saveFileName])

            # Once we know the file is successfully generated, add a background if defined
            if self.useBackground :
                if saveFile :
                    viewFile = self.pg_back.addBackground(saveFile)
                else :
                    viewFile = self.pg_back.addBackground(self.local.gidPdfFile)
                    
            # Add a timestamp and doc info if requested in addition to background
            if self.useDocInfo :
                if saveFile :
                    if os.path.isfile(viewFile) :
                        viewFile = self.pg_back.addDocInfo(viewFile)
                    else :
                        viewFile = self.pg_back.addDocInfo(saveFile)
                else :
                    if os.path.isfile(viewFile) :
                        viewFile = self.pg_back.addDocInfo(viewFile)
                    else :
                        viewFile = self.pg_back.addDocInfo(self.local.gidPdfFile)

            # To avoid confusion with file names, if this is a saved file,
            # and it has a background, we need to remove the original, non-
            # background file (remembering originals are kept in the group
            # Component folder), then rename the -view version to whatever
            # the saved name should be
            if save or override :
                if os.path.isfile(saveFile) and os.path.isfile(viewFile) :
                    # First remove
                    os.remove(saveFile)
                    # Next rename
                    os.rename(viewFile, saveFile)

            ##### Viewing #####
            # First get the right file name to view
            if saveFile :
                # If there was a saveFile, that will be the viewFile
                viewFile = saveFile
                self.log.writeToLog(self.errorCodes['5020'], [saveFile])
            else :
                # The view file in this case is just temporary
                if not os.path.isfile(viewFile) :
                    viewFile = self.local.gidPdfFile.replace(gid + '.pdf', gid + '-view.pdf')
                    shutil.copy(self.local.gidPdfFile, viewFile)
                    self.log.writeToLog(self.errorCodes['5020'], [self.tools.fName(viewFile)])

            if os.path.isfile(viewFile) :
                if not len(self.pdfViewerCmd[0]) == 0 :
                    # Add the file to the viewer command
                    self.pdfViewerCmd.append(viewFile)
                    # Run the XeTeX and collect the return code for analysis
                    try :
                        subprocess.Popen(self.pdfViewerCmd)
                        return True
                    except Exception as e :
                        # If we don't succeed, we should probably quite here
                        self.log.writeToLog(self.errorCodes['5010'], [str(e)])
                else :
                    self.log.writeToLog(self.errorCodes['5210'])
            else :
                self.log.writeToLog(self.errorCodes['5200'], [self.tools.fName(viewFile)])
                
            # If we made it this far, return True
            return True



