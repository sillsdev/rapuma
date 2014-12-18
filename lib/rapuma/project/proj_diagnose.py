#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle page elements that are used for diagnosing format
# issues in the document. Elements like lines for leading lines and other
# indicators that help with formating tasks can be added to the output.

###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, subprocess, shutil, tempfile, codecs

# Load the local classes
from rapuma.core.tools                  import Tools
from rapuma.core.user_config            import UserConfig
from rapuma.project.proj_config         import Config
from rapuma.core.proj_local             import ProjLocal
from rapuma.core.proj_log               import ProjLog


class ProjDiagnose (object) :

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
        self.layoutConfig               = self.proj_config.layoutConfig
        self.user                       = UserConfig()
        self.userConfig                 = self.user.userConfig
        self.log                        = ProjLog(pid)

        # to [px] is 72/25.4 
        self.mmToPx                     = 72 / 25.4
        # page width [px]
        self.paperPxWidth               = round(self.mmToPx * float(self.layoutConfig['PageLayout']['pageWidth']),1)
        # page height [px]
        self.paperPxHeight              = round(self.mmToPx * float(self.layoutConfig['PageLayout']['pageHeight']),1)

        # Log messages for this module
        self.errorCodes     = {

            '0000' : ['MSG', 'Placeholder message'],
            '1310' : ['WRN', 'Failed to add diagnostic component: [<<1>>] with error: [<<2>>]']

        }


###############################################################################
############################### Create Functions ##############################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################


    def addTransparency (self, target, force = False) :
        '''Add a transparent layer to a rendered PDF file. This will
        add in diagnosing format issues. Using force will cause any
        existing layer file to be remade.'''

        # Do a quick check if the transparency needs to be remade
        # The transparency normally is not remade if one already exists.
        # If one is there, it can be remade in two ways, with a force
        # or a regenerate command.
        if force :
            self.createDiagnostic()
        elif self.tools.str2bool(self.layoutConfig['DocumentFeatures']['regenerateTransparency']) :
            self.createDiagnostic()
        else :
            # If there isn't one, make it
            if not os.path.exists(self.local.diagnosticFile) :
                self.createDiagnostic()

        # Create a special temp named file for the target
        tmpTarget = tempfile.NamedTemporaryFile().name
        # Copy the target to the tmpTarget
        shutil.copy(target, tmpTarget)
        # Overlay the transparency diagnostic file over the tmpTarget
        self.tools.mergePdfFilesPdftk(tmpTarget, self.local.diagnosticFile)
        # Copy the results back to the target (should be done now)
        shutil.copy(tmpTarget, target)


    def createDiagnostic (self) :
        '''Create a diagnostic transparency (file) that will be
        superimposed over the page contents to help diagnose format
        issues. This will overwrite any existing transparency file and
        will add each recognoized diagnostic type found in the 
        diagnosticComponents config setting.'''

#        import pdb; pdb.set_trace()

        self.createBlankTransparency()

        # Add each component to the blank transparency file
        for comp in self.layoutConfig['DocumentFeatures']['diagnosticComponents'] :
            try :
                getattr(self, 'merge' + comp.capitalize())()
            except Exception as e :
                self.log.writeToLog(self.errorCodes['1310'],[comp,str(e)])
                pass

        return True


    def createBlankTransparency (self) :
        '''Create a blank background page according to the trim size
        specified.'''

        # Set the temp svg file name
        svgFile   = tempfile.NamedTemporaryFile().name

        # Be sure there is an illustrations folder in place
        if not os.path.isdir(self.local.projIllustrationFolder) :
            os.mkdir(self.local.projIllustrationFolder)

        #   Write out SVG document text 
        with codecs.open(svgFile, 'wb') as fbackgr :            # open file for writing 
            fbackgr.write( '''<svg xmlns="http://www.w3.org/2000/svg"
                version="1.1" width = "''' + str(self.paperPxWidth) + '''" height = "''' + str(self.paperPxHeight)+ '''">
                </svg>''')

        shutil.copy(self.tools.convertSvgToPdfRsvg(svgFile), self.local.diagnosticFile)


