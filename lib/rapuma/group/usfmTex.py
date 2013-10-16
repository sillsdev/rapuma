#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle usfmTex macro tasks.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os

# Load the local classes
from rapuma.core.tools                  import Tools

###############################################################################
################################## Begin Class ################################
###############################################################################

class UsfmTex (object) :

    def __init__(self, layoutConfig) :
        '''Do the primary initialization for this class.'''

        self.tools                          = Tools()
        self.layoutConfig                   = layoutConfig

        # Log messages for this module
        self.errorCodes     = {

            '0000' : ['MSG', 'Placeholder message'],

        }



###############################################################################
############################ Macro Level Functions ############################
###############################################################################
####################### Error Code Block Series = 1000 ########################
###############################################################################

    def getTitleColumns (self) :
        '''Return 2 if titleColumnsTwo is True.'''

        if self.tools.str2bool(self.layoutConfig['PageLayout']['titleColumnsTwo']) :
            return 2
        else :
            return 1


    def getIntroColumns (self) :
        '''Return 2 if introColumnsTwo is True.'''

        if self.tools.str2bool(self.layoutConfig['PageLayout']['introColumnsTwo']) :
            return 2
        else :
            return 1


    def getBodyColumns (self) :
        '''Return 2 if bodyColumnsTwo is True.'''

        if self.tools.str2bool(self.layoutConfig['PageLayout']['bodyColumnsTwo']) :
            return 2
        else :
            return 1


    def getHeaderPosition (self) :
        '''Return the calculated relative position of the header based
        on the top margin setting.'''

        tm              = float(self.layoutConfig['PageLayout']['topMargin'])
        hp              = float(self.layoutConfig['PageLayout']['headerPosition'])

        return float("{0:.2f}".format(round(hp / tm, 2)))


    def getFooterPosition (self) :
        '''Return the calculated relative position of the footer based
        on the bottom margin setting.'''

        bm              = float(self.layoutConfig['PageLayout']['bottomMargin'])
        hp              = float(self.layoutConfig['PageLayout']['footerPosition'])

        return float("{0:.2f}".format(round(hp / bm, 2)))


    def getMarginUnit (self) :
        '''Calculate the basic margin unit for the macro package. This will be
        based on the largest amount set for the top, bottom and side margins.'''

        tm              = float(self.layoutConfig['PageLayout']['topMargin'])
        bm              = float(self.layoutConfig['PageLayout']['bottomMargin'])
        im              = float(self.layoutConfig['PageLayout']['insideMargin'])
        om              = float(self.layoutConfig['PageLayout']['outsideMargin'])
        # Adjust for binding gutter setting (extra insideMargin)
        if self.getBindingGutterWidth() :
            im          = im - self.getBindingGutterWidth()

        return max(float(u) for u in [tm, bm, im, om])


    def getTopMarginFactor (self) :
        '''Calculate the top margin factor based on what the base margin
        and top margin settings are.'''

        marginUnit      = self.getMarginUnit()
        topMargin       = float(self.layoutConfig['PageLayout']['topMargin'])

        return float("{0:.2f}".format(round(topMargin / marginUnit, 2)))


    def getBottomMarginFactor (self) :
        '''Calculate the bottom margin factor based on what the base margin
        and bottom margin settings are.'''

        marginUnit      = self.getMarginUnit()
        bottomMargin    = float(self.layoutConfig['PageLayout']['bottomMargin'])

        return float("{0:.2f}".format(round(bottomMargin / marginUnit, 2)))


    def getSideMarginFactor (self) :
        '''Calculate the side margin factor based on what the base margin
        and outside margin settings are.'''

        # For this we will be using the outsideMargin setting not the inside
        marginUnit      = self.getMarginUnit()
        outsideMargin   = float(self.layoutConfig['PageLayout']['outsideMargin'])
        insideMargin    = float(self.layoutConfig['PageLayout']['insideMargin'])
        self.tools.writeConfFile(self.layoutConfig)

        return float("{0:.2f}".format(round(outsideMargin / marginUnit, 2)))


    def getBindingGutterWidth (self) :
        '''Calculate the binding gutter width based on any extra space added
        to the inside margin which exceeds the outside margin.'''

        insideMargin    = float(self.layoutConfig['PageLayout']['insideMargin'])
        outsideMargin   = float(self.layoutConfig['PageLayout']['outsideMargin'])
        results         = insideMargin - outsideMargin
        # If nothing, just 0, rather than a float (0.0) so binding gutter
        # can be turned off automatically
        if int(results) == 0 :
            return      0
        else :
            return      results


    def getFontSizeUnit (self) :
        '''Calculate the font size unit. This counts on the style marker for "p" 
        being set to 12pt. If for some reason it is not, then this will fail.
        This will divide the body font size by 12 to get the size unit.'''

        fontDefaultSize     = float(self.layoutConfig['TextElements']['fontDefaultSize'])
        bodyFontSize        = float(self.layoutConfig['TextElements']['bodyFontSize'])
        return float("{0:.2f}".format(round(bodyFontSize / fontDefaultSize, 2)))


    def getLineSpacingFactor (self) :
        '''Calculate the line spacing factor. This is based on the body font size.
        It will divide the body text leading by the body font size to get the factor
        unit.'''

        fontDefaultSize     = float(self.layoutConfig['TextElements']['fontDefaultSize'])
        bodyTextLeading     = float(self.layoutConfig['TextElements']['bodyTextLeading'])
        return float("{0:.2f}".format(round(bodyTextLeading / fontDefaultSize, 2)))


