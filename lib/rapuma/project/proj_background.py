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

import codecs, os, difflib, subprocess, shutil, re, tempfile, pyPdf
from pyPdf                              import PdfFileReader
from configobj                          import ConfigObj

# Load the local classes
from rapuma.core.tools                  import Tools
from rapuma.core.user_config            import UserConfig
from rapuma.project.proj_config         import Config
from rapuma.core.proj_local             import ProjLocal
from rapuma.core.proj_log               import ProjLog


class ProjBackground (object) :

    def __init__(self, pid, gid = None) :
        '''Intitate the whole class and create the object.'''
        
# FIXME: Doing a complete rewrite to allow this process to occure at any time in the process

#        import pdb; pdb.set_trace()

        self.pid                        = pid
        self.gid                        = gid
        self.local                      = ProjLocal(pid, gid)
        self.tools                      = Tools()
        self.proj_config                = Config(pid, gid)
        self.proj_config.getProjectConfig()
        self.proj_config.getLayoutConfig()
        self.projectConfig              = self.proj_config.projectConfig
        self.layoutConfig               = self.proj_config.layoutConfig
        self.log                        = ProjLog(pid)
        self.user                       = UserConfig()
        self.userConfig                 = self.user.userConfig
        self.projHome                   = os.path.join(self.userConfig['Resources']['projects'], self.pid)
        self.svgPdfConverter            = self.userConfig['System']['svgPdfConvertCommand']


        # Log messages for this module
        self.errorCodes     = {

            '0000' : ['MSG', 'Placeholder message'],
            '1110' : ['MSG', 'File exsits: [<<1>>]. Use \"force\" to remove it.'],
            '1280' : ['ERR', 'Failed to merge background file with command: [<<1>>]. This is the error: [<<2>>]'],
            '1290' : ['ERR', 'Failed to convert background file [<<1>>]. Error: [<<2>>]'],
            '1300' : ['MSG', 'Background merge operation in process, please wait...'],

        }


###############################################################################
############################### Basic Functions ###############################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################


    def addBackground (self, target, force = False) :
        '''Add a background (watermark) to a rendered PDF file. This will
        figure out what the background is to be composed of and create
        a master background page. Using force will cause it to be remade.'''

# FIXME(1): Need to figure out a way to keep intact the original target so
# it can be delivered without having to be rerendered. This will prevent
# possible problems of things not rendering exactly the same. The output
# the client reviews should be the output that is delivered.

