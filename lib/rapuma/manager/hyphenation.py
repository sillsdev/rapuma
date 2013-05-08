#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle generic project hyphenation tasks.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, re, shutil, subprocess, codecs


# Load the local classes
from rapuma.core.tools          import Tools
from rapuma.project.manager     import Manager
from rapuma.core.proj_config    import ConfigTools
from rapuma.core.proj_compare   import Compare
from rapuma.core.paratext       import Paratext


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
        self.tools                  = Tools()
        self.cfg                    = cfg
        self.cType                  = cType
        self.Ctype                  = cType.capitalize()
        self.gid                    = project.gid
        self.project                = project
        self.local                  = project.local
        self.manager                = self.cType + '_Hyphenation'
        self.managers               = project.managers
        self.configTools            = ConfigTools(project)
        self.paratext               = Paratext(project.projectIDCode, self.gid)
        # Necessary config objects
        self.projConfig             = project.projConfig
        if self.cType + '_Layout' not in self.managers :
            self.project.createManager('layout')
        self.layoutConfig           = self.managers[self.cType + '_Layout'].layoutConfig
        self.csid                   = project.projConfig['Groups'][self.gid]['csid']
        # File Names
        self.preProcessFileName     = self.cType + '_' + self.projConfig['Managers']['usfm_Hyphenation']['sourcePreProcessScriptName']
        self.ptHyphFileName         = self.projConfig['Managers']['usfm_Hyphenation']['ptHyphenFileName']
        lccodeValue                 = self.layoutConfig['Hyphenation']['lccodeFile']
        self.lccodeTexFileName      = self.configTools.processLinePlaceholders(lccodeValue, lccodeValue)
        compHyphValue               = self.layoutConfig['Hyphenation']['compHyphenFile']
        self.compHyphFileName       = self.configTools.processLinePlaceholders(compHyphValue, compHyphValue)
        grpHyphExcValue             = self.layoutConfig['Hyphenation']['grpHyphenExceptionsFile']
        self.grpHyphExcTexFileName  = self.configTools.processLinePlaceholders(grpHyphExcValue, grpHyphExcValue)
        # Folder Paths
        self.projScriptsFolder      = project.local.projScriptsFolder
        self.projHyphenationFolder  = project.local.projHyphenationFolder
        self.rapumaScriptsFolder    = project.local.rapumaScriptsFolder
        self.projComponentsFolder   = project.local.projComponentsFolder
        self.gidFolder              = os.path.join(self.projComponentsFolder, self.gid)
        # Set file names with full path 
        self.lccodeTexFile          = os.path.join(self.projHyphenationFolder, self.lccodeTexFileName)
        self.compHyphFile           = os.path.join(self.projHyphenationFolder, self.compHyphFileName)
        self.grpHyphExcTexFile      = os.path.join(self.projHyphenationFolder, self.grpHyphExcTexFileName)
        self.preProcessFile         = os.path.join(self.projHyphenationFolder, self.preProcessFileName)
        self.rapumaPreProcessFile   = os.path.join(self.rapumaScriptsFolder, self.preProcessFileName)
        self.ptHyphFile             = os.path.join(self.projHyphenationFolder, self.ptHyphFileName)
        self.ptHyphBakFile          = os.path.join(self.projHyphenationFolder, self.ptHyphFileName + '.bak')
        # Misc Settings
        self.sourceEditor           = self.projConfig['CompTypes'][self.Ctype]['sourceEditor']
        self.useHyphenation         = self.tools.str2bool(self.projConfig['Groups'][self.gid]['useHyphenation'])
        self.useSourcePreprocess    = self.tools.str2bool(self.projConfig['Managers']['usfm_Hyphenation']['useHyphenSourcePreprocess'])
        # Data containers for this module
        self.allHyphenWords         = set()

        # Log messages for this module
        self.errorCodes     = {
            '0000' : ['MSG', 'Placeholder message'],
            '0240' : ['LOG', 'Hyphenation report: <<1>> = <<2>>'],
            '0250' : ['MSG', 'Turned on hyphenation for group: [<<1>>]'],
            '0255' : ['MSG', 'Hyphenation is already on for group: [<<1>>]'],
            '0260' : ['MSG', 'Turned off hyphenation for group: [<<1>>]'],
            '0265' : ['MSG', 'Hyphenation is already off for group: [<<1>>]'],
            '0270' : ['MSG', 'Updated hyphenation files for component type: [<<1>>]'],

            'HYPH-000' : ['MSG', 'Hyphenation module messages'],
            'HYPH-010' : ['ERR', 'TeX hyphenation dependent file [<<1>>] is missing! This is a required file when hyphenation is turned on.'],
            'HYPH-020' : ['ERR', 'Unable to harvest words from ParaTExt project. This is required when hyphenation is turned on.'],
            'HYPH-030' : ['ERR', 'Unable to convert hyphated words from ParaTExt to formate needed for use with TeX. This is required when hyphenation is turned on.'],
            'HYPH-080' : ['ERR', 'New default hyphen preprocess script copied into the project. Please edit before using.'],
            'HYPH-090' : ['MSG', 'Ran hyphen preprocess script on project hyphenation source file.'],
            'HYPH-095' : ['ERR', 'Preprocess script failed to run on source file.'],
            'HYPH-100' : ['ERR', 'Failed to run preprocess script on project hyphenation source file.'],
        }

