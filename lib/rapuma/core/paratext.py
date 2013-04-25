#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle functions that work with ParaTExt data.

###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, dircache, subprocess, re
from configobj import ConfigObj
from importlib import import_module

# Load the local classes
from rapuma.core.tools          import Tools
from rapuma.core.proj_config    import ProjConfig
from rapuma.core.user_config    import UserConfig
from rapuma.core.proj_local     import ProjLocal
from rapuma.core.proj_log       import ProjLog


class Paratext (object) :

    def __init__(self, pid) :
        '''Intitate the whole class and create the object.'''

        self.pid                    = pid
        self.tools                  = Tools()
        self.user                   = UserConfig()
        self.userConfig             = self.user.userConfig
        self.projHome               = self.userConfig['Projects'][pid]['projectPath']
        self.projectMediaIDCode     = self.userConfig['Projects'][pid]['projectMediaIDCode']
        self.local                  = ProjLocal(pid)
        self.projConfig             = ProjConfig(self.local).projConfig
        self.log                    = ProjLog(self.pid)
        self.cType                  = 'usfm'
        self.Ctype                  = self.cType.capitalize()
        self.useHyphenation         = False
        # Folder paths
        self.projHyphenationFolder  = self.local.projHyphenationFolder
        # Some hyphenation handling settings and data that might work
        # better if they were more global
        self.allPtHyphenWords       = set()
        self.goodPtHyphenWords      = set()
        self.badWords               = set()
        self.hyphenWords            = set()
        self.approvedWords          = set()

        self.softHyphenWords        = set()
        self.nonHyphenWords         = set()

        self.finishInit()


        self.errorCodes     = {
            '0000' : ['MSG', 'Group processing messages'],

            '0250' : ['LOG', 'Updated project file: [<<1>>]'],
            '0255' : ['LOG', 'Did not update project file: [<<1>>]'],
            '0260' : ['MSG', 'Force switch was set. Removed hyphenation source files for update proceedure.'],
            '0280' : ['WRN', 'New default hyphen preprocess script copied into the project. Please edit before using.'],
            '0290' : ['MSG', 'Ran hyphen preprocess script on project hyphenation source file.'],
            '0295' : ['ERR', 'Preprocess script failed to run on source file.'],

        }


    def finishInit (self) :
        '''Some times not all the information is available that is needed
        but that may not be a problem for some functions. We will atempt to
        finish the init here but will fail silently, which may not be a good
        idea in the long run.'''

#        import pdb; pdb.set_trace()

        try :
            self.useHyphenation         = self.tools.str2bool(self.projConfig['Managers'][self.cType + '_Hyphenation']['useHyphenation'])
        except :
            pass

###############################################################################
############################# General PT Functions ############################
###############################################################################
####################### Error Code Block Series = 0200 ########################
###############################################################################


    def getUsfmCidInfo (self, cid) :
        '''Return a list of info about a specific cid used in the PT context.'''

#        import pdb; pdb.set_trace()

        try :
            return self.usfmCidInfo()[cid]
        except :
            return False


    def getNWFChars (self, gid) :
        '''Return a list of non-word-forming characters from the PT settings
        field [ValidPunctuation] in the translation project.'''

        ptSet = self.getPTSettings(gid)
        chars = []
        if self.tools.testForSetting(ptSet['ScriptureText'], 'ValidPunctuation') :
            for c in ptSet['ScriptureText']['ValidPunctuation'].split() :
                # Leave it a lone if it is a single character
                if len(c) == 1 :
                    chars.append(c)
                # A pair is what we expect
                elif len(c) == 2 :
                    # We expect "_" to be part of the pair
                    try :
                        if c.find('_') > 0 :
                            chars.append(c.replace('_', ''))
                    except Exception as e :
                        # If we don't succeed, we should probably quite here
                        self.log.writeToLog('USFM-010', [str(e)])
                else :
                    # Something really strange happened
                    self.log.writeToLog('USFM-020', [c])
        else :
            self.log.writeToLog('USFM-025')
        return chars


    def formPTName (self, gid, cid) :
        '''Using valid PT project settings from the project configuration, form
        a valid PT file name that can be used for a number of operations.'''

        # Assumed that this is for a ParaTExt USFM file, there should be
        # a nameFormID setting. If not, try updating the manager. If there
        # still is not a nameFormID, die in a very spectacular way.
        if not self.projConfig['Managers']['usfm_Text']['nameFormID'] :
            self.project.managers['usfm_Text'].updateManagerSettings(gid)

        # Hopefully all is well now
        nameFormID = self.projConfig['Managers']['usfm_Text']['nameFormID']
        postPart = self.projConfig['Managers']['usfm_Text']['postPart']
        prePart = self.projConfig['Managers']['usfm_Text']['prePart']

        # Sanity test
        if not nameFormID :
            self.tools.dieNow('ERROR: usfm.PT_Tools.formPTName() could not determine the nameFormID. All is lost! Please crawl under your desk and wait for a large explosion. (Just kidding!)')

