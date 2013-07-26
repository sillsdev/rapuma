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

import codecs, os, dircache, subprocess, re, shutil
from configobj import ConfigObj
from importlib import import_module

# Load the local classes
from rapuma.core.tools              import Tools
from rapuma.core.user_config        import UserConfig
from rapuma.core.proj_local         import ProjLocal
from rapuma.core.proj_log           import ProjLog
from rapuma.core.proj_compare       import ProjCompare
from rapuma.project.proj_config     import ProjConfig


class Paratext (object) :

    def __init__(self, pid, gid = None) :
        '''Intitate the whole class and create the object.'''

        self.pid                    = pid
        self.gid                    = gid
        self.tools                  = Tools()
        self.user                   = UserConfig()
        self.userConfig             = self.user.userConfig
        self.proj_config            = ProjConfig(pid, gid)
        self.projHome               = self.userConfig['Projects'][pid]['projectPath']
        self.local                  = ProjLocal(pid)
        self.projConfig             = self.proj_config.projConfig
        self.layoutConfig           = self.proj_config.layoutConfig
        self.illustrationConfig     = self.proj_config.illustrationConfig
        self.log                    = ProjLog(pid)
        self.cType                  = 'usfm'
        self.Ctype                  = self.cType.capitalize()
        self.csid                   = None
        self.sourcePath             = None

        self.errorCodes     = {
            '0000' : ['MSG', 'Group processing messages'],
            '0005' : ['LOG', 'Paratext module finishInit() failed. No GID provided'],
            '0010' : ['WRN', 'Paratext module finishInit() failed with this error: [<<1>>]'],
        }

        # A source path is often important, try to get that now
        try :
            self.csid                   = self.projConfig['Groups'][self.gid]['csid']
            self.sourcePath             = self.userConfig['Projects'][self.pid][self.csid + '_sourcePath']
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


    def getNWFChars (self) :
        '''Return a list of non-word-forming characters from the PT settings
        field [ValidPunctuation] in the translation project.'''

        ptSet = self.getPTSettings()
        chars = []
        if ptSet['ScriptureText'].has_key('ValidPunctuation') :
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


    def formPTName (self, cid) :
        '''Using valid PT project settings from the project configuration, form
        a valid PT file name that can be used for a number of operations.'''

        # Assumed that this is for a ParaTExt USFM file, there should be
        # a nameFormID setting. If not, try updating the manager. If there
        # still is not a nameFormID, die in a very spectacular way.
        if not self.projConfig['Managers']['usfm_Text']['nameFormID'] :
            self.project.managers['usfm_Text'].updateManagerSettings(gid)

        # Hopefully all is well now
        nameFormID  = self.projConfig['Managers']['usfm_Text']['nameFormID']
        postPart    = self.projConfig['Managers']['usfm_Text']['postPart']
        prePart     = self.projConfig['Managers']['usfm_Text']['prePart']

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


    def formGenericName (self, cid) :
        '''Figure out the best way to form a valid file name given the
        source is not coming from a PT project. In the end, this is almost
        impossible to do because of all the different possibilities. We
        will just try to make our best guess. A better way will be needed.'''

        postPart = self.projConfig['Managers']['usfm_Text']['postPart']
        if postPart == '' :
            postPart = self.cType

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


    def findSsfFile (self) :
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
        parentFolder = self.getGroupSourcePath()
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


    def getPTSettings (self) :
        '''Return the data into a dictionary for the system to use.'''

