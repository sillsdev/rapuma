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
        # Paths
        self.projIllustrationsFolder    = None
        # File names and paths

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
            # File names


            # Paths
            self.projIllustrationsFolder    = self.local.projIllustrationsFolder
            self.rpmIllustrationsFolder     = self.local.rapumaIllustrationsFolder
            # Files with path


        except Exception as e :
            # If this doesn't work, we should probably say something
            self.tools.terminal('Error: PageBackground() extra init failed because of: ' + str(e))


###############################################################################
############################## Compare Functions ##############################
###############################################################################
######################## Error Code Block Series = 0200 #######################
###############################################################################

#    def backgroundOff (self) :
#        '''Turn off all page backgrounds.'''

#        self.layoutConfig['PageLayout']['useWatermark'] = False
#        self.layoutConfig['PageLayout']['useLines'] = False
#        self.layoutConfig['PageLayout']['useBoxBoarder'] = False
#        self.layoutConfig['PageLayout']['useCropmarks'] = False
#        if self.tools.writeConfFile(self.layoutConfig) :
#            self.log.writeToLog(self.errorCodes['0250'])


#    def addBackground (self, bType, force = False) :
#        '''Add a page background type to a project. In some cases, there can
#        be more than one. This function will determine what is allowed.'''

#        change = False
#        if bType == 'watermark' :
#            # Turn on watermark and make sure there is a file to use
#            if self.useWatermark == False :
#                self.installDefaultWatermarkFile(force)
#                self.layoutConfig['PageLayout']['useWatermark'] = True
#                change = True
#        elif bType == 'lines' :
#            # Turn on lines and make sure there is a file to use
#            if self.installLinesFile(force) :
#                change = True
#            if self.useLines == False :
#                self.layoutConfig['PageLayout']['useLines'] = True
#                self.layoutConfig['PageLayout']['useBoxBoarder'] = False
#                self.layoutConfig['PageLayout']['useCropmarks'] = False
#                change = True
#        elif bType == 'boarder' :
#            # Turn on lines and make sure there is a file to use
#            if self.useLines == False :
#                self.installBoxBoarderFile(force)
#                self.layoutConfig['PageLayout']['useBoxBoarder'] = True
#                self.layoutConfig['PageLayout']['useLines'] = False
#                self.layoutConfig['PageLayout']['useCropmarks'] = False
#                change = True
#        elif bType == 'cropmarks' :
#                self.layoutConfig['PageLayout']['useCropmarks'] = True
#                self.layoutConfig['PageLayout']['useLines'] = False
#                self.layoutConfig['PageLayout']['useBoxBoarder'] = False
#                change = True

#        if change :
#            if self.tools.writeConfFile(self.layoutConfig) :
#                self.log.writeToLog(self.errorCodes['0220'], [bType])
#        else :
#            self.log.writeToLog(self.errorCodes['0240'], [bType])


#    def removeBackground (self, bType) :
#        '''Remove a page background type.'''

#        change = False
#        if bType == 'watermark' :
#            # Turn it off if it is on but do not do anything with the watermark file
#            if self.useWatermark == True :
#                self.layoutConfig['PageLayout']['useWatermark'] = False
#                change = True
#        elif bType == 'lines' :
#            if self.useLines == True :
#                self.layoutConfig['PageLayout']['useLines'] = False
#                change = True
#        elif bType == 'boarder' :
#                self.layoutConfig['PageLayout']['useBoxBoarder'] = False
#                change = True
#        elif bType == 'cropmarks' :
#                self.layoutConfig['PageLayout']['useCropmarks'] = False
#                change = True

