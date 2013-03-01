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

import os, re


# Load the local classes
from rapuma.core.tools import *
from rapuma.project.manager import Manager
from rapuma.core.proj_config import ConfigTools


###############################################################################
################################## Begin Class ################################
###############################################################################

class Hyphenation (Manager) :

#    _hyphens_re = re.compile(u'\u002D|\u00AD|\u2010') # Don't include U+2011 so we don't break on it.

    # Shared values
    xmlConfFile     = 'hyphenation.xml'


###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def __init__(self, project, cfg, cType) :
        '''Initialize the Hyphenation manager.'''

        super(Hyphenation, self).__init__(project, cfg)

        # Set values for this manager
        self.cfg                        = cfg
        self.cType                      = cType
        self.Ctype                      = cType.capitalize()
        self.project                    = project
        self.manager                    = self.cType + '_Hyphenation'
        self.managers                   = project.managers
        self.configTools                = ConfigTools(project)
        # Necessary config objects
        self.projConfig                 = project.projConfig
        if self.cType + '_Layout' not in self.managers :
            self.project.createManager(self.cType, 'layout')
        self.layoutConfig               = self.managers[self.cType + '_Layout'].layoutConfig
        # File Names
#        self.prefixSuffixHyphFileName   = self.cType + '_' + self.projConfig['Managers']['usfm_Hyphenation']['prefixSuffixHyphFileName']
        compHyphenValue                 = self.layoutConfig['Hyphenation']['compHyphenFile']
        self.compHyphenFileName         = self.configTools.processLinePlaceholders(compHyphenValue, compHyphenValue)
        # Paths
        self.projHyphenationFolder      = project.local.projHyphenationFolder
#        self.prefixSuffixHyphFile       = os.path.join(self.projHyphenationFolder, self.prefixSuffixHyphFileName)
        self.sourcePath                 = getattr(project, cType + '_sourcePath')
        self.compHyphenFile             = os.path.join(self.projHyphenationFolder, self.compHyphenFileName)
        # Misc Settings
        self.sourceEditor               = self.projConfig['CompTypes'][self.Ctype]['sourceEditor']
        # Data containers for this module
        self.nonProcessWords            = set()
        self.processWords               = set()
        self.fullList                   = set()
        self.finalList                  = list()

###############################################################################
############################ Manager Level Functions ##########################
###############################################################################


    def turnOnHyphenation (self) :
        '''Turn on hyphenation to a project for a specified component type.'''

        # Make sure we turn it on if it isn't already
        if not str2bool(self.projConfig['Managers'][self.cType + '_Hyphenation']['useHyphenation']) :
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
        if str2bool(self.projConfig['Managers'][self.cType + '_Hyphenation']['useHyphenation']) :
            self.projConfig['Managers'][self.cType + '_Hyphenation']['useHyphenation'] = False
            writeConfFile(self.projConfig)
            self.project.log.writeToLog('HYPH-060', [self.cType])
        else :
            self.project.log.writeToLog('HYPH-065', [self.cType])


    def updateHyphenation (self, force = False) :
        '''Update critical hyphenation control files for a specified component type.'''

        # Clean out the previous version of the component hyphenation file
        if os.path.isfile(self.compHyphenFile) :
            os.remove(self.compHyphenFile)
        # Create a new version
        self.harvestSource(force)
        self.makeHyphenatedWords()
        # Quick sanity test
        if not os.path.isfile(self.compHyphenFile) :
            dieNow('Failed to create: ' + self.compHyphenFile)
        self.project.log.writeToLog('HYPH-070', [self.cType])


    def harvestSource (self, force = None) :
        '''Harvest from a source hyphenation word list all the properly formated words
        and put them into their proper hyphenation category for further processing. This
        will populate two lists that will be used for further processing. They are
        self.nonProcessWords, and self.processWords.'''

        # Break our source down into the following sets:
        # allWords       All words from the master hyphen list
        # hyphenWords    Words spelled with hyphens (can be broken)
        # softHyphWords  Words with inserted soft hyphens (for line breaking)
        # exceptionWords Exception words (not to be acted on)
        # processWords   Words that (may) need hyphens inserted

        # Process according to sourceEditor (PT is all we can support right now)
        if self.sourceEditor == 'paratext' :
            from rapuma.component.usfm import PT_HyphenTools
            pt_hyTools = PT_HyphenTools(self.project)
            pt_hyTools.processHyphens(force)
            # Report the word harvest to the log
            rpt = pt_hyTools.wordTotals()
            for c in rpt :
                self.project.log.writeToLog('HYPH-040', [c[0], c[1]])
            # Change to gneric hyphens
            pt_hyTools.pt2GenHyphens(pt_hyTools.hyphenWords)
            pt_hyTools.pt2GenHyphens(pt_hyTools.softHyphenWords)
            pt_hyTools.pt2GenHyphens(self.managers[self.cType + '_Hyphenation'].hardenExceptWords(pt_hyTools.exceptionWords))

        else :
            dieNow('Error: Editor not supported: ' + self.sourceEditor)

        # Pull together all the words that do not need to be processed but
        # will be added back in when the process portion is done.