#        import pdb; pdb.set_trace()

        thisFile = ''

        if nameFormID == '41MAT' :
            mainName = self.getUsfmCidInfo(cid)[2] + cid.upper()
            if prePart and prePart != 'None' :
                thisFile = prePart + mainName + postPart
            else :
                thisFile = mainName + postPart
                
        if thisFile != '' :
            return thisFile
        else :
            return None


    def formGenericName (self, gid, cid) :
        '''Figure out the best way to form a valid file name given the
        source is not coming from a PT project. In the end, this is almost
        impossible to do because of all the different possibilities. We
        will just try to make our best guess. A better way will be needed.'''

        postPart = self.projConfig['Managers']['usfm_Text']['postPart']
        if postPart == '' :
            postPart = self.projConfig['Groups'][gid]['cType']

        return cid + '.' + postPart


    def mapPTTextSettings (self, sysSet, ptSet, force=False) :
        '''Map the text settings from a PT project SSF file into the text
        manager's settings. If no setting is present in the config, add
        what is in the PT SSF. If force is True, replace any exsisting
        settings.'''

        # A PT to Rapuma text mapping dictionary
        mapping   = {
                    'FileNameBookNameForm'      : 'nameFormID',
                    'FileNameForm'              : 'nameFormID',
                    'FileNamePrePart'           : 'prePart',
                    'FileNamePostPart'          : 'postPart',
                    'DefaultFont'               : 'ptDefaultFont'
                    }

        # Loop through all the PT settings and check against the mapping
        for k in mapping.keys() :
            try :
                if sysSet[mapping[k]] == '' or sysSet[mapping[k]] == 'None' :
                    # This is for getting rid of "None" settings in the config
                    if not ptSet['ScriptureText'][k] :
                        sysSet[mapping[k]] = ''
                    else :
                        sysSet[mapping[k]] = ptSet['ScriptureText'][k]
                elif force :
                    sysSet[mapping[k]] = ptSet['ScriptureText'][k]
            except :
                pass

        return sysSet


    def findSsfFile (self, gid) :
        '''Look for the ParaTExt project settings file. The immediat PT project
        is the parent folder and the PT environment that the PT projet is found
        in, if any, is the grandparent folder. the .ssf (settings) file in the
        grandparent folder takes presidence over the one found in the parent folder.
        This function will determine where the primary .ssf file is and return the
        .ssf path/file and the PT path. If not found, return None.'''

        # Not sure where the PT SSF file might be or even what its name is.
        # Starting in parent, we should find the first .ssf file. That will
        # give us the name of the file. Then we will look in the grandparent
        # folder and if we find the same named file there, that will be
        # harvested for the settings. Otherwise, the settings will be taken
        # from the parent folder.
        # Note: Starting with PT 7 the "gather" folder was introduced to
        # projects. We will need to look in that folder as well for the 
        # .ssf file.
        ssfFileName = ''
        ptPath = ''
        parentFolder = self.getGroupSourcePath(gid)
        grandparentFolder = os.path.dirname(parentFolder)
        gatherFolder = os.path.join(parentFolder, 'gather')

        # For now, we will assume that if there is a gather folder, it must have a .ssf file in it
        if os.path.isdir(gatherFolder) :
            parentFolder = gatherFolder
        # Get a file list from the parent folder and look for a .ssf/.SSF file
        # This assumes there is (has to be) only one ssf/SSF file in the folder.
        # The main problem at this point is we don't really know the name of
        # the file, only the extention.
        parentFileList = dircache.listdir(parentFolder)
        grandparentFileList = dircache.listdir(grandparentFolder)

        # Parent first to find the actual settings file name. Right now, there
        # can only be 2 possibilities, either ssf or SSF. (No one in their right
        # mind would ever use mixed case on an extention. That would be stupid!)
        for f in parentFileList :
            if os.path.isfile(os.path.join(parentFolder, f)) :
                # Not every file we test has an extention, look first
                if len(f.split('.')) > 1 :
                    if f.split('.')[1] == 'ssf' or f.split('.')[1] == 'SSF' :
                        ssfFileName = f
                        ptPath = parentFolder

        # At this point we need a sanity test. If no ssfFileName is present
        # then there probably isn't one and we should just return False now
        if not ssfFileName :
            return False

        # Now now look in the grandparent folder and change to override settings
        # file if there is one
        for f in grandparentFileList :
            if os.path.isfile(os.path.join(grandparentFolder, f)) :
                ucn = ssfFileName.split('.')[0] + '.' + ssfFileName.split('.')[1].upper()
                lcn = ssfFileName.split('.')[0] + '.' + ssfFileName.split('.')[1].lower()
                if f == (ucn or lcn) :
                    ssfFileName = f
                    ptPath = grandparentFolder

        return os.path.join(ptPath, ssfFileName)


    def getPTSettings (self, gid) :
        '''Return the data into a dictionary for the system to use.'''

        sourcePath = self.getGroupSourcePath(gid)

        # Return the dictionary
        if os.path.isdir(sourcePath) :
            ssfFile = self.findSsfFile(gid)
            if ssfFile :
                if os.path.isfile(ssfFile) :
                    return self.tools.xmlFileToDict(ssfFile)


    def getSourceEditor (self, gid) :
        '''Return the sourceEditor if it is set. If not try to
        figure out what it should be and return that. Unless we
        find we are in a PT project, we'll call it generic.'''

    #    import pdb; pdb.set_trace()
        se = 'generic'
        # FIXME: This may need expanding as more use cases arrise
        if self.tools.testForSetting(self.projConfig['CompTypes'][self.Ctype], 'sourceEditor') :
            se = self.projConfig['CompTypes'][self.Ctype]['sourceEditor']
        else :
            if self.findSsfFile(gid) :
                se = 'paratext'

        return se


    def getGroupSourcePath (self, gid) :
        '''Get the source path for a specified group.'''

