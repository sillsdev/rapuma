#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project tasks.

# History:
# 20111222 - djd - Started with intial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os


# Load the local classes
from tools import *
from component import Component


###############################################################################
################################## Begin Class ################################
###############################################################################

# As we load the module we will bring in all the common information about all the
# components this type will handle.

# All valid USFM Scripture IDs
matterCompsScripture = {'mat' : 'Matthew', 'mrk' : 'Mark', 'luk' : 'Luke', 'jhn' : 'John', 
                            'act' : '', 'rom' : '', '1co' : '', '2co' : '', 
                            'gal' : '', 'eph' : '', 'php' : '', 'col' : '', 
                            '1th' : '', '2th' : '', '1ti' : '', '2ti' : '', 
                            'tit' : '', 'phm' : '', 'heb' : '', 'jas' : 'James', 
                            '1pe' : '', '2pe' : '', '1jn' : '', '2jn' : '', 
                            '3jn' : '', 'jud' : '', 'rev' : '' 
                        } 
# All valid USFM front matter IDs
matterCompsFront     = {'frt' : 'Front Matter', 
# FIXME: How do we emmbed a dict in a dict?
                            {'periph' : ['Title Page', 'Half Title Page', 'Promotional Page', 'Imprimatur', 'Publication Data', 'Forward', 'Preface', 'Table of Contents', 'Alphabetical Contents', 'Table of Abbreviations']}, 
                        'int' : 'Introductions', 
                            'periph' : ['Bible Introduction', 'Old Testament Introduction', 'Pentateuch Introduction', 'History Introduction', 'Poetry Introduction', 'Prophecy Introduction', 'New Testament Introduction', 'Gospels Introduction', 'Epistles Introduction', 'Deuterocanon Introduction' ]
                        }
# All valid USFM back matter IDs
matterCompsBack      = {'bak' : 'Back Matter', 
                            'periph' : ['Chronology', 'Weights and Measures', 'Map Index']
                        }
matterCompsBackOther = {'cnc' : 'Concordance', 'glo' : 'Glossary', 'tdx' : 'Topical Index', 'ndx' : 'Names Index'}
# Any remaining USFM that do not fall in the above categories
matterCompsOther     = {'xxa' : 'Extra A', 'xxb' : 'Extra B', 'xxc' : 'Extra C', 'xxd' : 'Extra D',
                            'xxe' : 'Extra E', 'xxf' : 'Extra F', 'xxg' : 'Extra G'
                        }
matterCompsOtherCover = {'oth' : 'Other',
                            'periph' : ['Cover', 'Spine']
                        }
# Combine all the above into one master dictionary
matterCompsBackComplete = matterCompsBack.update(matterCompsBackOther)
matterCompsOtherComplete = matterCompsOther.update(matterCompsOtherCover)
structureinfo = {'scripture' : matterCompsScripture, 'front' : matterCompsFront, 'back' : matterCompsBackComplete, 'other' : matterCompsOtherComplete}



class Usfm (Component) :
    '''This class contains information about a type of component used in type of project.'''

    def __init__(self, project, config) :
        super(Usfm, self).__init__(project, config)

#    # The default managers are named here in this dictionary with name:type
#    # format. Where the 'name' is for this text type. The 'type' is the kind of
#    # manager to use.
#    # by the Book project type right here.
#    defaultManagers = {'FontUsfmMain' : 'font', 'FormatUsfmMain' : 'format', 'StyleUsfmMain' : 'style',
#        'FontUsfmFront' : 'font', 'FormatUsfmFront' : 'format', 'StyleUsfmFront' : 'style'}

        self.comps = structureinfo

    def render(self) :
        """Does USFM specific rendering of a USFM component"""
        #useful variables: self.project, self.cfg

        # Is this a valid component ID for this component type?
        print self.comps
        if self.cfg['name'] in self.comps['scripture'] :
            terminal("Rendering: " + self.cfg['name'])