#        self.nonProcessWords = pt_hyTools.hyphenWords.union(pt_hyTools.exceptionWords).union(pt_hyTools.softHyphenWords)
        self.nonProcessWords.update(pt_hyTools.exceptionWords)
        self.nonProcessWords.update(pt_hyTools.hyphenWords)
        self.nonProcessWords.update(pt_hyTools.softHyphenWords)
        # For clarity we will declare the set for process words
        self.processWords = pt_hyTools.processWords


    def doProcessWords (self) :
        '''If there is a regex for word processing, run all the words in
        the processWords set through the regex.'''

        pwRegex = self.projConfig['Managers'][self.cType + '_Hyphenation']['hyphWordProcessRegEx']
        if pwRegex :
            for word in list(self.processWords) :
                nw = re.sub(pwRegex[0], pwRegex[1], word)
                if nw != word :
                    self.processWords.add(nw)
                    self.processWords.remove(word)

#            for w in self.processWords :
#                print w
#                
#            dieNow()




    def makeHyphenatedWords (self) :
        '''Create a file that contains sorted list of hyphenated words
        for the current component type.'''

#        import pdb; pdb.set_trace()

        # See if there is any thing to be done with the processWords set
        self.doProcessWords()
        # Merge the nonProcess words with the processWords
        self.fullList = self.nonProcessWords.union(self.processWords)
        # Turn set into list
        self.finalList = list(self.fullList)
        # Sort the list
        self.finalList.sort()
        # Output to the project storage file for other processes
        with codecs.open(self.compHyphenFile, "w", encoding='utf_8') as compHyphObject :
            compHyphObject.write('# ' + fName(self.compHyphenFile) + '\n')
            compHyphObject.write('# This is an auto-generated file which contains hyphenation words for the ' + self.cType + ' component.\n')
            for word in self.finalList :
                compHyphObject.write(word + '\n')


    def hardenExceptWords (self, words) :
        '''Harden a list of hyphated words by changing soft hyphens
        for non-breaking hyphens.'''

        for w in list(words) :
            nw = re.sub(u'\u002D', u'\u2011', w)
            if w != nw :
                words.add(nw)
                words.remove(w)

        return words


#    def makePrefixSuffixHyphFile (self) :
#        '''Create a file that will (or might) contain prefixes and suffixes.'''

#        if not os.path.isfile(self.prefixSuffixHyphFile) :
#            with codecs.open(self.prefixSuffixHyphFile, "w", encoding='utf_8') as psHyphObject :
#                psHyphObject.write('# ' + fName(self.prefixSuffixHyphFile) + '\n')
#                psHyphObject.write('# This file may contain prefixes and/or suffixes that are used with project root words.\n')
#                psHyphObject.write('# Each one must be listed on a separate line. Prefixes must have a hyphen character\n')
#                psHyphObject.write('# after it like this: "pre-". Suffixes need to have the same character following it\n')
#                psHyphObject.write('# like this: "-suf". Data in any other form will be ignored.\n\n')


#    def getPrefixSufixLists (self) :
#        '''Call the proper function to create prefix and suffix lists if the file exsists and
#        there is data in it.'''

#        if os.path.isfile(self.prefixSuffixHyphFile) :
#            with codecs.open(self.prefixSuffixHyphFile, "r", encoding='utf_8') as psWords :
#                for line in psWords :
#                    # Using the logic that there can only be one word in a line
#                    # if the line contains more than one word it is not wanted
#                    ps = line.split()
#                    if len(ps) == 1 :
#                        # Look for suffixes
#                        if ps[0][:1] == '-' :
##                            self.suffixes.append(ps[0][1:])
#                            self.suffixes.append(ps[0])
#                        # Look for prefixes
#                        elif ps[0][-1:] == '-' :
##                            self.prefixes.append(ps[0][:-1])
#                            self.prefixes.append(ps[0])



