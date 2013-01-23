#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project tasks.

# History:
# 20111222 - djd - Started with intial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os

# Load the local classes
from rapuma.core.tools import *
from rapuma.core.pt_tools import *
from rapuma.component.component import Component


###############################################################################
################################## Begin Class ################################
###############################################################################

# As we load the module we will bring in all the common information about all the
# components this type will handle.



class Usfm (Component) :
    '''This class contains information about a type of component 
    used in a type of project.'''

    # Shared values
    xmlConfFile     = 'usfm.xml'

    def __init__(self, project, cfg) :
        super(Usfm, self).__init__(project, cfg)

        # Set values for this manager
        self.project                = project
        self.cName                  = ''
        self.cfg                    = cfg
        self.cType                  = 'usfm'
        self.Ctype                  = self.cType.capitalize()
        self.rapumaXmlCompConfig    = os.path.join(self.project.local.rapumaConfigFolder, self.xmlConfFile)
        self.sourcePath             = getSourcePath(self.project.userConfig, self.project.projectIDCode, self.cType)
        self.renderer               = self.project.projConfig['CompTypes'][self.Ctype]['renderer']

        # Get the comp settings
#        self.project.addComponentType(self.Ctype)
        self.compSettings = self.project.projConfig['CompTypes'][self.Ctype]

        # Get persistant values from the config if there are any
        newSectionSettings = getPersistantSettings(self.project.projConfig['CompTypes'][self.Ctype], self.rapumaXmlCompConfig)
        if newSectionSettings != self.project.projConfig['CompTypes'][self.Ctype] :
            self.project.projConfig['CompTypes'][self.Ctype] = newSectionSettings

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)

        self.usfmManagers = ['text', 'style', 'font', 'layout', 'hyphenation', 'illustration', self.renderer]
#        self.usfmManagers = ['text', 'style', 'font', 'layout', 'illustration', self.renderer]

        # Init the general managers
        for mType in self.usfmManagers :
            self.project.createManager(self.cType, mType)

        # Pick up some init settings that come after the managers have been installed
        self.macroPackage           = self.project.projConfig['Managers'][self.cType + '_' + self.renderer.capitalize()]['macroPackage']

        # Check if there is a font installed
        self.project.createManager(self.cType, 'font')
        if not self.project.managers[self.cType + '_Font'].varifyFont() :
            # If a PT project, use that font, otherwise, install default
            if self.sourceEditor.lower() == 'paratext' :
                font = self.project.projConfig['Managers'][self.cType + '_Font']['ptDefaultFont']
            else :
                font = 'DefaultFont'

            self.project.managers[self.cType + '_Font'].installFont(font)

        # To better facilitate rendering that might be happening on this run, we
        # will update source file names and other settings used in the usfm_Text
        # manager (It might be better to do this elsewhere, but where?)
        self.project.managers[self.cType + '_Text'].updateManagerSettings()


###############################################################################
############################ Functions Begin Here #############################
###############################################################################

    def getCidPath (self, cid) :
        '''Return the full path of the cName working text file. This assumes
        the cName is valid.'''

        cName = self.getRapumaCName(cid)
        cType = self.project.projConfig['Components'][cName]['type']
        return os.path.join(self.project.local.projComponentsFolder, cName, cid + '.' + cType)


    def getCidAdjPath (self, cid) :
        '''Return the full path of the cName working text adjustments file. 
        This assumes the cName is valid.'''

        cName = self.getRapumaCName(cid)
        cType = self.project.projConfig['Components'][cName]['type']
        return os.path.join(self.project.local.projComponentsFolder, cName, cid + '.adj')


    def getCidPiclistPath (self, cid) :
        '''Return the full path of the cName working text illustrations file. 
        This assumes the cName is valid.'''

        cName = self.getRapumaCName(cid)
        cType = self.project.projConfig['Components'][cName]['type']
        return os.path.join(self.project.local.projComponentsFolder, cName, cid + '.piclist')


    def render(self, force) :
        '''Does USFM specific rendering of a USFM component'''
            # useful variables: self.project, self.cfg

        self.cidList = self.cfg['cidList']

