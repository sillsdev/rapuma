
#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle map groups in book projects.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, codecs, re, subprocess, tempfile
from configobj                      import ConfigObj, Section
from functools                      import partial

# Load the local classes
from rapuma.core.tools              import Tools, ToolsPath, ToolsGroup
from rapuma.core.proj_config        import ProjConfig
from rapuma.core.user_config        import UserConfig
from rapuma.core.proj_local         import ProjLocal
from rapuma.core.proj_log           import ProjLog
from rapuma.core.paratext           import Paratext
from rapuma.project.project         import Project


###############################################################################
################################## Begin Class ################################
###############################################################################

class ProjToc (object) :

    def __init__(self, pid, gid) :
        '''Do the primary initialization for this class.'''

        self.pid                        = pid
        self.gid                        = gid
        self.tools                      = Tools()
        self.user                       = UserConfig()
        self.userConfig                 = self.user.userConfig
        self.projHome                   = self.userConfig['Projects'][self.pid]['projectPath']
        self.projectMediaIDCode         = self.userConfig['Projects'][self.pid]['projectMediaIDCode']
        self.local                      = ProjLocal(self.pid)
        self.projConfig                 = ProjConfig(self.local).projConfig
        self.log                        = ProjLog(self.pid)
        self.tools_path                 = ToolsPath(self.local, self.projConfig, self.userConfig)
        self.tools_group                = ToolsGroup(self.local, self.projConfig, self.userConfig)
        self.tocData                    = {}
        self.columns                    = str(0)
        # File names
        self.tocWorkFileName            = self.pid + '.toc'
        # Folder paths
        self.projComponentsFolder       = self.local.projComponentsFolder
        self.gidFolder                  = os.path.join(self.projComponentsFolder, self.gid)
        # File names with paths
        self.tocWorkFile                = os.path.join(self.gidFolder, self.tocWorkFileName)

        self.finishInit()

        # Log messages for this module
        self.errorCodes     = {

            '0050' : ['ERR', 'Map group [<<1>>] is locked, no action can be taken. Use force (-f) to override.'],

            '0210' : ['LOG', 'Created TOC working file.'],
            '0220' : ['MSG', 'Added TOC group to the project.'],
            '0225' : ['ERR', 'TOC group not found in this project.'],
            '0250' : ['LOG', 'Created TOC group folder'],
            '0260' : ['ERR', 'Only support for two or three columns, [<<1>>] columns requested.'],

            '0420' : ['MSG', 'Removed Table of Contents'],

            '0610' : ['ERR', 'No TOC data found. Process cannot proceed.'],
            '0620' : ['MSG', 'TOC working file not found. Replacement has been recreated.'],
            '0630' : ['MSG', 'Updated TOC working file.'],
            '0640' : ['MSG', 'Table of Contents has been updated.'],
            '0660' : ['WRN', 'Auto-generated TOC information file could not be found. Please check your TOC settings.'],

            '0840' : ['MSG', 'Rendered the project table of contents.'],

        }

    def finishInit (self) :
        '''If this is a new project we need to handle these settings special.'''
        if self.projConfig['Groups'].has_key(self.gid) :
            self.columns                = str(self.projConfig['Groups'][self.gid]['columns'])


###############################################################################
################################ Add Functions ################################
###############################################################################
######################## Error Code Block Series = 0200 #######################
###############################################################################


    def addGroup (self, force = False) :
        '''Add maps to the project.'''

