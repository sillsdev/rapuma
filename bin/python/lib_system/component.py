#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110823
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle mostly housekeeping processes at the component level.

# History:
# 20110823 - djd - Started with intial file from RPM project


###############################################################################
################################### Shell Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

# import codecs, os

# Load the local classes

componentTypes = {}

class MetaCommand(type) :

    def __init__(cls, namestring, t, d) :
        global componentTypes
        super(MetaCommand, cls).__init__(namestring, t, d)
        if cls.type :
            componentTypes[cls.type] = cls


class Component (object) :
    __metaclass__ = MetaCommand
    type = None

    initialised = False

    # Intitate the whole class
    def __init__(self, aProject, compType, typeConfig) :
        self.project = aProject
        self.compType = compType
        if not self.initialised : self.__class__.initType(aProject, typeConfig)

    def initClass(self) :
        '''Ensures everything is in place for components of this type to do their thing'''
        self.__class__.initialised = True
        
    @classmethod
    def initType(cls, aProject, typeConfig) :
        '''Internal housekeeping for the component type when it first wakes up'''
        cls.typeConfig = typeConfig

    def preProcess(self) :
        pass