# FIXME(2): Adding the background slows performance. There needs to be a
# a way to do this faster. The centerOnPrintPage() seems to be the problem
# GS tends to take longer than pdftk but when merging, pdftk cannot
# maintain the individual sizes of two docs. One will always be stretched
# or shrunk. GS over comes that, but at the cost of speed.

        # Do a quick check if the background needs to be remade
        if force :
            self.createBlankBackground()
            # Add each component to the blank background file
            for comp in self.layoutConfig['DocumentFeatures']['backgroundComponents'] :
                getattr(self, 'merge' + comp.capitalize())()
        else :
            # If there isn't one, make it
            if not os.path.exists(self.local.backgroundFile) :
                self.createBlankBackground()
                # Add each component to the blank background file
                for comp in self.layoutConfig['DocumentFeatures']['backgroundComponents'] :
                    getattr(self, 'merge' + comp.capitalize())()

        # Merge target with the background
        self.log.writeToLog(self.errorCodes['1300'])
        shutil.copy(self.mergePdfFilesPdftk(self.centerOnPrintPage(target), self.local.backgroundFile), target)

        return True


    def addDocInfo (self, target) :
        '''Add (merge) document information to the rendered target doc.'''

        # Initialize the process
        docInfoText         = self.layoutConfig['DocumentFeatures']['docInfoText']
        timestamp           = self.tools.tStamp()
        headerLine          = self.pid + ' / ' + self.gid + ' / ' + timestamp
        svgFile             = tempfile.NamedTemporaryFile().name
        pdfFile             = tempfile.NamedTemporaryFile().name

        ## RENDERED PAGE DIMENSIONS (body)
        # This can be determined with the pyPdf element 
        # "pdf.getPage(0).mediaBox", which returns a 
        # RectangleObject([0, 0, Width, Height]). The
        # width and height are in points. Hopefully we will
        # always be safe by measuring the gidPdfFile size.
        pdf = PdfFileReader(open(self.local.gidPdfFile,'rb'))
        var2 = pdf.getPage(0).mediaBox
        bdWidth = float(var2.getWidth())
        bdHeight = float(var2.getHeight())
        # Printer page size
        pps = self.printerPageSize()
        pgWidth = pps[0]
        pgHeight = pps[1]
        pgCenter = pgWidth/2

        #   Write out SVG document text 
        with codecs.open(svgFile, 'wb') as fbackgr :            # open file for writing 
            fbackgr.write( '''<svg xmlns="http://www.w3.org/2000/svg"
                version="1.1" width = "''' + str(pgWidth) + '''" height = "''' + str(pgHeight) + '''">
                <g><text x = "''' + str(pgCenter) + '''" y = "''' + str(20) + '''" style="font-family:DejaVu Sans;font-style:regular;font-size:8;text-anchor:middle;fill:#000000;fill-opacity:1">''' + headerLine + '''</text></g>
                <g><text x = "''' + str(pgCenter) + '''" y = "''' + str(pgHeight-30) + '''" style="font-family:DejaVu Sans;font-style:regular;font-size:8;text-anchor:middle;fill:#000000;fill-opacity:1">''' + self.tools.fName(target) + '''</text></g>
                <g><text x = "''' + str(pgCenter) + '''" y = "''' + str(pgHeight-20) + '''" style="font-family:DejaVu Sans;font-style:regular;font-size:8;text-anchor:middle;fill:#000000;fill-opacity:1">''' + docInfoText + '''</text></g>
                </svg>''')

        self.convertSvgToPdf(svgFile, pdfFile)
        # Merge target with the background
        self.log.writeToLog(self.errorCodes['1300'])
        shutil.copy(self.mergePdfFilesPdftk(self.centerOnPrintPage(target), pdfFile), target)
        
        return True


    ##### Background Creation Functions #####

    def createBlankBackground (self) :
        '''Create a blank background page according to the print page
        size specified. If force is used, the page will be remade.'''
        
        # Set the temp svg file name
        svgFile   = tempfile.NamedTemporaryFile().name

        # Printer page size
        pps = self.printerPageSize()
        pgWidth = pps[0]
        pgHeight = pps[1]

        # Be sure there is an illustrations folder in place
        if not os.path.isdir(self.local.projIllustrationFolder) :
            os.mkdir(self.local.projIllustrationFolder)

        #   Write out SVG document text 
        with codecs.open(svgFile, 'wb') as fbackgr :            # open file for writing 
            fbackgr.write( '''<svg xmlns="http://www.w3.org/2000/svg"
                version="1.1" width = "''' + str(pgWidth) + '''" height = "''' + str(pgHeight)+ '''">
                </svg>''')

        self.convertSvgToPdf(svgFile, self.local.backgroundFile)


    def mergeWatermark (self) :
        '''Create a watermark file and return the file name. Using force
        will cause any exsiting versions to be recreated.'''

