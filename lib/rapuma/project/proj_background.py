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

import codecs, os, difflib, subprocess, shutil, re, tempfile
from configobj                          import ConfigObj

# Load the local classes
from rapuma.core.tools                  import Tools
from rapuma.core.user_config            import UserConfig
from rapuma.core.proj_local             import ProjLocal
from rapuma.core.proj_log               import ProjLog
from rapuma.project.proj_config         import Config
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
        self.svgPdfConverter            = self.userConfig['System']['svgPdfConvertCommand']
        self.local                      = ProjLocal(pid, gid)
        self.proj_config                = Config(pid, gid)
        self.proj_config.getProjectConfig()
        self.proj_config.getLayoutConfig()
        self.projectConfig              = self.proj_config.projectConfig
        self.layoutConfig               = self.proj_config.layoutConfig
        self.log                        = ProjLog(pid)
        self.cType                      = self.projectConfig['Groups'][gid]['cType']
        self.Ctype                      = self.cType.capitalize()
        self.macPack                    = None
        self.macPackConfig              = None
        self.macPackFunctions           = None
        if self.projectConfig['CompTypes'][self.Ctype].has_key('macroPackage') and self.projectConfig['CompTypes'][self.Ctype]['macroPackage'] != '' :
            self.macPack                = self.projectConfig['CompTypes'][self.Ctype]['macroPackage']
            self.proj_config.getMacPackConfig(self.macPack)
            self.proj_config.loadMacPackFunctions(self.macPack)
            self.macPackConfig          = self.proj_config.macPackConfig
            self.macPackFunctions       = self.proj_config.macPackFunctions

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

        bgList = self.projectConfig['Managers']['usfm_Xetex'][outType + 'Background']
        if not bgName in bgList :
            bgList.append(bgName)
            self.projectConfig['Managers']['usfm_Xetex'][outType + 'Background'] = bgList
            self.tools.writeConfFile(self.projectConfig)
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

        bgList = self.projectConfig['Managers']['usfm_Xetex'][outType + 'Background']
        if bgName in bgList :
            bgList.remove(bgName)
            self.projectConfig['Managers']['usfm_Xetex'][outType + 'Background'] = bgList
            self.tools.writeConfFile(self.projectConfig)
            self.log.writeToLog(self.errorCodes['0240'], [bgName, outType])
        else :
            self.log.writeToLog(self.errorCodes['0250'], [bgName, outType])


    def updateBackground (self, outType, bgrd) :
        '''Update a background for a specific output type.'''

        bgName = bgrd
        # Handle cropmarks
        if bgrd != 'cropmarks' :
            bgName = bgrd + 'Watermark'

        bgList = self.projectConfig['Managers']['usfm_Xetex'][outType + 'Background']
        if bgName in bgList :
            if bgrd != 'cropmarks' :
                self.checkForBackground(bgName, outType, True)
            self.log.writeToLog(self.errorCodes['0260'], [bgName, outType])
        else :
            self.log.writeToLog(self.errorCodes['0270'], [bgName, outType])


    def checkForBackground (self, bg, mode, force = False) :
        '''Check to see if a required backgound file is present. If not,
        make it so.'''

        projBgFile      = os.path.join(self.local.projIllustrationFolder, bg + '.pdf')
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
        rpmDefWatermarkFile = os.path.join(self.local.rapumaIllustrationFolder, mode + 'Watermark.pdf')

        try :
            shutil.copy(rpmDefWatermarkFile, target)
            self.log.writeToLog(self.errorCodes['0280'], [self.tools.fName(target)])
        except Exception as e :
            # If this doesn't work, we should probably quit here
            self.log.writeToLog(self.errorCodes['0290'], [self.tools.fName(target),str(e)])


    def createBorderFile (self, pdfOutFile) :
        '''Create a border backgound file used for proof reading.'''

        # Set our file names
        borderSource        = os.path.join(self.local.rapumaIllustrationFolder, 'border.svg')
        svgInFile           = tempfile.NamedTemporaryFile().name + '.svg'

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

        # Read in the borderSource file
        contents = codecs.open(borderSource, "rt", encoding="utf_8_sig").read()

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
        codecs.open(svgInFile, "wt", encoding="utf_8_sig").write(contents)

        # Run the conversion utility
        if self.convertSvgToPdf(svgInFile, pdfOutFile) :
            return True


    def createLinesFile (self, pdfOutFile) :
        '''Create a lines background file used for composition work. The code
        in this file came from Flip Wester (flip_wester@sil.org)'''

        # Set our file names
        gridSource          = os.path.join(self.local.rapumaIllustrationFolder, 'grid.svg')
        svgInFile           = tempfile.NamedTemporaryFile().name + '.svg'

        # For testing
        debug = True

        # input and calculation
        # get the values  for lineSpaceFactor and fontSizeUnit
        # from Rapuma usfm_layout.conf 
        pageHeight          = float(self.layoutConfig['PageLayout']['pageHeight'])
        pageWidth           = float(self.layoutConfig['PageLayout']['pageWidth'])

        fontSizeUnit        = self.macPackFunctions.getFontSizeUnit()
        lineSpacingFactor   = self.macPackFunctions.getLineSpacingFactor()
        marginUnit          = self.macPackFunctions.getMarginUnit()
        topMarginFactor     = self.macPackFunctions.getTopMarginFactor()
        bottomMarginFactor  = self.macPackFunctions.getBottomMarginFactor()

        topMargin           = float(self.layoutConfig['PageLayout']['topMargin'])
        bottomMargin        = float(self.layoutConfig['PageLayout']['bottomMargin'])
        outsideMargin       = float(self.layoutConfig['PageLayout']['outsideMargin'])
        insideMargin        = float(self.layoutConfig['PageLayout']['insideMargin'])
        textWidth           = pageWidth - (outsideMargin + insideMargin)

        # The values of lineSpacingFactor, fontSizeUnit, topMarginFactor and bottomMarginFactor
        # are configured as floats. Changing them to integer reduces fontSizeUnits <1 to 0,
        # causing the script to hang. Changing the values back to floats solves the problem.

        # The page size is defined in [mm] but is entered in pixels [px] and points [pt]. 
        # The conversion factor for [px] is 90/25.4 and for [pt] 72/25.4.
        
        def mmToPx (mm) :
            return round(mm * 90 / 25.4, 2)

        def mmToPt (mm) :
            return int(mm * 72 / 25.4)

        # paper height [px]
        paperPxHeight = mmToPx(pageHeight)
        # paper height [pt]
        paperPtHeight = mmToPt(pageHeight)
        # paper width [px]
        paperPxWidth = mmToPx(pageWidth)
        # paper width [pt]
        paperPtWidth = mmToPt(pageWidth)
        # text width [px]
        textPxWidth = mmToPx(textWidth)
        # text width [pt]
        textPtWidth = mmToPt(textWidth)
        # top margin [px]
        topPxMargin = mmToPx(topMargin)
        # outside margin [px]
        outsidePxMargin = mmToPx(outsideMargin)

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
        if debug :
            self.tools.terminal('topskipcalc: ' + str(topskip))

        # The firstBaseLine is topMargin minus topskip in [px] 
        firstBaseLine = topMargin - topskip
        if debug :
            self.tools.terminal('firstBaseLine: ' + str(firstBaseLine))
        firstBaseLineTtb = round((paperPxHeight - firstBaseLine),3) # from top of page
        if debug :
            self.tools.terminal('firstBaseLineTtb: ' + str(firstBaseLineTtb))

        # The dimensions of the grid rectangle are needed to prepare a placeholder for the
        # gridlines. 
        lineGridHeight = round(firstBaseLine - bottomMarginFactor * marginUnit*90/25.40, 3)
        if debug :
            self.tools.terminal('lineGridHeight: ' + str(lineGridHeight))

        lineGridWidth = textPxWidth
        if debug :
            self.tools.terminal('lineGridWidth: ' + str(lineGridWidth))

        lineGridMargin = outsidePxMargin
        if debug :
            self.tools.terminal('lineGridMargin: ' + str(lineGridMargin))

        # Set the position where the line numbers get printed, this is
        # just to the left of the lineGridMargin
        lineNumberPos = lineGridMargin - 10

        # Open the temp svg file
        fo = open(svgInFile, "wb")
        fo.write( '''<?xml version="1.0" standalone="no"?>
        <!DOCTYPE svg SYSTEM "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
        <svg xmlns="http://www.w3.org/2000/svg"
             version="1.1" width="''')
        fo.write(str (paperPxWidth))
        fo.write( '''" height="''')
        fo.write(str (paperPxHeight))
        fo.write( '''">
          <g>
            <title>linegrid</title>
            <desc>
              This a sheet with lines.
            </desc>
        <!-- PARTIAL FRAME FOR LINE NUMBER 1 AT TOP OF LINEGRID -->
            <path 
               d="M ''')
        fo.write(str (lineGridMargin))
        fo.write(" " )
        fo.write(str (firstBaseLineTtb))
        fo.write(" v-" )
        fo.write(str (topskip))
        fo.write( ''' h 15"
                  style="fill:#ffffff;fill-opacity:1;stroke-width:0.2px;stroke:rgb(255,200,0);stroke-opacity:1"/>
        <!-- VERTICAL LINE ALONG LEFT OF LINEGRID --> 
            <path
               d="m ''')
        fo.write(str (lineGridMargin))
        fo.write("," )
        fo.write(str (firstBaseLineTtb))
        fo.write(" 0," )
        fo.write(str (lineGridHeight))
        fo.write( '''"
                  style="stroke-width:0.2px;stroke:rgb(255,200,0);stroke-opacity:1"/>
        <!-- THE ACTUAL LINEGRID --> 
        
            <path       
               d= "m ''')
        # top most line on the page below the top margin
        fo.write(str (lineGridMargin))
        fo.write("," )
        fo.write(str (firstBaseLineTtb))
        fo.write(" " )
        fo.write(str (lineGridWidth))
        fo.write( ''',0\n''')
        # while loop to generate lines to the bottom margin        
        num = 0
        while (num < int(lineGridHeight/baselineskip)):

            if num%2 == 0: 
                fo.write( '''           m 0, ''')
                fo.write(str (baselineskip))
                fo.write(" -" )
                fo.write(str (lineGridWidth))
                fo.write( ''',0\n''')
            else:
                fo.write( '''           m 0, ''')
                fo.write(str (baselineskip))
                fo.write(" " )
                fo.write(str (lineGridWidth))
                fo.write( ''',0\n''')
            num = num +1

        fo.write( '''"           style="stroke-width:0.2px;stroke:rgb(255,200,0);stroke-opacity:1"/>
                   
        <!-- LINE NUMBERS --> 
                   
            <text  y="''')
        # vertical position of the line numbers
        fo.write(str (firstBaseLineTtb))
        fo.write( '''" style="font-family: Charis SIL;font-style:italic;font-size:5;fill:rgb(200,100,0)\n">''')
        # line number 1 beside the top most line on the page
        fo.write('''        <tspan x="''')
        fo.write(str (lineNumberPos))
        fo.write( '''" dy="0" baseline-shift="super">1</tspan>\n''')    
        # while loop to place line numbers from the second line down
        num = 0
        linecount = 2
        while (num < int(lineGridHeight/baselineskip)):

            fo.write( '''           <tspan x="''')
            fo.write(str (lineNumberPos))
            fo.write('''" dy="''' )
            fo.write(str (baselineskip))
            fo.write( '''" baseline-shift="super">''')
            fo.write(str (linecount))
            fo.write('''</tspan>\n''') 
            
            linecount = linecount +1  

            num = num +1
            
        fo.write('''    </text>
          </g>
        </svg>''')
        # Close opened file
        fo.close()

        # Run the conversion utility to convert the temp svg to pdf
        if self.convertSvgToPdf(svgInFile, pdfOutFile) :
            return True


    def buildCommandList (self, svgInFile, pdfOutFile) :
        '''Convert a command line from the config that has keys in it for
        input and output files. The commands in the config should look like
        this coming in:
            svgPdfConverter = convert,svgInFile,pdfOutFile
            svgPdfConverter = rsvg-convert,-f,pdf,-o,pdfOutFile,svgInFile
            svgPdfConverter = inkscape,-f,svgInFile,-A,pdfOutFile
        This will insert the right value for svgInFile and pdfOutFile.'''

        cmds = list()
        for c in self.svgPdfConverter :
            if c == 'svgInFile' :
                cmds.append(svgInFile)
            elif c == 'pdfOutFile' :
                cmds.append(pdfOutFile)
            else :
                cmds.append(c)

        return cmds















    def convertSvgToPdf (self, svgInFile, pdfOutFile) :
        '''Convert/render an SVG file to produce a PDF file.'''

        # Simple try statement seems to work best for this
        try:
            subprocess.call(self.buildCommandList(svgInFile, pdfOutFile)) 
            return True
        except Exception as e :
            self.log.writeToLog(self.errorCodes['0290'], [self.tools.fName(pdfOutFile),str(e)])


