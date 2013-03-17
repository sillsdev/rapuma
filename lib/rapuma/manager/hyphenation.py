#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle generic project hyphenation tasks.

# History:
# 20111207 - djd - Started with intial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, re, shutil, subprocess


# Load the local classes
from rapuma.core.tools import *
from rapuma.project.manager import Manager
from rapuma.core.proj_config import ConfigTools


###############################################################################
################################## Begin Class ################################
###############################################################################

class Hyphenation (Manager) :

    # Shared values
    xmlConfFile     = 'hyphenation.xml'


    def __init__(self, project, cfg, cType) :
        '''Initialize the Hyphenation manager.'''

        super(Hyphenation, self).__init__(project, cfg)

        # Set values for this manager
        self.cfg                    = cfg
        self.cType                  = cType
        self.Ctype                  = cType.capitalize()
        self.project                = project
        self.local                  = project.local
        self.manager                = self.cType + '_Hyphenation'
        self.managers               = project.managers
        self.configTools            = ConfigTools(project)
        # Necessary config objects
        self.projConfig             = project.projConfig
        if self.cType + '_Layout' not in self.managers :
            self.project.createManager(self.cType, 'layout')
        self.layoutConfig           = self.managers[self.cType + '_Layout'].layoutConfig
        # File Names
        self.hyphExcepTexFileName   = self.cType + '_hyphenation.tex'
        self.preProcessFileName     = self.projConfig['Managers']['usfm_Hyphenation']['sourcePreProcessScriptName']
        self.ptHyphFileName         = self.projConfig['Managers']['usfm_Hyphenation']['ptHyphenFileName']
        lccodeValue                 = self.layoutConfig['Hyphenation']['lccodeFile']
        self.lccodeTexFileName      = self.configTools.processLinePlaceholders(lccodeValue, lccodeValue)
        compHyphValue               = self.layoutConfig['Hyphenation']['compHyphenFile']
        self.compHyphFileName       = self.configTools.processLinePlaceholders(compHyphValue, compHyphValue)
        # Folder Paths
        self.projScriptsFolder      = project.local.projScriptsFolder
        self.projHyphenationFolder  = project.local.projHyphenationFolder
        self.rapumaScriptsFolder    = project.local.rapumaScriptsFolder
        # Set file names with full path 
        self.lccodeTexFile          = os.path.join(self.projHyphenationFolder, self.lccodeTexFileName)
        self.preProcessFile         = os.path.join(self.projScriptsFolder, self.cType + '_' + self.preProcessFileName)
        self.rapumaPreProcessFile   = os.path.join(self.rapumaScriptsFolder, self.preProcessFileName)
        self.compHyphFile           = os.path.join(self.projHyphenationFolder, self.compHyphFileName)
        self.ptHyphFile             = os.path.join(self.projHyphenationFolder, self.ptHyphFileName)
        self.ptHyphBakFile          = os.path.join(self.projHyphenationFolder, self.ptHyphFileName + '.bak')
        # Misc Settings
        self.sourceEditor           = self.projConfig['CompTypes'][self.Ctype]['sourceEditor']
        self.useHyphenation         = str2bool(self.projConfig['Managers'][self.cType + '_Hyphenation']['useHyphenation'])
        self.useSourcePreprocess    = str2bool(self.projConfig['Managers']['usfm_Hyphenation']['useHyphenSourcePreprocess'])
        # Data containers for this module
        self.allHyphenWords         = set()

