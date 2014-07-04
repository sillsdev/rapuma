#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class handles USFM component type tasks for book projects.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, codecs, re
from configobj import ConfigObj, Section
#from functools import partial

# Load the local classes
from rapuma.core.tools                  import Tools
from rapuma.group.group                 import Group
from rapuma.project.proj_font           import ProjFont
from rapuma.project.proj_illustration   import ProjIllustration
from rapuma.project.proj_config         import Config
from rapuma.project.proj_background     import ProjBackground


###############################################################################
################################## Begin Class ################################
###############################################################################

# As we load the module we will bring in all the common information about all the
# components this type will handle.

class Usfm (Group) :
    '''This class contains information about a type of component 
    used in a type of project.'''

    # Shared values
    xmlConfFile     = 'usfm.xml'

    def __init__(self, project, cfg) :
        super(Usfm, self).__init__(project, cfg)

        # Set values for this manager
        self.pid                    = project.projectIDCode
        self.gid                    = project.gid
        self.cType                  = 'usfm'
        self.Ctype                  = self.cType.capitalize()
        self.project                = project
        self.local                  = project.local
        self.tools                  = Tools()
        self.proj_font              = ProjFont(self.pid, self.gid)
        self.proj_illustration      = ProjIllustration(self.pid, self.gid)
        self.proj_config            = Config(self.pid, self.gid)
        self.proj_config.getProjectConfig()
        self.proj_config.getAdjustmentConfig()
        self.projectConfig          = self.proj_config.projectConfig
        self.adjustmentConfig       = self.proj_config.adjustmentConfig
        self.log                    = project.log
        self.cfg                    = cfg
        self.mType                  = project.projectMediaIDCode
        self.renderer               = project.projectConfig['CompTypes'][self.Ctype]['renderer']
        self.sourceEditor           = project.projectConfig['CompTypes'][self.Ctype]['sourceEditor']
        self.macPack                = project.projectConfig['CompTypes'][self.Ctype]['macroPackage']
        # Get the comp settings
        self.compSettings           = project.projectConfig['CompTypes'][self.Ctype]
        # Get macro package settings
        self.proj_config.getMacPackConfig(self.macPack)
        self.macPackConfig          = self.proj_config.macPackConfig
        # Build a tuple of managers this component type needs to use
        self.usfmManagers = ('text', self.renderer)

        # Init the general managers
        for mType in self.usfmManagers :
            self.project.createManager(mType)

        # Create the internal ref names we use in this module
        self.text                   = self.project.managers[self.cType + '_Text']
        # File names

        # Folder paths
        self.projScriptFolder       = self.local.projScriptFolder
        self.projComponentFolder    = self.local.projComponentFolder
        self.gidFolder              = os.path.join(self.projComponentFolder, self.gid)
        # File names with folder paths
        self.rapumaXmlCompConfig    = os.path.join(self.project.local.rapumaConfigFolder, self.xmlConfFile)

        # Get persistant values from the config if there are any
        newSectionSettings = self.tools.getPersistantSettings(self.projectConfig['CompTypes'][self.Ctype], self.rapumaXmlCompConfig)
        if newSectionSettings != self.projectConfig['CompTypes'][self.Ctype] :
            self.projectConfig['CompTypes'][self.Ctype] = newSectionSettings
        # Set them here
        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)

        # Check if there is a primary font installed
        if not self.proj_font.varifyFont() :
            self.proj_font.installFont('DefaultFont')

        # Module Error Codes
        self.errorCodes     = {
            'USFM-000' : ['MSG', 'Messages for the USFM module.'],
            'USFM-005' : ['MSG', 'Unassigned error message ID.'],
            'USFM-010' : ['ERR', 'Could not process character pair. This error was found: [<<1>>]. Process could not complete. - usfm.pt_tools.getNWFChars()'],
            'USFM-020' : ['ERR', 'Improper character pair found: [<<1>>].  Process could not complete. - usfm.pt_tools.getNWFChars()'],
            'USFM-025' : ['WRN', 'No non-word-forming characters were found in the PT settings file. - usfm.pt_tools.getNWFChars()'],
            'USFM-040' : ['ERR', 'Hyphenation source file not found: [<<1>>]. Process halted!'],
            'USFM-080' : ['LOG', 'Normalizing Unicode text to the [<<1>>] form.'],
            'USFM-090' : ['ERR', 'USFM file: [<<1>>] did NOT pass the validation test. Because of an encoding conversion, the terminal output is from the file [<<2>>]. Please only edit [<<1>>].'],
            'USFM-095' : ['WRN', 'Validation for USFM file: [<<1>>] was turned off.'],
            'USFM-100' : ['MSG', 'Source file editor [<<1>>] is not recognized by this system. Please double check the name used for the source text editor setting.'],
            'USFM-110' : ['ERR', 'Source file name could not be built because the Name Form ID for [<<1>>] is missing or incorrect. Double check to see which editor created the source text.'],
            'USFM-120' : ['ERR', 'Source file: [<<1>>] not found! Cannot copy to project. Process halting now.'],
            'USFM-130' : ['ERR', 'Failed to complete preprocessing on component [<<1>>]'],
            'USFM-140' : ['MSG', 'Completed installation on [<<1>>] component working text.'],
            'USFM-150' : ['ERR', 'Unable to copy [<<1>>] to [<<2>>] - error in text.'],

            '0010' : ['LOG', 'Created the [<<1>>] master adjustment file.'],
            '0220' : ['ERR', 'Cannot find: [<<1>>] working file, unable to complete preprocessing for rendering.'],
            '0230' : ['LOG', 'Created the [<<1>>] component adjustment file.'],
            '0240' : ['LOG', 'Could not find adjustments section for [<<1>>], created place holder setting.'],
            '0245' : ['LOG', 'Could not find adjustments for [<<1>>]. No ajustment file has been output.'],
            '0255' : ['LOG', 'Illustrations not being used. The piclist file has been removed from the [<<1>>] illustrations folder.'],
            '0260' : ['LOG', 'Piclist file for [<<1>>] has been created.'],
            '0265' : ['ERR', 'Failed to create piclist file for [<<1>>]!'],
        }


