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
from configobj import ConfigObj

# Load the local classes
from rapuma.core.tools          import Tools
from rapuma.core.proj_config    import ProjConfig
from rapuma.core.user_config    import UserConfig
from rapuma.core.proj_local     import ProjLocal
from rapuma.core.proj_log       import ProjLog


class PageBackground (object) :

    def __init__(self, pid) :
        '''Intitate the whole class and create the object.'''

        self.pid                        = pid
        self.tools                      = Tools()
        self.user                       = UserConfig()
        self.userConfig                 = self.user.userConfig
        self.projHome                   = None
        self.projectMediaIDCode         = None
        self.local                      = None
        self.projConfig                 = None
        self.layoutConfig               = None
        self.useWatermark               = False
        self.useLines                   = False
        self.useBoxBoarder              = False
        # Paths
        self.projIllustrationsFolder    = None
        # File names and paths
        self.projWatermarkFile          = None
        self.rpmDefWatermarkFile        = None
        self.projLinesFile              = None
        self.projBaselineGridFileName   = None
        self.rpmLinesTemplateFileName   = None
        self.boxBoarderFile             = None
        self.rpmBoxBoarderFile          = None
        # Try to finish the init (failing is okay for some functions in this module)
        self.finishInit()
        # Log messages for this module
        self.errorCodes     = {
            '0000' : ['MSG', 'Placeholder message'],
            '0220' : ['MSG', 'Set [<<1>>] background to True.'],
            '0230' : ['MSG', 'Set [<<1>>] background to False.'],
            '0240' : ['MSG', 'No change to [<<1>>] background.'],
            '0250' : ['MSG', 'All backgrounds have been turned off.'],
            '0280' : ['LOG', 'Installed background file [<<1>>] into the project.'],
            '0290' : ['ERR', 'Failed to install background file [<<1>>]. It ended with this error: [<<2>>]'],
        }


    def finishInit (self, projHome = None) :
        '''Finishing collecting settings that would be needed for most
        functions in this module.'''

        try :
            self.projHome                   = self.userConfig['Projects'][self.pid]['projectPath']
            self.projectMediaIDCode         = self.userConfig['Projects'][self.pid]['projectMediaIDCode']
            self.local                      = ProjLocal(self.pid)
            self.projConfig                 = ProjConfig(self.local).projConfig
            self.log                        = ProjLog(self.pid)
            self.layoutConfig               = ConfigObj(os.path.join(self.local.projConfFolder, self.projectMediaIDCode + '_layout.conf'), encoding='utf-8')
            # Set booleans
            self.useWatermark               = self.tools.str2bool(self.layoutConfig['PageLayout']['useWatermark'])
            self.useLines                   = self.tools.str2bool(self.layoutConfig['PageLayout']['useLines'])
            self.useBoxBoarder              = self.tools.str2bool(self.layoutConfig['PageLayout']['useBoxBoarder'])
            # File names
            self.projWatermarkFileName      = self.layoutConfig['PageLayout']['watermarkFile']
            self.rpmDefWatermarkFileName    = 'watermark_default.pdf'
            self.projLinesFileName          = self.layoutConfig['PageLayout']['linesFile']
            self.projBaselineGridFileName   = 'baselinegrid.svg'
            self.rpmLinesTemplateFileName   = 'grid.svg'
            self.boxBoarderFileName         = self.layoutConfig['PageLayout']['boxBoarderFile']
            self.rpmBoxBoarderFileName      = 'box_background.pdf'
            # Paths
            self.projIllustrationsFolder    = self.local.projIllustrationsFolder
            self.rpmIllustrationsFolder     = self.local.rapumaIllustrationsFolder
            # Files with path
            self.projWatermarkFile          = os.path.join(self.projIllustrationsFolder, self.projWatermarkFileName)
            self.rpmDefWatermarkFile        = os.path.join(self.rpmIllustrationsFolder, self.rpmDefWatermarkFileName)
            self.projLinesFile              = os.path.join(self.projIllustrationsFolder, self.projLinesFileName)
            self.projBaselineGridFile       = os.path.join(self.projIllustrationsFolder, self.projBaselineGridFileName)
            self.rpmLinesTemplateFile       = os.path.join(self.rpmIllustrationsFolder, self.rpmLinesTemplateFileName)
            self.boxBoarderFile             = os.path.join(self.projIllustrationsFolder, self.boxBoarderFileName)
            self.rpmBoxBoarderFile          = os.path.join(self.rpmIllustrationsFolder, self.rpmBoxBoarderFileName)
        except Exception as e :
            # If this doesn't work, we should probably say something
            self.tools.terminal('Error: PageBackground() extra init failed because of: ' + str(e))