#        import pdb; pdb.set_trace()

        # First be sure the component type exists in the conf
        self.projConfig = self.tools.addComponentType(self.projConfig, self.local, 'toc')

        # Having made it this far we can output information to the project config
        self.createTocFolder()
        self.createTocStyleFile(force)
        self.tools.buildConfSection(self.projConfig, 'Groups')
        self.projConfig['Groups'][self.gid] = {}
        self.projConfig['Groups'][self.gid]['startPageNumber'] = 0
        self.projConfig['Groups'][self.gid]['cType'] = 'toc'
        self.projConfig['Groups'][self.gid]['isLocked'] = True
        self.projConfig['Groups'][self.gid]['bindingOrder'] = 2
        self.projConfig['Groups'][self.gid]['mainTitle'] = 'Table of Contents'
        self.projConfig['Groups'][self.gid]['hdrName'] = 'Book Name'
        self.projConfig['Groups'][self.gid]['hdrAbbr'] = 'Abbreviation'
        self.projConfig['Groups'][self.gid]['hdrPgNum'] = 'Page Number'
        self.projConfig['Groups'][self.gid]['columns'] = 2
        self.tools.writeConfFile(self.projConfig)

        # With the group installed we can finish the initialization
        self.finishInit()

        # Make a container file for the images
        self.createTocWorkingFile(force)

        # Add/update with any available TOC info
        self.updateToc(force)

        self.log.writeToLog(self.errorCodes['0220'], [self.gid])
        return True


    def createTocWorkingFile (self, force) :
        '''Create the TOC working file that will be rendered into
        the final form.'''

        if force :
            if os.path.exists(self.tocWorkFile) :
                os.remove(self.tocWorkFile)

        if self.projConfig['Groups'].has_key(self.gid) :
            if not os.path.exists(self.tocWorkFile) or force :
                mainTitle = self.projConfig['Groups'][self.gid]['mainTitle']
                hdrName = self.projConfig['Groups'][self.gid]['hdrName']
                hdrAbbr = self.projConfig['Groups'][self.gid]['hdrAbbr']
                hdrPgNum = self.projConfig['Groups'][self.gid]['hdrPgNum']
                with codecs.open(self.tocWorkFile, "w", encoding="utf_8_sig") as contents :
                    contents.write('\\id TOC - Rapuma TOC working file, edit as needed.\n')
                    contents.write('\\rem Generated on: ' + self.tools.tStamp() + '\n')
                    contents.write('\\rem This file contains both USFM and TeX markup.\n\n')
                    contents.write('\\mt1 ' + mainTitle + '\n')
                    contents.write('\\p \n')
                    contents.write('\\makedigitsother\\catcode`{=1 \\catcode`}=2 \n')
                    contents.write('\\baselineskip=12pt \n')
                    # Output header by number of columns requested
                    if self.columns == '2' :
                        contents.write('\\tbltwowlheader{' + hdrName + '}{' + hdrPgNum + '}\n')
                    elif self.columns == '3' :
                        contents.write('\\tblthreewlheader{' + hdrName + '}{' + hdrAbbr + '}{' + hdrPgNum + '}\n')
                    else :
                        self.log.writeToLog(self.errorCodes['0260'], [self.columns], 'proj_toc.createTocWorkingFile()')

                self.log.writeToLog(self.errorCodes['0210'], [self.gid])
                return True
        else :
            self.log.writeToLog(self.errorCodes['0225'], [self.gid])


    def createTocFolder (self) :
        '''Create a project TOC folder if one is not there.'''

        folder = os.path.join(self.projComponentsFolder, self.gid)
        if not os.path.exists(folder) :
            os.makedirs(folder)
            self.log.writeToLog(self.errorCodes['0250'], [self.gid])


    def createTocStyleFile (self, force) :
        '''Create the TOC style file.'''

#        styFileName     = 'usfm-grp-ext.sty'
#        styFile         = os.path.join(self.projComponentsFolder, self.gid, styFileName)

#        # Lets start with just a simple file and go from there
#        # This should go in before any other auto-generated sty
#        # file so we should be good to go
#        if not os.path.exists(styFile) or force :
#            contents = codecs.open(styFile, "w", encoding="utf_8_sig")
#            contents.write('# Auto-generated style file for map rendering. Edit as needed.\n')
#            contents.write('# ' + styFileName + ' Generated on: ' + self.tools.tStamp() + '\n\n')
#            contents.write('\\Marker v\n')
#            contents.write('\\FontSize 0.2\n\n')
#            contents.write('\\Marker mt1\n')
#            contents.write('\\FontSize 14\n')
#            contents.write('\\SpaceAfter 0\n')
#            contents.write('\\SpaceBefore 0\n\n')
#            contents.write('\\Marker p\n')
#            contents.write('\\FontSize 0.2\n\n')
#            contents.close()

        return True

