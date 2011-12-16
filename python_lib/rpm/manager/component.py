#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111210
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project tasks.

# History:
# 20111210 - djd - Started with intial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, codecs


# Load the local classes
from tools import *
from manager import Manager
import component_command as cmpCmd


###############################################################################
################################## Begin Class ################################
###############################################################################

class Component (object) :

    def __init__(self, project, parent = None) :
        '''Initialize this class.'''
        self.project = project
        self.parent = parent or project


class ComponentGroup(Component) :

    def initComponent(self) :
        self.components = {}
        complist = self._config['bindingOrder']
        for c in complist :
            self.components[c] = self.project.createComponent(c, parent=self)


class PublishingComponent(Component) :

    def initComponent(self) :
        self.fontList = self.parent._config['fontList']
        self.compType = self.parent._config['compType']
        self.rendering = self.parent._config['rendering']
        self.useHyphenation = self.parent._config['useHyphenation']
        self.useIllustration = self.parent._config['useIllustration']


