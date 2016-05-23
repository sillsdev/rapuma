#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (sparkycbr at gmail dot com)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle page background tasks, creating lines, watermarks, etc.

###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, difflib, subprocess, shutil, re, tempfile, pyPdf, filecmp
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
        self.projHome                   = os.path.join(os.environ['RAPUMA_PROJECTS'], self.pid)
        self.mmToPx                     = 72 / 25.4
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
            '1310' : ['WRN', 'Failed to add background component: [<<1>>] with error: [<<2>>]'],
            '1320' : ['MSG', 'New background created.']

        }


###############################################################################
############################### Basic Functions ###############################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################

    def turnOnBackground (self) :
        '''Change the layout config settings to turn on the background.'''

        if not self.tools.str2bool(self.layoutConfig['DocumentFeatures']['useBackground']) :
            self.layoutConfig['DocumentFeatures']['useBackground'] = True
            self.tools.writeConfFile(self.layoutConfig)


    def turnOffBackground (self) :
        '''Change the layout config settings to turn off the background.'''

        if self.tools.str2bool(self.layoutConfig['DocumentFeatures']['useBackground']) :
            self.layoutConfig['DocumentFeatures']['useBackground'] = False
            self.tools.writeConfFile(self.layoutConfig)


    def turnOnDocInfo (self) :
        '''Change the layout config settings to turn on the doc info in the background.'''

        if not self.tools.str2bool(self.layoutConfig['DocumentFeatures']['useDocInfo']) :
            self.layoutConfig['DocumentFeatures']['useDocInfo'] = True
            self.tools.writeConfFile(self.layoutConfig)


    def turnOffDocInfo (self) :
        '''Change the layout config settings to turn off the doc info in the background.'''

        if self.tools.str2bool(self.layoutConfig['DocumentFeatures']['useDocInfo']) :
            self.layoutConfig['DocumentFeatures']['useDocInfo'] = False
            self.tools.writeConfFile(self.layoutConfig)


    def addBackground (self, target) :
        '''Add a background (watermark) to a rendered PDF file. This will
        figure out what the background is to be composed of and create
        a master background page. Using force will cause it to be remade.'''

        # Do a quick check if the background needs to be remade
        # The background normally is not remade if one already exists.
        # If one is there, it can be remade if regenerate is set to
        # to True. Obviously, if one is not there, it will be made.
        if self.tools.str2bool(self.layoutConfig['DocumentFeatures']['regenerateBackground']) :
            self.createBackground()
        else :
            # If there isn't one, make it
            if not os.path.exists(self.local.backgroundFile) :
                self.createBackground()

        # Merge target with the project's background file in the Illustraton folder
        self.log.writeToLog(self.errorCodes['1300'])

        # Create a special name for the file with the background
        # Then merge and save it
        viewFile = self.tools.alterFileName(target, 'view')
        
        shutil.copy(self.tools.mergePdfFilesPdftk(self.centerOnPrintPage(target), self.local.backgroundFile), viewFile)

        # Not returning a file name would mean it failed
        if os.path.exists(viewFile) :
            return viewFile


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
        #trimWidth     = float(var2.getWidth())
        #trimHeight    = float(var2.getHeight())
        trimWidth = float(self.layoutConfig['PageLayout']['pageWidth'])
        trimHeight = float(self.layoutConfig['PageLayout']['pageHeight'])
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
        viewFile = self.tools.alterFileName(target, 'view')
        # Compare the new file name with the target to see if we are
        # already working with a background file
        if viewFile == target :
            # If the target is a BG file all we need to do is merge it
            self.tools.mergePdfFilesPdftk(viewFile, self.tools.convertSvgToPdfRsvg(svgFile))
        else :
            # If not a BG file, we need to be sure the target is the same
            # size as the print page to merge with pdftk
            shutil.copy(self.tools.mergePdfFilesPdftk(self.centerOnPrintPage(target), self.tools.convertSvgToPdfRsvg(svgFile)), viewFile)

        # Not returning a file name would mean it failed
        if os.path.exists(viewFile) :
            return viewFile


    ##### Background Creation Functions #####

    def createBackground (self) :
        '''Create a background file. This will overwrite any existing
        background file and will add each recognized background type
        found in the bacgroundComponents config setting.'''

        self.createBlankBackground()

        # Add each component to the blank background file
        for comp in self.layoutConfig['DocumentFeatures']['backgroundComponents'] :
            try :
                getattr(self, 'merge' + comp.capitalize())()
            except Exception as e :
                self.log.writeToLog(self.errorCodes['1310'],[comp,str(e)])
                pass

        self.log.writeToLog(self.errorCodes['1320'])
        return True


    def createBlankBackground (self) :
        '''Create a blank background page according to the print page
        size specified.'''
        
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

        shutil.copy(self.tools.convertSvgToPdfRsvg(svgFile), self.local.backgroundFile)


    def mergeWatermark (self) :
        '''Create a watermark file and return the file name. Using force
        will cause any exsiting versions to be recreated.'''