#        import pdb; pdb.set_trace()
        csid = self.projConfig['Groups'][gid]['csid']

        try :
            return self.userConfig['Projects'][self.pid][csid + '_sourcePath']
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.tools.terminal('No source path found for: [' + str(e) + ']')
            self.tools.terminal('Please add a source path for this component type.')
            self.tools.dieNow()


    def usfmCidInfo (self) :
        '''Return a dictionary of all valid information about USFMs used in PT.'''

    #            ID     Comp Name                               Comp ID                         PT ID  Chps
        return {
                '_z_' : ['USFM InternalCaller',                 'usfm_internal_caller',         '00',   0], 
                'gen' : ['Genesis',                             'genesis',                      '01',  50], 
                'exo' : ['Exodus',                              'exodus',                       '02',  40], 
                'lev' : ['Leviticus',                           'leviticus',                    '03',  27], 
                'num' : ['Numbers',                             'numbers',                      '04',  36], 
                'deu' : ['Deuteronomy',                         'deuteronomy',                  '05',  34], 
                'jos' : ['Joshua',                              'joshua',                       '06',  24], 
                'jdg' : ['Judges',                              'judges',                       '07',  21], 
                'rut' : ['Ruth',                                'ruth',                         '08',   4], 
                '1sa' : ['1 Samuel',                            '1_samuel',                     '09',  31], 
                '2sa' : ['2 Samuel',                            '2_samuel',                     '10',  24], 
                '1ki' : ['1 Kings',                             '1_kings',                      '11',  22], 
                '2ki' : ['2 Kings',                             '2_kings',                      '12',  25], 
                '1ch' : ['1 Chronicles',                        '1_chronicles',                 '13',  29], 
                '2ch' : ['2 Chronicles',                        '2_chronicles',                 '14',  36], 
                'ezr' : ['Ezra',                                'ezra',                         '15',  10], 
                'neh' : ['Nehemiah',                            'nehemiah',                     '16',  13], 
                'est' : ['Esther',                              'esther',                       '17',  10], 
                'job' : ['Job',                                 'job',                          '18',  42], 
                'psa' : ['Psalms',                              'psalms',                       '19', 150], 
                'pro' : ['Proverbs',                            'proverbs',                     '20',  31], 
                'ecc' : ['Ecclesiastes',                        'ecclesiastes',                 '21',  12], 
                'sng' : ['Song of Songs',                       'song_of_songs',                '22',   8], 
                'isa' : ['Isaiah',                              'isaiah',                       '23',  66], 
                'jer' : ['Jeremiah',                            'jeremiah',                     '24',  52], 
                'lam' : ['Lamentations',                        'lamentations',                 '25',   5], 
                'ezk' : ['Ezekiel',                             'ezekiel',                      '26',  48], 
                'dan' : ['Daniel',                              'daniel',                       '27',  12], 
                'hos' : ['Hosea',                               'hosea',                        '28',  14], 
                'jol' : ['Joel',                                'joel',                         '29',   3], 
                'amo' : ['Amos',                                'amos',                         '30',   9], 
                'oba' : ['Obadiah',                             'obadiah',                      '31',   1], 
                'jon' : ['Jonah',                               'jonah',                        '32',   4], 
                'mic' : ['Micah',                               'micah',                        '33',   7], 
                'nam' : ['Nahum',                               'nahum',                        '34',   3], 
                'hab' : ['Habakkuk',                            'habakkuk',                     '35',   3], 
                'zep' : ['Zephaniah',                           'zephaniah',                    '36',   3], 
                'hag' : ['Haggai',                              'haggai',                       '37',   2], 
                'zec' : ['Zechariah',                           'zechariah',                    '38',  14], 
                'mal' : ['Malachi',                             'malachi',                      '39',   4],
                'mat' : ['Matthew',                             'matthew',                      '41',  28], 
                'mrk' : ['Mark',                                'mark',                         '42',  16], 
                'luk' : ['Luke',                                'luke',                         '43',  24], 
                'jhn' : ['John',                                'john',                         '44',  21], 
                'act' : ['Acts',                                'acts',                         '45',  28], 
                'rom' : ['Romans',                              'romans',                       '46',  16], 
                '1co' : ['1 Corinthians',                       '1_corinthians',                '47',  16], 
                '2co' : ['2 Corinthians',                       '2_corinthians',                '48',  13], 
                'gal' : ['Galatians',                           'galatians',                    '49',   6], 
                'eph' : ['Ephesians',                           'ephesians',                    '50',   6], 
                'php' : ['Philippians',                         'philippians',                  '51',   4], 
                'col' : ['Colossians',                          'colossians',                   '52',   4], 
                '1th' : ['1 Thessalonians',                     '1_thessalonians',              '53',   5], 
                '2th' : ['2 Thessalonians',                     '2_thessalonians',              '54',   3], 
                '1ti' : ['1 Timothy',                           '1_timothy',                    '55',   6], 
                '2ti' : ['2 Timothy',                           '2_timothy',                    '56',   4], 
                'tit' : ['Titus',                               'titus',                        '57',   3], 
                'phm' : ['Philemon',                            'philemon',                     '58',   1], 
                'heb' : ['Hebrews',                             'hebrews',                      '59',  13], 
                'jas' : ['James',                               'james',                        '60',   5], 
                '1pe' : ['1 Peter',                             '1_peter',                      '61',   5], 
                '2pe' : ['2 Peter',                             '2_peter',                      '62',   3], 
                '1jn' : ['1 John',                              '1_john',                       '63',   5], 
                '2jn' : ['2 John',                              '2_john',                       '64',   1], 
                '3jn' : ['3 John',                              '3_john',                       '65',   1], 
                'jud' : ['Jude',                                'jude',                         '66',   1], 
                'rev' : ['Revelation',                          'revelation',                   '67',  22], 
                'tob' : ['Tobit',                               'tobit',                        '68', '?'], 
                'jdt' : ['Judith',                              'judith',                       '69', '?'], 
                'esg' : ['Esther',                              'esther',                       '70', '?'], 
                'wis' : ['Wisdom of Solomon',                   'wisdom_of_solomon',            '71', '?'], 
                'sir' : ['Sirach',                              'sirach',                       '72', '?'], 
                'bar' : ['Baruch',                              'baruch',                       '73', '?'], 
                'lje' : ['Letter of Jeremiah',                  'letter_of_jeremiah',           '74', '?'], 
                's3y' : ['Song of the Three Children',          'song_3_children',              '75', '?'], 
                'sus' : ['Susanna',                             'susanna',                      '76', '?'], 
                'bel' : ['Bel and the Dragon',                  'bel_dragon',                   '77', '?'], 
                '1ma' : ['1 Maccabees',                         '1_maccabees',                  '78', '?'], 
                '2ma' : ['2 Maccabees',                         '2_maccabees',                  '79', '?'], 
                '3ma' : ['3 Maccabees',                         '3_maccabees',                  '80', '?'], 
                '4ma' : ['4 Maccabees',                         '4_maccabees',                  '81', '?'], 
                '1es' : ['1 Esdras',                            '1_esdras',                     '82', '?'], 
                '2es' : ['2 Esdras',                            '2_esdras',                     '83', '?'], 
                'man' : ['Prayer of Manasses',                  'prayer_of_manasses',           '84', '?'], 
                'ps2' : ['Psalms 151',                          'psalms_151',                   '85', '?'], 
                'oda' : ['Odae',                                'odae',                         '86', '?'], 
                'pss' : ['Psalms of Solomon',                   'psalms_of_solomon',            '87', '?'], 
                'jsa' : ['Joshua A',                            'joshua_a',                     '88', '?'], 
                'jdb' : ['Joshua B',                            'joshua_b',                     '89', '?'], 
                'tbs' : ['Tobit S',                             'tobit_s',                      '90', '?'], 
                'sst' : ['Susannah (Theodotion)',               'susannah_t',                   '91', '?'], 
                'dnt' : ['Daniel (Theodotion)',                 'daniel_t',                     '92', '?'], 
                'blt' : ['Bel and the Dragon (Theodotion)',     'bel_dragon_t',                 '93', '?'], 
                'frt' : ['Front Matter',                        'front_matter',                 'A0',   0], 
                'int' : ['Introductions',                       'introductions',                'A7',   0], 
                'bak' : ['Back Matter',                         'back_matter',                  'A1',   0], 
                'cnc' : ['Concordance',                         'concordance',                  'A8',   0], 
                'glo' : ['Glossary',                            'glossary',                     'A9',   0], 
                'tdx' : ['Topical Index',                       'topical_index',                'B0',   0], 
                'ndx' : ['Names Index',                         'names_index',                  'B1',   0], 
                'xxa' : ['Extra A',                             'extra_a',                      '94',   0], 
                'xxb' : ['Extra B',                             'extra_b',                      '95',   0], 
                'xxc' : ['Extra C',                             'extra_c',                      '96',   0], 
                'xxd' : ['Extra D',                             'extra_d',                      '97',   0],
                'xxe' : ['Extra E',                             'extra_e',                      '98',   0], 
                'xxf' : ['Extra F',                             'extra_f',                      '99',   0], 
                'xxg' : ['Extra G',                             'extra_g',                      '100',  0], 
                'oth' : ['Other',                               'other',                        'A2',   0], 
                'eza' : ['Apocalypse of Ezra',                  'apocalypse_of_ezra',           'A4', '?'], 
                '5ez' : ['5 Ezra',                              '5_ezra_lp',                    'A5', '?'], 
                '6ez' : ['6 Ezra (Latin Epilogue)',             '6_ezra_lp',                    'A6', '?'], 
                'dag' : ['Daniel Greek',                        'daniel_greek',                 'B2', '?'], 
                'ps3' : ['Psalms 152-155',                      'psalms_152-155',               'B3', '?'], 
                '2ba' : ['2 Baruch (Apocalypse)',               '2_baruch_apocalypse',          'B4', '?'], 
                'lba' : ['Letter of Baruch',                    'letter_of_baruch',             'B5', '?'], 
                'jub' : ['Jubilees',                            'jubilees',                     'B6', '?'], 
                'eno' : ['Enoch',                               'enoch',                        'B7', '?'], 
                '1mq' : ['1 Meqabyan',                          '1_meqabyan',                   'B8', '?'], 
                '2mq' : ['2 Meqabyan',                          '2_meqabyan',                   'B9', '?'], 
                '3mq' : ['3 Meqabyan',                          '3_meqabyan',                   'C0', '?'], 
                'rep' : ['Reproof (Proverbs 25-31)',            'reproof_proverbs_25-31',       'C1', '?'], 
                '4ba' : ['4 Baruch (Rest of Baruch)',           '4_baruch',                     'C2', '?'], 
                'lao' : ['Laodiceans',                          'laodiceans',                   'C3', '?'] 

               }


