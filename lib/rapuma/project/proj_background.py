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


class ProjBackground (object) :

    def __init__(self, pid) :
        '''Intitate the whole class and create the object.'''
        
# FIXME: Doing a complete rewrite to allow this process to occure at any time in the process

#        import pdb; pdb.set_trace()

        self.pid                        = pid
        self.tools                      = Tools()

        # Log messages for this module
        self.errorCodes     = {

            '0000' : ['MSG', 'Placeholder message'],

        }


###############################################################################
############################### Basic Functions ###############################
###############################################################################
######################## Error Code Block Series = 0200 #######################
###############################################################################

    def addCropmarksBackground (self, target) :
        '''Add a background that puts cropmarks around the page area.'''

        print 'Calling: addCropmarksBackground()'


    def addBoxBackground (self, target) :
        '''Add a background that puts a box around the page area.'''

        print 'Calling: addBoxBackground()'


    def addLinesBackground (self, target) :
        '''Add a background that has lines that represent the type
        leading.'''

        print 'Calling: addLinesBackground()'


    def addWatermarkBackground (self, gid, cid_list, pages, override) :
        '''Add a background (watermark) to a specific PDF file.'''

# Start rewrite here
        print 'Calling: addWatermarkBackground()'
        print gid, cid_list, pages, override


    def createWatermarkFile (self, watermark) :
        '''Create a watermark file and return the file name.'''

        print 'Calling: createWatermarkFile()'
        

    def createBoxFile (self, pdfOutFile) :
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
        debug = False

        # input and calculation
        # get the values  for lineSpaceFactor and fontSizeUnit
        # from Rapuma usfm_layout.conf 
        pageHeight          = float(self.layoutConfig['PageLayout']['pageHeight'])
        pageWidth           = float(self.layoutConfig['PageLayout']['pageWidth'])
        bodyFontSize        = float(self.layoutConfig['TextElements']['bodyFontSize'])
        bodyTextLeading     = float(self.layoutConfig['TextElements']['bodyTextLeading'])
        topMargin           = float(self.layoutConfig['PageLayout']['topMargin'])
        bottomMargin        = float(self.layoutConfig['PageLayout']['bottomMargin'])
        outsideMargin       = float(self.layoutConfig['PageLayout']['outsideMargin'])
        insideMargin        = float(self.layoutConfig['PageLayout']['insideMargin'])
        textWidth           = pageWidth - (outsideMargin + insideMargin)

        # The page dimensions are given in [mm] but are converted to pixels [px],
        # the conversion factor for [mm] to [px] is 90/25.4 
        def mmToPx (mm) :
            return round(mm * 90 / 25.4, 2)
            
        # paper height [px]
        paperPxHeight = mmToPx(pageHeight)
        # paper width [px]
        paperPxWidth = mmToPx(pageWidth)
        # text width [px]
        textPxWidth = mmToPx(textWidth)
        # top margin [px]
        topPxMargin = mmToPx(topMargin)
        # outside margin [px]
        outsidePxMargin = mmToPx(outsideMargin)
        # inside margin [px]
        insidePxMargin = mmToPx(outsideMargin)
        # bottom margin [px]
        bottomPxMargin = mmToPx(bottomMargin)

        # The font and leading are given in TeX point [pt] and are converted 
        # to pixels [px], the conversion factor for [pt] to [px] is 90/72.27 
        # bodyFontSize [px]
        bodyFontPxSize =  round(bodyFontSize * 90/72.27,2)
        # bodyTextLeading [px]
        bodyTextPxLeading =  round(bodyTextLeading * 90/72.27,2)    

        # Grid positions are measured from the top left of the page.
        # The grid starts at the top margin
        if debug :
            self.tools.terminal('Grid dimensions are in [px] = 1/90 in')
            self.tools.terminal('top margin: ' + str(topPxMargin))
         
        # The first line of text is topskip down from the top margin
        topskip = bodyFontPxSize
        if debug :
            self.tools.terminal('topskip: ' + str(topskip))

        # The y-position of the first baseline of text is topPtmargin + topskip
        firstBaseLine = topPxMargin + topskip        
        if debug :
            self.tools.terminal('firstBaseLine: ' + str(firstBaseLine))

        # The y-position of the next gridlines is baselineskip down from the previous
        baselineskip = bodyTextPxLeading
        if debug :
            self.tools.terminal('baselineskip: ' + str(baselineskip))
                
        # The last gridline is just before or on the bottom margin 
        bottomMarginTtb = paperPxHeight - bottomPxMargin
        if debug :
            self.tools.terminal('bottom margin from the top: ' + str(bottomMarginTtb))

        # Overall dimensions of the grid
        # Grid Height
        lineGridHeight = round(bottomMarginTtb - firstBaseLine)

        # Grid Width
        lineGridWidth = round(textPxWidth + outsidePxMargin * 0.25, 2) 
        if debug :
            self.tools.terminal('Grid H x W: ' + str(lineGridHeight) + ' x ' + str(lineGridWidth))

        # left Grid border
        leftGridMargin = round(outsidePxMargin * 0.75,2)

        # right Grid border
        rightGridMargin=round(textPxWidth + outsidePxMargin,2)

        # number position in relation to left grid border
        lineNumberPos = leftGridMargin-3

        # Grid bottom 
        posGridBottom = bottomMarginTtb

        # Create the temporary template file
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

        <!-- LINeGRID MARGINS top, bottom, left and right--> 

            <path 
               d="M ''')
        fo.write(str (outsidePxMargin))
        fo.write("," )
        fo.write(str (topPxMargin))
        fo.write(" " )
        fo.write(str (rightGridMargin))
        fo.write("," )
        fo.write(str (topPxMargin))
        fo.write('''"
                       style="fill:#ffffff;fill-opacity:1;stroke-width:0.2px;stroke:rgb(118,000,118);stroke-opacity:1"/>
            <path 
            
              d="M ''')
        fo.write(str (outsidePxMargin))
        fo.write("," )
        fo.write(str (topPxMargin))
        fo.write(" " )
        fo.write(str (outsidePxMargin))
        fo.write("," )
        fo.write(str (bottomMarginTtb))
        fo.write( '''"
                  style="fill:#ffffff;fill-opacity:1;stroke-width:0.2px;stroke:rgb(255,200,0);stroke-opacity:1"/>

            <path 
               d="M ''')
        fo.write(str (outsidePxMargin))
        fo.write("," )
        fo.write(str (bottomMarginTtb))
        fo.write(" " )
        fo.write(str (rightGridMargin))
        fo.write("," )
        fo.write(str (bottomMarginTtb))
        fo.write('''"
                       style="fill:#ffffff;fill-opacity:1;stroke-width:0.2px;stroke:rgb(118,000,118);stroke-opacity:1"/>
                       
            <path 
               d="M ''')
        fo.write(str (rightGridMargin))
        fo.write("," )
        fo.write(str (topPxMargin))
        fo.write(" " )
        fo.write(str (rightGridMargin))
        fo.write("," )
        fo.write(str (bottomMarginTtb))

        fo.write( '''"
                  style="fill:#ffffff;fill-opacity:1;stroke-width:0.2px;stroke:rgb(255,200,0);stroke-opacity:1"/> ''')

        fo.write( ''' <!-- THE ACTUAL LINEGRID --> 
                                  
            <path       
               d= "m ''')
        fo.write(str (leftGridMargin-1))
        fo.write("," )
        fo.write(str (firstBaseLine))
        fo.write(" " )
        fo.write(str (lineGridWidth))
        fo.write( ''',0\n''')
               
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
        fo.write(str (firstBaseLine-3))
        fo.write( '''" style="font-family: Charis SIL;font-style:italic;font-size:7;fill:rgb(118,000,118)\n">''')

        fo.write('''        <tspan x="''')
        fo.write(str (lineNumberPos))
        fo.write( '''" dy="0" >1</tspan>\n''')    

        num = 0
        linecount = 2
        while (num < int(lineGridHeight/baselineskip)):

            fo.write( '''           <tspan x="''')
            fo.write(str (lineNumberPos))
            fo.write('''" dy="''' )
            fo.write(str (baselineskip))
            fo.write( '''">''')
            fo.write(str (linecount))
            fo.write('''</tspan>\n''') 
            
            linecount = linecount +1  

            num = num +1
            
        fo.write('''    </text>

        <!-- LINE OF TEXT IN THE BOTTOM MARGIN --> 

            <text  x="36" y="''')
        fo.write(str (bottomMarginTtb+10))
        fo.write('''" style="font-family: Charis SIL;font-style:italic;font-size:7;fill:rgb(255,200,0)"
            >page size: ''')
        fo.write(str (pageWidth))
        fo.write('''x''')
        fo.write(str (pageHeight))
        fo.write(''' mm ; font size: ''')
        fo.write(str (bodyFontSize))
        fo.write(''' pt; leading: ''')
        fo.write(str (bodyTextLeading))
        fo.write(''' pt</text>
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


    
    