#        import pdb; pdb.set_trace()

        # Initialize the process
        pubProg             = "Rapuma"
        watermarkText       = self.layoutConfig['DocumentFeatures']['watermarkText']
        svgFile             = tempfile.NamedTemporaryFile().name
        pdfFile             = tempfile.NamedTemporaryFile().name

        ## RENDERED PAGE DIMENSIONS (body)
        # This can be determined with the pyPdf element 
        # "pdf.getPage(0).mediaBox", which returns a 
        # RectangleObject([0, 0, Width, Height]). The
        # width and height are in points. Hopefully we will
        # always be safe by measuring the gidPdfFile size.
        pdf = PdfFileReader(open(self.local.gidPdfFile,'rb'))
        var2 = pdf.getPage(0).mediaBox
        bdWidth = float(var2.getWidth())
        bdHeight = float(var2.getHeight())
        # Printer page size
        pps = self.printerPageSize()
        pgWidth = pps[0]
        pgHeight = pps[1]

        #   Write out SVG document text 
        with codecs.open(svgFile, 'wb') as fbackgr :            # open file for writing 
            fbackgr.write( '''<svg xmlns="http://www.w3.org/2000/svg"
                version="1.1" width = "''' + str(pgWidth) + '''" height = "''' + str(pgHeight)+ '''">
                <g><text x = "''' + str((pgWidth - bdWidth)/2 + 54) + '''" y = "''' + str((pgHeight - bdHeight)/2 + 120) + '''" style="font-family:DejaVu Sans;font-style:regular;font-size:32;text-anchor:start;fill:#e6e6ff;fill-opacity:1">''' + str(pubProg)+'''
                <tspan x = "''' + str((pgWidth)/2) + '''" y = "''' + str((pgHeight - bdHeight)/2 + 194)+ '''" style="text-anchor:middle">''' + str(pubProg) + '''</tspan>
                <tspan x = "''' + str((pgWidth + bdWidth)/2-54)+ '''" y = "''' + str((pgHeight - bdHeight)/2 + 268) + '''" style="text-anchor:end">''' + str(pubProg) + '''</tspan>
                <tspan x = "''' + str(pgWidth/2) + '''" y = "''' + str((pgHeight - bdHeight)/2 + 342)+ '''" style="text-anchor:middle">''' + str(pubProg) + '''</tspan>
                <tspan x = "''' + str((pgWidth - bdWidth)/2 + 54)+ '''" y = "''' + str((pgHeight - bdHeight)/2 + 416) + '''" style="text-anchor:start">''' + str(pubProg) + '''</tspan>
                <tspan x = "''' + str((pgWidth + bdWidth)/2 - 36)+ '''" y = "''' + str((pgHeight - bdHeight)/2 + 520 + 36)+ '''" style="font-weight:bold;font-size:68;text-anchor:end">''' + watermarkText + ''' </tspan>
                </text></g></svg>''')

        self.convertSvgToPdf(svgFile, pdfFile)
        self.mergePdfFilesPdftk(self.local.backgroundFile, pdfFile)
        
        return True


    def mergeCropmarks (self) :
        '''Merge cropmarks on to the background page.'''

        # Initialize the process
        svgFile             = tempfile.NamedTemporaryFile().name
        pdfFile             = tempfile.NamedTemporaryFile().name

        ## RENDERED PAGE DIMENSIONS (body)
        # This can be determined with the pyPdf element 
        # "pdf.getPage(0).mediaBox", which returns a 
        # RectangleObject([0, 0, Width, Height]). The
        # width and height are in points. Hopefully we will
        # always be safe by measuring the gidPdfFile size.
        pdf = PdfFileReader(open(self.local.gidPdfFile,'rb'))
        var2 = pdf.getPage(0).mediaBox
        bdWidth = float(var2.getWidth())
        bdHeight = float(var2.getHeight())
        # Printer page size
        pps = self.printerPageSize()
        pgWidth = pps[0]
        pgHeight = pps[1]

        with codecs.open(svgFile, 'wb') as fbackgr : 
                    # starting lines of SVG xml
            fbackgr.write( '''<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width = "''' + str(pgWidth) + '''" height = "''' + str(pgHeight) + '''">\n''') 
                    # vertical top left
            fbackgr.write( '''<path d = "m'''+str ((pgWidth - bdWidth)/2)+''','''+str ((pgHeight - bdHeight)/2 - 32.0)+''',v27," style="stroke:#000000;stroke-width:.2"/>\n''')   
                    # vertical bottom left
            fbackgr.write( '''<path d = "m'''+str ((pgWidth - bdWidth)/2)+''','''+str ((pgHeight + bdHeight)/2 + 5.0)+''',v27" style="stroke:#000000;stroke-width:.2" />\n''')
                    # vertical bottom right
            fbackgr.write( '''<path d = "m'''+str ((pgWidth + bdWidth)/2)+''','''+str ((pgHeight - bdHeight)/2 - 32.0)+''',v27" style="stroke:#000000;stroke-width:.2"/>\n''')
                    # vertical top right
            fbackgr.write( '''<path d = "m'''+str ((pgWidth + bdWidth)/2)+''','''+str ((pgHeight + bdHeight)/2 + 5.0)+''',v27" style="stroke:#000000;stroke-width:.2" />\n''')
                    # horzontal top left
            fbackgr.write( '''<path d =" m'''+str ((pgWidth - bdWidth)/2 - 32.0)+''','''+str ((pgHeight - bdHeight)/2)+''',h27" style="stroke:#000000;stroke-width:.2" />\n''')
                    # horzontal top right
            fbackgr.write( '''<path d =" m'''+str ((pgWidth + bdWidth)/2 + 5.0)+''','''+str ((pgHeight - bdHeight)/2)+''',h27" style="stroke:#000000;stroke-width:.2" />\n''')
                    # horzontal bottom right
            fbackgr.write( '''<path d =" m'''+str ((pgWidth - bdWidth)/2 - 32.0)+''','''+str ((pgHeight + bdHeight)/2)+''',h27" style="stroke:#000000;stroke-width:.2" />\n''')
                    # horzontal bottom left
            fbackgr.write( '''<path d =" m'''+str ((pgWidth + bdWidth)/2 +5.0)+''','''+str ((pgHeight + bdHeight)/2)+''',h27" style="stroke:#000000;stroke-width:.2" />\n''')
            fbackgr.write( '''</svg>''')

        self.convertSvgToPdf(svgFile, pdfFile)
        self.mergePdfFilesPdftk(self.local.backgroundFile, pdfFile)
        
        return True


    def mergePagebox (self) :
        '''Merge a page box with the background page to be used for proof reading.'''

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


    def mergeLines (self) :
        '''Merge a lines component with the background file.'''

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
        textWidth           = bdWidth - (outsideMargin + insideMargin)

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


    def centerOnPrintPage (self, contents) :
        '''Center a PDF file on the printerPageSize page. GhostScript
        is the only way to do this at this point.'''