#        import pdb; pdb.set_trace()

        # Preprocess all subcomponents (one or more)
        # Stop if it breaks at any point
        for cid in self.cidList :
            cName = self.getRapumaCName(cid)
            if not self.preProcessComponent(cName) :
                return False

        # With everything in place we can render the component and we pass-through
        # the force (render/view) command so the renderer will do the right thing.
        self.project.managers['usfm_' + self.renderer.capitalize()].run(force)

        return True


    def preProcessComponent (self, cName) :
        '''This will prepare a component for rendering by checking for
        and/or creating any dependents it needs to render properly.'''

        # Get some relevant settings
        useWatermark            = str2bool(self.project.managers[self.cType + '_Layout'].layoutConfig['PageLayout']['useWatermark'])
        useLines                = str2bool(self.project.managers[self.cType + '_Layout'].layoutConfig['PageLayout']['useLines'])
        usePageBorder           = str2bool(self.project.managers[self.cType + '_Layout'].layoutConfig['PageLayout']['usePageBorder'])
        useIllustrations        = str2bool(self.project.managers[self.cType + '_Layout'].layoutConfig['Illustrations']['useIllustrations'])
        useManualAdjustments    = str2bool(self.project.projConfig['CompTypes'][self.Ctype]['useManualAdjustments'])

        # First see if this is a valid component. This is a little
        # redundant as this is done in project.py as well. It should
        # be caught there first but just in case we'll do it here too.
        if not self.hasCNameEntry(cName) :
            self.project.log.writeToLog('COMP-010', [cName])
            return False
        else :
            # See if the working text is present for each subcomponent in the
            # component and try to install it if it is not
            for cid in self.project.projConfig['Components'][cName]['cidList'] :
                cidCName = self.getRapumaCName(cid)
                cType = self.project.projConfig['Components'][cidCName]['type']
                cidUsfm = self.getCidPath(cid)
                # Build a component object for this cid (cidCName)
                self.project.buildComponentObject(self.cType, cidCName)

                if not os.path.isfile(cidUsfm) :
                    self.project.managers[self.cType + '_Text'].installUsfmWorkingText(cName, cid)

                # Add/manage the dependent files for this cid
                if self.macroPackage == 'usfmTex' :
                    # Component adjustment file
                    cidAdj = self.getCidAdjPath(cid)
                    if useManualAdjustments :
                        if os.path.isfile(cidAdj + '.bak') :
                            os.rename(cidAdj + '.bak', cidAdj)
                        else :
                            self.createAjustmentFile(cid)
                    else :
                        # If we are not using manual adjustments check to see if there is a
                        # adjustment file and if there is, rename it so usfmTex (if we are
                        # using it) will not pick it up
                        if os.path.isfile(cidAdj) :
                            os.rename(cidAdj, cidAdj + '.bak')
                    # Component piclist file
                    self.project.buildComponentObject(self.cType, cidCName)
                    cidPiclist = self.project.components[cidCName].getCidPiclistPath(cid)
                    if useIllustrations :
                        # First check if we have the illustrations we think we need
                        # and get them if we do not.
                        self.project.managers[cType + '_Illustration'].getPics(cid)

                        # If that all went well, create the piclist file if needed
                        if os.path.isfile(cidPiclist + '.bak') :
                            os.rename(cidPiclist + '.bak', cidPiclist)
                        else :
                            self.project.managers[cType + '_Illustration'].createPiclistFile(cName, cid)
                    else :
                        # If we are not using illustrations check to see if there is a
                        # piclist file and if there is, rename it so usfmTex (if we are
                        # using it) will not pick it up
                        if os.path.isfile(cidPiclist) :
                            os.rename(cidPiclist, cidPiclist + '.bak')
                else :
                    self.project.log.writeToLog('COMP-220', [self.macroPackage])

            # Run any hyphenation or word break routines


            # Be sure there is a watermark file listed in the conf and
            # installed if watermark is turned on (True). Fallback on the
            # the default if needed.
            if useWatermark :
                if not self.project.managers[cType + '_Illustration'].hasBackgroundFile('watermark') :
                    self.project.managers[cType + '_Illustration'].installBackgroundFile('watermark', 'watermark_default.pdf', self.project.local.rapumaIllustrationsFolder, True)

            # Same for lines background file used for composition
            if useLines :
                if not self.project.managers[cType + '_Illustration'].hasBackgroundFile('lines') :
                    self.project.managers[cType + '_Illustration'].installBackgroundFile('lines', 'lines_default.pdf', self.project.local.rapumaIllustrationsFolder, True)

            # Any more stuff to run?

        return True


    def createAjustmentFile (self, cid) :
        '''Create a manual adjustment file for this cid.'''

        # Check for a .adj file
        adjFile = self.getCidAdjPath(cid)
        if not os.path.isfile(adjFile) :
            with codecs.open(adjFile, "w", encoding='utf_8') as writeObject :
                writeObject.write('% Text adjustments file for: ' + cid + '\n\n')
                writeObject.write('%' + cid.upper() + ' 1.1 +1 \n')