###############################################################################
############################ Functions Begin Here #############################
###############################################################################
######################## Error Code Block Series = 0200 #######################
###############################################################################

    def makeFileName(self, cid) :
        '''From what we know, return the full file name.'''

        # FIXME: We default this to "base" but for a diglot implementation
        # this is not going to work because we need to have a second
        # file name. Cross that bridge...

        return cid + '_base'


    def makeFileNameWithExt(self, cid) :
        '''From what we know, return the full file name.'''

        return self.makeFileName(cid) + '.' + self.cType


    def getCidPath (self, cid) :
        '''Return the full path of the cName working text file. This assumes
        the cid is valid.'''

        return os.path.join(self.local.projComponentFolder, cid, self.makeFileNameWithExt(cid))


    def getCidAdjPath (self, cid) :
        '''Return the full path of the cName working text adjustments file. 
        This assumes the cName is valid. Note that all macro packages that have
        a manual adjustment feature must use this naming scheme. The name syntax
        comes from the "mother" macro package which is ptx2pdf.'''

        return os.path.join(self.local.projComponentFolder, cid, self.makeFileNameWithExt(cid) + '.adj')


    def render(self, gid, cidList, pages, override, save) :
        '''Does USFM specific rendering of a USFM component'''

#        import pdb; pdb.set_trace()

        # If the whole group is being rendered, we need to preprocess it
        cids = []
        if not cidList :
            cids = self.projectConfig['Groups'][gid]['cidList']
        else :
            cids = cidList

        # Preprocess all subcomponents (one or more)
        # Stop if it breaks at any point
        for cid in cids :
            if not self.preProcessGroup(gid, [cid]) :
                return False

        # With everything in place we can render the component.
        # Note: We pass the cidList straight through
        self.project.managers['usfm_' + self.renderer.capitalize()].run(gid, cidList, pages, override, save)

        return True


    def preProcessGroup (self, gid, cidList) :
        '''This will prepare a component group for rendering by checking for
        and/or creating any dependents it needs to render properly.'''

#        import pdb; pdb.set_trace()

        # Get some relevant settings
        # FIXME: Note page border has not really been implemented yet.
        # It is different from backgound management
        useIllustrations        = self.tools.str2bool(self.projectConfig['Groups'][gid]['useIllustrations'])
        useManualAdjustments    = self.tools.str2bool(self.projectConfig['Groups'][gid]['useManualAdjustments'])

        # Adjust the page number if necessary