#        import pdb; pdb.set_trace()

        # Initialize the process
        pubProg             = "Rapuma"
        watermarkText       = self.layoutConfig['DocumentFeatures']['watermarkText']
        svgFile             = tempfile.NamedTemporaryFile().name

        ## RENDERED PAGE DIMENSIONS (body)
        # Trim page width [px]
        trimWidth = round(self.mmToPx * float(self.layoutConfig['PageLayout']['pageWidth']),1)
        # Trim page height [px]
        trimHeight = round(self.mmToPx * float(self.layoutConfig['PageLayout']['pageHeight']),1)
        # Printer page size [px]
        (ppsWidth, ppsHeight) = self.printerPageSize()

        pageX = ppsWidth/2
        pageY = ppsHeight/2
        
        #   Write out SVG document text 
        with codecs.open(svgFile, 'wb') as fbackgr :            # open file for writing 
            fbackgr.write( '''<svg xmlns="http://www.w3.org/2000/svg"
                version="1.1" width = "''' + str(ppsWidth) + '''" height = "''' + str(ppsHeight) + '''">
                <g><text x = "''' + str(pageX-trimWidth*.42) + '''" y = "''' + str(pageY-trimHeight*0.39) + '''" style="font-family:DejaVu Sans;font-style:regular;font-size:32;text-anchor:start;fill:#d5d5f5;fill-opacity:1">''' + str(pubProg) + '''
                <tspan x = "''' + str(pageX) + '''" y = "''' + str(pageY - trimHeight*0.22) + '''" style="text-anchor:middle">''' + str(pubProg) + '''</tspan>
                <tspan x = "''' + str(pageX+trimWidth*0.42)+ '''" y = "''' + str(pageY-trimHeight*0.05) + '''" style="text-anchor:end">''' + str(pubProg) + '''</tspan>
                <tspan x = "''' + str(pageX) + '''" y = "''' + str(pageY+trimHeight*0.12) + '''" style="text-anchor:middle">''' + str(pubProg) + '''</tspan>
                <tspan x = "''' + str(pageX-trimWidth*0.42) + '''" y = "''' + str(pageY+trimHeight*0.29) + '''" style="text-anchor:start">''' + str(pubProg) + '''</tspan>
                <tspan x = "''' + str(pageX+trimWidth*0.49) + '''" y = "''' + str(pageY+trimHeight*0.455) + '''" style="font-weight:bold;font-size:68;text-anchor:end">''' + watermarkText + ''' </tspan>
                </text></g></svg>''')

        # Convert the temp svg to pdf and merge into backgroundFile
        results = self.tools.mergePdfFilesPdftk(self.local.backgroundFile, self.tools.convertSvgToPdfRsvg(svgFile))
        if os.path.isfile(results) :
            return True


    def mergeCropmarks (self) :
        '''Merge cropmarks on to the background page.'''

        # Initialize the process
        svgFile             = tempfile.NamedTemporaryFile().name

        ## RENDERED PAGE DIMENSIONS (body)
        # Trim page width [px]
        trimWidth = round(self.mmToPx * float(self.layoutConfig['PageLayout']['pageWidth']),1)
        # Trim page height [px]
        trimHeight = round(self.mmToPx * float(self.layoutConfig['PageLayout']['pageHeight']),1)
        # Printer page size [px]
        pps = self.printerPageSize()
        ppsWidth = pps[0]
        ppsHeight = pps[1]

        with codecs.open(svgFile, 'wb') as fbackgr : 
                    # starting lines of SVG xml
            fbackgr.write( '''<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width = "''' + str(ppsWidth) + '''" height = "''' + str(ppsHeight) + '''">\n''') 
                    # vertical top left
            fbackgr.write( '''<path d = "m''' + str((ppsWidth - trimWidth)/2) + ''',''' + str((ppsHeight - trimHeight)/2 - 32.0) + ''',v27," style="stroke:#000000;stroke-width:.2"/>\n''')   
                    # vertical bottom left
            fbackgr.write( '''<path d = "m''' + str((ppsWidth - trimWidth)/2) + ''',''' + str((ppsHeight + trimHeight)/2 + 5.0) + ''',v27" style="stroke:#000000;stroke-width:.2" />\n''')
                    # vertical bottom right
            fbackgr.write( '''<path d = "m''' + str((ppsWidth + trimWidth)/2) + ''',''' + str((ppsHeight - trimHeight)/2 - 32.0) + ''',v27" style="stroke:#000000;stroke-width:.2"/>\n''')
                    # vertical top right
            fbackgr.write( '''<path d = "m''' + str((ppsWidth + trimWidth)/2) + ''',''' + str((ppsHeight + trimHeight)/2 + 5.0) + ''',v27" style="stroke:#000000;stroke-width:.2" />\n''')
                    # horzontal top left
            fbackgr.write( '''<path d =" m''' + str((ppsWidth - trimWidth)/2 - 32.0) + ''',''' + str((ppsHeight - trimHeight)/2) + ''',h27" style="stroke:#000000;stroke-width:.2" />\n''')
                    # horzontal top right
            fbackgr.write( '''<path d =" m''' + str((ppsWidth + trimWidth)/2 + 5.0) + ''',''' + str((ppsHeight - trimHeight)/2) + ''',h27" style="stroke:#000000;stroke-width:.2" />\n''')
                    # horzontal bottom right
            fbackgr.write( '''<path d =" m''' + str((ppsWidth - trimWidth)/2 - 32.0) + ''',''' + str((ppsHeight + trimHeight)/2) + ''',h27" style="stroke:#000000;stroke-width:.2" />\n''')
                    # horzontal bottom left
            fbackgr.write( '''<path d =" m''' + str((ppsWidth + trimWidth)/2 +5.0) + ''',''' + str((ppsHeight + trimHeight)/2) + ''',h27" style="stroke:#000000;stroke-width:.2" />\n''')
            fbackgr.write( '''</svg>''')

        # Convert the temp svg to pdf and merge into backgroundFile
        results = self.tools.mergePdfFilesPdftk(self.local.backgroundFile, self.tools.convertSvgToPdfRsvg(svgFile))
        if os.path.isfile(results) :
            return True


    def mergePagebox (self) :
        '''Merge a page box with the background page to be used for proof reading.'''

        # Initialize the process
        svgFile             = tempfile.NamedTemporaryFile().name

        ## RENDERED PAGE DIMENSIONS (body)
        # Trim page width [px]
        trimWidth = round(self.mmToPx * float(self.layoutConfig['PageLayout']['pageWidth']),1)
        # Trim page height [px]
        trimHeight = round(self.mmToPx * float(self.layoutConfig['PageLayout']['pageHeight']),1)
        # Printer page size [px]
        pps = self.printerPageSize()
        ppsWidth = pps[0]
        ppsHeight = pps[1]

        with codecs.open(svgFile, 'wb') as fbackgr :
                    # starting lines of SVG xml
            fbackgr.write( '''<svg xmlns="http://www.w3.org/2000/svg"
                version="1.1" width = "''' + str(ppsWidth) + '''" height = "''' + str(ppsHeight) + '''">''')
                    # rectangle
            fbackgr.write( '''<rect x = "''' + str((ppsWidth - trimWidth)/2) + '''" y= "''' + str((ppsHeight - trimHeight)/2) + '''" height = "''' + str(trimHeight) + '''" width = "''' + str(trimWidth) + '''" style = "fill:none;fill-opacity:1;stroke:#000000;stroke-opacity:1;stroke-width:.2"/>
                </svg>''')

        # Convert the temp svg to pdf and merge into backgroundFile
        results = self.tools.mergePdfFilesPdftk(self.local.backgroundFile, self.tools.convertSvgToPdfRsvg(svgFile))
        if os.path.isfile(results) :
            return True