#        import pdb; pdb.set_trace()

        # Return the dictionary
        if os.path.isdir(self.sourcePath) :
            ssfFile = self.findSsfFile()
            if ssfFile :
                if os.path.isfile(ssfFile) :
                    return self.tools.xmlFileToDict(ssfFile)


    def getDefaultFont (self, macPackConfig) :
        '''Return the default font for this project unless it is not a PT
        project, then return None. This gets set in the macPackConfig but
        it is hard to load that in this module so we'll pass it in.'''

        ptDefaultFont = None
        if macPackConfig['FontSettings'].has_key('ptDefaultFont') :
            ptDefaultFont = macPackConfig['FontSettings']['ptDefaultFont']
        # Now check to see if anything is really there
        if not ptDefaultFont :
            ptSet = self.getPTSettings()
            if ptSet :
                ptDefaultFont = ptSet['ScriptureText']['DefaultFont']
                macPackConfig['FontSettings']['ptDefaultFont'] = ptDefaultFont
                self.tools.writeConfFile(macPackConfig)

        return ptDefaultFont


    def getSourceEditor (self) :
        '''Return the sourceEditor if it is set. If not try to
        figure out what it should be and set it to that. Unless
        we find we are in a PT project, we'll call it generic.'''

#        import pdb; pdb.set_trace()

        se = 'generic'
        # FIXME: This may need expanding as more use cases arrise
        if self.projConfig['CompTypes'][self.Ctype].has_key('sourceEditor') \
            and self.projConfig['CompTypes'][self.Ctype]['sourceEditor'] != '' \
            and self.projConfig['CompTypes'][self.Ctype]['sourceEditor'] != 'None' :
            se = self.projConfig['CompTypes'][self.Ctype]['sourceEditor']
        else :
            if self.findSsfFile() :
                se = 'paratext'
                self.projConfig['CompTypes'][self.Ctype]['sourceEditor'] = se
                self.tools.writeConfFile(self.projConfig)

        return se


    def getGroupSourcePath (self) :
        '''Get the source path for a specified group.'''

#        import pdb; pdb.set_trace()

        try :
            return self.userConfig['Projects'][self.pid][self.csid + '_sourcePath']
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.tools.terminal('No source path found for: [' + str(e) + ']')
            self.tools.terminal('Please add a source path for this component type.')
            self.tools.dieNow()


    def usfmCidInfo (self) :
        '''Return a dictionary of all valid information about USFMs used in PT. Note
        that a couple special non-standard IDs have been added at the top of the list.'''

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
################### ParaTExt Illustration Handling Functions ##################
###############################################################################
####################### Error Code Block Series = 0600 ########################
###############################################################################

    def collectEndNotes (self, cid, endNoteConts) :
        '''Collect the end notes from a cid.'''

# FIXME: Output the endnotes to a separate file in the component folder for future processing

