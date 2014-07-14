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
#   Answer(1): Using "save", Have XeTeX preserve the original file name
#               and add extra information to the file(s) that have background
#               or doc info on them

# FIXME(2): Adding the background slows performance. There needs to be a
# a way to do this faster. The centerOnPrintPage() seems to be the problem
# GS tends to take longer than pdftk but when merging, pdftk cannot
# maintain the individual sizes of two docs. One will always be stretched
# or shrunk. GS over comes that, but at the cost of speed.

        # Do a quick check if the background needs to be remade
        if force :
            self.createBackground()
        else :
            # If there isn't one, make it
            if not os.path.exists(self.local.backgroundFile) :
                self.createBackground()

        # Merge target with the project's background file in the Illustraton folder
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

        ## RENDERED PAGE DIMENSIONS (body)
        # This can be determined with the pyPdf element 
        # "pdf.getPage(0).mediaBox", which returns a 
        # RectangleObject([0, 0, Width, Height]). The
        # width and height are in points. Hopefully we will
        # always be safe by measuring the gidPdfFile size.
        pdf         = PdfFileReader(open(self.local.gidPdfFile,'rb'))
        var2        = pdf.getPage(0).mediaBox
        bdWidth     = float(var2.getWidth())
        bdHeight    = float(var2.getHeight())
        # Printer page size
        pps         = self.printerPageSize()
        ppsWidth    = pps[0]
        ppsHeight   = pps[1]
        ppsCenter   = ppsWidth/2

        #   Write out SVG document text 
        with codecs.open(svgFile, 'wb') as fbackgr :            # open file for writing 
            fbackgr.write( '''<svg xmlns="http://www.w3.org/2000/svg"
                version="1.1" width = "''' + str(ppsWidth) + '''" height = "''' + str(ppsHeight) + '''">
                <g><text x = "''' + str(ppsCenter) + '''" y = "''' + str(20) + '''" style="font-family:DejaVu Sans;font-style:regular;font-size:8;text-anchor:middle;fill:#000000;fill-opacity:1">''' + headerLine + '''</text></g>
                <g><text x = "''' + str(ppsCenter) + '''" y = "''' + str(ppsHeight-30) + '''" style="font-family:DejaVu Sans;font-style:regular;font-size:8;text-anchor:middle;fill:#000000;fill-opacity:1">''' + self.tools.fName(target) + '''</text></g>
                <g><text x = "''' + str(ppsCenter) + '''" y = "''' + str(ppsHeight-20) + '''" style="font-family:DejaVu Sans;font-style:regular;font-size:8;text-anchor:middle;fill:#000000;fill-opacity:1">''' + docInfoText + '''</text></g>
                </svg>''')

        # Merge target with the background
        self.log.writeToLog(self.errorCodes['1300'])
        shutil.copy(self.mergePdfFilesPdftk(self.centerOnPrintPage(target), self.convertSvgToPdf(svgFile)), target)
        
        return True


    ##### Background Creation Functions #####

    def createBackground (self) :
        '''Create a background file. This will overwrite any existing
        background file.'''

        self.createBlankBackground()
        # Add each component to the blank background file
        for comp in self.layoutConfig['DocumentFeatures']['backgroundComponents'] :
            getattr(self, 'merge' + comp.capitalize())()


    def createBlankBackground (self) :
        '''Create a blank background page according to the print page
        size specified. If force is used, the page will be remade.'''
        
        # Set the temp svg file name
        svgFile   = tempfile.NamedTemporaryFile().name

        # Printer page size
        pps = self.printerPageSize()
        ppsWidth = pps[0]
        ppsHeight = pps[1]

        # Be sure there is an illustrations folder in place
        if not os.path.isdir(self.local.projIllustrationFolder) :
            os.mkdir(self.local.projIllustrationFolder)

        #   Write out SVG document text 
        with codecs.open(svgFile, 'wb') as fbackgr :            # open file for writing 
            fbackgr.write( '''<svg xmlns="http://www.w3.org/2000/svg"
                version="1.1" width = "''' + str(ppsWidth) + '''" height = "''' + str(ppsHeight)+ '''">
                </svg>''')

        shutil.copy(self.convertSvgToPdf(svgFile), self.local.backgroundFile)


    def mergeWatermark (self) :
        '''Create a watermark file and return the file name. Using force
        will cause any exsiting versions to be recreated.'''