###############################################################################
########################## USFM Component Functions ###########################
###############################################################################

    def getComponentType (self, cName) :
        '''Return the cType for a component.'''

        try :
            cType = self.project.projConfig['Components'][cName]['type']
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.log.writeToLog('COMP-200', ['Key not found ' + str(e)])
            dieNow()

        return cType


    def isCompleteComponent (self, cName) :
        '''A two-part test to see if a component has a config entry and a file.'''

        if self.hasCNameEntry(cName) :
            for cid in self.getSubcomponentList(cName) :
                cidName = self.getRapumaCName(cid)
                cType = self.getComponentType(cidName)
                # For subcomponents look for working text
                if not self.hasCidFile(cidName, cid, cType) :
                    return False
        else :
            return False

        return True


    def hasCNameEntry (self, cName) :
        '''Check for a config component entry.'''

        buildConfSection(self.project.projConfig, 'Components')

        if testForSetting(self.project.projConfig['Components'], cName) :
            return True


    def hasUsfmCidInfo (self, cid) :
        '''Return True if this cid is in the PT USFM cid info dictionary.'''

        if cid in self.usfmCidInfo().keys() :
            return True


    def hasCidFile (self, cName, cid, cType) :
        '''Return True or False depending on if a working file exists 
        for a given cName.'''

        return os.path.isfile(os.path.join(self.project.local.projComponentsFolder, cName, cid + '.' + cType))


    def getUsfmCidInfo (self, cid) :
        '''Return a list of info about a specific cid used in the PT context.'''

        try :
            return self.usfmCidInfo()[cid]
        except :
            return False


    def getUsfmName (self, cid) :
        '''Look up and return the actual name for a valid cid.'''

        if self.hasUsfmCidInfo(cid) :
            return self.getUsfmCidInfo(cid)[0]


    def getRapumaCName (self, cid) :
        '''Look up and return the Rapuma component name for a valid cid.
        But if the cid happens to be a cName already, that will be returned.'''

        if self.hasUsfmCidInfo(cid) :
            return self.getUsfmCidInfo(cid)[1]
        else :
            # FIXME: This seems a little weak. What if the cid is an invalid cName?
            return cid


    def getUsfmCid (self, cName) :
        '''Find the cid by using the cName to look.'''

        info = self.usfmCidInfo()
        for k, v in info.iteritems() :
            if info[k][1] == cName :
                return k


    def getSubcomponentList (self, cName) :
        '''Return the list of subcomponents for a cName.'''

        try :
            cidList = self.project.projConfig['Components'][cName]['cidList']
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.log.writeToLog('COMP-200', ['Key not found ' + str(e)])
            dieNow()

        return cidList


    def usfmCidInfo (self) :
        '''Return a dictionary of all valid information about USFMs used in PT.'''

    #            ID     Comp Name                               Comp ID                         PT ID
        return {
                'gen' : ['Genesis',                             'genesis',                      '01'],
                'exo' : ['Exodus',                              'exodus',                       '02'], 
                'lev' : ['Leviticus',                           'leviticus',                    '03'], 
                'num' : ['Numbers',                             'numbers',                      '04'], 
                'deu' : ['Deuteronomy',                         'deuteronomy',                  '05'], 
                'jos' : ['Joshua',                              'joshua',                       '06'], 
                'jdg' : ['Judges',                              'judges',                       '07'], 
                'rut' : ['Ruth',                                'ruth',                         '08'], 
                '1sa' : ['1 Samuel',                            '1_samuel',                     '09'], 
                '2sa' : ['2 Samuel',                            '2_samuel',                     '10'], 
                '1ki' : ['1 Kings',                             '1_kings',                      '11'], 
                '2ki' : ['2 Kings',                             '2_kings',                      '12'], 
                '1ch' : ['1 Chronicles',                        '1_chronicles',                 '13'], 
                '2ch' : ['2 Chronicles',                        '2_chronicles',                 '14'], 
                'ezr' : ['Ezra',                                'ezra',                         '15'], 
                'neh' : ['Nehemiah',                            'nehemiah',                     '16'], 
                'est' : ['Esther',                              'esther',                       '17'], 
                'job' : ['Job',                                 'job',                          '18'], 
                'psa' : ['Psalms',                              'psalms',                       '19'], 
                'pro' : ['Proverbs',                            'proverbs',                     '20'], 
                'ecc' : ['Ecclesiastes',                        'ecclesiastes',                 '21'], 
                'sng' : ['Song of Songs',                       'song_of_songs',                '22'], 
                'isa' : ['Isaiah',                              'isaiah',                       '23'], 
                'jer' : ['Jeremiah',                            'jeremiah',                     '24'], 
                'lam' : ['Lamentations',                        'lamentations',                 '25'], 
                'ezk' : ['Ezekiel',                             'ezekiel',                      '26'], 
                'dan' : ['Daniel',                              'daniel',                       '27'], 
                'hos' : ['Hosea',                               'hosea',                        '28'], 
                'jol' : ['Joel',                                'joel',                         '29'], 
                'amo' : ['Amos',                                'amos',                         '30'], 
                'oba' : ['Obadiah',                             'obadiah',                      '31'], 
                'jon' : ['Jonah',                               'jonah',                        '32'], 
                'mic' : ['Micah',                               'micah',                        '33'], 
                'nam' : ['Nahum',                               'nahum',                        '34'], 
                'hab' : ['Habakkuk',                            'habakkuk',                     '35'], 
                'zep' : ['Zephaniah',                           'zephaniah',                    '36'], 
                'hag' : ['Haggai',                              'haggai',                       '37'], 
                'zec' : ['Zechariah',                           'zechariah',                    '38'], 
                'mal' : ['Malachi',                             'malachi',                      '39'],
                'mat' : ['Matthew',                             'matthew',                      '41'], 
                'mrk' : ['Mark',                                'mark',                         '42'], 
                'luk' : ['Luke',                                'luke',                         '43'], 
                'jhn' : ['John',                                'john',                         '44'], 
                'act' : ['Acts',                                'acts',                         '45'], 
                'rom' : ['Romans',                              'romans',                       '46'], 
                '1co' : ['1 Corinthians',                       '1_corinthians',                '47'], 
                '2co' : ['2 Corinthians',                       '2_corinthians',                '48'], 
                'gal' : ['Galatians',                           'galatians',                    '49'], 
                'eph' : ['Ephesians',                           'ephesians',                    '50'], 
                'php' : ['Philippians',                         'philippians',                  '51'], 
                'col' : ['Colossians',                          'colossians',                   '52'], 
                '1th' : ['1 Thessalonians',                     '1_thessalonians',              '53'], 
                '2th' : ['2 Thessalonians',                     '2_thessalonians',              '54'], 
                '1ti' : ['1 Timothy',                           '1_timothy',                    '55'], 
                '2ti' : ['2 Timothy',                           '2_timothy',                    '56'], 
                'tit' : ['Titus',                               'titus',                        '57'], 
                'phm' : ['Philemon',                            'philemon',                     '58'], 
                'heb' : ['Hebrews',                             'hebrews',                      '59'], 
                'jas' : ['James',                               'james',                        '60'], 
                '1pe' : ['1 Peter',                             '1_peter',                      '61'], 
                '2pe' : ['2 Peter',                             '2_peter',                      '62'], 
                '1jn' : ['1 John',                              '1_john',                       '63'], 
                '2jn' : ['2 John',                              '2_john',                       '64'], 
                '3jn' : ['3 John',                              '3_john',                       '65'], 
                'jud' : ['Jude',                                'jude',                         '66'], 
                'rev' : ['Revelation',                          'revelation',                   '67'], 
                'tob' : ['Tobit',                               'tobit',                        '68'], 
                'jdt' : ['Judith',                              'judith',                       '69'], 
                'esg' : ['Esther',                              'esther',                       '70'], 
                'wis' : ['Wisdom of Solomon',                   'wisdom_of_solomon',            '71'], 
                'sir' : ['Sirach',                              'sirach',                       '72'], 
                'bar' : ['Baruch',                              'baruch',                       '73'], 
                'lje' : ['Letter of Jeremiah',                  'letter_of_jeremiah',           '74'], 
                's3y' : ['Song of the Three Children',          'song_3_children',              '75'], 
                'sus' : ['Susanna',                             'susanna',                      '76'], 
                'bel' : ['Bel and the Dragon',                  'bel_dragon',                   '77'], 
                '1ma' : ['1 Maccabees',                         '1_maccabees',                  '78'], 
                '2ma' : ['2 Maccabees',                         '2_maccabees',                  '79'], 
                '3ma' : ['3 Maccabees',                         '3_maccabees',                  '80'], 
                '4ma' : ['4 Maccabees',                         '4_maccabees',                  '81'], 
                '1es' : ['1 Esdras',                            '1_esdras',                     '82'], 
                '2es' : ['2 Esdras',                            '2_esdras',                     '83'], 
                'man' : ['Prayer of Manasses',                  'prayer_of_manasses',           '84'], 
                'ps2' : ['Psalms 151',                          'psalms_151',                   '85'], 
                'oda' : ['Odae',                                'odae',                         '86'], 
                'pss' : ['Psalms of Solomon',                   'psalms_of_solomon',            '87'], 
                'jsa' : ['Joshua A',                            'joshua_a',                     '88'], 
                'jdb' : ['Joshua B',                            'joshua_b',                     '89'], 
                'tbs' : ['Tobit S',                             'tobit_s',                      '90'], 
                'sst' : ['Susannah (Theodotion)',               'susannah_t',                   '91'], 
                'dnt' : ['Daniel (Theodotion)',                 'daniel_t',                     '92'], 
                'blt' : ['Bel and the Dragon (Theodotion)',     'bel_dragon_t',                 '93'], 
                'frt' : ['Front Matter',                        'front_matter',                 'A0'], 
                'int' : ['Introductions',                       'introductions',                'A7'], 
                'bak' : ['Back Matter',                         'back_matter',                  'A1'], 
                'cnc' : ['Concordance',                         'concordance',                  'A8'], 
                'glo' : ['Glossary',                            'glossary',                     'A9'], 
                'tdx' : ['Topical Index',                       'topical_index',                'B0'], 
                'ndx' : ['Names Index',                         'names_index',                  'B1'], 
                'xxa' : ['Extra A',                             'extra_a',                      '94'], 
                'xxb' : ['Extra B',                             'extra_b',                      '95'], 
                'xxc' : ['Extra C',                             'extra_c',                      '96'], 
                'xxd' : ['Extra D',                             'extra_d',                      '97'],
                'xxe' : ['Extra E',                             'extra_e',                      '98'], 
                'xxf' : ['Extra F',                             'extra_f',                      '99'], 
                'xxg' : ['Extra G',                             'extra_g',                      '100'], 
                'oth' : ['Other',                               'other',                        'A2'], 
                'eza' : ['Apocalypse of Ezra',                  'apocalypse_of_ezra',           'A4'], 
                '5ez' : ['5 Ezra',                              '5_ezra_lp',                    'A5'], 
                '6ez' : ['6 Ezra (Latin Epilogue)',             '6_ezra_lp',                    'A6'], 
                'dag' : ['Daniel Greek',                        'daniel_greek',                 'B2'], 
                'ps3' : ['Psalms 152-155',                      'psalms_152-155',               'B3'], 
                '2ba' : ['2 Baruch (Apocalypse)',               '2_baruch_apocalypse',          'B4'], 
                'lba' : ['Letter of Baruch',                    'letter_of_baruch',             'B5'], 
                'jub' : ['Jubilees',                            'jubilees',                     'B6'], 
                'eno' : ['Enoch',                               'enoch',                        'B7'], 
                '1mq' : ['1 Meqabyan',                          '1_meqabyan',                   'B8'], 
                '2mq' : ['2 Meqabyan',                          '2_meqabyan',                   'B9'], 
                '3mq' : ['3 Meqabyan',                          '3_meqabyan',                   'C0'], 
                'rep' : ['Reproof (Proverbs 25-31)',            'reproof_proverbs_25-31',       'C1'], 
                '4ba' : ['4 Baruch (Rest of Baruch)',           '4_baruch',                     'C2'], 
                'lao' : ['Laodiceans',                          'laodiceans',                   'C3'] 
               }