###############################################################################
############################ Manager Level Functions ##########################
###############################################################################

    def preprocessSource (self) :
        '''Run a hyphenation preprocess script on the project's source hyphenation
        file. This happens when the component type import processes are happening.'''

        if str2bool(self.useSourcePreprocess) :
            if not os.path.isfile(self.preProcessFile) :
                shutil.copy(self.rapumaPreProcessFile, self.preProcessFile)
                makeExecutable(self.preProcessFile)
                self.project.log.writeToLog('HYPH-080')
                dieNow()
            else :
                err = subprocess.call([self.preProcessFile, self.ptHyphFile])
                if err == 0 :
                    self.project.log.writeToLog('HYPH-090')
                    return True
                else :
                    self.project.log.writeToLog('HYPH-095')
                    return False


    def compareWithSource (self) :
        '''Compare working hyphenation file with the original copied read-only
        source file found in the project. This will help to konw what preprocess
        changes were made (if changes where made) when it was imported into the
        project. '''

        self.project.compare(self.ptHyphFile, self.ptHyphBakFile)


    def turnOnHyphenation (self) :
        '''Turn on hyphenation to a project for a specified component type.'''

        # Make sure we turn it on if it isn't already
        if not self.useHyphenation :
            self.projConfig['Managers'][self.cType + '_Hyphenation']['useHyphenation'] = True
            writeConfFile(self.projConfig)
            self.project.log.writeToLog('HYPH-050', [self.cType])
        else :
            self.project.log.writeToLog('HYPH-055', [self.cType])


    def turnOffHyphenation (self) :
        '''Turn off hyphenation from a project for a specified component type.
        No removal of files will occure, only the useHyphenation will be set 
        to false.'''

        # Make sure we turn it on if it isn't already
        if self.useHyphenation :
            self.projConfig['Managers'][self.cType + '_Hyphenation']['useHyphenation'] = False
            writeConfFile(self.projConfig)
            self.project.log.writeToLog('HYPH-060', [self.cType])
        else :
            self.project.log.writeToLog('HYPH-065', [self.cType])


    def updateHyphenation (self, force = False) :
        '''Update critical hyphenation control files for a specified component type.'''

        # Clean out the previous version of the component hyphenation file
        if os.path.isfile(self.compHyphFile) :
            os.remove(self.compHyphFile)
        # Run a hyphenation source preprocess if specified
        if self.useSourcePreprocess :
            self.preprocessSource()
        # Create a new version
        self.harvestSource(force)
        self.makeHyphenatedWords()
        # Quick sanity test
        if not os.path.isfile(self.compHyphFile) :
            dieNow('Failed to create: ' + self.compHyphFile)
        self.project.log.writeToLog('HYPH-070', [self.cType])


    def harvestSource (self, force = None) :
        '''Call on the component type to harvest sets of hyphenation words
        from its source list. These will be combined to form the master set.'''

#        import pdb; pdb.set_trace()

        # Break our source down into the following sets:
        # allWords          All words from the master hyphen list
        # approvedWords     Words of any kind that the user has explicitly approved
        # hyphenWords       Words spelled with hyphens (can be broken)
        # softHyphWords     Words with inserted soft hyphens (for line breaking)
        # nonHyphenWords    Exception words (not to be acted on but included in list)

        # Process according to sourceEditor (PT is all we can support right now)
        if self.sourceEditor == 'paratext' :
            from rapuma.group.usfm import PT_HyphenTools
            pt_hyTools = PT_HyphenTools(self.project)
            pt_hyTools.processHyphens(force)
            # Report the word harvest to the log
            rpt = pt_hyTools.wordTotals()
            for c in rpt :
                self.project.log.writeToLog('HYPH-040', [c[0], c[1]])
            # Change to gneric hyphens
            pt_hyTools.pt2GenHyphens(pt_hyTools.approvedWords)
            pt_hyTools.pt2GenHyphens(pt_hyTools.hyphenWords)
            pt_hyTools.pt2GenHyphens(pt_hyTools.softHyphenWords)
        else :
            dieNow('Error: Editor not supported: ' + self.sourceEditor)

        # Pull together all the words that will be in our final list.
        self.allHyphenWords.update(pt_hyTools.approvedWords)
        self.allHyphenWords.update(pt_hyTools.hyphenWords)
        self.allHyphenWords.update(pt_hyTools.softHyphenWords)
        # Add nonHyphenWords because they are exceptions
        self.allHyphenWords.update(pt_hyTools.nonHyphenWords)


    def makeHyphenatedWords (self) :
        '''Create a file that contains sorted list of hyphenated words
        for the current component type.'''

#        import pdb; pdb.set_trace()

        description = 'This file contains a sorted list of hyphenated words \
            for a single component type.'

        # Turn set into list
        self.finalList = list(self.allHyphenWords)
        # Sort the list
        self.finalList.sort()
        # Output to the project storage file for other processes
        with codecs.open(self.compHyphFile, "w", encoding='utf_8') as compHyphObject :
            compHyphObject.write(makeFileHeader(fName(self.compHyphFile), description))
            for word in self.finalList :
                compHyphObject.write(word + '\n')