###############################################################################
################### ParaTExt Hyphenation Handling Functions ###################
###############################################################################
####################### Error Code Block Series = 0400 ########################
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


    def preprocessSource (self, ptHyphFile, preProcessFile, rapumaPreProcessFile) :
        '''Run a hyphenation preprocess script on the project's source hyphenation
        file. This happens when the component type import processes are happening.'''

        if self.tools.str2bool(self.projConfig['Managers']['usfm_Hyphenation']['useHyphenSourcePreprocess']) :
            if not os.path.isfile(preProcessFile) :
                shutil.copy(rapumaPreProcessFile, preProcessFile)
                self.tools.makeExecutable(preProcessFile)
                self.log.writeToLog(self.errorCodes['0280'])
            else :
                err = subprocess.call([preProcessFile, ptHyphFile])
                if err == 0 :
                    self.log.writeToLog(self.errorCodes['0290'])
                    return True
                else :
                    self.log.writeToLog(self.errorCodes['0295'])
                    return False


    def copyPtHyphenWords (self, ptHyphFile, ptProjHyphFile, preProcessFile, rapumaPreProcessFile) :
        '''Simple copy of the ParaTExt project hyphenation words list to the project.
        We will also create a backup as well to be used for comparison or fallback.'''

        if os.path.isfile(ptHyphFile) :
            # Use a special kind of copy to prevent problems with BOMs
            self.tools.utf8Copy(ptHyphFile, ptProjHyphFile)
            # Once copied, check if any preprocessing is needed
            self.preprocessSource(ptHyphFile, preProcessFile, rapumaPreProcessFile)
        else :
            self.log.writeToLog('USFM-040', [ptHyphFile])


    def backupPtHyphenWords (self, ptHyphFile, ptProjHyphBakFile) :
        '''Backup the ParaTExt project hyphenation words list to the project.'''

        if os.path.isfile(ptHyphFile) :
            # Use a special kind of copy to prevent problems with BOMs
            self.tools.utf8Copy(ptHyphFile, ptProjHyphBakFile)
            self.tools.makeReadOnly(ptProjHyphBakFile)
        else :
            self.log.writeToLog('USFM-040', [ptHyphFile])


    def processHyphens(self, gid, force = False) :
        '''This controls the processing of the master PT hyphenation file. The end
        result are four data sets that are ready to be handed off to the next part
        of the process. It is assumed that at this point we have a valid PT hyphen
        file that came out of PT that way or it was fixed during copy by a preprocess
        script that was made to fix specific problems.'''

        # Get group setting vars
        csid = self.projConfig['Groups'][gid]['csid']
        cType = self.projConfig['Groups'][gid]['cType']

        # File Names
        preProcessFileName          = cType + '_' + self.projConfig['Managers']['usfm_Hyphenation']['sourcePreProcessScriptName']
        ptProjHyphErrFileName       = csid + '_' + self.projConfig['Managers']['usfm_Hyphenation']['ptHyphErrFileName']
        ptHyphFileName              = self.projConfig['Managers']['usfm_Hyphenation']['ptHyphenFileName']
        sourcePath                  = self.userConfig['Projects'][self.pid][csid + '_sourcePath']
        # Set file names with full path 
        ptHyphFile                  = os.path.join(sourcePath, ptHyphFileName)
        ptProjHyphFile              = os.path.join(self.projHyphenationFolder, ptHyphFileName)
        ptProjHyphBakFile           = os.path.join(self.projHyphenationFolder, ptHyphFileName + '.bak')
        ptProjHyphErrFile           = os.path.join(self.projHyphenationFolder, ptProjHyphErrFileName)
        preProcessFile              = os.path.join(self.local.projHyphenationFolder, preProcessFileName)
        rapumaPreProcessFile        = os.path.join(self.local.rapumaScriptsFolder, preProcessFileName)

        # The project source files are protected but if force is used
        # we need to delete them here.
        if force :
            if os.path.exists(ptProjHyphFile) :
                os.remove(ptProjHyphFile)
            if os.path.exists(ptProjHyphBakFile) :
                os.remove(ptProjHyphBakFile)
            self.log.writeToLog(self.errorCodes['0260'])

        # These calls may be order-sensitive, update local project source
        if not os.path.isfile(ptProjHyphFile) or self.tools.isOlder(ptProjHyphFile, ptHyphFile) :
            self.copyPtHyphenWords(ptHyphFile, ptProjHyphFile, preProcessFile, rapumaPreProcessFile)
            self.backupPtHyphenWords(ptHyphFile, ptProjHyphBakFile)
            self.log.writeToLog(self.errorCodes['0250'], [self.tools.fName(ptHyphFile)])
        else :
            self.log.writeToLog(self.errorCodes['0255'], [self.tools.fName(ptHyphFile)])

        # Continue by processing the files located in the project
        self.getAllPtHyphenWords(ptProjHyphFile, ptProjHyphErrFile)
        self.getApprovedWords()
        self.getHyphenWords()
        self.getSoftHyphenWords()
        self.getNonHyhpenWords()


    def getAllPtHyphenWords (self, ptProjHyphFile, ptProjHyphErrFile) :
        '''Return a data set of all the words found in a ParaTExt project
        hyphated words text file. The Py set() method is used for moving
        the data because some lists can get really big. This will return the
        entire wordlist as it is found in the ptHyphenFile. That can be used
        for other processing.'''

        # Go get the file if it is to be had
        if os.path.isfile(ptProjHyphFile) :
            with codecs.open(ptProjHyphFile, "r", encoding='utf_8') as hyphenWords :
                for line in hyphenWords :
                    # Using the logic that there can only be one word in a line
                    # if the line contains more than one word it is not wanted
                    word = line.split()
                    if len(word) == 1 :
                        self.allPtHyphenWords.add(word[0])

            # Now remove any bad/mal-formed words
            self.checkForBadWords(ptProjHyphErrFile)


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


    def checkForBadWords (self, ptProjHyphErrFile) :
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
            with codecs.open(ptProjHyphErrFile, "w", encoding='utf_8') as wordErrorsObject :
                wordErrorsObject.write('# ' + self.tools.fName(ptProjHyphErrFile) + '\n')
                wordErrorsObject.write('# This is an auto-generated file which contains errors in the hyphenation words file.\n')
                for word in errWords :
                    wordErrorsObject.write(word + '\n')

            # Report the problem to the user
            self.log.writeToLog('USFM-030', [ptProjHyphErrFile])


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


