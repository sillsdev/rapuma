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

import codecs, os, difflib, subprocess
from configobj import ConfigObj

# Load the local classes
from rapuma.core.tools          import *
from rapuma.core.proj_config    import ProjConfig
from rapuma.core.user_config    import UserConfig
from rapuma.core.proj_local     import ProjLocal
from rapuma.core.proj_log       import ProjLog


class PageBackground (object) :

    def __init__(self, pid) :
        '''Intitate the whole class and create the object.'''

        self.rapumaHome             = os.environ.get('RAPUMA_BASE')
        self.userHome               = os.environ.get('RAPUMA_USER')
        self.user                   = UserConfig(self.rapumaHome, self.userHome)
        self.userConfig             = self.user.userConfig
        self.pid                    = pid
        self.projHome               = None
        self.projectMediaIDCode     = None
        self.local                  = None
        self.projConfig             = None
        self.layoutConfig           = None
        self.useWatermark           = False
        self.useLines               = False
        self.useBoxBoarder          = False
        # Paths
        self.projIllustrationsFolder = None
        # File names and paths
        self.projWatermarkFile      = None
        self.rpmDefWatermarkFile    = None
        self.projLinesFile          = None
        self.rpmDefLinesFile        = None
        self.boxBoarderFile         = None
        self.rpmBoxBoarderFile      = None
        # Try to finish the init (failing is okay for some functions in this module)
        self.finishInit()
        # Log messages for this module
        self.errorCodes     = {
            '000' : ['MSG', 'Placeholder message'],
            '220' : ['MSG', 'Set [<<1>>] background to True.'],
            '230' : ['MSG', 'Set [<<1>>] background to False.'],
        }


    def finishInit (self, projHome = None) :
        '''Finishing collecting settings that would be needed for most
        functions in this module.'''

        try :
            self.projHome           = self.userConfig['Projects'][self.pid]['projectPath']
            self.projectMediaIDCode = self.userConfig['Projects'][self.pid]['projectMediaIDCode']
            self.local              = ProjLocal(self.rapumaHome, self.userHome, self.projHome)
            self.projConfig         = ProjConfig(self.local).projConfig
            self.log                = ProjLog(self.local, self.user)
            self.layoutConfig       = ConfigObj(os.path.join(self.local.projConfFolder, self.projectMediaIDCode + '_layout.conf'), encoding='utf-8')
            # Set booleans
            self.useWatermark       = str2bool(self.layoutConfig['PageLayout']['useWatermark'])
            self.useLines           = str2bool(self.layoutConfig['PageLayout']['useLines'])
            self.useBoxBoarder      = str2bool(self.layoutConfig['PageLayout']['useBoxBoarder'])
            # File names
            self.projWatermarkFileName      = self.layoutConfig['PageLayout']['watermarkFile']
            self.rpmDefWatermarkFileName    = 'watermark_default.pdf'
            self.projLinesFileName          = self.layoutConfig['PageLayout']['linesFile']
            self.rpmDefLinesFileName        = 'lines_default.pdf'
            self.boxBoarderFileName         = self.layoutConfig['PageLayout']['boxBoarderFile']
            self.rpmBoxBoarderFileName      = 'box_background.pdf'
            # Paths
            self.projIllustrationsFolder = self.local.projIllustrationsFolder
            self.rpmIllustrationsFolder     = self.local.rapumaIllustrationsFolder
            # Files with path
            self.projWatermarkFile          = os.path.join(self.projIllustrationsFolder, self.projWatermarkFileName)
            self.rpmDefWatermarkFile        = os.path.join(self.rpmIllustrationsFolder, self.rpmDefWatermarkFileName)
            self.projLinesFile              = os.path.join(self.projIllustrationsFolder, self.projLinesFileName)
            self.rpmDefLinesFile            = os.path.join(self.rpmIllustrationsFolder, self.rpmDefLinesFileName)
            self.boxBoarderFile             = os.path.join(self.projIllustrationsFolder, self.boxBoarderFileName)
            self.rpmBoxBoarderFile          = os.path.join(self.rpmIllustrationsFolder, self.rpmBoxBoarderFileName)
        except Exception as e :
            # If this doesn't work, we should probably say something
            terminal('Error: PageBackground() extra init failed because of: ' + str(e))


###############################################################################
############################## Compare Functions ##############################
###############################################################################
######################## Error Code Block Series = 200 ########################
###############################################################################

    def addBackground (self, bType) :
        '''Add a page background type to a project. In some cases, there can
        be more than one. This function will determine what is allowed.'''

        change = False
        if bType == 'watermark' :
            # Turn on watermark and make sure there is a file to use
            if self.useWatermark == False :
                self.layoutConfig['PageLayout']['useWatermark'] = True
                # FIXME: Need to check to see if there is a watermark file, etc so this works
                change = True
        elif bType == 'lines' :
            print bType
        elif bType == 'boarder' :
            print bType
        elif bType == 'cropmarks' :
            print bType

        if change :
            if writeConfFile(self.layoutConfig) :
                self.log.writeToLog(self.errorCodes['220'], [bType])


    def removeBackground (self, bType) :
        '''Remove a page background type.'''

        change = False
        if bType == 'watermark' :
            # Turn it off if it is on but do not do anything with the watermark file
            if self.useWatermark == True :
                self.layoutConfig['PageLayout']['useWatermark'] = False
                change = True
        elif bType == 'lines' :
            print bType
        elif bType == 'boarder' :
            print bType
        elif bType == 'cropmarks' :
            print bType

        if change :
            if writeConfFile(self.layoutConfig) :
                self.log.writeToLog(self.errorCodes['230'], [bType])


    def changeWatermarkFile (self) :
        '''Change the current watermark file.'''

# FIXME: This is a place holder function

        terminal('This does not work yet.')


    def installDefaultWatermarkFile (self) :
        '''Install a default Rapuma watermark file into the project.'''

        if not os.path.exists(self.projWatermarkFile) :
            try :
                shutil.copy(self.rpmDefWatermarkFile, self.projWatermarkFile)
                self.project.log.writeToLog('ILUS-080', [fName(self.projWatermarkFile)])
            except Exception as e :
                # If this doesn't work, we should probably quite here
                dieNow('Error: Failed to install default watermark background file with this error: ' + str(e) + '\n')


    def installLinesFile (self) :
        '''Install a background lines file into the project.'''

        if not os.path.exists(self.projLinesFile) :
            try :
                shutil.copy(self.rpmDefLinesFile, self.projLinesFile)
                self.project.log.writeToLog('ILUS-080', [fName(self.projLinesFile)])
            except Exception as e :

                # If this doesn't work, we should probably quite here
                dieNow('Error: Failed to install lines background file with this error: ' + str(e) + '\n')


    def installBoxBoarderFile (self) :
        '''Install a background lines file into the project.'''

        if not os.path.exists(self.boxBoarderFile) :
            try :
                shutil.copy(self.rpmBoxBoarderFile, self.boxBoarderFile)
                self.project.log.writeToLog('ILUS-080', [fName(self.boxBoarderFile)])
            except Exception as e :

                # If this doesn't work, we should probably quite here
                dieNow('Error: Failed to install lines background file with this error: ' + str(e) + '\n')











# FIXME: Work on integrating Flip's code

    def flipsCode (self) :

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
            