###############################################################################
############################ Manager Level Functions ##########################
###############################################################################

    def compareWithSource (self) :
        '''Compare working hyphenation file with the original copied read-only
        source file found in the project. This will help to konw what preprocess
        changes were made (if changes where made) when it was imported into the
        project. '''

        # This is the only time we call a compare in the module (so far)
        Compare(self.project.projectIDCode).compare(self.ptHyphFile, self.ptHyphBakFile)


    def turnOnHyphenation (self) :
        '''Turn on hyphenation to a project for a specified component type.'''

        # Make sure we turn it on if it isn't already
        if not self.useHyphenation :
            self.projConfig['Groups'][self.gid]['useHyphenation'] = True
            self.tools.writeConfFile(self.projConfig)
            self.project.log.writeToLog(self.errorCodes['0250'], [self.gid])
        else :
            self.project.log.writeToLog(self.errorCodes['0255'], [self.gid])


    def turnOffHyphenation (self) :
        '''Turn off hyphenation from a project for a specified component type.
        No removal of files will occure, only the useHyphenation will be set 
        to false.'''

        # Make sure we turn it on if it isn't already
        if self.useHyphenation :
            self.projConfig['Groups'][self.gid]['useHyphenation'] = False
            self.tools.writeConfFile(self.projConfig)
            self.project.log.writeToLog(self.errorCodes['0260'], [self.gid])
        else :
            self.project.log.writeToLog(self.errorCodes['0265'], [self.gid])


    def updateHyphenation (self, force = False) :
        '''Update critical hyphenation control files for a specified component type.'''

        # Clean out the previous version of the component hyphenation file
        if os.path.isfile(self.compHyphFile) :
            os.remove(self.compHyphFile)
        # Run a hyphenation source preprocess if specified
        if self.useSourcePreprocess :
            self.paratext.processHyphens()


        # Create a new version
        self.harvestSource(force)
        self.makeHyphenatedWords()
        # Quick sanity test
        if not os.path.isfile(self.compHyphFile) :
            self.tools.dieNow('Failed to create: ' + self.compHyphFile)
        self.project.log.writeToLog(self.errorCodes['0270'], [self.cType])


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
            self.paratext.processHyphens(force)
            # Report the word harvest to the log
            rpt = self.paratext.wordTotals()
            for c in rpt :
                self.project.log.writeToLog(self.errorCodes['0240'], [c[0], c[1]])
            # Change to gneric hyphens
            self.paratext.pt2GenHyphens(self.paratext.approvedWords)
            self.paratext.pt2GenHyphens(self.paratext.hyphenWords)
            self.paratext.pt2GenHyphens(self.paratext.softHyphenWords)
        else :
            self.tools.dieNow('Error: Editor not supported: ' + self.sourceEditor)

        # Pull together all the words that will be in our final list.
        self.allHyphenWords.update(self.paratext.approvedWords)
        self.allHyphenWords.update(self.paratext.hyphenWords)
        self.allHyphenWords.update(self.paratext.softHyphenWords)
        # Add nonHyphenWords because they are exceptions
        self.allHyphenWords.update(self.paratext.nonHyphenWords)


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
            compHyphObject.write(self.tools.makeFileHeader(self.tools.fName(self.compHyphFile), description))
            for word in self.finalList :
                compHyphObject.write(word + '\n')




