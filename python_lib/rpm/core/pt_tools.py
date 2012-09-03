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
    # file should be found in the parent or grandparent folder. If that
    # exact file is not found in either place, a substitute will be
    # copied in from RPM and given the designated name.
    (parent, grandparent)   = ancestorsPath(local.projHome)
    targetStyles            = os.path.join(local.projProcessFolder, mainStyleFile)
    ptProjStyles            = os.path.join(parent, mainStyleFile)
    ptStyles                = os.path.join(grandparent, mainStyleFile)
    rpmStyles               = os.path.join(local.rpmCompTypeFolder, 'usfm', 'usfm.sty')
    searchOrder             = [ptProjStyles, ptStyles, rpmStyles]

    # We will start by searching in order from the inside out and stop
    # as soon as we find one. If none is found, return False. If one is
    # found in the target folder, we will not overwrite it and return False
    if not os.path.isfile(targetStyles) :
        for sFile in searchOrder :
            if os.path.isfile(sFile) :
                try :
                    shutil.copy(sFile, targetStyles)
                    return True
                except :
                    return False


def installPTCustomStyles (local, customStyleFile) :
    '''Look in a PT project for a custom override style file and copy it into
    the project if it is there.  If it is not there, go one more folder up in
    case you are located in the [My Paratext Projects] folder.  If it is not
    there, then return False.'''

    # There may, or may not, be a custom style file in the parent folder.
    # If it is not there we look in the grandparent's folder
    (parent, grandparent)   = ancestorsPath(local.projHome)
    targetCustomStyles      = os.path.join(local.projProcessFolder, customStyleFile)
    ptProjectCustomStyles   = os.path.join(parent, customStyleFile)
    ptCustomStyles          = os.path.join(grandparent, customStyleFile)
    searchOrder             = [ptProjectCustomStyles, ptCustomStyles]
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
    '''Look for the ParaTExt project settings file. The immediat PT project
    is the parent folder and the PT environment that the PT projet is found
    in, if any, is the grandparent folder. the .ssf (settings) file in the
    grandparent folder takes presidence over the one found in the parent folder.
    This function will determine where the primary .ssf file is and turn the
    data into a dictionary for the system to use.'''

    # Not sure where the PT SSF file might be or even what its name is.
    # Starting in parent, we should find the first .ssf file. That will
    # give us the name of the file. Then we will look in the grandparent
    # folder and if we find the same named file there, that will be
    # harvested for the settings. Otherwise, the settings will be taken
    # from the parent folder.
    ssfFileName = ''
    ptPath = ''
    parentFolder = os.path.dirname(home)
    grandparentFolder = os.path.dirname(parentFolder)
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

    # Now now look in the grandparent folder and change to override settings
    # file if there is one
    for f in grandparentFileList :
        if os.path.isfile(os.path.join(grandparentFolder, f)) :
            ucn = ssfFileName.split('.')[0] + '.' + ssfFileName.split('.')[1].upper()
            lcn = ssfFileName.split('.')[0] + '.' + ssfFileName.split('.')[1].lower()
            if f == (ucn or lcn) :
                ssfFileName = f
                ptPath = grandparentFolder

    # Return the dictionary
    ssfFile = os.path.join(ptPath, ssfFileName)
    if os.path.isfile(ssfFile) :
        return xmlFileToDict(ssfFile)


def isMetaComponent (pc, cid) :
    '''Return True if this component has a list of component in it.'''

    try :
        l = pc['Components'][cid]['list']
        return True
    except :
        return False


def isValidCID (pc, cid) :
    '''Try to figure out if this is a valid component.'''

    if hasUsfmCidInfo(cid) :
        return True
    else :
        if isMetaComponent(pc, cid) :
            for i in pc['Components'][cid]['list'] :
                if not hasUsfmCidInfo(i) :
                    return False
            # If no bad components were found it must be okay
            return True


def findBadComp (pc, cid) :
    '''Much like isValidCID() but it returns the first offending
    cid ID it finds.'''

    if isMetaComponent(pc, cid) :
        for i in pc['Components'][cid]['list'] :
            if not hasUsfmCidInfo(i) :
                return i
            else :
                return cid


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



