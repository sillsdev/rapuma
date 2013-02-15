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
#from configobj import ConfigObj, Section
from rapuma.core.tools import *
import palaso.sfm as sfm
from palaso.sfm import usfm, style, element, text


###############################################################################
############################ Functions Begin Here #############################
###############################################################################




# FIXME: Working here yet


#def getPTHyphenWordList (rcfg, pcfg) :
#    '''Return a list of hyphenated words found in a ParaTExt project
#    hyphated words text file.'''

#    # Note: it is a given that the cType is usfm
#    projectIDCode = pcfg['ProjectInfo']['projectIDCode']
#    usfm_sourcePath = rcfg['Projects'][projectIDCode]['usfm_sourcePath']
#    ptHyphenFileName = pcfg['Managers']['usfm_Hyphenation']['ptHyphenFileName']
#    ptHyphenFile = os.path.join(usfm_sourcePath, ptHyphenFileName)
#    wordList = []
#    
#    # Go get the file if it is to be had
#    if os.path.isfile(ptHyphenFile) :
#        with codecs.open(ptHyphenFile, "r", encoding='utf_8') as hyphenWords :
#            for line in hyphenWords :
#                # Using the logic that there can only be one word in a line
#                # if the line contains more than one word it is not wanted
#                word = line.split()
#                if len(word) == 1 :
#                    wordList.append(word[0])
#        return wordList
#    else :
#        return False


#def ptToTexHyphenWordList (pcfg, wordList) :
#    '''Convert a hyphenated word list from PT to a TeX type word list.'''

#    # The ptHyphenImportRegEx will come in in a 2 element list
#    ptHyphenImportRegEx = pcfg['Managers']['usfm_Hyphenation']['ptHyphenImportRegEx']
#    advancedHyphenImportRegEx = pcfg['Managers']['usfm_Hyphenation']['advancedHyphenImportRegEx']
#    search = ptHyphenImportRegEx[0]
#    replace = ptHyphenImportRegEx[1]
#    texWordList = []
#    for word in wordList :
#        tWord = re.sub(ptHyphenImportRegEx[0], ptHyphenImportRegEx[1], word)
#        # In case we want to do more...
#        if advancedHyphenImportRegEx :
#            tWord = re.sub(advancedHyphenImportRegEx[0], advancedHyphenImportRegEx[1], tWord)
#        texWordList.append(tWord)

#    if len(texWordList) > 0 :
#        return texWordList
#    else :
#        return False
#    









def formPTName (project, cName, cid) :
    '''Using valid PT project settings from the project configuration, form
    a valid PT file name that can be used for a number of operations.'''

    # FIXME: Currently very simplistic, will need to be more refined for
    #           number of use cases.

    try :
        nameFormID = project.projConfig['Managers']['usfm_Text']['nameFormID']
        postPart = project.projConfig['Managers']['usfm_Text']['postPart']
        prePart = project.projConfig['Managers']['usfm_Text']['prePart']

        if nameFormID == '41MAT' :
            mainName = project.components[cName].getUsfmCidInfo(cid)[2] + cid.upper()
            if prePart and prePart != 'None' :
                thisFile = prePart + mainName + postPart
            else :
                thisFile = mainName + postPart
        return thisFile
    except :
        return False


def formGenericName (project, cid) :
    '''Figure out the best way to form a valid file name given the
    source is not coming from a PT project.'''

# FIXME: This will be expanded as we find more use cases

    postPart = project.projConfig['Managers']['usfm_Text']['postPart']
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

#    import pdb; pdb.set_trace()

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




