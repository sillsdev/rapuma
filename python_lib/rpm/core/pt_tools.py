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

import codecs, os, sys, shutil
from datetime import *
from xml.etree import ElementTree
from configobj import ConfigObj, Section
from tools import *


###############################################################################
############################ Functions Begin Here #############################
###############################################################################


def getPTFont (home) :
    '''Just return the name of the font used in a PT project.'''

    ssf = getPTSettings(home)
    return ssf['ScriptureText']['DefaultFont']


def mapPTTextSettings (sysSet, ptSet, reset=False) :
    '''Map the text settings from a PT project SSF file into the text
    manager's settings.'''

    # A PT to RPM text mapping dictionary
    mapping   = {
                'FileNameBookNameForm'    : 'nameFormID',
                'FileNamePrePart'         : 'prePart',
                'FileNamePostPart'        : 'postPart'
                }

    # Loop through all the PT settings and check against the mapping
    for k in mapping.keys() :
        try :
            if sysSet[mapping[k]] == '' or sysSet[mapping[k]] == 'None' :
                sysSet[mapping[k]] = ptSet['ScriptureText'][k]
            elif reset == True :
                sysSet[mapping[k]] = ptSet['ScriptureText'][k]
        except :
            pass

    return sysSet


def installPTStyles (local, mainStyleFile) :
    '''Go get the style sheet from the local PT project this is in
    and install it into the project where and how it needs to be. If it
    doesn't find it there go to the [My Paratext Projects] folder and
    look there. If none is found a default file will come be copied in
    from the RPM system.'''

    # As this is call is for a PT based project, it is certain the style
    # file should be found in the parent folder.
    ptStyles = os.path.join(os.path.dirname(local.projHome), mainStyleFile)
    projStyles = os.path.join(local.projProcessFolder, mainStyleFile)
    # We will start with a very simple copy operation. Once we get going
    # we will need to make this more sophisticated.
    if os.path.isfile(ptStyles) :
        shutil.copy(ptStyles, projStyles)
        return True


def installPTCustomStyles (local, customStyleFile) :
    '''Look in a PT project for a custom override style file and copy it into
    the project if it is there.  If it is not there, go one more folder up in
    case you are located in the [My Paratext Projects] folder.  If it is not
    there, then return False.'''

    # There may, or may not, be a custom style file in the parent folder.
    # If it is not there we look in the grandparent's folder
    (parent, grandparent) = ancestorsPath(local.projHome)
    targetCustomStyles  = os.path.join(local.projProcessFolder, customStyleFile)
    projectCustomStyles = os.path.join(parent, customStyleFile)
    ptCustomStyles      = os.path.join(grandparent, customStyleFile)
    searchOrder         = [projectCustomStyles, ptCustomStyles]
    # We will start by searching in order from the inside out and stop
    # as soon as we find one. If none is found, return False. If one is
    # found in the target folder, we will not overwrite it and return False
    if not os.path.isfile(targetCustomStyles) :
        for sFile in searchOrder :
            if os.path.isfile(sFile) :
                try :
                    shutil.copy(sFile, targetCustomStyles)
                    return True
                except :
                    return False


def getPTSettings (home) :
    '''Get the ParaTExt project settings from the parent/source PT project.
    Turn the data into a dictionary.'''

    # Not sure where the PT SSF file might be. We will get a list of
    # files from the cwd and the parent. If it exsists, it should
    # be in one of those folders
    ssfFileName = ''
    ptPath = ''
    parentFolder = os.path.dirname(home)
    localFolder = home
    parentIDL = os.path.split(parentFolder)[1] + '.ssf'
    parentIDU = os.path.split(parentFolder)[1] + '.SSF'
    localIDL = os.path.split(localFolder)[1] + '.ssf'
    localIDU = os.path.split(localFolder)[1] + '.SSF'
    fLParent = os.listdir(parentFolder)
    fLLocal = os.listdir(localFolder)
    if parentIDL in fLParent :
        ssfFileName = parentIDL
        ptPath = parentFolder
    elif parentIDU in fLParent :
        ssfFileName = parentIDU
        ptPath = parentFolder
    elif localIDL in localFolder :
        ssfFileName = localIDL
        ptPath = localFolder
    elif localIDU in localFolder :
        ssfFileName = localIDU
        ptPath = localFolder

    # Return the dictionary
    ssfFile = os.path.join(ptPath, ssfFileName)
    if os.path.isfile(ssfFile) :
        return xmlFileToDict(ssfFile)

    else :
        writeToLog(self.project, 'ERR', 'The ParaTExt SSF file [' + fName(ssfFile) + '] could not be found.')


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



