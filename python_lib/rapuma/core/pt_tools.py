#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110823
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This module will hold all the miscellaneous functions that are used for
# Paratext project processing

# History:
# 20120122 - djd - New file


###############################################################################
################################## Tools Class ################################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, sys, shutil, dircache
from datetime import *
from xml.etree import ElementTree
from configobj import ConfigObj, Section
from rapuma.core.tools import *
import palaso.sfm as sfm
from palaso.sfm import usfm, style, element, text


###############################################################################
############################ Functions Begin Here #############################
###############################################################################


def formPTName (projConfig, cid) :
    '''Using valid PT project settings from the project configuration, form
    a valid PT file name that can be used for a number of operations.'''

    # FIXME: Currently very simplistic, will need to be more refined for
    #           number of use cases.

    try :
        nameFormID = projConfig['Managers']['usfm_Text']['nameFormID']
        postPart = projConfig['Managers']['usfm_Text']['postPart']
        prePart = projConfig['Managers']['usfm_Text']['prePart']

        if nameFormID == '41MAT' :
            mainName = getUsfmCidInfo(cid)[2] + cid.upper()
            if prePart and prePart != 'None' :
                thisFile = prePart + mainName + postPart
            else :
                thisFile = mainName + postPart
        return thisFile
    except :
        return False


def formGenericName (projConfig, cid) :
    '''Figure out the best way to form a valid file name given the
    source is not coming from a PT project.'''

# FIXME: This will be expanded as we find more use cases

    postPart = projConfig['Managers']['usfm_Text']['postPart']
    return cid + '.' + postPart


def getPTFont (sourcePath) :
    '''Just return the name of the font used in a PT project.'''

    ssf = getPTSettings(sourcePath)
    return ssf['ScriptureText']['DefaultFont']


def mapPTTextSettings (sysSet, ptSet, force=False) :
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


def findSsfFile (sourcePath) :
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
    parentFolder = sourcePath
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


def getPTSettings (sourcePath) :
    '''Return the data into a dictionary for the system to use.'''

    # Return the dictionary
    if os.path.isdir(sourcePath) :
        ssfFile = findSsfFile(sourcePath)
        if ssfFile :
            if os.path.isfile(ssfFile) :
                return xmlFileToDict(ssfFile)


def getSourceEditor (projConfig, sourcePath, cType) :
    '''Return the sourceEditor if it is set. If not try to
    figure out what it should be and return that. Unless we
    find we are in a PT project, we'll call it generic.'''

#    import pdb; pdb.set_trace()
    se = 'generic'
    Ctype = cType.capitalize()
    # FIXME: This may need expanding as more use cases arrise
    if testForSetting(projConfig['CompTypes'][Ctype], 'sourceEditor') :
        se = projConfig['CompTypes'][Ctype]['sourceEditor']
    else :
        if findSsfFile(sourcePath) :
            se = 'paratext'

    return se


def getSourcePath (projConfig, Ctype) :
    '''Return the stored source path for a component type.'''

    if testForSetting(projConfig['CompTypes'][Ctype], 'sourcePath') :
        sp = projConfig['CompTypes'][Ctype]['sourcePath']
        if sp :
            return resolvePath(sp)


def hasUsfmCidInfo (cid) :
    '''Return True if this cid is in the PT USFM cid info dictionary.'''

    if cid in usfmCidInfo().keys() :
        return True


def getUsfmCidInfo (cid) :
    '''Return a list of info about a specific cid used in the PT context.'''

    try :
        return usfmCidInfo()[cid]
    except :
        return False


def getUsfmName (cid) :
    '''Look up and return the actual name for a valid cid.'''

    if hasUsfmCidInfo(cid) :
        return getUsfmCidInfo(cid)[0]


def getRapumaCName (cid) :
    '''Look up and return the Rapuma component name for a valid cid.
    But if the cid happens to be a cName already, that will be returned.'''

    if hasUsfmCidInfo(cid) :
        return getUsfmCidInfo(cid)[1]
    else :
        # FIXME: This seems a little weak. What if the cid is an invalid cName?
        return cid


def getUsfmCid (cName) :
    '''Find the cid by using the cName to look.'''

    info = usfmCidInfo()
    for k, v in info.iteritems() :
        if info[k][0] == cName :
            return k


def usfmCidInfo () :
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