#        print endNoteConts.group(1)

        pass


    def logFigure (self, gid, cid, figConts) :
        '''Log the figure data in the illustration.conf. If nothing is returned, the
        existing \fig markers with their contents will be removed. That is the default
        behavior.'''

        # Just in case this section isn't there
        self.tools.buildConfSection(self.illustrationConfig, gid)

        # Description of figKeys (in order found in \fig)
            # description = A brief description of what the illustration is about
            # file = The file name of the illustration (only the file name)
            # caption = The caption that will be used with the illustration (if turned on)
            # width = The width or span the illustration will have (span/col)
            # location = Location information that could be printed in the caption reference
            # copyright = Copyright information for the illustration
            # reference = The book ID (upper-case) plus the chapter and verse (eg. MAT 8:23)

        # We want the figConts to be a list but it comes in as a re group
        figList = figConts.group(1).split('|')

        figKeys = ['description', 'fileName', 'width', 'location', 'copyright', 'caption', 'reference']
        figDict = {}
        # FIXME: If this is for a map and no layout information has been added
        # to the project yet, the cvSep look up will fail, get around with a try
        try :
            cvSep = self.layoutConfig['Illustrations']['chapterVerseSeperator']
        except :
            cvSep = ':'

        # Add all the figure info to the dictionary
        c = 0
        for value in figList :
            figDict[figKeys[c]] = value
            c +=1

        # Add additional information, get rid of stuff we don't need
        figDict['illustrationID'] = figDict['fileName'].split('.')[0]
        figDict['useThisIllustration'] = True
        figDict['useThisCaption'] = True
        figDict['useThisCaptionRef'] = True
        figDict['bid'] = cid
        c = re.search(ur'([0-9]+)[.:][0-9]+', figDict['reference'].upper())
        if c is None :
            figDict['chapter'] = 0  # Or however you want to handle "pattern not found"
        else:
            figDict['chapter'] = c.group(1)

        v = re.search(ur'[0-9]+[.:]([0-9]+)', figDict['reference'].upper())
        if v is None :
            figDict['verse'] = 0  # Or however you want to handle "pattern not found"
        else:
            figDict['verse'] = v.group(1)

        # If this is an update, we need to keep the original settings in case the
        # default settings have been modified for this project.
        # Illustration Scale
        if self.illustrationConfig[gid].has_key(figDict['illustrationID']) :
            figDict['scale'] = self.illustrationConfig[gid][figDict['illustrationID']]['scale']
        else :
            figDict['scale'] = '1.0'
        # Illustration Position
        if self.illustrationConfig[gid].has_key(figDict['illustrationID']) :
            figDict['position'] = self.illustrationConfig[gid][figDict['illustrationID']]['position']
        else :
            if figDict['width'] == 'col' :
                figDict['position'] = 'tl'
            else :
                figDict['position'] = 't'
        # Illustration Location
        if self.illustrationConfig[gid].has_key(figDict['illustrationID']) :
            figDict['location'] = self.illustrationConfig[gid][figDict['illustrationID']]['location']
        else :
            if not figDict['location'] :
                figDict['location'] = figDict['chapter'] + cvSep + figDict['verse']
        # Now make (update) the actual illustration section
        if not self.illustrationConfig.has_key(gid) :
            self.tools.buildConfSection(self.illustrationConfig, gid)
        # Put the dictionary info into the illustration conf file
        if not self.illustrationConfig[gid].has_key(figDict['illustrationID']) :
            self.tools.buildConfSection(self.illustrationConfig[gid], figDict['illustrationID'])
        for k in figDict.keys() :
            self.illustrationConfig[gid][figDict['illustrationID']][k] = figDict[k]

        # Write out the conf file to preserve the data found
        self.tools.writeConfFile(self.illustrationConfig)

        # Just incase we need to keep the fig markers intact this will
        # allow for that. However, default behavior is to strip them
        # because usfmTex does not handle \fig markers. By returning
        # them here, they will not be removed from the working text.
        # FIXME: One issue here is that is is basicaly hard-wired for
        # usfm to be the only cType. This breaks if you are working with
        # something else. To get around it we will use a try statement
        try :
            if self.tools.str2bool(self.projConfig['Managers'][self.cType + '_Illustration']['preserveUsfmFigData']) :
                return '\\fig ' + figConts.group(1) + '\\fig*'
        except :
            return None


###############################################################################
########################### ParaTExt Style Functions ##########################
###############################################################################
####################### Error Code Block Series = 0800 ########################
###############################################################################


#    def usfmStyleFileIsValid (self, path) :
#        '''Use the USFM parser to validate a style file. This is meant to
#        be just a simple test so only return True or False.'''

#        try :
#            stylesheet = usfm.default_stylesheet.copy()
#            stylesheet_extra = usfm.style.parse(open(os.path.expanduser(path),'r'), usfm.style.level.Content)
#            return True
#        except Exception as e :
#            return False


#    def removeUsfmStyFile (self, sType, force) :
#        '''This would be useful for a style reset. Remove a style setting
#        from the config for a component type and if force is used, remove
#        the file from the project as well.'''

#        sType = sType.lower()

#        # Make sure there is something to do
#        if sType == 'main' :
#            oldStyle = self.project.projConfig['Managers'][self.cType + '_Style']['mainStyleFile']
#        elif sType == 'custom' :
#            oldStyle = self.project.projConfig['Managers'][self.cType + '_Style']['customStyleFile']

#        if not oldStyle :
#            self.log.writeToLog('STYL-100', [self.cType])
#            return
#        else :
#            if sType == 'main' :
#                self.project.projConfig['Managers'][self.cType + '_Style']['mainStyleFile'] = ''
#                self.mainStyleFile = ''
#            elif sType == 'custom' :
#                self.project.projConfig['Managers'][self.cType + '_Style']['customStyleFile'] = ''
#                self.customStyleFile = ''