###############################################################################
############################# Component Functions #############################
###############################################################################
######################## Error Code Block Series = 2000 #######################
###############################################################################

    def mergeLeading (self) :
        '''Create a diagnostic page component that has lines to indicate
        the text leading. This will be superimposed over the contents of
        the trim page, not in the background like a watermark, etc.'''

        # Initialize the process
        svgFile             = tempfile.NamedTemporaryFile().name

        # PAGE DIMENSIONS
        # The page dimensions extracted from layoutConfig are in [mm] and
        # must be converted to pixels [px], the conversion factor for [mm]
        # bodyFontSize [px]
        bodyFontSize = self.layoutConfig['TextElements']['bodyFontSize']
        bodyFontPxSize = round(float(bodyFontSize) * 72/72.27,3)
        # bodyTextLeading [px]
        bodyTextLeading = self.layoutConfig['TextElements']['bodyTextLeading']
        bodyTextPxLeading = round(float(bodyTextLeading) * 72/72.27,3)
        # top margin [px]
        topMargin = self.layoutConfig['PageLayout']['topMargin']
        topPxMargin = round(self.mmToPx * float(topMargin),1)
        # outside margin [px]
        outsideMargin = self.layoutConfig['PageLayout']['outsideMargin']
        outsidePxMargin = round(self.mmToPx * float(outsideMargin),1)
        #inside margin [px]
        insideMargin = self.layoutConfig['PageLayout']['insideMargin']
        insidePxMargin = round(self.mmToPx * float(outsideMargin),1)
        # bottom margin [px]
        bottomMargin = self.layoutConfig['PageLayout']['bottomMargin']
        bottomPxMargin = round(self.mmToPx * float(bottomMargin),1)
        # width of the body text
        textPxWidth = self.paperPxWidth - (outsidePxMargin + insidePxMargin)

        # Create the svg file
        with codecs.open(svgFile, 'wb') as fbackgr :            # open file for writing 
                # starting lines of SVG xml
            fbackgr.write( '''<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width = "''' + str(self.paperPxWidth)+ '''" height = "'''+str(self.paperPxHeight) + '''">
                \n    <!--RECTANGLE OF MARGINS-->\n''')
            fbackgr.write( '''<rect x = "''' + str(outsidePxMargin) + '''" y= "''' + str(topPxMargin) + '''" height = "''' + str(self.paperPxHeight - topPxMargin - bottomPxMargin) + '''" width = "''' + str(textPxWidth) + '''" style = "fill:none;fill-opacity:1;stroke:#ffc800;stroke-opacity:1;stroke-width:.2"/>
                \n    <!--START OF LINEGRID-->\n''')
            fbackgr.write( '''<path d= "m ''' + str(outsidePxMargin * 0.75-1) + "," + str(topPxMargin + bodyFontPxSize) + " " + str(textPxWidth + outsidePxMargin * 0.25)+ ''',0''')
                # filling the space between the top line and bottom margin, starting at distance
                # counter num = 0 up to the but not including the total of num x leading
                # equals the distance between top and bottom margin
            num = 0
            while (num < int(round(self.paperPxHeight - bottomPxMargin - topPxMargin)/bodyTextPxLeading)):
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
            while (num < int(round(self.paperPxHeight - bottomPxMargin - topPxMargin)/bodyTextPxLeading)):
                fbackgr.write( '''<tspan x="''' + str(outsidePxMargin * 0.75-2) + '''" dy="''' + str(bodyTextPxLeading) + '''">''' + str(linenumber) + '''</tspan>''') 
                linenumber = linenumber +1  
                num = num +1
            fbackgr.write('''</text> 
                \n  <!--LINEGRID CAPTION-->
                <text  x="36" y="''' + str(self.paperPxHeight - bottomPxMargin+10) + '''" style="font-family: Charis SIL;font-style:italic;font-size:7;fill:#ffc800">page size: ''' + str(int(self.paperPxWidth/72*25.4+.5)) + ''' x ''' + str(int(self.paperPxHeight/72*25.4+.5)) + ''' mm ; font size: ''' + str(bodyFontSize) + ''' pt; leading: ''' + str(bodyTextLeading) + ''' pt</text>
                \n    <!--PURPLE LINES TOP AND BOTTOM MARGINS--> 
                <path d="M ''' + str(outsidePxMargin) + "," + str(topPxMargin) + " " + str(textPxWidth + outsidePxMargin) + "," + str(topPxMargin) + '''" style="fill:#ffffff;fill-opacity:1;stroke-width:0.4px;stroke:#760076;stroke-opacity:1"/>
                <path d="M ''' + str(outsidePxMargin) + "," + str(self.paperPxHeight - bottomPxMargin) + " " + str(textPxWidth + outsidePxMargin) + "," + str(self.paperPxHeight - bottomPxMargin) + '''" style="fill:#ffffff;fill-opacity:1;stroke-width:0.4px;stroke:#760076;stroke-opacity:1"/>
                </svg>''')
    
        # Convert the lines background component to PDF
        leadingPdf = self.tools.convertSvgToPdfRsvg(svgFile)

        # Merge leadingPdf with existing transparency
        results = self.tools.mergePdfFilesPdftk(self.local.diagnosticFile, leadingPdf)
        # Test and return if good
        if os.path.isfile(results) :
            return True

     