###############################################################################
############################## Remove Functions ###############################
###############################################################################
######################## Error Code Block Series = 0400 #######################
###############################################################################

    def removeGroup (self, force = False) :
        '''Remove the maps from a project.'''

        return True


###############################################################################
############################## Update Functions ###############################
###############################################################################
######################## Error Code Block Series = 0600 #######################
###############################################################################

    def updateToc (self, force = False) :
        '''Update or add TOC information from group TOC info files
        to the TOC working file. This should not add identical/repeated
        information and will try to append information to the end of 
        the file.'''

        # Do not bother if no TOC data exists
        if self.collectTocData() :
            if os.path.exists(self.tocWorkFile) :
                # Do a quick check for data the dict was empty when we started
                if len(self.tocData) > 0 :
                    with open(self.tocWorkFile, "a") as contents :
                        for (idx, item) in enumerate(self.tocData['bindGroup0']['lines'].keys()) :
                            thisLine = self.tocData['bindGroup0']['lines']['line{}'.format(idx+1)]
                            if self.columns == '2' :
                                contents.write('\\tbltwowlrow{' + thisLine['toc1'] + '}{' + thisLine['pgn'] + '}\n')
                            elif self.columns == '3' :
                                contents.write('\\tblthreewlrow{' + thisLine['toc1'] + '}{' + thisLine['toc2'] + '}{' + thisLine['pgn'] + '}\n')
                            else :
                                self.log.writeToLog(self.errorCodes['0260'], [self.columns], 'proj_toc.updateToc()')

                self.log.writeToLog(self.errorCodes['0630'])
                return True
            else :
                self.createTocWorkingFile(force)
                self.log.writeToLog(self.errorCodes['0620'])
        else :
            self.log.writeToLog(self.errorCodes['0610'])


    def collectTocData (self) :
        '''Go through the groups and collect any TOC information that
        exsists and return it in a dictionary.'''

        for gid in self.projConfig['Groups'].keys() :
            if self.projConfig['Groups'][gid].has_key('tocInclude') :
                if self.tools.str2bool(self.projConfig['Groups'][gid]['tocInclude']) :
                    bg = 'bindGroup{}'.format(self.projConfig['Groups'][gid]['bindingOrder'])
                    self.tocData[bg] = {}
                    self.tocData[bg]['title'] = self.projConfig['Groups'][gid]['tocSectionTitle']
                    self.tocData[bg] = {'lines' : self.getTocData(gid)}
                    return True


    def getTocData (self, gid) :
        '''Return a list of TOC lines from this group TOC file.'''

        tocFile = os.path.join(self.projComponentsFolder, gid, 'toc.usfm')
        
        if os.path.exists(tocFile) :
            contents = codecs.open(tocFile, "rt", encoding="utf_8_sig").read()
            rtnDict = {}
            lc = 0
            for line in contents.split('\n') :
                if line[:3] == '\\tr' :
                    lc +=1
                    ln = 'line{}'.format(lc)
                    rtnDict[ln] = {}
                    rtn = ''
                    rtn = re.sub(ur'\\tr\s', ur'', line)
                    rtn = re.sub(ur'\\t[rc0-9]+\s', ur'<>', rtn)
                    rtn = re.sub(ur'^<>', ur'', rtn)
                    rtn = rtn.split('<>')
                    # Loop through the list but don't take the last item
                    for (idx, item) in enumerate(rtn[:-1]) : 
                        rtnDict[ln]['toc{}'.format(idx+1)] = item
                    # Add page number (last item) here
                    rtnDict[ln]['pgn'] = rtn[-1]
            return rtnDict
        else :
            self.log.writeToLog(self.errorCodes['0660'])


    def appendToTOCWorkingFile (self) :
        '''Append TOC source to the TOC working file.'''

        return True


###############################################################################
############################## Render Functions ###############################
###############################################################################
######################## Error Code Block Series = 0800 #######################
###############################################################################

    def renderToc (self, mode, force = False) :
        '''Render the table of contents.'''

        # Probably should do a little preprocessing here

        # TeX rendering
        Project(self.pid, self.gid).renderGroup(mode, '', True)


        self.log.writeToLog(self.errorCodes['0840'])