# FIXME: I moved this to xetex module, was this a good idea?
#        self.checkStartPageNumber()

        # See if the working text is present for each subcomponent in the
        # component and try to install it if it is not
        for cid in cidList :
            cType = self.cfg['cType']
            cidUsfm = self.getCidPath(cid)
            # Test for source here and die if it isn't there
            if not os.path.isfile(cidUsfm) :
                self.log.writeToLog(self.errorCodes['0220'], [cidUsfm], 'usfm.preProcessGroup():0220')
            # Add/manage the dependent files for this cid
            if self.macPack == 'usfmTex' or self.macPack == 'ptx2pdf' :
                # Component adjustment file
                cidAdjFile = self.getCidAdjPath(cid)
                if useManualAdjustments :
                    self.createCompAdjustmentFile(cid)
                else :
                    # If no adjustments, remove any exsiting file
                    if os.path.isfile(cidAdjFile) :
                        os.remove(cidAdjFile)
                # Component piclist file
                cidPiclistFile = self.proj_illustration.getCidPiclistFile(cid)
                if useIllustrations :
                    if self.proj_illustration.hasIllustrations(gid, cid) :
                        # Create if not there or if the config has changed
                        if not os.path.isfile(cidPiclistFile) or self.tools.isOlder(cidPiclistFile, self.local.illustrationConfFile) :
                            # First check if we have the illustrations we think we need
                            # and get them if we do not.
                            self.proj_illustration.getPics(gid, cid)
                            # Now make a fresh version of the piclist file
                            if self.proj_illustration.createPiclistFile(gid, cid) :
                                self.log.writeToLog(self.errorCodes['0260'], [cid])
                            else :
                                self.log.writeToLog(self.errorCodes['0265'], [cid])
                        else :
                            for f in [self.local.layoutConfFile, self.local.illustrationConfFile] :
                                if self.tools.isOlder(cidPiclistFile, f) or not os.path.isfile(cidPiclistFile) :
                                    # Remake the piclist file
                                    if self.proj_illustration.createPiclistFile(gid, cid) :
                                        self.log.writeToLog(self.errorCodes['0260'], [cid])
                                    else :
                                        self.log.writeToLog(self.errorCodes['0265'], [cid])
                        # Do a quick check to see if the illustration files for this book
                        # are in the project. If it isn't, the run will be killed
                        self.proj_illustration.getPics(gid, cid)
                    else :
                        # Does not seem to be any illustrations for this cid
                        # clean out any piclist file that might be there
                        if os.path.isfile(cidPiclistFile) :
                            os.remove(cidPiclistFile)
                else :
                    # If we are not using illustrations then any existing piclist file will be removed
                    if os.path.isfile(cidPiclistFile) :
                        os.remove(cidPiclistFile)
                        self.log.writeToLog(self.errorCodes['0255'], [cid])


# FIXME: This error message is all wrong.



            else :
                self.log.writeToLog(self.errorCodes['0220'], [self.macPack], 'usfm.preProcessGroup():0220')

        # Any more stuff to run?

        return True

# FIXME: Moved this to xetex.py as that was the only place it was called from
    #def checkStartPageNumber (self) :
        #'''Adjust page number for the current group. The current logic is
        #if there is no number in the startPageNumber setting, we can put
        #one in there as a suggestion. If there is already one there, the
        #user will be responsible for seeing that it is correct.'''

##        import pdb; pdb.set_trace()

        #try :
            ## Simply try to return anything that is in the field
            #cStrPgNo = self.projectConfig['Groups'][self.gid]['startPageNumber']
            #if cStrPgNo != '' :
                #return cStrPgNo
        #except :
            ## If nothing is there, we'll make a suggestion
            #pGrp = str(self.projectConfig['Groups'][self.gid]['precedingGroup'])
            #if pGrp == 'None' :
                #self.projectConfig['Groups'][self.gid]['startPageNumber'] = 1
                #self.tools.writeConfFile(self.projectConfig)
                #return '1'
            #else :
                ## Calculate the suggested number based on the preceeding group
                #try :
                    #cStrPgNo    = str(self.projectConfig['Groups'][self.gid]['startPageNumber'])
                #except :
                    #cStrPgNo    = 1
                    #self.projectConfig['Groups'][self.gid]['startPageNumber'] = 1
                #try :
                    #pGrpPgs     = int(self.projectConfig['Groups'][pGrp]['totalPages'])
                    #pGrpStrPgNo = int(self.projectConfig['Groups'][pGrp]['startPageNumber'])
                #except :
                    ## FIXME: Maybe this could go out and find out exactly how many pages were in the preceeding group
                    #pGrpPgs     = 1
                    #pGrpStrPgNo = 1
                    #self.projectConfig['Groups'][pGrp]['totalPages'] = 1
                    #self.projectConfig['Groups'][pGrp]['startPageNumber'] = 1
                ## Whether this is right or wrong set it the way it is
                #self.projectConfig['Groups'][self.gid]['startPageNumber'] = (pGrpStrPgNo + pGrpPgs)
                #self.tools.writeConfFile(self.projectConfig)
                #return self.projectConfig['Groups'][pGrp]['startPageNumber']


    def createCompAdjustmentFile (self, cid) :
        '''Create an adjustment file for this cid. If entries exsist in
        the adjustment.conf file.'''

        description = 'Auto-generated text adjustments file for: ' + cid + '\n'

