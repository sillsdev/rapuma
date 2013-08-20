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
from rapuma.core.tools              import Tools
from rapuma.project.proj_config     import Config
from rapuma.core.proj_compare       import ProjCompare
from rapuma.core.paratext           import Paratext
from rapuma.core.user_config        import UserConfig
from rapuma.core.proj_local         import ProjLocal
from rapuma.core.proj_log           import ProjLog


###############################################################################
################################## Begin Class ################################
###############################################################################

class ProjHyphenation (object) :

    def __init__(self, pid, gid) :
        '''Do the primary initialization for this class.'''

        self.pid                        = pid
        self.gid                        = gid
        self.tools                      = Tools()
        self.local                      = ProjLocal(pid)
        self.log                        = ProjLog(pid)
        self.user                       = UserConfig()
        self.userConfig                 = self.user.userConfig
        self.proj_config                = Config(pid, gid)
        self.proj_config.getProjectConfig()
        self.proj_config.getHyphenationConfig()
        self.projectConfig              = self.proj_config.projectConfig
        self.hyphenationConfig          = self.proj_config.hyphenationConfig
        self.cType                      = self.projectConfig['Groups'][gid]['cType']
        self.Ctype                      = self.cType.capitalize()
        self.macPack                    = None
        self.macPackConfig              = None
        if self.projectConfig['CompTypes'][self.Ctype].has_key('macroPackage') and self.projectConfig['CompTypes'][self.Ctype]['macroPackage'] != '' :
            self.macPack                = self.projectConfig['CompTypes'][self.Ctype]['macroPackage']
            self.proj_config.getMacPackConfig(self.macPack)
            self.proj_config.loadMacPackFunctions(self.macPack)
            self.macPackConfig      = self.proj_config.macPackConfig
            self.macPackFunctions   = self.proj_config.macPackFunctions

        # Misc Settings
        self.sourceEditor               = self.projectConfig['CompTypes'][self.Ctype]['sourceEditor']
        self.useHyphenation             = self.tools.str2bool(self.projectConfig['Groups'][self.gid]['useHyphenation'])
        self.useSourcePreprocess        = self.tools.str2bool(self.hyphenationConfig['GeneralSettings']['useHyphenSourcePreprocess'])
        # Data containers for this module
        self.allHyphenWords             = set()
        self.allPtHyphenWords           = set()
        self.goodPtHyphenWords          = set()
        self.badWords                   = set()
        self.hyphenWords                = set()
        self.approvedWords              = set()
        self.softHyphenWords            = set()
        self.nonHyphenWords             = set()

        # Log messages for this module
        self.errorCodes     = {
            '0000' : ['MSG', 'Placeholder message'],
            '0240' : ['LOG', 'Hyphenation report: <<1>> = <<2>>'],
            '0250' : ['MSG', 'Turned on hyphenation for group: [<<1>>]'],
            '0255' : ['MSG', 'Hyphenation is already on for group: [<<1>>]'],
            '0260' : ['MSG', 'Turned off hyphenation for group: [<<1>>]'],
            '0265' : ['MSG', 'Hyphenation is already off for group: [<<1>>]'],
            '0270' : ['MSG', 'Updated hyphenation files for component type: [<<1>>]'],
            '0275' : ['ERR', 'Cannot create file: [<<1>>]'],
            '0280' : ['MSG', 'Cannot update project hyphenation files. No difference found with source. Use force (-f) to run the update process.'],

            '1410' : ['ERR', 'ParaTExt source hypenation file not found.'],
            '1430' : ['WRN', 'Problems found in hyphenation word list. They were reported in [<<1>>].  Process continued but results may not be right. - paratext.checkForBadWords()'],
            '1450' : ['LOG', 'Updated project file: [<<1>>]'],
            '1455' : ['LOG', 'Did not update project file: [<<1>>]'],
            '1460' : ['MSG', 'Force switch was set. Removed hyphenation source files for update proceedure.'],
            '1480' : ['ERR', 'New default hyphen preprocess script copied into the project. Please edit and rerun this process.'],
            '1485' : ['ERR', 'Unable to install default hyphen preprocess script. Failed with error: [<<1>>]'],
            '1490' : ['MSG', 'Ran hyphen preprocess script on project hyphenation source file.'],
            '1495' : ['ERR', 'Preprocess script failed to run on source file.'],

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
############################ Project Level Functions ##########################
###############################################################################
####################### Error Code Block Series = 0200 ########################
###############################################################################

    def manageHyphenation (self, action, force = False) :
        '''Run a hyphenation management command.'''

        if action == 'add' :
            self.turnOnHyphenation()
        elif action == 'remove' :
            self.turnOffHyphenation()
        elif action == 'update' :
            self.updateHyphenation(force)


    def compareWithSource (self) :
        '''Compare working hyphenation file with the original copied read-only
        source file found in the project. This will help to konw what preprocess
        changes were made (if changes where made) when it was imported into the
        project. '''

        # This is the only time we call a compare in the module (so far)
        ProjCompare(self.pid).compare(self.ptHyphFile, self.ptProjHyphBakFile)


    def turnOnHyphenation (self) :
        '''Turn on hyphenation to a project for a specified component type.'''

        # Make sure we turn it on if it isn't already
        if not self.useHyphenation :
            self.macPackConfig['Hyphenation']['setHyphenLanguage'] = self.projectConfig['Groups'][self.gid]['csid']
            self.macPackConfig['Hyphenation']['createHyphenLanguage'] = self.projectConfig['Groups'][self.gid]['csid']
            self.tools.writeConfFile(self.macPackConfig)
            self.projectConfig['Groups'][self.gid]['useHyphenation'] = True
            self.tools.writeConfFile(self.projectConfig)
            self.log.writeToLog(self.errorCodes['0250'], [self.gid])
        else :
            self.log.writeToLog(self.errorCodes['0255'], [self.gid])


    def turnOffHyphenation (self) :
        '''Turn off hyphenation from a project for a specified component type.
        No removal of files will occure, only the useHyphenation will be set 
        to false.'''

        # Make sure we turn it on if it isn't already
        if self.useHyphenation :
            self.projectConfig['Groups'][self.gid]['useHyphenation'] = False
            self.tools.writeConfFile(self.projectConfig)
            self.log.writeToLog(self.errorCodes['0260'], [self.gid])
        else :
            self.log.writeToLog(self.errorCodes['0265'], [self.gid])


    def updateHyphenation (self, force) :
        '''Update critical hyphenation control files for a specified component type.'''

        def update () :
            # Clean out the previous version of the component hyphenation file
            if os.path.isfile(self.compHyphFile) :
                os.remove(self.compHyphFile)
            # Run a hyphenation source preprocess if specified
            if self.useSourcePreprocess :
                self.processHyphens(force)

            # Create a new version
            self.harvestSource(force)
            self.makeHyphenatedWords()
            # Quick sanity test
            if not os.path.isfile(self.compHyphFile) :
                self.log.writeToLog(self.errorCodes['0275'], [self.tools.fName(self.compHyphFile)])
            self.log.writeToLog(self.errorCodes['0270'], [self.cType])

        if force :
            update()
        elif not os.path.exists(self.compHyphFile) :
            update()
        elif os.path.exists(self.ptProjHyphBakFile) and self.tools.isOlder(self.ptProjHyphBakFile, self.ptHyphFile) :
            update()
        else :
            self.log.writeToLog(self.errorCodes['0280'])


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
            self.processHyphens(force)
            # Report the word harvest to the log
            rpt = self.wordTotals()
            for c in rpt :
                self.log.writeToLog(self.errorCodes['0240'], [c[0], c[1]])
            # Change to gneric hyphens
            self.pt2GenHyphens(self.approvedWords)
            self.pt2GenHyphens(self.hyphenWords)
            self.pt2GenHyphens(self.softHyphenWords)
        else :
            self.tools.dieNow('Error: Editor not supported: ' + self.sourceEditor)

        # Pull together all the words that will be in our final list.
        self.allHyphenWords.update(self.approvedWords)
        self.allHyphenWords.update(self.hyphenWords)
        self.allHyphenWords.update(self.softHyphenWords)
        # Add nonHyphenWords because they are exceptions
        self.allHyphenWords.update(self.nonHyphenWords)


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


###############################################################################
################### ParaTExt Hyphenation Handling Functions ###################
###############################################################################
####################### Error Code Block Series = 1000 ########################
###############################################################################


# Overview:
# A ParaTExt hyphenation word list (hyphenatedWords.txt) can potentually contain
# the following types of words:
#
#   1) abc-efg      = abc-efg   / exsiting words that contain a hyphen(s)
#   2) *abc-efg     = abc-efg   / approved words (by PT user) demarked by '*'
#   3) abc=efg      = abc-efg   / soft hyphens are added to a word
#   4) abcefg       = abcefg    / no hyphens found (may need further processing)
#
# (* Note that the "*" demarker is added by ParaTExt as a user approves a given
#   word. This character must be added manually if any processing is done outside
#   of PT so that PT can "learn" how words should be hyphenated and will make
#   better decisions in its automated hyphening. In theory, the user should be
#   teach PT to the point where no outside processing is needed.
#
# There may be some problems with words encountered. If any of the following are
# found they will be reported but it will not stop processing:
#
#   1) mixed syntax is illegal (abc-efg=hij)


    def preprocessSource (self) :
        '''Run a hyphenation preprocess script on the project's source hyphenation
        file. This happens when the component type import processes are happening.'''

#        import pdb; pdb.set_trace()

        # Check first to see if there is a preprocess script
        if self.tools.str2bool(self.hyphenationConfig['GeneralSettings']['useHyphenSourcePreprocess']) :
            if not os.path.isfile(self.preProcessFile) :
                self.installHyphenPreprocess()
            else :
                err = subprocess.call([self.preProcessFile, self.ptProjHyphFile])
                if err == 0 :
                    self.log.writeToLog(self.errorCodes['1490'])
                    return True
                else :
                    self.log.writeToLog(self.errorCodes['1495'])
                    return False


    def copyPtHyphenWords (self) :
        '''Simple copy of the ParaTExt project hyphenation words list to the project.
        We will also create a backup as well to be used for comparison or fallback.'''

        if os.path.isfile(self.ptHyphFile) :
            # Use a special kind of copy to prevent problems with BOMs
            self.tools.utf8Copy(self.ptHyphFile, self.ptProjHyphFile)
        else :
            self.log.writeToLog(self.errorCodes['1410'], '', 'copyPtHyphenWords()')


    def backupPtHyphenWords (self) :
        '''Backup the ParaTExt project hyphenation words list to the project.'''

#        import pdb; pdb.set_trace()

        # Remove any existing backup file if it is different.
        if os.path.exists(self.ptHyphFile) :
        
            if os.path.exists(self.ptProjHyphBakFile) :
                if ProjCompare(self.pid).isDifferent(self.ptHyphFile, self.ptProjHyphBakFile) :
                    if os.path.exists(self.ptProjHyphBakFile) :
                        os.remove(self.ptProjHyphBakFile)
                    # Use a special kind of copy to prevent problems with BOMs
                    self.tools.utf8Copy(self.ptHyphFile, self.ptProjHyphBakFile)
                    self.tools.makeReadOnly(self.ptProjHyphBakFile)
            else :
                # Use a special kind of copy to prevent problems with BOMs
                self.tools.utf8Copy(self.ptHyphFile, self.ptProjHyphBakFile)
                self.tools.makeReadOnly(self.ptProjHyphBakFile)
        else :
            self.log.writeToLog(self.errorCodes['1410'])


    def installHyphenPreprocess (self) :
        '''Install the hypenation preprocess script.'''

        try :
            shutil.copy(self.rapumaPreProcessFile, self.preProcessFile)
            self.tools.makeExecutable(self.preProcessFile)
            self.log.writeToLog(self.errorCodes['1480'])
        except Exception as e :
            self.log.writeToLog(self.errorCodes['1485'], [str(e)])



    def processHyphens(self, force) :
        '''This controls the processing of the master PT hyphenation file. The end
        result are four data sets that are ready to be handed off to the next part
        of the process. It is assumed that at this point we have a valid PT hyphen
        file that came out of PT that way or it was fixed during copy by a preprocess
        script that was made to fix specific problems.'''

#        import pdb; pdb.set_trace()

        # The project source files are protected but if force is used
        # we need to delete them here.
        if force :
            if os.path.exists(self.ptProjHyphFile) :
                os.remove(self.ptProjHyphFile)
            if os.path.exists(self.ptProjHyphBakFile) :
                os.remove(self.ptProjHyphBakFile)
            self.log.writeToLog(self.errorCodes['1460'])

        # These calls may be order-sensitive, update local project source
        if not os.path.isfile(self.ptProjHyphFile) or self.tools.isOlder(self.ptProjHyphFile, self.ptHyphFile) :
            self.copyPtHyphenWords()
            self.backupPtHyphenWords()
            self.preprocessSource()
            self.log.writeToLog(self.errorCodes['1450'], [self.tools.fName(self.ptHyphFile)])
        else :
            self.log.writeToLog(self.errorCodes['1455'], [self.tools.fName(self.ptHyphFile)])

        # Continue by processing the files located in the project
        self.getAllPtHyphenWords()
        self.getApprovedWords()
        self.getHyphenWords()
        self.getSoftHyphenWords()
        self.getNonHyhpenWords()


    def getAllPtHyphenWords (self) :
        '''Return a data set of all the words found in a ParaTExt project
        hyphated words text file. The Py set() method is used for moving
        the data because some lists can get really big. This will return the
        entire wordlist as it is found in the ptHyphenFile. That can be used
        for other processing.'''

        # Go get the file if it is to be had
        if os.path.isfile(self.ptProjHyphFile) :
            with codecs.open(self.ptProjHyphFile, "r", encoding='utf_8') as hyphenWords :
                for line in hyphenWords :
                    # Using the logic that there can only be one word in a line
                    # if the line contains more than one word it is not wanted
                    word = line.split()
                    if len(word) == 1 :
                        self.allPtHyphenWords.add(word[0])

            # Now remove any bad/mal-formed words
            self.checkForBadWords()


    def getApprovedWords (self) :
        '''Return a data set of approved words found in a ParaTExt project
        hyphen word list that have a '*' in front of them. This indicates that
        the spelling has been manually approved by the user. These words may
        or may not contain hyphens'''

        # Go get the file if it is to be had
        for word in list(self.goodPtHyphenWords) :
            if word[:1] == '*' :
                self.approvedWords.add(word[1:])
                self.goodPtHyphenWords.remove(word)


    def getHyphenWords (self) :
        '''Return a data set of pre-hyphated words found in a ParaTExt project
        hyphen words list. These are words that are spelled with a hyphen in
        them but can break on line endings.'''

        # Go get the file if it is to be had
        for word in list(self.goodPtHyphenWords) :
            if '-' in word :
                self.hyphenWords.add(word)
                self.goodPtHyphenWords.remove(word)


    def getSoftHyphenWords (self) :
        '''Return a data set of words that contain soft hyphens but have not
        been approved by the user. These are normally created by PT or some
        external process.'''

        for word in list(self.goodPtHyphenWords) :
            if '=' in word :
                self.softHyphenWords.add(word)
                self.goodPtHyphenWords.remove(word)


    def getNonHyhpenWords (self) :
        '''Return a data set of words that do not contain hyphens. These are
        words that cannot normally be broken. This process must be run after
        getApprovedWords(), getSoftHyphenWords() and getHyphenWords().'''

        self.nonHyphenWords = self.goodPtHyphenWords.copy()
        self.nonHyphenWords.difference_update(self.approvedWords)
        self.nonHyphenWords.difference_update(self.softHyphenWords)
        self.nonHyphenWords.difference_update(self.hyphenWords)


    def checkForBadWords (self) :
        '''Check the words in the master list for bad syntax. Remove them
        and put them in a hyphen error words file in the project and give
        a warning to the user.'''

        for word in list(self.allPtHyphenWords) :
            if '-' in word and '=' in word :
                self.badWords.add(word)
            else :
                # Make the good words list here
                self.goodPtHyphenWords.add(word)

        if len(self.badWords) :
            errWords = list(self.badWords)
            errWords.sort()
            with codecs.open(self.ptProjHyphErrFile, "w", encoding='utf_8') as wordErrorsObject :
                wordErrorsObject.write('# ' + self.tools.fName(self.ptProjHyphErrFile) + '\n')
                wordErrorsObject.write('# This is an auto-generated file which contains errors in the hyphenation words file.\n')
                for word in errWords :
                    wordErrorsObject.write(word + '\n')

            # Report the problem to the user
            self.log.writeToLog(self.errorCodes['1430'], [self.tools.fName(self.ptProjHyphErrFile)])


    def wordTotals (self) :
        '''Return a report on word processing totals. For accuracy this is
        dependent on getApprovedWords(), getSoftHyphenWords(), getHyphenWords()
        and getNonHyhpenWords to be run before it. If the difference is off, die
        here and report the numbers.'''

        wrds = len(self.allPtHyphenWords)
        badw = len(self.badWords)
        excp = len(self.approvedWords)
        soft = len(self.softHyphenWords)
        hyph = len(self.hyphenWords)
        pwrd = len(self.nonHyphenWords)
        diff = wrds - (badw + excp + soft + hyph + pwrd)
        
        rpt = '\tAll words = ' + str(wrds) + '\n' \
                '\tBad words = ' + str(badw) + '\n' \
                '\tException words = ' + str(excp) + '\n' \
                '\tSoft hyphen words = ' + str(soft) + '\n' \
                '\tHyphen words = ' + str(hyph) + '\n' \
                '\tProcess words = ' + str(pwrd) + '\n' \
                '\tDifference = ' + str(diff) + '\n\n' \

        # Die here if the diff is off (not 0)
        if diff != 0 :
            self.tools.dieNow('\nWord totals do not balance.\n\n' + rpt + 'Rapuma halted!\n')

        return [['Total words', str(wrds)], ['Bad words', str(badw)], ['Exception words', str(excp)], ['Soft Hyphen words', str(soft)], ['Hyphen words', str(hyph)], ['Process words', str(pwrd)]]


    def pt2GenHyphens (self, hyphenWords) :
        '''Create a set of generic hyphen markers on a given list of words
        that contain hyphens or PT hyphen markers (=).'''
        
        # Make a new set to work on and pass on
        for word in list(hyphenWords) :
            soft = re.sub(u'\=', u'<->', word)
            norm = re.sub(u'\-', u'<->', word)
            if word != soft :
                hyphenWords.add(soft)
                hyphenWords.remove(word)
            elif word != norm :
                hyphenWords.add(norm)
                hyphenWords.remove(word)

        return hyphenWords



