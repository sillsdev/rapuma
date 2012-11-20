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
from tools import *
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
            mainName = getUsfmCidInfo(cid)[1] + cid.upper()
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
    ssfFile = findSsfFile(sourcePath)
    if ssfFile :
        if os.path.isfile(ssfFile) :
            return xmlFileToDict(ssfFile)


def getSourceEditor (projConfig, sourcePath, cType) :
    '''Return the sourceEditor if it is set. If not try to
    figure out what it should be and return that.'''

    Ctype = cType.capitalize()
    # FIXME: This may need expanding as more use cases arrise
    if testForSetting(projConfig['CompTypes'][Ctype], 'sourceEditor') :
        se = projConfig['CompTypes'][Ctype]['sourceEditor']
    else :
        if findSsfFile(sourcePath) :
            se = 'paratext'
        else :
            se = 'generic'

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


def usfmCidInfo () :
    '''Return a dictionary of all valid information about USFMs used in PT.'''

    return {
                'gen' : ['Genesis', '01'], 'exo' : ['Exodus', '02'], 'lev' : ['Leviticus', '03'], 'num' : ['Numbers', '04'], 
                'deu' : ['Deuteronomy', '05'], 'jos' : ['Joshua', '06'], 'jdg' : ['Judges', '07'], 'rut' : ['Ruth', '08'], 
                '1sa' : ['1 Samuel', '09'], '2sa' : ['2 Samuel', '10'], '1ki' : ['1 Kings', '11'], '2ki' : ['2 Kings', '12'], 
                '1ch' : ['1 Chronicles', '13'], '2ch' : ['2 Chronicles', '14'], 'ezr' : ['Ezra', '15'], 'neh' : ['Nehemiah', '16'], 
                'est' : ['Esther', '17'], 'job' : ['Job', '18'], 'psa' : ['Psalms', '19'], 'pro' : ['Proverbs', '20'], 'ecc' : ['Ecclesiastes', '21'], 
                'sng' : ['Song of Songs', '22'], 'isa' : ['Isaiah', '23'], 'jer' : ['Jeremiah', '24'], 'lam' : ['Lamentations', '25'], 
                'ezk' : ['Ezekiel', '26'], 'dan' : ['Daniel', '27'], 'hos' : ['Hosea', '28'], 'jol' : ['Joel', '29'], 
                'amo' : ['Amos', '30'], 'oba' : ['Obadiah', '31'], 'jon' : ['Jonah', '32'], 'mic' : ['Micah', '33'], 
                'nam' : ['Nahum', '34'], 'hab' : ['Habakkuk', '35'], 'zep' : ['Zephaniah', '36'], 'hag' : ['Haggai', '37'], 
                'zec' : ['Zechariah', '38'], 'mal' : ['Malachi', '39'],
                'mat' : ['Matthew', '41'], 'mrk' : ['Mark', '42'], 'luk' : ['Luke', '43'], 'jhn' : ['John', '44'], 
                'act' : ['Acts', '45'], 'rom' : ['Romans', '46'], '1co' : ['1 Corinthians', '47'], '2co' : ['2 Corinthians', '48'], 
                'gal' : ['Galatians', '49'], 'eph' : ['Ephesians', '50'], 'php' : ['Philippians', '51'], 'col' : ['Colossians', '52'], 
                '1th' : ['1 Thessalonians', '53'], '2th' : ['2 Thessalonians', '54'], '1ti' : ['1 Timothy', '55'], '2ti' : ['2 Timothy', '56'], 
                'tit' : ['Titus', '57'], 'phm' : ['Philemon', '58'], 'heb' : ['Hebrews', '59'], 'jas' : ['James', '60'], 
                '1pe' : ['1 Peter', '61'], '2pe' : ['2 Peter', '62'], '1jn' : ['1 John', '63'], '2jn' : ['2 John', '64'], 
                '3jn' : ['3 John', '65'], 'jud' : ['Jude', '66'], 'rev' : ['Revelation', '67'], 
                'tob' : ['Tobit', '68'], 'jdt' : ['Judith', '69'], 'esg' : ['Esther', '70'], 'wis' : ['Wisdom of Solomon', '71'], 
                'sir' : ['Sirach', '72'], 'bar' : ['Baruch', '73'], 'lje' : ['Letter of Jeremiah', '74'], 's3y' : ['Song of the Three Children', '75'], 
                'sus' : ['Susanna', '76'], 'bel' : ['Bel and the Dragon', '77'], '1ma' : ['1 Maccabees', '78'], '2ma' : ['2 Maccabees', '79'], 
                '3ma' : ['3 Maccabees', '80'], '4ma' : ['4 Maccabees', '81'], '1es' : ['1 Esdras', '82'], '2es' : ['2 Esdras', '83'], 
                'man' : ['Prayer of Manasses', '84'], 'ps2' : ['Psalms 151', '85'], 'oda' : ['Odae', '86'], 'pss' : ['Psalms of Solomon', '87'], 
                'jsa' : ['Joshua A', '88'], 'jdb' : ['Joshua B', '89'], 'tbs' : ['Tobit S', '90'], 'sst' : ['Susannah (Theodotion)', '91'], 
                'dnt' : ['Daniel (Theodotion)', '92'], 'blt' : ['Bel and the Dragon (Theodotion)', '93'], 
                'frt' : ['Front Matter', 'A0'], 'int' : ['Introductions', 'A7'], 'bak' : ['Back Matter', 'A1'], 
                'cnc' : ['Concordance', 'A8'], 'glo' : ['Glossary', 'A9'], 'tdx' : ['Topical Index', 'B0'], 'ndx' : ['Names Index', 'B1'], 
                'xxa' : ['Extra A', '94'], 'xxb' : ['Extra B', '95'], 'xxc' : ['Extra C', '96'], 'xxd' : ['Extra D', '97'],
                'xxe' : ['Extra E', '98'], 'xxf' : ['Extra F', '99'], 'xxg' : ['Extra G', '100'], 'oth' : ['Other', 'A2'], 
                'eza' : ['Apocalypse of Ezra', 'A4'], '5ez' : ['5 Ezra (Latin Prologue)', 'A5'], '6ez' : ['6 Ezra (Latin Epilogue)', 'A6'], 'dag' : ['Daniel Greek', 'B2'], 
                'ps3' : ['Psalms 152-155', 'B3'], '2ba' : ['2 Baruch (Apocalypse)', 'B4'], 'lba' : ['Letter of Baruch', 'B5'], 'jub' : ['Jubilees', 'B6'], 
                'eno' : ['Enoch', 'B7'], '1mq' : ['1 Meqabyan', 'B8'], '2mq' : ['2 Meqabyan', 'B9'], '3mq' : ['3 Meqabyan', 'C0'], 
                'rep' : ['Reproof (Proverbs 25-31)', 'C1'], '4ba' : ['4 Baruch (Rest of Baruch)', 'C2'], 'lao' : ['Laodiceans', 'C3'] 
              }



