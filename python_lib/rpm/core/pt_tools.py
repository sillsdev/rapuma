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


def xmltodict(element):
    if not isinstance(element, ElementTree.Element):
        raise ValueError("must pass xml.etree.ElementTree.Element object")

    def xmltodict_handler(parent_element):
        result = dict()
        for element in parent_element:
            if len(element):
                obj = xmltodict_handler(element)
            else:
                obj = element.text

            if result.get(element.tag):
                if hasattr(result[element.tag], "append"):
                    result[element.tag].append(obj)
                else:
                    result[element.tag] = [result[element.tag], obj]
            else:
                result[element.tag] = obj
        return result

    return {element.tag: xmltodict_handler(element)}


def xmlfiletodict(filename):
    return xmltodict(ElementTree.parse(filename).getroot())


def parseSSF (fileName) :
    '''Parse a Paratext SSF file and return a configobj to be used in
    other processes.'''

    return xmlfiletodict(fileName)