#        import pdb; pdb.set_trace()

        # Initialize the process
        pubProg             = "Rapuma"
        watermarkText       = self.layoutConfig['DocumentFeatures']['watermarkText']
        svgFile             = tempfile.NamedTemporaryFile().name

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
        ppsWidth = pps[0]
        ppsHeight = pps[1]

        #   Write out SVG document text 
        with codecs.open(svgFile, 'wb') as fbackgr :            # open file for writing 
            fbackgr.write( '''<svg xmlns="http://www.w3.org/2000/svg"
                version="1.1" width = "''' + str(ppsWidth) + '''" height = "''' + str(ppsHeight)+ '''">
                <g><text x = "''' + str((ppsWidth - bdWidth)/2 + 54) + '''" y = "''' + str((ppsHeight - bdHeight)/2 + 120) + '''" style="font-family:DejaVu Sans;font-style:regular;font-size:32;text-anchor:start;fill:#e6e6ff;fill-opacity:1">''' + str(pubProg) + '''
                <tspan x = "''' + str((ppsWidth)/2) + '''" y = "''' + str((ppsHeight - bdHeight)/2 + 194)+ '''" style="text-anchor:middle">''' + str(pubProg) + '''</tspan>
                <tspan x = "''' + str((ppsWidth + bdWidth)/2-54)+ '''" y = "''' + str((ppsHeight - bdHeight)/2 + 268) + '''" style="text-anchor:end">''' + str(pubProg) + '''</tspan>
                <tspan x = "''' + str(ppsWidth/2) + '''" y = "''' + str((ppsHeight - bdHeight)/2 + 342)+ '''" style="text-anchor:middle">''' + str(pubProg) + '''</tspan>
                <tspan x = "''' + str((ppsWidth - bdWidth)/2 + 54)+ '''" y = "''' + str((ppsHeight - bdHeight)/2 + 416) + '''" style="text-anchor:start">''' + str(pubProg) + '''</tspan>
                <tspan x = "''' + str((ppsWidth + bdWidth)/2 - 36)+ '''" y = "''' + str((ppsHeight - bdHeight)/2 + 520 + 36)+ '''" style="font-weight:bold;font-size:68;text-anchor:end">''' + watermarkText + ''' </tspan>
                </text></g></svg>''')