#        import pdb; pdb.set_trace()

        # This breaks if the printerPageSizeCode is not A4 or US Letter
        printerPageSizeCode = self.layoutConfig['PageLayout']['printerPageSizeCode']
        tmpFile = tempfile.NamedTemporaryFile().name
        # Get the size of our printer page
        pps = self.printerPageSize()
        # Get the size of our contents page
        cPdf = PdfFileReader(open(contents,'rb'))
        var2 = cPdf.getPage(0).mediaBox
        bw = float(var2.getWidth())
        bh = float(var2.getHeight())
        # Get the offset. We assume that pps is bigger than the contents
        # Note: Offset is measured in points
        wo = float((int(pps[0]) - bw)/2)
        ho = float((int(pps[1]) - bh)/2)
        pageOffset = str(wo) + ' ' + str(ho)
        # Assemble the GhostScript command
        cmd = ['gs',  '-o', tmpFile,  '-sDEVICE=pdfwrite',  '-dQUIET', '-sPAPERSIZE=' + printerPageSizeCode.lower(),  '-dFIXEDMEDIA' , '-c', '<</PageOffset [' + str(pageOffset) + ']>>', 'setpagedevice', '-f', contents]
        # Run the process
        try:
            subprocess.call(cmd) 
            # Return the name of the temp PDF
            return tmpFile
        except Exception as e :
            self.log.writeToLog(self.errorCodes['1280'], [str(cmd), str(e)])
        # Return the temp file name for further processing


    def mergePdfFilesPdftk (self, front, back) :
        '''Merge two PDF files together using pdftk.'''

        tmpFile = tempfile.NamedTemporaryFile().name
        cmd = ['pdftk', front, 'background', back, 'output', tmpFile]
        try:
            subprocess.call(cmd) 
            shutil.copy(tmpFile, front)
            # Return the name of the primary PDF
            return front
        except Exception as e :
            self.log.writeToLog(self.errorCodes['1280'], [str(cmd), str(e)])


    def convertSvgToPdf (self, svgInFile, pdfOutFile) :
        '''Convert/render an SVG file to produce a PDF file.'''

        # Simple try statement seems to work best for this
        try:
            subprocess.call(self.buildCommandList(svgInFile, pdfOutFile)) 
            return True
        except Exception as e :
            self.log.writeToLog(self.errorCodes['1290'], [self.tools.fName(pdfOutFile),str(e)])


    def printerPageSize (self) :
        '''Return the width and height of the printer page size in
        points. If there is a problem just return the size for A4.
        Only US Letter and A4 are currently supported.'''
    
        size = []
        printerPageSizeCode = self.layoutConfig['PageLayout']['printerPageSizeCode']
        ## STANDARD PRINTER PAGE SIZES
        # The output page (printer page) is what the typeset page will be placed on
        # with a watermark behind it. There are only two page sizes supported.
        # They are A4 and US Letter. We will determine the size by the ID code
        # found in the layout.conf file. If that doesn't make sense, then just
        # default to the A4 size.
        if printerPageSizeCode.lower() == 'a4' :
            size.append(float(595))
            size.append(float(842))
        elif printerPageSizeCode.lower() == 'letter' :
            size.append(float(612))
            size.append(float(792))
        else :
            # Just use the default A4 size in pts so it doesn't die from this
            size.append(float(595))
            size.append(float(842))

        return [size[0], size[1]]



    