#        import pdb; pdb.set_trace()

        # Check for a master adj conf file
        if os.path.exists(self.local.adjustmentConfFile) :
            adjFile = self.getCidAdjPath(cid)
            # Clean up old file if there is one so we can start fresh
            if os.path.exists(adjFile) :
                os.remove(adjFile)
            # Nothing to do if no gid section is found
            if not self.adjustmentConfig.has_key(self.gid) :
                self.tools.buildConfSection(self.adjustmentConfig, self.gid)
            if not self.adjustmentConfig[self.gid].has_key(cid) :
                self.tools.buildConfSection(self.adjustmentConfig[self.gid], cid)
                self.adjustmentConfig[self.gid][cid]['%1.1'] = '1'
                self.tools.writeConfFile(self.adjustmentConfig)
                self.log.writeToLog(self.errorCodes['0240'], [cid])
                return False
            # Sort through commented adjustment lines ()
            if self.adjustmentConfig[self.gid].has_key(cid) :
                c = False
                for k in self.adjustmentConfig[self.gid][cid].keys() :
                    if not re.search(r'%|#', k) :
                        c = True
                if not c :
                    self.log.writeToLog(self.errorCodes['0245'], [cid])
                    return False
            # If we make it this far, create the new adjustment file
            with codecs.open(adjFile, "w", encoding='utf_8') as writeObject :
                writeObject.write(self.tools.makeFileHeader(adjFile, description, True))
                # Output like this: JAS 1.13 +1
                for k, v in self.adjustmentConfig[self.gid][cid].iteritems() :
                    if re.search(r'%|#', k) :
                        continue
                    adj = v
                    if int(v) > 0 : 
                        adj = '+' + str(v)
                    writeObject.write(cid.upper() + ' ' + k + ' ' + adj + '\n')

                self.log.writeToLog(self.errorCodes['0230'], [self.tools.fName(adjFile)])

            return True


    def createProjAdjustmentConfFile (self) :
        '''Create a project master component adjustment file that group component
        ajustment files will be created automatically from. This will run every 
        time preprocess is run but after the first time it will only add a sections
        for new groups or components.'''

        if not os.path.exists(self.adjustmentConfFile) :
            self.adjustmentConfig = ConfigObj(self.adjustmentConfFile, encoding='utf-8')
            self.adjustmentConfig.filename = self.adjustmentConfFile
            self.updateCompAdjustmentConf()
        return True


    def updateCompAdjustmentConf (self) :
        '''Update an adjustmentConfig based on changes in the projectConfig.'''

        for gid in self.projectConfig['Groups'].keys() :
            if gid not in self.adjustmentConfig.keys() :
                self.tools.buildConfSection(self.adjustmentConfig, gid)
            for comp in self.projectConfig['Groups'][gid]['cidList'] :
                if not self.adjustmentConfig[gid].has_key(comp) :
                    self.tools.buildConfSection(self.adjustmentConfig[gid], comp)
                self.adjustmentConfig[gid][comp]['%1.1'] = '1'
        self.tools.writeConfFile(self.adjustmentConfig)
        return True


###############################################################################
######################## USFM Component Text Functions ########################
###############################################################################
######################## Error Code Block Series = 0400 #######################
###############################################################################


    def getComponentType (self, gid) :
        '''Return the cType for a component.'''

#        import pdb; pdb.set_trace()

        try :
            cType = self.projectConfig['Groups'][gid]['cType']
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.log.writeToLog('COMP-200', ['Key not found ' + str(e)])
            self.tools.dieNow()

        return cType


    def isCompleteComponent (self, gid, cid) :
        '''A two-part test to see if a component has a config entry and a file.'''

        if self.hasCidFile(gid, cid) :
            return True


    def hasUsfmCidInfo (self, cid) :
        '''Return True if this cid is in the PT USFM cid info dictionary.'''

        if cid in self.usfmCidInfo().keys() :
            return True


    def hasCidFile (self, gid, cid) :
        '''Return True or False depending on if a working file exists 
        for a given cName.'''

        cType = self.projectConfig['Groups'][gid]['cType']
        return os.path.isfile(os.path.join(self.local.projComponentFolder, cid, cid + '.' + cType))


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