# For testing
        #shutil.copy(self.convertSvgToPdf(svgFile), os.path.join(self.local.projIllustrationFolder, 'lines.pdf'))
        #shutil.copy(svgFile, os.path.join(self.local.projIllustrationFolder, 'lines.svg'))



        # Convert the temp svg to pdf and merge into backgroundFile
        results = self.mergePdfFilesPdftk(self.local.backgroundFile, self.convertSvgToPdf(svgFile))
        if os.path.isfile(results) :
            return True


    def mergeCropmarks (self) :
        '''Merge cropmarks on to the background page.'''

        # Initialize the process
        svgFile             = tempfile.NamedTemporaryFile().name

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
        ppsWidth = pps[0]
        ppsHeight = pps[1]

        with codecs.open(svgFile, 'wb') as fbackgr : 
                    # starting lines of SVG xml
            fbackgr.write( '''<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width = "''' + str(ppsWidth) + '''" height = "''' + str(ppsHeight) + '''">\n''') 
                    # vertical top left
            fbackgr.write( '''<path d = "m''' + str((ppsWidth - bdWidth)/2) + ''',''' + str((ppsHeight - bdHeight)/2 - 32.0) + ''',v27," style="stroke:#000000;stroke-width:.2"/>\n''')   
                    # vertical bottom left
            fbackgr.write( '''<path d = "m''' + str((ppsWidth - bdWidth)/2) + ''',''' + str((ppsHeight + bdHeight)/2 + 5.0) + ''',v27" style="stroke:#000000;stroke-width:.2" />\n''')
                    # vertical bottom right
            fbackgr.write( '''<path d = "m''' + str((ppsWidth + bdWidth)/2) + ''',''' + str((ppsHeight - bdHeight)/2 - 32.0) + ''',v27" style="stroke:#000000;stroke-width:.2"/>\n''')
                    # vertical top right
            fbackgr.write( '''<path d = "m''' + str((ppsWidth + bdWidth)/2) + ''',''' + str((ppsHeight + bdHeight)/2 + 5.0) + ''',v27" style="stroke:#000000;stroke-width:.2" />\n''')
                    # horzontal top left
            fbackgr.write( '''<path d =" m''' + str((ppsWidth - bdWidth)/2 - 32.0) + ''',''' + str((ppsHeight - bdHeight)/2) + ''',h27" style="stroke:#000000;stroke-width:.2" />\n''')
                    # horzontal top right
            fbackgr.write( '''<path d =" m''' + str((ppsWidth + bdWidth)/2 + 5.0) + ''',''' + str((ppsHeight - bdHeight)/2) + ''',h27" style="stroke:#000000;stroke-width:.2" />\n''')
                    # horzontal bottom right
            fbackgr.write( '''<path d =" m''' + str((ppsWidth - bdWidth)/2 - 32.0) + ''',''' + str((ppsHeight + bdHeight)/2) + ''',h27" style="stroke:#000000;stroke-width:.2" />\n''')
                    # horzontal bottom left
            fbackgr.write( '''<path d =" m''' + str((ppsWidth + bdWidth)/2 +5.0) + ''',''' + str((ppsHeight + bdHeight)/2) + ''',h27" style="stroke:#000000;stroke-width:.2" />\n''')
            fbackgr.write( '''</svg>''')

        # Convert the temp svg to pdf and merge into backgroundFile
        results = self.mergePdfFilesPdftk(self.local.backgroundFile, self.convertSvgToPdf(svgFile))
        if os.path.isfile(results) :
            return True


    def mergePagebox (self) :
        '''Merge a page box with the background page to be used for proof reading.'''

        # Initialize the process
        svgFile             = tempfile.NamedTemporaryFile().name

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
        ppsWidth = pps[0]
        ppsHeight = pps[1]

        with codecs.open(svgFile, 'wb') as fbackgr :
                    # starting lines of SVG xml
            fbackgr.write( '''<svg xmlns="http://www.w3.org/2000/svg"
                version="1.1" width = "''' + str(ppsWidth) + '''" height = "''' + str(ppsHeight) + '''">''')
                    # rectangle
            fbackgr.write( '''<rect x = "''' + str((ppsWidth - bdWidth)/2) + '''" y= "''' + str((ppsHeight - bdHeight)/2) + '''" height = "''' + str(bdHeight) + '''" width = "''' + str(bdWidth) + '''" style = "fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-opacity:1;stroke-width:.2"/>
                </svg>''')

        # Convert the temp svg to pdf and merge into backgroundFile
        results = self.mergePdfFilesPdftk(self.local.backgroundFile, self.convertSvgToPdf(svgFile))
        if os.path.isfile(results) :
            return True


    def mergeLines (self) :
        '''Merge a lines component with the background file.'''

        # Initialize the process
        svgFile             = tempfile.NamedTemporaryFile().name

        # CONVERSIONS OF IMPORTS TO [PX]
        # The variable type of pageWidth and pageHeight can be 'int' or
        # <class 'decimal.Decimal'>. In order to work properly in the linessvg 
        # function the variables dimensions have to be [px], the conversion is
        # done by changing the variables' type to 'float'.

        # The page dimensions extracted from layoutConfig are in [mm] and
        # must be converted to pixels [px], the conversion factor for [mm]
        # to [px] is 72/25.4 
        mmToPx              = 72 / 25.4

        # The page dimensions are given in [mm] but are converted to pixels [px],
        # the conversion factor for [mm] to [px] is 90/25.4 
        def convertMmToPx (mm) :
            return round(mm * 90 / 25.4, 1)
        #def convertMmToPx (mm) :
            #return round(mm * 3.8, 1)


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
        ppsWidth = pps[0]
        ppsHeight = pps[1]

        
        
        # Top margin
        topMargin           = int(self.layoutConfig['PageLayout']['topMargin'])
        # Outside margin
        outsideMargin       = int(self.layoutConfig['PageLayout']['outsideMargin'])
        # Inside margin
        insideMargin        = int(self.layoutConfig['PageLayout']['insideMargin'])
        # Bottom margin
        bottomMargin        = int(self.layoutConfig['PageLayout']['bottomMargin'])
        # Width of the text area