###############################################################################
################### ParaTExt Illustration Handling Functions ##################
###############################################################################
####################### Error Code Block Series = 0600 ########################
###############################################################################


    def logFigure (self, gid, cid, figConts) :
        '''Log the figure data in the illustration.conf. If nothing is returned, the
        existing \fig markers with their contents will be removed. That is the default
        behavior.'''

        # Get config objects unique to this function
        layoutConfig            = ConfigObj(os.path.join(self.local.projConfFolder, self.projectMediaIDCode + '_layout.conf'), encoding='utf-8')
        illustrationConfig      = ConfigObj(os.path.join(self.local.projConfFolder, self.projectMediaIDCode + '_illustration.conf'), encoding='utf-8')
        # Description of figKeys (in order found in \fig)
            # description = A brief description of what the illustration is about
            # file = The file name of the illustration (only the file name)
            # caption = The caption that will be used with the illustration (if turned on)
            # width = The width or span the illustration will have (span/col)
            # location = Location information that could be printed in the caption reference
            # copyright = Copyright information for the illustration
            # reference = The book ID (upper-case) plus the chapter and verse (eg. MAT 8:23)

        fig = figConts.group(1).split('|')
        figKeys = ['description', 'fileName', 'width', 'location', 'copyright', 'caption', 'reference']
        figDict = {}
        cvSep = layoutConfig['Illustrations']['chapterVerseSeperator']

        # Add all the figure info to the dictionary
        c = 0
        for value in fig :
            figDict[figKeys[c]] = value
            c +=1

        # Add additional information, get rid of stuff we don't need
        figDict['illustrationID'] = figDict['fileName'].split('.')[0]
        figDict['useThisIllustration'] = True
        figDict['useThisCaption'] = True
        figDict['useThisCaptionRef'] = True
        figDict['bid'] = cid.lower()
        figDict['chapter'] = re.sub(ur'([0-9]+)[.:][0-9]+', ur'\1', figDict['reference'].upper())
        figDict['verse'] = re.sub(ur'[0-9]+[.:]([0-9]+)', ur'\1', figDict['reference'].upper())
        figDict['scale'] = '1.0'
        if figDict['width'] == 'col' :
            figDict['position'] = 'tl'
        else :
            figDict['position'] = 't'
        if not figDict['location'] :
            figDict['location'] = figDict['chapter'] + cvSep + figDict['verse']
        if not self.tools.testForSetting(illustrationConfig, gid) :
            self.tools.buildConfSection(illustrationConfig, gid)
        # Put the dictionary info into the illustration conf file
        if not self.tools.testForSetting(illustrationConfig[gid], figDict['illustrationID'].upper()) :
            self.tools.buildConfSection(illustrationConfig[gid], figDict['illustrationID'].upper())
        for k in figDict.keys() :
            illustrationConfig[gid][figDict['illustrationID'].upper()][k] = figDict[k]

        # Write out the conf file to preserve the data found
        self.tools.writeConfFile(illustrationConfig)

        # Just incase we need to keep the fig markers intact this will
        # allow for that. However, default behavior is to strip them
        # because usfmTex does not handle \fig markers. By returning
        # them here, they will not be removed from the working text.
        if self.tools.str2bool(self.projConfig['Managers'][self.cType + '_Illustration']['preserveUsfmFigData']) :
            return '\\fig ' + figConts.group(1) + '\\fig*'