###############################################################################
############################## Compare Functions ##############################
###############################################################################
######################## Error Code Block Series = 0200 #######################
###############################################################################

    def backgroundOff (self) :
        '''Turn off all page backgrounds.'''

        self.layoutConfig['PageLayout']['useWatermark'] = False
        self.layoutConfig['PageLayout']['useLines'] = False
        self.layoutConfig['PageLayout']['useBoxBoarder'] = False
        self.layoutConfig['PageLayout']['useCropmarks'] = False
        if self.tools.writeConfFile(self.layoutConfig) :
            self.log.writeToLog(self.errorCodes['0250'])


    def addBackground (self, bType, force = False) :
        '''Add a page background type to a project. In some cases, there can
        be more than one. This function will determine what is allowed.'''

        change = False
        if bType == 'watermark' :
            # Turn on watermark and make sure there is a file to use
            if self.useWatermark == False :
                self.installDefaultWatermarkFile(force)
                self.layoutConfig['PageLayout']['useWatermark'] = True
                change = True
        elif bType == 'lines' :
            # Turn on lines and make sure there is a file to use
            self.installLinesFile(force)
            if self.useLines == False :
                self.layoutConfig['PageLayout']['useLines'] = True
                self.layoutConfig['PageLayout']['useBoxBoarder'] = False
                self.layoutConfig['PageLayout']['useCropmarks'] = False
                change = True
        elif bType == 'boarder' :
            # Turn on lines and make sure there is a file to use
            if self.useLines == False :
                self.installBoxBoarderFile(force)
                self.layoutConfig['PageLayout']['useBoxBoarder'] = True
                self.layoutConfig['PageLayout']['useLines'] = False
                self.layoutConfig['PageLayout']['useCropmarks'] = False
                change = True
        elif bType == 'cropmarks' :
                self.layoutConfig['PageLayout']['useCropmarks'] = True
                self.layoutConfig['PageLayout']['useLines'] = False
                self.layoutConfig['PageLayout']['useBoxBoarder'] = False
                change = True

        if change :
            if self.tools.writeConfFile(self.layoutConfig) :
                self.log.writeToLog(self.errorCodes['0220'], [bType])
        else :
            self.log.writeToLog(self.errorCodes['0240'], [bType])


    def removeBackground (self, bType) :
        '''Remove a page background type.'''

        change = False
        if bType == 'watermark' :
            # Turn it off if it is on but do not do anything with the watermark file
            if self.useWatermark == True :
                self.layoutConfig['PageLayout']['useWatermark'] = False
                change = True
        elif bType == 'lines' :
            if self.useLines == True :
                self.layoutConfig['PageLayout']['useLines'] = False
                change = True
        elif bType == 'boarder' :
                self.layoutConfig['PageLayout']['useBoxBoarder'] = False
                change = True
        elif bType == 'cropmarks' :
                self.layoutConfig['PageLayout']['useCropmarks'] = False
                change = True

        if change :
            if self.tools.writeConfFile(self.layoutConfig) :
                self.log.writeToLog(self.errorCodes['0230'], [bType])
        else :
            self.log.writeToLog(self.errorCodes['0240'], [bType])


    def changeWatermarkFile (self) :
        '''Change the current watermark file.'''

# FIXME: This is a place holder function

        terminal('This does not work yet.')


    def installDefaultWatermarkFile (self, force = False) :
        '''Install a default Rapuma watermark file into the project.'''

        if not os.path.exists(self.projWatermarkFile or force) :
            try :
                shutil.copy(self.rpmDefWatermarkFile, self.projWatermarkFile)
                self.log.writeToLog(self.errorCodes['0280'], [self.tools.fName(self.projWatermarkFile)])
            except Exception as e :
                # If this doesn't work, we should probably quite here
                self.log.writeToLog(self.errorCodes['0290'], [self.tools.fName(self.projWatermarkFile),str(e)])


    def installBoxBoarderFile (self, force = False) :
        '''Install a background lines file into the project.'''

        if not os.path.exists(self.boxBoarderFile) or force :
            try :
                shutil.copy(self.rpmBoxBoarderFile, self.boxBoarderFile)
                self.log.writeToLog(self.errorCodes['0280'], [self.tools.fName(self.boxBoarderFile)])
            except Exception as e :
                # If this doesn't work, we should probably quite here
                self.log.writeToLog(self.errorCodes['0290'], [self.tools.fName(self.boxBoarderFile),str(e)])


    def installLinesFile (self, force = False) :
        '''Install a background lines file into the project.'''

        if not os.path.exists(self.projLinesFile) or force:
            try :
                self.createLinesFile()
                self.log.writeToLog(self.errorCodes['0280'], [self.tools.fName(self.projLinesFile)])
            except Exception as e :
                # If this doesn't work, we should probably quite here
                self.log.writeToLog(self.errorCodes['0290'], [self.tools.fName(self.projLinesFile),str(e)])


    def createLinesFile (self) :
        '''Create a lines background file used for composition work. The code
        in this file came from Flip Wester (flip_wester@sil.org)'''

        # Set our file names
        source = self.rpmLinesTemplateFile
        output = self.projBaselineGridFile
        final_output = self.projLinesFile

        # input and calculation
        # get the values  for lineSpaceFactor and fontSizeUnit
        # from Rapuma book_layout.conf 
        pageHeight          = int(self.layoutConfig['PageLayout']['pageHeight'])
        pageWidth           = int(self.layoutConfig['PageLayout']['pageWidth'])
        lineSpacingFactor   = int(float(self.layoutConfig['Fonts']['lineSpacingFactor']))
        fontSizeUnit        = int(float(self.layoutConfig['Fonts']['fontSizeUnit'].replace('pt', '')))
        marginUnit          = int(self.layoutConfig['Margins']['marginUnit'])
        topMarginFactor     = int(float(self.layoutConfig['Margins']['topMarginFactor']))
        bottomMarginFactor  = int(float(self.layoutConfig['Margins']['bottomMarginFactor']))

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

#        import pdb; pdb.set_trace()

        try:
            subprocess.call(commands) 
        except Exception as e :
            print 'Error found: ' + str(e)
            