#        gridWidth           = bdWidth - ((outsideMargin + insideMargin) / 0.35)
        gridWidth           = bdWidth - ((outsideMargin + insideMargin) * 3)
        # Height of the text area
        gridHeight          = bdHeight - ((topMargin + bottomMargin) * 3)

        # The font and leading are given in TeX point [pt] and are converted 
        # to pixels [px], the conversion factor for [pt] to [px] is 72/72.27 
        # bodyFontSize [px]
        bodyFontSize        = self.layoutConfig['TextElements']['bodyFontSize']
        bodyFontPxSize      = round(float(bodyFontSize) * 72/72.27,3)
        # bodyTextLeading [px]
        bodyTextLeading     = self.layoutConfig['TextElements']['bodyTextLeading']
        bodyTextPxLeading   = round(float(bodyTextLeading) * 72/72.27,3)

# Definition of CROP MARK SVG function
#def linesvg(paperPxWidth,paperPxHeight,topPxMargin,outsidePxMargin,insidePxMargin,bottomPxMargin,textPxWidth,bodyFontPxSize,bodyTextPxLeading) :
#    "This function writes the SVG code for a linegrid, based on pagedimensions, margins body font and body leading"

        with codecs.open(svgFile, 'wb') as fbackgr : 
                # starting lines of SVG xml
            fbackgr.write( '''<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width = "''' + str(ppsWidth)+ '''" height = "''' + str(ppsHeight) + '''">
                \n    <!--RECTANGLE OF MARGINS-->\n''')
            fbackgr.write( '''<rect x = "''' + str((ppsWidth - gridWidth) / 2) + '''" y= "''' + str((ppsHeight - gridHeight) / 2) + '''" height = "''' + str(gridHeight) + '''" width = "''' + str(gridWidth) + '''" style = "fill:#ffffff;fill-opacity:1;stroke:#ffc800;stroke-opacity:1;stroke-width:.2"/>
                \n    <!--START OF LINEGRID-->\n''')
            fbackgr.write( '''<path d= "m ''' + str((ppsWidth - bdWidth)/2) + "," + str((ppsHeight - bdHeight)/2) + " " + str(bdWidth) + ''',0''')
                # filling the space between the top line and bottom margin, starting at distance
                # counter num = 0 up to the but not including the total of num x leading
                # equals the distance between top and bottom margin
            num = 0
            while (num < int(round(bdHeight - bottomMargin - topMargin )/bodyTextPxLeading)):
                    # lines are drawn in zigzag pattern: RTL when num is even and LTR when odd
                if num%2 == 0: 
                    fbackgr.write( ''' m 0, ''' + str(bodyTextPxLeading) + " - " + str(bdWidth + outsideMargin * 0.25) + ''',0''')
                else:
                    fbackgr.write( ''' m 0, ''' + str(bodyTextPxLeading) + " " + str(bdWidth + outsideMargin * 0.25) + ''',0''')
                num = num +1
                # draw all lines with following style 
            fbackgr.write( '''" style="stroke-width:0.2px;stroke:#ffc800;stroke-opacity:1"/>
                \n    <!--LINE NUMBERS-->\n''')
                # add line number '1' to top line just left of margin
            fbackgr.write( '''<text x="''' + str(outsideMargin * 0.75-2) + '''" y="''' + str(topMargin + bodyFontPxSize-3) + '''" style="font-family: Charis SIL;font-style:italic;font-size:7;fill:#760076">1\n''')
                # add line numbers to all lines down to bottom margin, starting with line number
                # counter linecount = 2, the distance counter runs from '0' till one short of 
                # the quotient (distance between top and bottom margin)/bodyTextPxLeading
            num = 0         # line counter
            linenumber = 2   # line number
            while (num < int(round(bdHeight - bottomMargin - topMargin)/bodyTextPxLeading)):
                fbackgr.write( '''<tspan x="''' + str(outsideMargin * 0.75-2) + '''" dy="''' + str(bodyTextPxLeading) + '''">''' + str(linenumber) + '''</tspan>\n''') 
                linenumber = linenumber +1  
                num = num +1
            fbackgr.write('''</text>\n''' 
                '''<!--LINEGRID CAPTION-->\n'''
                '''<text  x="36" y="''' + str(bdHeight - bottomMargin+10) + '''" style="font-family: Charis SIL;font-style:italic;font-size:7;fill:#ffc800">page size: ''' + str(int(bdWidth/72*25.4+.5)) + ''' x ''' + str(int(bdHeight/72*25.4+.5)) + ''' mm ; font size: ''' + str(bodyFontSize) + ''' pt; leading: ''' + str(bodyTextLeading) + ''' pt</text>
                \n    <!--PURPLE LINES TOP AND BOTTOM MARGINS--> 
                <path d="M ''' + str(outsideMargin) + "," + str(topMargin) + " " + str(bdWidth + outsideMargin) + "," + str(topMargin) + '''" style="fill:#ffffff;fill-opacity:1;stroke-width:0.4px;stroke:#760076;stroke-opacity:1"/>
                <path d="M ''' + str(outsideMargin) + "," + str(bdHeight - bottomMargin) + " " + str(bdWidth + outsideMargin) + "," + str(bdHeight - bottomMargin) + '''" style="fill:#ffffff;fill-opacity:1;stroke-width:0.4px;stroke:#760076;stroke-opacity:1"/>
                </svg>''')
    
        shutil.copy(self.convertSvgToPdf(svgFile), os.path.join(self.local.projIllustrationFolder, 'lines.pdf'))
        shutil.copy(svgFile, os.path.join(self.local.projIllustrationFolder, 'lines.svg'))
    
    
        # Convert the temp svg to pdf and merge into backgroundFile
        results = self.mergePdfFilesPdftk(self.local.backgroundFile, self.convertSvgToPdf(svgFile))
        if os.path.isfile(results) :
            return True


    def buildCommandList (self, svgFile, pdfFile) :
        '''Convert a command line from the config that has keys in it for
        input and output files. The commands in the config should look like
        this coming in:
            svgPdfConverter = convert,svgFile,pdfOutFile
            svgPdfConverter = rsvg-convert,-f,pdf,-o,pdfOutFile,svgFile
            svgPdfConverter = inkscape,-f,svgFile,-A,pdfOutFile
        This will insert the right value for svgFile and pdfOutFile.'''

        cmds = list()
        for c in self.svgPdfConverter :
            if c == 'svgFile' :
                cmds.append(svgFile)
            elif c == 'pdfFile' :
                cmds.append(pdfFile)
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


    def convertSvgToPdf (self, svgFile) :
        '''Convert/render an SVG file to produce a PDF file. Return
        a temp file name to the caller.'''

        pdfFile = tempfile.NamedTemporaryFile().name

        # Simple try statement seems to work best for this
        try:
            subprocess.call(self.buildCommandList(svgFile, pdfFile)) 
            return pdfFile
        except Exception as e :
            self.log.writeToLog(self.errorCodes['1290'], [pdfFile,str(e)])


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



    