###############################################################################
########################### ParaTExt Style Functions ##########################
###############################################################################
####################### Error Code Block Series = 0800 ########################
###############################################################################


    def usfmStyleFileIsValid (self, path) :
        '''Use the USFM parser to validate a style file. This is meant to
        be just a simple test so only return True or False.'''

        try :
            stylesheet = usfm.default_stylesheet.copy()
            stylesheet_extra = usfm.style.parse(open(os.path.expanduser(path),'r'), usfm.style.level.Content)
            return True
        except Exception as e :
            return False


    def removeUsfmStyFile (self, sType, force) :
        '''This would be useful for a style reset. Remove a style setting
        from the config for a component type and if force is used, remove
        the file from the project as well.'''

        sType = sType.lower()

        # Make sure there is something to do
        if sType == 'main' :
            oldStyle = self.project.projConfig['Managers'][self.cType + '_Style']['mainStyleFile']
        elif sType == 'custom' :
            oldStyle = self.project.projConfig['Managers'][self.cType + '_Style']['customStyleFile']

        if not oldStyle :
            self.log.writeToLog('STYL-100', [self.cType])
            return
        else :
            if sType == 'main' :
                self.project.projConfig['Managers'][self.cType + '_Style']['mainStyleFile'] = ''
                self.mainStyleFile = ''
            elif sType == 'custom' :
                self.project.projConfig['Managers'][self.cType + '_Style']['customStyleFile'] = ''
                self.customStyleFile = ''

            self.tools.writeConfFile(self.project.projConfig)

            if force :
                target = os.path.join(self.project.local.projStylesFolder, oldStyle)
                if os.path.isfile(target) :
                    os.remove(target)

                self.log.writeToLog('STYL-110', [self.tools.fName(oldStyle),self.cType])
            else :
                self.log.writeToLog('STYL-120', [self.tools.fName(oldStyle),self.cType])

            return True


    def addExsitingUsfmStyFile (self, sFile, sType, force) :
        '''Add a specific style file that is on the local system.'''

        sFile = self.tools.resolvePath(sFile)
        target = os.path.join(self.project.local.projStylesFolder, self.tools.fName(sFile))

        if not force and os.path.isfile(target) :
            self.log.writeToLog('STYL-030', [self.tools.fName(sFile)])
            return False
        elif os.path.isfile(sFile) :
            # It's there? Good, we're done!
            # If this is not an Rapuma custom style file we will validate it
            if sType.lower() == 'main' :
                if self.usfmStyleFileIsValid(sFile) :
                    shutil.copy(sFile, target)
                    self.log.writeToLog('STYL-060', [self.tools.fName(sFile)])
                    return True
                else :
                    # We die if it does not validate
                    self.log.writeToLog('STYL-070', [self.tools.fName(sFile)])
            else :
                # Assuming a custom style file we can grab most anything
                # without validating it
                shutil.copy(sFile, target)
                self.log.writeToLog('STYL-065', [self.tools.fName(sFile)])
                return True
        else :
            # Not finding the file may not be the end of the world 
            self.log.writeToLog('STYL-020', [self.tools.fName(sFile)])
            return False


    def addPtUsfmStyFile (self) :
        '''Install a PT project style file. Merg in any custom
        project styles too.'''

        # First pick up our PT settings
        ptConf = self.pt_tools.getPTSettings(self.gid)
        if not ptConf :
            return False

        # If nothing is set, give it a default to start off
        if not self.mainStyleFile :
            self.mainStyleFile = 'usfm.sty'
        # Now, override default styleFile name if we found something in the PT conf
        if ptConf['ScriptureText']['StyleSheet'] :
            self.mainStyleFile = ptConf['ScriptureText']['StyleSheet']


        # Set the target destination
        target = os.path.join(self.project.local.projStylesFolder, self.mainStyleFile)
        # As this is call is for a PT based project, it is certain the style
        # file should be found in the source or parent folder. If that
        # exact file is not found in either place, a substitute will be
        # copied in from Rapuma and given the designated name.
        sourceStyle             = os.path.join(self.sourcePath, self.mainStyleFile)
        parent                  = os.path.dirname(self.sourcePath)
        # If there is a "gather" folder, assume the style file is there
        if os.path.isdir(os.path.join(self.sourcePath, 'gather')) :
            ptProjStyle             = os.path.join(self.sourcePath, 'gather', self.mainStyleFile)
        else :
            ptProjStyle             = os.path.join(self.sourcePath, self.mainStyleFile)
        ptStyle                     = os.path.join(parent, self.mainStyleFile)
        searchOrder                 = [sourceStyle, ptProjStyle, ptStyle]
        # We will start by searching in order from the inside out and stop
        # as soon as we find one.
        for sFile in searchOrder :
            if os.path.isfile(sFile) :
                if self.usfmStyleFileIsValid(sFile) :
                    if not shutil.copy(sFile, target) :
                        return self.tools.fName(target)
                else :
                    self.log.writeToLog('STYL-075', [sFile,self.cType])
            else : 
                self.log.writeToLog('STYL-090', [sFile])