#            self.tools.writeConfFile(self.project.projConfig)

#            if force :
#                target = os.path.join(self.project.local.projStylesFolder, oldStyle)
#                if os.path.isfile(target) :
#                    os.remove(target)

#                self.log.writeToLog('STYL-110', [self.tools.fName(oldStyle),self.cType])
#            else :
#                self.log.writeToLog('STYL-120', [self.tools.fName(oldStyle),self.cType])

#            return True


#    def addExsitingUsfmStyFile (self, sFile, sType, force) :
#        '''Add a specific style file that is on the local system.'''

#        sFile = self.tools.resolvePath(sFile)
#        target = os.path.join(self.project.local.projStylesFolder, self.tools.fName(sFile))

#        if not force and os.path.isfile(target) :
#            self.log.writeToLog('STYL-030', [self.tools.fName(sFile)])
#            return False
#        elif os.path.isfile(sFile) :
#            # It's there? Good, we're done!
#            # If this is not an Rapuma custom style file we will validate it
#            if sType.lower() == 'main' :
#                if self.usfmStyleFileIsValid(sFile) :
#                    shutil.copy(sFile, target)
#                    self.log.writeToLog('STYL-060', [self.tools.fName(sFile)])
#                    return True
#                else :
#                    # We die if it does not validate
#                    self.log.writeToLog('STYL-070', [self.tools.fName(sFile)])
#            else :
#                # Assuming a custom style file we can grab most anything
#                # without validating it
#                shutil.copy(sFile, target)
#                self.log.writeToLog('STYL-065', [self.tools.fName(sFile)])
#                return True
#        else :
#            # Not finding the file may not be the end of the world 
#            self.log.writeToLog('STYL-020', [self.tools.fName(sFile)])
#            return False


#    def addPtUsfmStyFile (self) :
#        '''Install a PT project style file. Merg in any custom
#        project styles too.'''

#        # First pick up our PT settings
#        ptConf = self.pt_tools.getPTSettings()
#        if not ptConf :
#            return False

#        # If nothing is set, give it a default to start off
#        if not self.mainStyleFile :
#            self.mainStyleFile = 'usfm.sty'
#        # Now, override default styleFile name if we found something in the PT conf
#        if ptConf['ScriptureText']['StyleSheet'] :
#            self.mainStyleFile = ptConf['ScriptureText']['StyleSheet']

#        # Set the target destination
#        target = os.path.join(self.project.local.projStylesFolder, self.mainStyleFile)
#        # As this is call is for a PT based project, it is certain the style
#        # file should be found in the source or parent folder. If that
#        # exact file is not found in either place, a substitute will be
#        # copied in from Rapuma and given the designated name.
#        sourceStyle             = os.path.join(self.sourcePath, self.mainStyleFile)
#        parent                  = os.path.dirname(self.sourcePath)
#        # If there is a "gather" folder, assume the style file is there
#        if os.path.isdir(os.path.join(self.sourcePath, 'gather')) :
#            ptProjStyle             = os.path.join(self.sourcePath, 'gather', self.mainStyleFile)
#        else :
#            ptProjStyle             = os.path.join(self.sourcePath, self.mainStyleFile)
#        ptStyle                     = os.path.join(parent, self.mainStyleFile)
#        searchOrder                 = [sourceStyle, ptProjStyle, ptStyle]
#        # We will start by searching in order from the inside out and stop
#        # as soon as we find one.
#        for sFile in searchOrder :
#            if os.path.isfile(sFile) :
#                if self.usfmStyleFileIsValid(sFile) :
#                    if not shutil.copy(sFile, target) :
#                        return self.tools.fName(target)
#                else :
#                    self.log.writeToLog('STYL-075', [sFile,self.cType])
#            else : 
#                self.log.writeToLog('STYL-090', [sFile])



