#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle page background tasks, creating lines, watermarks, etc.

###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, difflib, subprocess, shutil, re
from configobj                          import ConfigObj

# Load the local classes
from rapuma.core.tools                  import Tools
from rapuma.core.user_config            import UserConfig
from rapuma.core.proj_local             import ProjLocal
from rapuma.core.proj_log               import ProjLog
from rapuma.project.proj_config         import ProjConfig
from rapuma.group.usfmTex               import UsfmTex


class ProjBackground (object) :

    def __init__(self, pid, gid) :
        '''Intitate the whole class and create the object.'''
        
        # FIXME: because the usfm cType is most common at this time, to make
        # things easier we set that as the cType. If the project is not using
        # that cType, this will all break.

#        import pdb; pdb.set_trace()

        self.pid                        = pid
        self.gid                        = gid
        self.tools                      = Tools()
        self.user                       = UserConfig()
        self.userConfig                 = self.user.userConfig
        self.projHome                   = self.userConfig['Projects'][pid]['projectPath']
        self.local                      = ProjLocal(pid)
        self.proj_config                = ProjConfig(pid, gid)
        self.log                        = ProjLog(pid)
        self.projConfig                 = self.proj_config.projConfig
        self.layoutConfig               = self.proj_config.layoutConfig
        self.macPackConfig              = self.proj_config.macPackConfig
        self.cType                      = self.projConfig['Groups'][gid]['cType']
        self.Ctype                      = self.cType.capitalize()
        self.macPackFunctions           = UsfmTex(self.layoutConfig)
        # Paths
        self.projIllustrationsFolder    = self.local.projIllustrationsFolder
        self.rpmIllustrationsFolder     = self.local.rapumaIllustrationsFolder

        # Log messages for this module
        self.errorCodes     = {
            '0000' : ['MSG', 'Placeholder message'],
            '0220' : ['MSG', 'Background [<<1>>] is already being used for the [<<2>>] background type.'],
            '0230' : ['MSG', 'Background [<<1>>] has been added for use in the [<<2>>] background.'],
            '0240' : ['MSG', 'Background [<<1>>] has been removed from the [<<2>>] background type.'],
            '0250' : ['MSG', 'Background [<<1>>] is not used in [<<2>>] background type. Cannot remove.'],
            '0260' : ['MSG', 'Background [<<1>>] has been updated for the [<<2>>] background type.'],
            '0270' : ['MSG', 'Background [<<1>>] is not found in the [<<2>>] background type. Cannot update.'],
            '0280' : ['MSG', 'Installed background file [<<1>>] into the project.'],
            '0290' : ['ERR', 'Failed to install background file [<<1>>]. Error: [<<2>>]'],
        }


###############################################################################
############################## Compare Functions ##############################
###############################################################################
######################## Error Code Block Series = 0200 #######################
###############################################################################

