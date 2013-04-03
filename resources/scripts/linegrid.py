#!/usr/bin/python
# -*- coding: utf_8 -*-

###############################################################################
################################### Intro #####################################
###############################################################################

# This python script will generate a baselinegrid in Inkscape to assist 
# the adjusting of pages in components of Rapuma. 
# It is based on variables defined in book_layout.conf in the Config 
# folder of the Rapuma project. The following variables need to be copied
# into the program:
#     pageHeight [mm]
#     pageWidth [mm]
#     lineSpacingFactor [no dimension]
#     fontSizeUnit [pt]
#     marginUnit [mm]
#     topMarginFactor [no dimension]
#     bottomMarginFactor [no dimension]
# The items with dimensions need to be converted to either pixels [px] or
# points [pt]. 
# The grid is generated with the Life Path Effect Ruler of Inkscape. There are 
# three variables: linespace position of the firstBaseline, height and width of
# the baselinegrid. Testing has been done with the Charis SIL font, Norasi and 
# Padauk Book and that works OK. 
# The variables are entered in a Inkscape svg template called grid.svg. At the 
# end the template is saved as baselinegrid.svg and converted to baselinegrid.pdf. 

###############################################################################
############################## Setup Environment ##############################
###############################################################################

import os, sys, shutil, re, codecs, subprocess

###############################################################################
################################# Process Code ################################
###############################################################################
source = 'grid.svg'
output = 'baselinegrid.svg'
final_output = 'baselinegrid.pdf'

# input and calculation
# get the values  for lineSpaceFactor and fontSizeUnit
# from Rapuma book_layout.conf 
pageHeight = 210
pageWidth = 148
lineSpacingFactor = 1.1
fontSizeUnit = 1
marginUnit = 10
topMarginFactor = 1.75
bottomMarginFactor = 1.12

# The page size is defined in [mm] but is entered in pixels [px] and points [pt]. 
# The conversion factor for [px] is 90/25.4 and for [pt] 72/25.4.
# paper height [px]
paperHeight = round(pageHeight*90/25.4, 2)
# paper height [pt]
paperPointsHeight = int(pageHeight*72/25.4)
# paper width [px]
paperWidth = round(pageWidth*90/25.4, 2)
# paper width [pt]
paperPointsWidth = int(pageWidth*72/25.4)

# The lineSpace formula is a linear equation (y = m.x + b) generated based on 
# [pt] measurements in Inkscape
lineSpace = round(((1.1627 * 12 * fontSizeUnit + -0.0021) * lineSpacingFactor),2)
print 'Space between lines: ', lineSpace, 'pt'

# The topMargin position depends on the pagesize and defined in [mm]. It needs to be
# converted to points [pt]
topMargin = round((pageHeight - topMarginFactor * marginUnit)*72/25.4, 3)

# To determine the position of the firstBaseLine independent of the page size 
# the distance topMargin to firstBaseLine. The formula is a linear equation 
# based on [pt] measurements in Inkscape 
topMarginToBaseLine = round((0.9905 * 12 * fontSizeUnit + 0.0478),3)

# The firstBaseLine is smaller than the topMargin 
firstBaseLine = topMargin - topMarginToBaseLine

# The dimensions of the grid rectangle are needed to prepare a placeholder for the
# gridlines.   
lineGridHeight = round(firstBaseLine - bottomMarginFactor*marginUnit*72/25.40, 3)

lineGridWidth = int((pageWidth-marginUnit*1.5)*72/25.4)

lineGridMargin = int(marginUnit*54/25.4)

# Read in the source file
contents = codecs.open(source, "rt", encoding="utf_8_sig").read()


# Make the changes

# 01 enter paper dimensions
# paper height [px]
# SearchText: @pH
# ReplaceText: variable paperHeight
contents = re.sub(ur'@pH', ur'%r' % paperHeight, contents)

# 02 paper height [pt]
# SearchText: @pPH
# ReplaceText: variable paperHeight
contents = re.sub(ur'@pPH', ur'%r' % paperPointsHeight, contents)

# 03 paper width [px]
# SearchText: @pW
# ReplaceText: variable paperWidth
contents = re.sub(ur'@pW', ur'%r' % paperWidth, contents)

# 04 paper height [pt]
# SearchText: @pPW
# ReplaceText: variable paperHeight
contents = re.sub(ur'@pPW', ur'%r' % paperPointsWidth, contents)

# 05 Enter the position first base line
# SearchText: @fBL
# ReplaceText: variable firstBaseLine
contents = re.sub(ur'@fBL', ur'%r' % firstBaseLine, contents)

# 06 Enter the height of the line grid
# SearchText: @lGH
# ReplaceText: variable lineGridHeight
contents = re.sub(ur'@lGH', ur'%r' % lineGridHeight, contents)

# 02 Enter the width of the line grid
# SearchText: @lGW
# ReplaceText: variable lineGridWidth
contents = re.sub(ur'@lGW', ur'%r' % lineGridWidth, contents)

# 07 Enter the right margin of the line grid
# SearchText: @lGM
# ReplaceText: variable lineGridWidth
contents = re.sub(ur'@lGM', ur'%r' % lineGridMargin, contents)

# 08 enter the linespace value
# SearchText: @lS
# ReplaceText: variable lineSpace
contents = re.sub(ur'@lS', ur'%r' % lineSpace, contents)


# Write out a temp file so we can do some checks
codecs.open(output, "wt", encoding="utf_8_sig").write(contents)

# commands = ['inkscape', output, final_output]
commands = ['inkscape', '-f', output, '-A', final_output]

try:
    subprocess.call(commands) 
except Exception as e :
    print 'Error found: ' + str(e)
    

