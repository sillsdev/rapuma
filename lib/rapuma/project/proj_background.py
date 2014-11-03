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

        # For debugging purposes a switch can be set here for verbose
        # message output via the terminal
        self.debugMode                  = self.tools.str2bool(self.userConfig['System']['debugging'])

        # Log messages for this module
        self.errorCodes     = {

            '0000' : ['MSG', 'Placeholder message'],
            '1110' : ['MSG', 'File exsits: [<<1>>]. Use \"force\" to remove it.'],
            '1280' : ['ERR', 'Failed to merge background file with command: [<<1>>]. This is the error: [<<2>>]'],
            '1290' : ['ERR', 'Failed to convert background file [<<1>>]. Error: [<<2>>] The command was: [<<3>>]'],
            '1300' : ['MSG', 'Background merge operation in process, please wait...'],
            '1305' : ['MSG', 'Adding document information, please wait...'],
            '1310' : ['WRN', 'Failed to add background component: [<<1>>] with error: [<<2>>]']

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
        # The background normally is not remade if one already exists.
        # If one is there, it can be remade in two ways, with a force
        # or a regenerate command.
        if force :
            self.createBackground()
        elif self.tools.str2bool(self.layoutConfig['DocumentFeatures']['regenerateBackground']) :
            self.createBackground()
        else :
            # If there isn't one, make it
            if not os.path.exists(self.local.backgroundFile) :
                self.createBackground()

        # Merge target with the project's background file in the Illustraton folder
        self.log.writeToLog(self.errorCodes['1300'])

        # Create a special name for the file with the background
        # Then merge and save it
        bgFile = self.makeBgFileName(target)
        shutil.copy(self.mergePdfFilesPdftk(self.centerOnPrintPage(target), self.local.backgroundFile), bgFile)

        # Not returning a file name would mean it failed
        if os.path.exists(bgFile) :
            return bgFile


    def addDocInfo (self, target) :
        '''Add (merge) document information to the rendered target doc.'''

        # Initialize the process
        docInfoText         = self.layoutConfig['DocumentFeatures']['docInfoText']
        timestamp           = self.tools.tStamp()
        if self.gid :
            headerLine          = self.pid + ' / ' + self.gid + ' / ' + timestamp
        else :
            headerLine          = self.pid + ' / ' + timestamp
        svgFile             = tempfile.NamedTemporaryFile().name

        ## RENDERED PAGE DIMENSIONS (body)
        # This can be determined with the pyPdf element 
        # "pdf.getPage(0).mediaBox", which returns a 
        # RectangleObject([0, 0, Width, Height]). The
        # width and height are in points. Hopefully we will
        # always be safe by measuring the gidPdfFile size.
        #pdf         = PdfFileReader(open(self.local.gidPdfFile,'rb'))
        #var2        = pdf.getPage(0).mediaBox
        #bdWidth     = float(var2.getWidth())
        #bdHeight    = float(var2.getHeight())
        bdWidth = float(self.layoutConfig['PageLayout']['pageWidth'])
        bdHeight = float(self.layoutConfig['PageLayout']['pageHeight'])
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
        self.log.writeToLog(self.errorCodes['1305'])

        # Create a special name for the file with the background
        # Then merge and save it
        bgFile = self.makeBgFileName(target)
        shutil.copy(self.mergePdfFilesPdftk(self.centerOnPrintPage(target), self.convertSvgToPdf(svgFile)), bgFile)

        # Not returning a file name would mean it failed
        if os.path.exists(bgFile) :
            return bgFile


    ##### Background Creation Functions #####

    def createBackground (self) :
        '''Create a background file. This will overwrite any existing
        background file and will add each recognoized background type
        found in the bacgroundComponents config setting.'''

        self.createBlankBackground()

        # Add each component to the blank background file
        for comp in self.layoutConfig['DocumentFeatures']['backgroundComponents'] :
            try :
                getattr(self, 'merge' + comp.capitalize())()
            except Exception as e :
                self.log.writeToLog(self.errorCodes['1310'],[comp,str(e)])
                pass

        return True


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
        # Convert formula - mm to px
        mmToPx = 72 / 25.4
        # Trim page width [px]
        tsw = round(mmToPx * float(self.layoutConfig['PageLayout']['pageWidth']),1)
        # Trim page height [px]
        tsh = round(mmToPx * float(self.layoutConfig['PageLayout']['pageHeight']),1)
        # Printer page size [px]
        (ppsw, ppsh) = self.printerPageSize()

        pageX = ppsw - tsw
        pageY = ppsh - tsh
        
        #   Write out SVG document text 
        with codecs.open(svgFile, 'wb') as fbackgr :            # open file for writing 
            fbackgr.write( '''<svg xmlns="http://www.w3.org/2000/svg"
                version="1.1" width = "''' + str(ppsw) + '''" height = "''' + str(ppsh) + '''">
                <g><text x = "''' + str(pageX * 1.75) + '''" y = "''' + str(pageY) + '''" style="font-family:DejaVu Sans;font-style:regular;font-size:32;text-anchor:middle;fill:#e6e6ff;fill-opacity:1">''' + str(pubProg) + '''
                <tspan x = "''' + str(pageX * 1.5) + '''" y = "''' + str(tsh * 0.35) + '''" style="text-anchor:middle">''' + str(pubProg) + '''</tspan>
                <tspan x = "''' + str(pageX * 1.25)+ '''" y = "''' + str(tsh * 0.50) + '''" style="text-anchor:middle">''' + str(pubProg) + '''</tspan>
                <tspan x = "''' + str(pageX * 1.5) + '''" y = "''' + str(tsh * 0.65) + '''" style="text-anchor:middle">''' + str(pubProg) + '''</tspan>
                <tspan x = "''' + str(pageX * 1.75) + '''" y = "''' + str(tsh * 0.80) + '''" style="text-anchor:middle">''' + str(pubProg) + '''</tspan>
                <tspan x = "''' + str(pageX * 2.5) + '''" y = "''' + str(tsh) + '''" style="font-weight:bold;font-size:68;text-anchor:end">''' + watermarkText + ''' </tspan>
                </text></g></svg>''')

        # Convert the temp svg to pdf and merge into backgroundFile
        results = self.mergePdfFilesPdftk(self.local.backgroundFile, self.convertSvgToPdf(svgFile))
        if os.path.isfile(results) :
            return True


    def mergeCropmarks (self) :
        '''Merge cropmarks on to the background page.'''

        # Initialize the process
        svgFile             = tempfile.NamedTemporaryFile().name

        ## RENDERED PAGE DIMENSIONS (body)
        # Convert formula - mm to px
        mmToPx = 72 / 25.4
        # Trim page width [px]
        bdWidth = round(mmToPx * float(self.layoutConfig['PageLayout']['pageWidth']),1)
        # Trim page height [px]
        bdHeight = round(mmToPx * float(self.layoutConfig['PageLayout']['pageHeight']),1)
        # Printer page size [px]
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
        # Convert formula - mm to px
        mmToPx = 72 / 25.4
        # Trim page width [px]
        bdWidth = round(mmToPx * float(self.layoutConfig['PageLayout']['pageWidth']),1)
        # Trim page height [px]
        bdHeight = round(mmToPx * float(self.layoutConfig['PageLayout']['pageHeight']),1)
        # Printer page size [px]
        pps = self.printerPageSize()
        ppsWidth = pps[0]
        ppsHeight = pps[1]

        with codecs.open(svgFile, 'wb') as fbackgr :
                    # starting lines of SVG xml
            fbackgr.write( '''<svg xmlns="http://www.w3.org/2000/svg"
                version="1.1" width = "''' + str(ppsWidth) + '''" height = "''' + str(ppsHeight) + '''">''')
                    # rectangle
            fbackgr.write( '''<rect x = "''' + str((ppsWidth - bdWidth)/2) + '''" y= "''' + str((ppsHeight - bdHeight)/2) + '''" height = "''' + str(bdHeight) + '''" width = "''' + str(bdWidth) + '''" style = "fill:none;fill-opacity:1;stroke:#000000;stroke-opacity:1;stroke-width:.2"/>
                </svg>''')

        # Convert the temp svg to pdf and merge into backgroundFile
        results = self.mergePdfFilesPdftk(self.local.backgroundFile, self.convertSvgToPdf(svgFile))
        if os.path.isfile(results) :
            return True


    def mergeLines (self) :
        '''Merge a lines component with the background file.'''

        # Initialize the process
        svgFile             = tempfile.NamedTemporaryFile().name

        # PAGE DIMENSIONS
        # The page dimensions extracted from layoutConfig are in [mm] and
        # must be converted to pixels [px], the conversion factor for [mm]
        # to [px] is 72/25.4 
        mmToPx = 72 / 25.4
        # page width [px]
        paperPxWidth = round(mmToPx * float(self.layoutConfig['PageLayout']['pageWidth']),1)
        # page height [px]
        paperPxHeight = round(mmToPx * float(self.layoutConfig['PageLayout']['pageHeight']),1)
        # bodyFontSize [px]
        bodyFontSize = self.layoutConfig['TextElements']['bodyFontSize']
        bodyFontPxSize = round(float(bodyFontSize) * 72/72.27,3)
        # bodyTextLeading [px]
        bodyTextLeading = self.layoutConfig['TextElements']['bodyTextLeading']
        bodyTextPxLeading = round(float(bodyTextLeading) * 72/72.27,3)
        # top margin [px]
        topMargin = self.layoutConfig['PageLayout']['topMargin']
        topPxMargin = round(mmToPx * float(topMargin),1)
        # outside margin [px]
        outsideMargin = self.layoutConfig['PageLayout']['outsideMargin']
        outsidePxMargin = round(mmToPx * float(outsideMargin),1)
        #inside margin [px]
        insideMargin = self.layoutConfig['PageLayout']['insideMargin']
        insidePxMargin = round(mmToPx * float(outsideMargin),1)
        # bottom margin [px]
        bottomMargin = self.layoutConfig['PageLayout']['bottomMargin']
        bottomPxMargin = round(mmToPx * float(bottomMargin),1)
        # width of the body text
        textPxWidth = paperPxWidth - (outsidePxMargin + insidePxMargin)

        # Create the svg file
        with codecs.open(svgFile, 'wb') as fbackgr :            # open file for writing 
                # starting lines of SVG xml
            fbackgr.write( '''<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width = "''' + str(paperPxWidth)+ '''" height = "'''+str(paperPxHeight) + '''">
                \n    <!--RECTANGLE OF MARGINS-->\n''')
            fbackgr.write( '''<rect x = "''' + str(outsidePxMargin) + '''" y= "''' + str(topPxMargin) + '''" height = "''' + str(paperPxHeight - topPxMargin - bottomPxMargin) + '''" width = "''' + str(textPxWidth) + '''" style = "fill:none;fill-opacity:1;stroke:#ffc800;stroke-opacity:1;stroke-width:.2"/>
                \n    <!--START OF LINEGRID-->\n''')
            fbackgr.write( '''<path d= "m ''' + str(outsidePxMargin * 0.75-1) + "," + str(topPxMargin + bodyFontPxSize) + " " + str(textPxWidth + outsidePxMargin * 0.25)+ ''',0''')
                # filling the space between the top line and bottom margin, starting at distance
                # counter num = 0 up to the but not including the total of num x leading
                # equals the distance between top and bottom margin
            num = 0
            while (num < int(round(paperPxHeight - bottomPxMargin - topPxMargin)/bodyTextPxLeading)):
                    # lines are drawn in zigzag pattern: RTL when num is even and LTR when odd
                if num%2 == 0: 
                    fbackgr.write( ''' m 0, ''' + str(bodyTextPxLeading) + " -" + str(textPxWidth + outsidePxMargin * 0.25)+ ''',0''')
                else:
                    fbackgr.write( ''' m 0, ''' + str(bodyTextPxLeading) + " " + str(textPxWidth + outsidePxMargin * 0.25)+ ''',0''')
                num = num +1
                # draw all lines with following style 
            fbackgr.write( '''" style="stroke-width:0.2px;stroke:#ffc800;stroke-opacity:1"/>
                \n    <!--LINE NUMBERS-->\n''')
                # add line number '1' to top line just left of margin
            fbackgr.write( '''<text x="''' + str(outsidePxMargin * 0.75-2) + '''" y="''' + str(topPxMargin + bodyFontPxSize-3) + '''" style="font-family: Charis SIL;font-style:italic;font-size:7;fill:#760076"> 1''')
                # add line numbers to all lines down to bottom margin, starting with line number
                # counter linecount = 2, the distance counter runs from '0' till one short of 
                # the quotient (distance between top and bottom margin)/bodyTextPxLeading
            num = 0         # line counter
            linenumber = 2   # line number
            while (num < int(round(paperPxHeight - bottomPxMargin - topPxMargin)/bodyTextPxLeading)):
                fbackgr.write( '''<tspan x="''' + str(outsidePxMargin * 0.75-2) + '''" dy="''' + str(bodyTextPxLeading) + '''">''' + str(linenumber) + '''</tspan>''') 
                linenumber = linenumber +1  
                num = num +1
            fbackgr.write('''</text> 
                \n  <!--LINEGRID CAPTION-->
                <text  x="36" y="''' + str(paperPxHeight - bottomPxMargin+10) + '''" style="font-family: Charis SIL;font-style:italic;font-size:7;fill:#ffc800">page size: ''' + str(int(paperPxWidth/72*25.4+.5)) + ''' x ''' + str(int(paperPxHeight/72*25.4+.5)) + ''' mm ; font size: ''' + str(bodyFontSize) + ''' pt; leading: ''' + str(bodyTextLeading) + ''' pt</text>
                \n    <!--PURPLE LINES TOP AND BOTTOM MARGINS--> 
                <path d="M ''' + str(outsidePxMargin) + "," + str(topPxMargin) + " " + str(textPxWidth + outsidePxMargin) + "," + str(topPxMargin) + '''" style="fill:#ffffff;fill-opacity:1;stroke-width:0.4px;stroke:#760076;stroke-opacity:1"/>
                <path d="M ''' + str(outsidePxMargin) + "," + str(paperPxHeight - bottomPxMargin) + " " + str(textPxWidth + outsidePxMargin) + "," + str(paperPxHeight - bottomPxMargin) + '''" style="fill:#ffffff;fill-opacity:1;stroke-width:0.4px;stroke:#760076;stroke-opacity:1"/>
                </svg>''')
    
        # Convert the lines background component to PDF
        linesPdf = self.convertSvgToPdf(svgFile)
#        shutil.copy(linesPdf, os.path.join(self.local.projIllustrationFolder, 'linesPdf.pdf'))

        # Center linesPdf on the print page (this keeps the size right)
        linesBackground = self.centerOnPrintPage(linesPdf)
#        shutil.copy(linesBackground, os.path.join(self.local.projIllustrationFolder, 'linesBackground.pdf'))

        # Merge linesPdf with existing background
        results = results = self.mergePdfFilesPdftk(self.local.backgroundFile, linesBackground)
        # Test and return if good
        if os.path.isfile(results) :
            return True


    def makeBgFileName (self, orgName) :
        '''Alter the file name to reflect the fact it has a background
        added to it. This assumes the file only has a single extention.
        If that's not the case we're hosed.'''

        name    = orgName.split('.')[0]
        ext     = orgName.split('.')[1]
        # Just in case this is the second pass
        name    = name.replace('-bg', '')
        return name + '-bg.' + ext


    def buildSvg2PdfCommand (self, svgFile, pdfFile) :
        '''Convert a command line from the config that has keys in it for
        input and output files. The commands in the config should look like
        this coming in:
            svgPdfConverter = convert,svgFile,pdfFile
            svgPdfConverter = rsvg-convert,-f,pdf,-o,pdfFile,svgFile
            svgPdfConverter = inkscape,-f,svgFile,-A,pdfFile
        This will insert the right value for svgFile and pdfFile.'''

        cmd = list()
        for c in self.svgPdfConverter :
            if c == 'svgFile' :
                cmd.append(svgFile)
            elif c == 'pdfFile' :
                cmd.append(pdfFile)
            else :
                cmd.append(c)

        if self.debugMode :
            self.tools.terminal('Debug Mode On: \nbuildSvg2PdfCommand() command: ' + str(cmd))

        return cmd


    def centerOnPrintPage (self, contents) :
        '''Center a PDF file on the printerPageSize page. GhostScript
        is the only way to do this at this point.'''

#        import pdb; pdb.set_trace()

        tmpFile = tempfile.NamedTemporaryFile().name
        # Get the size of our printer page
        (ppsw, ppsh) = self.printerPageSize()
        (wo, ho) = self.getPageOffset()
        pageOffset = str(wo) + ' ' + str(ho)

        # Assemble the GhostScript command
        cmd = [ 'gs', 
                '-o', tmpFile, 
                '-sDEVICE=pdfwrite', 
                '-dQUIET', 
                '-dDEVICEWIDTHPOINTS=' + str(ppsw),
                '-dDEVICEHEIGHTPOINTS=' + str(ppsh),
                '-dFIXEDMEDIA', 
                '-c', 
                '<</PageOffset [' + str(pageOffset) + ']>>', 
                'setpagedevice', 
                '-f', 
                contents]

        if self.debugMode :
            self.tools.terminal('Debug Mode On: \centerOnPrintPage() command: ' + str(cmd))

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

        if self.debugMode :
            self.tools.terminal('Debug Mode On: \mergePdfFilesPdftk() command: ' + str(cmd))

        # Run the process
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

        cmd = self.buildSvg2PdfCommand(svgFile, pdfFile)

        if self.debugMode :
            self.tools.terminal('Debug Mode On: \convertSvgToPdf() command: ' + str(cmd))

        # Simple try statement seems to work best for this
        try:
            subprocess.call(cmd) 
            return pdfFile
        except Exception as e :
            self.log.writeToLog(self.errorCodes['1290'], [pdfFile,str(e),str(cmd)])


    def printerPageSize (self) :
        '''Return the width and height of the printer page size in
        points. Only US Letter and A4 are supported. If not specified
        return the page trim size.'''
    
        printerPageSizeCode = self.layoutConfig['PageLayout']['printerPageSizeCode'].lower()
        ## STANDARD PRINTER PAGE SIZES
        # The output page (printer page) is what the typeset page will be placed on
        # with a watermark behind it. There are only two page sizes supported.
        # They are A4 and US Letter. We will determine the size by the ID code
        # found in the layout.conf file. However, in some cases, for example
        # during the layout process, the trim size is what is needed. If
        # one of the two supported pages sizes are not used, this will defult
        # to the trim size.
        if printerPageSizeCode == 'a4' :
            return float(595), float(842)
        elif printerPageSizeCode == 'letter' :
            return float(612), float(792)
        else :
            # Just default to the page trim size (assumed mm coming in)
            return float(int(self.layoutConfig['PageLayout']['pageWidth']) * 2.845355), float(int(self.layoutConfig['PageLayout']['pageHeight']) * 2.845355)

    
    def getPageOffset (self) :
        '''Return the amount of horizontal and vertical offset that will
        enable the page trim size to be centered on the printer page. If
        something other than A4 or Letter is being used, the offset returned
        will be zero as this only supports those two sizes. The offset is
        based on the starting point being the lower-left side corner
        of the page. '''
        
        # Get the printer page size
        printerPageSizeCode = self.layoutConfig['PageLayout']['printerPageSizeCode'].lower()
        # Get the page trim size (assuming mm input)
        tsw = int(self.layoutConfig['PageLayout']['pageWidth']) * 2.845355
        tsh = int(self.layoutConfig['PageLayout']['pageHeight']) * 2.845355

        # The trim size of the content page can never be bigger than
        # the printer page size. If so, the offset is 0
        if printerPageSizeCode == 'a4' or printerPageSizeCode == 'letter' :
            (bw, bh) = self.printerPageSize()
            wo = float((bw/2)-(tsw/2))
            ho = float((bh/2)-(tsh/2))
            return wo, ho
        else :
            return 0, 0

        # Note:
        # Another way to get the size of our contents page would be
        # to use PdfFileReader() to open the contents and read the
        # trim size dimensions, like this:
        # cPdf = PdfFileReader(open(contents,'rb'))
        # var2 = cPdf.getPage(0).mediaBox
        # tsw = float(var2.getWidth())
        # tsh = float(var2.getHeight())
        
        
        
