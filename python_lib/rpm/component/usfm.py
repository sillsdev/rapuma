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
from pprint import pprint


# Load the local classes
from tools import *
from component import Component


###############################################################################
################################## Begin Class ################################
###############################################################################

# As we load the module we will bring in all the common information about all the
# components this type will handle.

# All valid USFM IDs
compIDs = {
            'gen' : ['Genesis', '01GEN'], 'exo' : ['Exodus', '02EXO'], 'lev' : ['Leviticus', '03LEV'], 'num' : ['Numbers', '04NUM'], 
            'deu' : ['Deuteronomy', '05DEU'], 'jos' : ['Joshua', '06JOS'], 'jdg' : ['Judges', '07JDG'], 'rut' : ['Ruth', '08RUT'], 
            '1sa' : ['1 Samuel', '091SA'], '2sa' : ['2 Samuel', '102SA'], '1ki' : ['1 Kings', '111KI'], '2ki' : ['2 Kings', '122KI'], 
            '1ch' : ['1 Chronicles', '131CH'], '2ch' : ['2 Chronicles', '142CH'], 'ezr' : ['Ezra', '15EZR'], 'neh' : ['Nehemiah', '16NEH'], 
            'est' : ['Esther', '17EST'], 'job' : ['Job', '18JOB'], 'psa' : ['Psalms', '19PSA'], 'pro' : ['Proverbs', '20PRO'], 'ecc' : ['Ecclesiastes', '21ECC'], 
            'sng' : ['Song of Songs', '22SNG'], 'isa' : ['Isaiah', '23ISA'], 'jer' : ['Jeremiah', '24JER'], 'lam' : ['Lamentations', '25LAM'], 
            'ezk' : ['Ezekiel', '26EZK'], 'dan' : ['Daniel', '27DAN'], 'hos' : ['Hosea', '28HOS'], 'jol' : ['Joel', '29JOL'], 
            'amo' : ['Amos', '30AMO'], 'oba' : ['Obadiah', '31OBA'], 'jon' : ['Jonah', '32JON'], 'mic' : ['Micah', '33MIC'], 
            'nam' : ['Nahum', '34NAM'], 'hab' : ['Habakkuk', '35HAB'], 'zep' : ['Zephaniah', '36ZEP'], 'hag' : ['Haggai', '37HAG'], 
            'zec' : ['Zechariah', '38ZEC'], 'mal' : ['Malachi', '39MAL'],
            'mat' : ['Matthew', '41MAT'], 'mrk' : ['Mark', '42MRK'], 'luk' : ['Luke', '43LUK'], 'jhn' : ['John', '44JHN'], 
            'act' : ['Acts', '45ACT'], 'rom' : ['Romans', '46ROM'], '1co' : ['1 Corinthians', '471CO'], '2co' : ['2 Corinthians', '482CO'], 
            'gal' : ['Galatians', '49GAL'], 'eph' : ['Ephesians', '50EPH'], 'php' : ['Philippians', '51PHP'], 'col' : ['Colossians', '52COL'], 
            '1th' : ['1 Thessalonians', '531TH'], '2th' : ['2 Thessalonians', '542TH'], '1ti' : ['1 Timothy', '551TI'], '2ti' : ['2 Timothy', '562TI'], 
            'tit' : ['Titus', '57TIT'], 'phm' : ['Philemon', '58PHM'], 'heb' : ['Hebrews', '59HEB'], 'jas' : ['James', '60JAS'], 
            '1pe' : ['1 Peter', '611PE'], '2pe' : ['2 Peter', '622PE'], '1jn' : ['1 John', '631JN'], '2jn' : ['2 John', '642JN'], 
            '3jn' : ['3 John', '653JN'], 'jud' : ['Jude', '66JUD'], 'rev' : ['Revelation', '67REV'], 
            'tob' : ['Tobit', '68TOB'], 'jdt' : ['Judith', '69JDT'], 'esg' : ['Esther', '70ESG'], 'wis' : ['Wisdom of Solomon', '71WIS'], 
            'sir' : ['Sirach', '72SIR'], 'bar' : ['Baruch', '73BAR'], 'lje' : ['Letter of Jeremiah', '74LJE'], 's3y' : ['Song of the Three Children', '75S3Y'], 
            'sus' : ['Susanna', '76SUS'], 'bel' : ['Bel and the Dragon', '77BEL'], '1ma' : ['1 Maccabees', '781MA'], '2ma' : ['2 Maccabees', '792MA'], 
            '3ma' : ['3 Maccabees', '803MA'], '4ma' : ['4 Maccabees', '814MA'], '1es' : ['1 Esdras', '821ES'], '2es' : ['2 Esdras', '832ES'], 
            'man' : ['Prayer of Manasses', '84MAN'], 'ps2' : ['Psalms 151', '85PS2'], 'oda' : ['Odae', '86ODA'], 'pss' : ['Psalms of Solomon', '87PSS'], 
            'jsa' : ['Joshua A', '88JSA'], 'jdb' : ['Joshua B', '89JDB'], 'tbs' : ['Tobit S', '90TBS'], 'sst' : ['Susannah (Theodotion)', '91SST'], 
            'dnt' : ['Daniel (Theodotion)', '92DNT'], 'blt' : ['Bel and the Dragon (Theodotion)', '93BLT'], 
            'frt' : ['Front Matter', 'A0FRT'], 'int' : ['Introductions', 'A7INT'], 'bak' : ['Back Matter', 'A1BAK'], 
            'cnc' : ['Concordance', 'A8CNC'], 'glo' : ['Glossary', 'A9GLO'], 'tdx' : ['Topical Index', 'B0TDX'], 'ndx' : ['Names Index', 'B1NDX'], 
            'xxa' : ['Extra A', '94XXA'], 'xxb' : ['Extra B', '95XXB'], 'xxc' : ['Extra C', '96XXC'], 'xxd' : ['Extra D', '97XXD'],
            'xxe' : ['Extra E', '98XXE'], 'xxf' : ['Extra F', '99XXF'], 'xxg' : ['Extra G', '100XXG'], 'oth' : ['Other', 'A2OTH'], 
            'eza' : ['Apocalypse of Ezra', 'A4EZA'], '5ez' : ['5 Ezra (Latin Prologue)', 'A55EZ'], '6ez' : ['6 Ezra (Latin Epilogue)', 'A66EZ'], 'dag' : ['Daniel Greek', 'B2DAG'], 
            'ps3' : ['Psalms 152-155', 'B3PS3'], '2ba' : ['2 Baruch (Apocalypse)', 'B42BA'], 'lba' : ['Letter of Baruch', 'B5LBA'], 'jub' : ['Jubilees', 'B6JUB'], 
            'eno' : ['Enoch', 'B7ENO'], '1mq' : ['1 Meqabyan', 'B81MQ'], '2mq' : ['2 Meqabyan', 'B92MQ'], '3mq' : ['3 Meqabyan', 'C03MQ'], 
            'rep' : ['Reproof (Proverbs 25-31)', 'C1REP'], '4ba' : ['4 Baruch (Rest of Baruch)', 'C24BA'], 'lao' : ['Laodiceans', 'C3LAO'] 
          }


class Usfm (Component) :
    '''This class contains information about a type of component used in type of project.'''

    def __init__(self, project, config) :
        super(Usfm, self).__init__(project, config)

#    # The default managers are named here in this dictionary with name:type
#    # format. Where the 'name' is for this text type. The 'type' is the kind of
#    # manager to use.
#    # by the Book project type right here.
#    defaultManagers = {'FontUsfmMain' : 'font', 'FormatUsfmMain' : 'format', 'StyleUsfmMain' : 'style',
#        'FontUsfmFront' : 'font', 'FormatUsfmFront' : 'format', 'StyleUsfmFront' : 'style'}

        self.compIDs = compIDs

    def render(self) :
        """Does USFM specific rendering of a USFM component"""
        #useful variables: self.project, self.cfg

        # Is this a valid component ID for this component type?
#        pprint(self.compIDs)
        if self.cfg['name'] in self.compIDs :
            terminal("Rendering: " + self.compIDs[self.cfg['name']][0])