#        if change :
#            if self.tools.writeConfFile(self.layoutConfig) :
#                self.log.writeToLog(self.errorCodes['0230'], [bType])
#        else :
#            self.log.writeToLog(self.errorCodes['0240'], [bType])


    def checkForBackground (self, bg, mode) :
        '''Check to see if a required backgound file is present. If not,
        make it so.'''

        bgFileName      = bg + '.pdf'
        projBgFile      = os.path.join(self.projIllustrationsFolder, bgFileName)
        if not os.path.exists(projBgFile) :
            if bg.find('lines') >= 0 :
                self.installLinesFile(projBgFile)
            elif bg.find('box') >= 0 :
                self.installBoxBoarderFile(projBgFile)
            else :
                self.installWatermarkFile(projBgFile, mode)


    def installWatermarkFile (self, target, mode) :
        '''Install a default Rapuma watermark file into the project.'''

        # FIXME: A custom watermark creation function is needed here, load default for now
        rpmDefWatermarkFile = os.path.join(self.rpmIllustrationsFolder, mode + 'Watermark.pdf')

        try :
            shutil.copy(rpmDefWatermarkFile, target)
            self.log.writeToLog(self.errorCodes['0280'], [self.tools.fName(target)])
        except Exception as e :
            # If this doesn't work, we should probably quit here
            self.log.writeToLog(self.errorCodes['0290'], [self.tools.fName(target),str(e)])


    def installBoxBoarderFile (self, target) :
        '''Install a background lines file into the project.'''

        # FIXME: A custom box watermark creation function is needed here, load default for now
        rpmDefBoxWatermarkFile = os.path.join(self.rpmIllustrationsFolder, 'box_view-210x145.pdf')

        try :
            shutil.copy(rpmDefBoxWatermarkFile, target)
            self.log.writeToLog(self.errorCodes['0280'], [self.tools.fName(target)])
        except Exception as e :
            # If this doesn't work, we should probably quit here
            self.log.writeToLog(self.errorCodes['0290'], [self.tools.fName(target),str(e)])


    def installLinesFile (self, target) :
        '''Install a background lines file into the project.'''

        try :
            if self.createLinesFile(target) :
                self.log.writeToLog(self.errorCodes['0280'], [self.tools.fName(target)])
                return True
        except Exception as e :
            # If this doesn't work, we should probably quit here
            self.log.writeToLog(self.errorCodes['0290'], [self.tools.fName(target),str(e)])


    def createLinesFile (self, bgLinesFile) :
        '''Create a lines background file used for composition work. The code
        in this file came from Flip Wester (flip_wester@sil.org)'''

        # Set our file names
        source = os.path.join(self.rpmIllustrationsFolder, 'grid.svg')
        output = os.path.join(self.projIllustrationsFolder,  'lines-grid.svg')
        final_output = bgLinesFile

        # input and calculation
        # get the values  for lineSpaceFactor and fontSizeUnit
        # from Rapuma book_layout.conf 
        pageHeight          = int(self.layoutConfig['PageLayout']['pageHeight'])
        pageWidth           = int(self.layoutConfig['PageLayout']['pageWidth'])
        #lineSpacingFactor   = int(float(self.layoutConfig['Fonts']['lineSpacingFactor']))
        lineSpacingFactor   = float(self.layoutConfig['Fonts']['lineSpacingFactor'])
        #fontSizeUnit        = int(float(self.layoutConfig['Fonts']['fontSizeUnit'].replace('pt', '')))
        fontSizeUnit        = float(self.layoutConfig['Fonts']['fontSizeUnit'].replace('pt', ''))
        marginUnit          = int(self.layoutConfig['Margins']['marginUnit'])
        #topMarginFactor     = int(float(self.layoutConfig['Margins']['topMarginFactor']))
        topMarginFactor     = float(self.layoutConfig['Margins']['topMarginFactor'])
        #bottomMarginFactor  = int(float(self.layoutConfig['Margins']['bottomMarginFactor']))
        bottomMarginFactor  = float(self.layoutConfig['Margins']['bottomMarginFactor'])

# FIXME: If the fontSizeUnit is less than 1 this will fail and cause the script to hang
# SOLUTION: 
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
        print 'Space between lines: ', baselineskip, 'px'

        # The topMargin position depends on the pagesize and defined in [mm]. It needs to be
        # converted to pixels [px]
        topMargin = round((pageHeight - topMarginFactor * marginUnit)*90/25.4, 3)
        print 'topMargin: ', topMargin, 'px'

        # The distance topMargin to firstBaseLine happens to be equal to the font size in pixels
        # based on pixel [px] measurements in Inkscape 
        topskip = round((1.25 * 12 * fontSizeUnit),3)
        #topskip = round((0.8 * 12 * fontSizeUnit),3)
        print 'topskipcalc: ', topskip

        # The firstBaseLine is topMargin minus topskip in [px] 
        firstBaseLine = topMargin - topskip
        print 'firstBaseLine: ', firstBaseLine

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
        except Exception as e :
            print 'Error found: ' + str(e)
            
        return True


