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
        # Necessary config objects
        self.projConfig                 = project.projConfig
        if self.cType + '_Layout' not in self.managers :
            self.project.createManager(self.cType, 'layout')
        self.layoutConfig               = self.managers[self.cType + '_Layout'].layoutConfig
        # File Names
        self.prefixSuffixHyphFileName   = self.cType + '_' + self.projConfig['Managers']['usfm_Hyphenation']['prefixSuffixHyphFileName']
        # Paths
        self.projHyphenationFolder      = project.local.projHyphenationFolder
        self.prefixSuffixHyphFile       = os.path.join(self.projHyphenationFolder, self.prefixSuffixHyphFileName)
        self.sourcePath                 = getattr(project, cType + '_sourcePath')
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

    def turnOnHyphenation (self, cType) :
        '''Turn on hyphenation for a specified component type.'''

        self.projConfig['Managers'][cType + '_Hyphenation']['useHyphenation'] = True
        writeConfFile(self.projConfig)
        self.project.log.writeToLog('HYPH-050', [cType])


    def turnOffHyphenation (self, cType) :
        '''Turn off hyphenation for a specified component type.'''

        self.projConfig['Managers'][cType + '_Hyphenation']['useHyphenation'] = False
        writeConfFile(self.projConfig)
        self.project.log.writeToLog('HYPH-055', [cType])


    def addHyphenation (self, cType) :
        '''Add hyphenation to a project for a specified component type.'''

        # Make sure we turn it on if it isn't already
        if not str2bool(self.projConfig['Managers'][cType + '_Hyphenation']['useHyphenation']) :
            self.turnOnHyphenation(cType)


    def removeHyphenation (self, cType) :
        '''Remove hyphenation from a project for a specified component type.'''

        # Make sure we turn it on if it isn't already
        if str2bool(self.projConfig['Managers'][cType + '_Hyphenation']['useHyphenation']) :
            self.turnOffHyphenation(cType)


    def updateHyphenation (self, cType) :
        '''Update critical hyphenation control files for a specified component type.'''

        self.harvestSource()
        self.makeHyphenatedWords()


    def harvestSource (self) :
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
            pt_hyTools.processHyphens()
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
        self.nonProcessWords = pt_hyTools.hyphenWords.union(pt_hyTools.exceptionWords).union(pt_hyTools.softHyphenWords)
        # For clarity we will declare the set for process words
        self.processWords = pt_hyTools.processWords


    def makeHyphenatedWords (self) :
        '''Return a sorted list of hyphenated words.'''

#        import pdb; pdb.set_trace()

        # Once words that have been pre-hyphenated and exception words have been
        # pulled out we can move on to working on the processWords, if that is
        # desired. This word set can have three primary components to a word. 
        # When processed for use in a TeX word hyphenation exceptions list, using
        # \hyphenation{}, it can look like this: abc-root-word-xyz
        #
        # Whereas "abc" is the prefix, "root-word" is the main part of the word
        # which can be divided by syllables and "xyz" is the suffix. Prefix and
        # suffix processing is triggered by the presence of the "prefixSuffixHyphens.txt"
        # file in the project Hyphenation folder. If that file is there and it contains
        # any prefix or suffix definitions, they will be loaded up and words will
        # be checked for them. That file is made by default here with this function:
        self.makePrefixSuffixHyphFile()
        # The prefixes and suffixes are pulled in with this function:
        self.getPrefixSufixLists()
        # This will create two sets of data: hy_tools.prefixList and hy_tools.suffixList
        # If either or both have data in them they will be used for building the main
        # process word dictionary data set.



        # -----------
        #
        # FIXME: At this point we will want to factor in prefixes, suffixes
        # and exceptions it might look like this:
        # 1) Look for prefix/suffix file, if found, load it up, set trigger
        
        #   1a Look for prefixes
        
        #   1b Look for suffixes
        
        # 2) Check to see if word processing is desired, use a regex to trigger
        # 3) Loop through the processWords, pull the prefix and/or suffix off (store)
        # 4) Process the root word with the syllable breaker regex, insert generic markers
        # 5) Reattach prefix and/or suffix with generic markers
        # 
        # -----------


#        dieNow()



        # Merge the nonProcess words with the processWords
        self.fullList = self.nonProcessWords.union(self.processWords)
        # Turn generic hyphen markers into markers that will work with XeTeX
        self.gen2TexHyphens(self.fullList)
        # Turn set into list
        self.finalList = list(self.fullList)
        # Sort the list
        self.finalList.sort()


    def gen2TexHyphens (self, wordList) :
        '''Change generic hyphen markers to plain 002D hyphen characters.'''

        for word in list(wordList) :
            nw = re.sub(u'<->', u'-', word)
            if nw != word :
                wordList.add(nw)
                wordList.remove(word)


    def hardenExceptWords (self, words) :
        '''Harden a list of hyphated words by changing soft hyphens
        for non-breaking hyphens.'''

        for w in list(words) :
            nw = re.sub(u'\u002D', u'\u2011', w)
            if w != nw :
                words.add(nw)
            words.remove(w)

        return words


    def makePrefixSuffixHyphFile (self) :
        '''Create a file that will (or might) contain prefixes and suffixes.'''

        print self.prefixSuffixHyphFile

        if not os.path.isfile(self.prefixSuffixHyphFile) :
            with codecs.open(self.prefixSuffixHyphFile, "w", encoding='utf_8') as psHyphObject :
                psHyphObject.write('# ' + fName(self.prefixSuffixHyphFile) + '\n')
                psHyphObject.write('# This file may contain prefixes and/or suffixes that are used with project root words.\n')
                psHyphObject.write('# Each one must be listed on a separate line. Prefixes must have a hyphen character\n')
                psHyphObject.write('# after it like this: "pre-". Suffixes need to have the same character following it\n')
                psHyphObject.write('# like this: "-suf". Data in any other form will be ignored.\n\n')


    def getPrefixSufixLists (self) :
        '''Call the proper function to create prefix and suffix lists if the file exsists and
        there is data in it.'''

        pass




