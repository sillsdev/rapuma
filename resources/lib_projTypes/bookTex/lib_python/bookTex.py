#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110728
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project level tasks specific for this type of project.

# History:
# 20110728 - djd - Initial draft


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

#import os, sys

# Load the local classes
from bookTex_command import Command
from project import Project
from component import Component

###############################################################################
############################ Define Global Functions ##########################
###############################################################################

# These root level functions work at a fundamental level of the system


###############################################################################
################################## Begin Class ################################
###############################################################################

class BookTex (Project) :

    def __init__(self, projConfig, projInit, userConfig, projHome, userHome, tipeHome) :
        '''Initialize this class.'''
        
        # Make it available to the Project Class with this
        super(BookTex, self).__init__(projConfig, projInit, userConfig, projHome, userHome, tipeHome)



###############################################################################
############################# Begin Main Functions ############################
###############################################################################