# Depricated
    #def makeBgFileName (self, orgName) :
        #'''Alter the file name to reflect the fact it has a background
        #added to it. This assumes the file only has a single extention.
        #If that's not the case we're hosed.'''

        #name    = orgName.split('.')[0]
        #ext     = orgName.split('.')[1]
        ## Just in case this is the second pass
        #name    = name.replace('-bg', '')
        #return name + '-bg.' + ext


    def centerOnPrintPage (self, contents) :
        '''Center a PDF file on the printerPageSize page. GhostScript
        is the only way to do this at this point.'''

#        import pdb; pdb.set_trace()

        tmpFile = tempfile.NamedTemporaryFile().name
        # Get the size of our printer page
        (ppsWidth, ppsHeight) = self.printerPageSize()
        (wo, ho) = self.getPageOffset()
        pageOffset = str(wo) + ' ' + str(ho)
        
        # Assemble the GhostScript command
        cmd = [ 'gs', 
                '-o', tmpFile, 
                '-sDEVICE=pdfwrite', 
                '-dQUIET', 
                '-dDEVICEWIDTHPOINTS=' + str(ppsWidth),
                '-dDEVICEHEIGHTPOINTS=' + str(ppsHeight),
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
            # Just default to the page trim size (assumed mm coming in) factor mmToPx = 72 / 25.4
            return float(int(self.layoutConfig['PageLayout']['pageWidth']) * self.mmToPx), float(int(self.layoutConfig['PageLayout']['pageHeight']) * self.mmToPx)

    
    def getPageOffset (self) :
        '''Return the amount of horizontal and vertical offset that will
        enable the page trim size to be centered on the printer page. If
        something other than A4 or Letter is being used, the offset returned
        will be zero as this only supports those two sizes. The offset is
        based on the starting point being the lower-left side corner
        of the page. '''
        
        # Get the printer page size
        printerPageSizeCode = self.layoutConfig['PageLayout']['printerPageSizeCode'].lower()
        # Get the page trim size (assuming mm input)factor mmToPx = 72 / 25.4
        trimWidth = int(self.layoutConfig['PageLayout']['pageWidth']) * self.mmToPx
        trimHeight = int(self.layoutConfig['PageLayout']['pageHeight']) * self.mmToPx

        # The trim size of the content page can never be bigger than
        # the printer page size. If so, the offset is 0
        if printerPageSizeCode == 'a4' or printerPageSizeCode == 'letter' :
            (bw, bh) = self.printerPageSize()
            wo = float((bw/2)-(trimWidth/2))
            ho = float((bh/2)-(trimHeight/2))
            return wo, ho
        else :
            return 0, 0

        # Note:
        # Another way to get the size of our contents page would be
        # to use PdfFileReader() to open the contents and read the
        # trim size dimensions, like this:
        # cPdf = PdfFileReader(open(contents,'rb'))
        # var2 = cPdf.getPage(0).mediaBox
        # trimWidth = float(var2.getWidth())
        # trimHeight = float(var2.getHeight())
        
        
        
