#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110610
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle mostly housekeeping processes at the component level.

# History:
# 20110610 - djd - Begin initial draft


###############################################################################
################################### Shell Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

# import codecs, os

# Load the local classes

class Component (object) :
    initialised = False
    
    # Intitate the whole class
    def __init__(self, aProject) :
        self.project = aProject
        if not self.initialised : self.initClass()

    def initClass(self) :
        '''Ensures everything is in place for components of this type to do their thing'''
        self.__class__.initialised = True
        
    @classmethod
    def initType(cls, aProject) :
        '''Internal housekeeping for the component type when it first wakes up'''
        pass

    def preProcess(self) :
        pass