# FIXME: We have a bit of a time-bomb here in that backgounds are managed at
# the project level but the settings info we need comes from the manager level
# which is tied to the cType. In the code below we will be making the assumption
# that the cType is "usfm". That will point us to the usfm_Xetex manager which
# all of this is currently tied to. If this ever changes, we are hosed as far
# as backgound management goes.


    def addBackground (self, outType, bgrd) :
        '''Add a backgound to a specific output type.'''

        bgName = bgrd
        # Handle cropmarks
        if bgrd != 'cropmarks' :
            bgName = bgrd + 'Watermark'

        bgList = self.projConfig['Managers']['usfm_Xetex'][outType + 'Background']
        if not bgName in bgList :
            bgList.append(bgName)
            self.projConfig['Managers']['usfm_Xetex'][outType + 'Background'] = bgList
            self.tools.writeConfFile(self.projConfig)
            if bgrd != 'cropmarks' :
                self.checkForBackground(bgName, outType)
            self.log.writeToLog(self.errorCodes['0230'], [bgName, outType])
        else :
            self.log.writeToLog(self.errorCodes['0220'], [bgName, outType])


    def removeBackground (self, outType, bgrd) :
        '''Remove a backgound from a specified output type.'''

        bgName = bgrd
        # Handle cropmarks
        if bgrd != 'cropmarks' :
            bgName = bgrd + 'Watermark'

        bgList = self.projConfig['Managers']['usfm_Xetex'][outType + 'Background']
        if bgName in bgList :
            bgList.remove(bgName)
            self.projConfig['Managers']['usfm_Xetex'][outType + 'Background'] = bgList
            self.tools.writeConfFile(self.projConfig)
            self.log.writeToLog(self.errorCodes['0240'], [bgName, outType])
        else :
            self.log.writeToLog(self.errorCodes['0250'], [bgName, outType])


    def updateBackground (self, outType, bgrd) :
        '''Update a background for a specific output type.'''

        bgName = bgrd
        # Handle cropmarks
        if bgrd != 'cropmarks' :
            bgName = bgrd + 'Watermark'

        bgList = self.projConfig['Managers']['usfm_Xetex'][outType + 'Background']
        if bgName in bgList :
            if bgrd != 'cropmarks' :
                self.checkForBackground(bgName, outType, True)
            self.log.writeToLog(self.errorCodes['0260'], [bgName, outType])
        else :
            self.log.writeToLog(self.errorCodes['0270'], [bgName, outType])


    def checkForBackground (self, bg, mode, force = False) :
        '''Check to see if a required backgound file is present. If not,
        make it so.'''

        projBgFile      = os.path.join(self.projIllustrationsFolder, bg + '.pdf')
        if not os.path.exists(projBgFile) or force :
            if bg.find('lines') >= 0 :
                if self.createLinesFile(projBgFile) :
                    self.log.writeToLog(self.errorCodes['0280'], [self.tools.fName(projBgFile)])
            elif bg.find('box') >= 0 :
                if self.createBorderFile(projBgFile) :
                    self.log.writeToLog(self.errorCodes['0280'], [self.tools.fName(projBgFile)])
            else :
                self.createWatermarkFile(projBgFile, mode)


    def createWatermarkFile (self, target, mode) :
        '''Install a default Rapuma watermark file into the project.'''

        # FIXME: A custom watermark creation function is needed here, load default for now
        rpmDefWatermarkFile = os.path.join(self.rpmIllustrationsFolder, mode + 'Watermark.pdf')

        try :
            shutil.copy(rpmDefWatermarkFile, target)
            self.log.writeToLog(self.errorCodes['0280'], [self.tools.fName(target)])
        except Exception as e :
            # If this doesn't work, we should probably quit here
            self.log.writeToLog(self.errorCodes['0290'], [self.tools.fName(target),str(e)])


    def createBorderFile (self, bgLinesFile) :
        '''Create a border backgound file used for proof reading.'''

        # Set our file names
        source = os.path.join(self.rpmIllustrationsFolder, 'border.svg')
        output = os.path.join(self.projIllustrationsFolder,  'pageborder.svg')
        final_output = bgLinesFile

        # input and calculation
        # get the values for page dimensions from Rapuma usfm_layout.conf 
        pageHeight          = float(self.layoutConfig['PageLayout']['pageHeight'])
        pageWidth           = float(self.layoutConfig['PageLayout']['pageWidth'])

        # The page size is defined in [mm] but is entered in pixels [px] 
        # The conversion factor for [px] is 90/25.4 
        # paper height [px]
        paperHeight = round(pageHeight*90/25.4, 2)
        # paper width [px]
        paperWidth = round(pageWidth*90/25.4, 2)

        # Read in the source file
        contents = codecs.open(source, "rt", encoding="utf_8_sig").read()

        # Make the changes

        # 01 enter paper dimensions
        # paper height [px]
        # SearchText: @pH
        # ReplaceText: variable paperHeight
        contents = re.sub(ur'@pH', ur'%r' % paperHeight, contents)

        # 02 paper width [px]
        # SearchText: @pW
        # ReplaceText: variable paperWidth
        contents = re.sub(ur'@pW', ur'%r' % paperWidth, contents)

        # Write out a temp file so we can do some checks
        codecs.open(output, "wt", encoding="utf_8_sig").write(contents)

        # commands = ['inkscape', output, final_output]
        commands = ['inkscape', '-f', output, '-A', final_output]

        try:
            subprocess.call(commands) 
            return True
        except Exception as e :
            self.log.writeToLog(self.errorCodes['0290'], [self.tools.fName(final_output),str(e)])


    def createLinesFile (self, bgLinesFile) :
        '''Create a lines background file used for composition work. The code
        in this file came from Flip Wester (flip_wester@sil.org)'''

        # Set our file names
        source = os.path.join(self.rpmIllustrationsFolder, 'grid.svg')
        output = os.path.join(self.projIllustrationsFolder,  'lines-grid.svg')
        final_output = bgLinesFile

        # For testing
        debug = False

        # input and calculation
        # get the values  for lineSpaceFactor and fontSizeUnit
        # from Rapuma usfm_layout.conf 
        pageHeight          = float(self.layoutConfig['PageLayout']['pageHeight'])
        pageWidth           = float(self.layoutConfig['PageLayout']['pageWidth'])
        lineSpacingFactor   = float(self.macPackConfig['FontSettings']['lineSpacingFactor'])
        fontSizeUnit        = float(self.macPackConfig['FontSettings']['fontSizeUnit'].replace('pt', ''))
        marginUnit          = self.macPackFunctions.getMarginUnit()
        topMarginFactor     = self.macPackFunctions.getTopMarginFactor()
        bottomMarginFactor  = self.macPackFunctions.getBottomMarginFactor()

        # The values of lineSpacingFactor, fontSizeUnit, topMarginFactor and bottomMarginFactor
        # are configured as floats. Changing them to integer reduces fontSizeUnits <1 to 0,
        # causing the script to hang. Changing the values back to floats solves the problem.

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

        # The baselineskip formula is a linear equation (y = m.x + b) generated based on 
        # [px] measurements in Inkscape
        baselineskip = round(((1.1650 * 12  * fontSizeUnit + -0.0300) * lineSpacingFactor*1.25),2)
        if debug :
            self.tools.terminal('Space between lines: ' + str(baselineskip) + ' px')

        # The topMargin position depends on the pagesize and defined in [mm]. It needs to be
        # converted to pixels [px]
        topMargin = round((pageHeight - topMarginFactor * marginUnit)*90/25.4, 3)
        if debug :
            self.tools.terminal('topMargin: ' + str(topMargin) + ' px')

        # The distance topMargin to firstBaseLine happens to be equal to the font size in pixels
        # based on pixel [px] measurements in Inkscape 
        topskip = round((1.25 * 12 * fontSizeUnit),3)
        #topskip = round((0.8 * 12 * fontSizeUnit),3)
        if debug :
            self.tools.terminal('topskipcalc: ' + str(topskip))

        # The firstBaseLine is topMargin minus topskip in [px] 
        firstBaseLine = topMargin - topskip
        if debug :
            self.tools.terminal('firstBaseLine: ' + str(firstBaseLine))

        # The dimensions of the grid rectangle are needed to prepare a placeholder for the
        # gridlines. 
        lineGridHeight = round(firstBaseLine - bottomMarginFactor * marginUnit*90/25.40, 3)

        lineGridWidth = int((pageWidth-marginUnit*1.5)*90/25.4)

        lineGridMargin = int(marginUnit*45/25.4)

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
        # ReplaceText: variable paperPointsHeight
        contents = re.sub(ur'@pPH', ur'%r' % paperPointsHeight, contents)

        # 03 paper width [px]
        # SearchText: @pW
        # ReplaceText: variable paperWidth
        contents = re.sub(ur'@pW', ur'%r' % paperWidth, contents)

        # 04 paper height [pt]
        # SearchText: @pPW
        # ReplaceText: variable paperPointsWidth
        contents = re.sub(ur'@pPW', ur'%r' % paperPointsWidth, contents)

        # 05 Enter the position first base line
        # SearchText: @fBL
        # ReplaceText: variable firstBaseLine
        contents = re.sub(ur'@fBL', ur'%r' % firstBaseLine, contents)

        # 06 Enter the height of the line grid
        # SearchText: @lGH
        # ReplaceText: variable lineGridHeight
        contents = re.sub(ur'@lGH', ur'%r' % lineGridHeight, contents)

        # 07 Enter the width of the line grid
        # SearchText: @lGW
        # ReplaceText: variable lineGridWidth
        contents = re.sub(ur'@lGW', ur'%r' % lineGridWidth, contents)

        # 08 Enter the right margin of the line grid
        # SearchText: @lGM
        # ReplaceText: variable lineGridMargin
        contents = re.sub(ur'@lGM', ur'%r' % lineGridMargin, contents)

        # 09 enter the baselineskip value
        # SearchText: @lS
        # ReplaceText: variable baselineskip
        contents = re.sub(ur'@lS', ur'%r' % baselineskip, contents)

        # Write out a temp file so we can do some checks
        codecs.open(output, "wt", encoding="utf_8_sig").write(contents)

        # commands = ['inkscape', output, final_output]
        commands = ['inkscape', '-f', output, '-A', final_output]

#        import pdb; pdb.set_trace()

        try:
            subprocess.call(commands) 
            return True
        except Exception as e :
            self.log.writeToLog(self.errorCodes['0290'], [self.tools.fName(final_output),str(e)])


