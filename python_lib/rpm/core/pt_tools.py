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


def mapPTTextSettings (managerSettings, ptSettings, reset=False) :
    '''Map the text settings from a PT project SSF file into the text
    manager's settings.'''

    # Get the SSF XML object
    # Find the appropreate text settings we need
    # Merge them with the manager settings object
    # Overwrite exsisting settings if reset set to True

# Work here ###################################################################
                
    return managerSettings


def installPTStyles (local, mainStyleFile) :
    '''Go get the style sheet from the local PT project this is in
    and install it into the project where and how it needs to be.'''

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
    '''Look in a PT project for a custom override style file and
    copy it into the project if it is there.'''

    # There may, or may not, be a custom style file. We need to look
    ptCustomStyles = os.path.join(os.path.dirname(local.projHome), customStyleFile)
    projCustomStyles = os.path.join(local.projProcessFolder, customStyleFile)
    # We will start with a very simple copy operation. Once we get going
    # we will need to make this more sophisticated.
    if os.path.isfile(ptCustomStyles) :
        shutil.copy(ptCustomStyles, projCustomStyles)
        return True


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


