#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This manager class will handle component rendering with XeTeX.



###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, re
import subprocess

# Load the local classes
from rapuma.core.tools import *
from rapuma.project.manager import Manager
from rapuma.group.usfm import PT_Tools
from rapuma.core.proj_config import ConfigTools


###############################################################################
################################## Begin Class ################################
###############################################################################

class Xetex (Manager) :

    # Shared values
    xmlConfFile     = 'xetex.xml'

    def __init__(self, project, cfg, cType) :
        '''Do the primary initialization for this manager.'''

        super(Xetex, self).__init__(project, cfg)

        # Create all the values we can right now for this manager.
        # Others will be created at run time when we know the cid.
        self.project                = project
        self.local                  = project.local
        self.cfg                    = cfg
        self.gid                    = project.gid
        self.cType                  = cType
        self.Ctype                  = cType.capitalize()
        self.renderer               = 'xetex'
        self.manager                = self.cType + '_' + self.renderer.capitalize()
        self.managers               = project.managers
        self.pt_tools               = PT_Tools(project)
        self.configTools            = ConfigTools(project)
        # Bring in some manager objects we will need
#        if self.cType + '_Component' not in self.manager :
#            self.project.createManager(self.cType, 'component')
        self.component = self.managers[self.cType + '_Component']
#        if self.cType + '_Hyphenation' not in self.manager :
#            self.project.createManager(self.cType, 'hyphenation')
        self.hyphenation = self.managers[self.cType + '_Hyphenation']
#        if self.cType + '_Layout' not in self.managers :
#            self.project.createManager(self.cType, 'layout')
        self.layout = self.managers[self.cType + '_Layout']
#        if self.cType + '_Font' not in self.managers :
#            self.project.createManager(self.cType, 'font')
        self.font = self.managers[self.cType + '_Font']
#        if self.cType + '_Style' not in self.managers :
#            self.project.createManager(self.cType, 'style')
        self.style = self.managers[self.cType + '_Style']
        # Get config objs
        self.projConfig             = project.projConfig
        self.layoutConfig           = self.layout.layoutConfig
        self.fontConfig             = self.font.fontConfig
        self.userConfig             = self.project.userConfig
        # Some config settings
        self.pdfViewer              = self.projConfig['Managers'][self.manager]['pdfViewerCommand']
        self.pdfUtilityCommand      = self.projConfig['Managers'][self.manager]['pdfUtilityCommand']
        self.sourceEditor           = self.projConfig['CompTypes'][self.Ctype]['sourceEditor']
        self.macroPackage           = self.projConfig['Managers'][self.manager]['macroPackage']

        # Get settings for this component
        self.managerSettings = self.projConfig['Managers'][self.manager]
        for k, v in self.managerSettings.iteritems() :
            if v == 'True' or v == 'False' :
                setattr(self, k, str2bool(v))
            else :
                setattr(self, k, v)

        # Set some Booleans (this comes after persistant values are set)
        self.usePdfViewer           = str2bool(self.projConfig['Managers'][self.manager]['usePdfViewer'])
        self.useHyphenation         = str2bool(self.projConfig['Groups'][self.gid]['useHyphenation'])
        self.useMarginalVerses      = str2bool(self.layoutConfig['ChapterVerse']['useMarginalVerses'])
        self.useIllustrations       = str2bool(self.layoutConfig['Illustrations']['useIllustrations'])
        self.useLines               = str2bool(self.layoutConfig['PageLayout']['useLines'])
        self.useWatermark           = str2bool(self.layoutConfig['PageLayout']['useWatermark'])

        # File names
        # Some of these file names will only be used once but for consitency
        # we will create them all in one place.
        self.gidTexFileName         = self.gid + '.tex'
        self.gidPdfFileName         = self.gid + '.pdf'
        self.macLinkFileName        = self.cType + '_macLink.tex'
        self.setTexFileName         = self.cType + '_set.tex'
        self.extTexFileName         = self.cType + '_set-ext.tex'
        self.grpExtTexFileName      = self.gid + '-ext.tex'
        self.ptxMargVerseFileName   = 'ptxplus-marginalverses.tex'
        self.watermarkFileName      = self.layoutConfig['PageLayout']['watermarkFile']
        self.linesFileName          = self.layoutConfig['PageLayout']['linesFile']
        # Folder paths
        self.rapumaMacrosFolder     = self.local.rapumaMacrosFolder
        self.rapumaMacPackFolder    = os.path.join(self.rapumaMacrosFolder, self.macroPackage)
        self.rapumaConfigFolder     = self.local.rapumaConfigFolder
        self.projConfFolder         = self.local.projConfFolder
        self.projComponentsFolder   = self.local.projComponentsFolder
        self.gidFolder              = os.path.join(self.projComponentsFolder, self.gid)
        self.projHyphenationFolder  = self.local.projHyphenationFolder
        self.projIllustrationsFolder = self.local.projIllustrationsFolder
        self.projFontsFolder        = self.local.projFontsFolder
        self.projMacrosFolder       = self.local.projMacrosFolder
        self.projMacPackFolder      = os.path.join(self.local.projMacrosFolder, self.macroPackage)
        # Set file names with full path 
        self.gidTexFile             = os.path.join(self.gidFolder, self.gidTexFileName)
        self.gidPdfFile             = os.path.join(self.gidFolder, self.gidPdfFileName)
        self.layoutXmlFile          = os.path.join(self.rapumaConfigFolder, self.project.projectMediaIDCode + '_layout.xml')
        self.layoutConfFile         = os.path.join(self.projConfFolder, self.project.projectMediaIDCode + '_layout.conf')
        self.fontConfFile           = os.path.join(self.projConfFolder, 'font.conf')
        self.illustrationConfFile   = os.path.join(self.projConfFolder, 'illustration.conf')
        self.projConfFile           = os.path.join(self.projConfFolder, 'project.conf')
        self.macLinkFile            = os.path.join(self.projMacrosFolder, self.macLinkFileName)
        self.setTexFile             = os.path.join(self.projMacrosFolder, self.setTexFileName)
        self.extTexFile             = os.path.join(self.projMacrosFolder, self.extTexFileName)
        self.grpExtTexFile          = os.path.join(self.gidFolder, self.grpExtTexFileName)
        self.usrGrpExtTexFile       = os.path.join(self.project.userConfig['Resources']['macros'], self.grpExtTexFile)
        self.defaultStyFile         = self.style.defaultStyFile
        self.defaultExtStyFile      = self.style.defaultExtStyFile
        self.grpExtStyFile          = self.style.grpExtStyFile
        self.rpmExtTexFile          = os.path.join(self.rapumaMacrosFolder, self.extTexFileName)
        self.usrExtTexFile          = os.path.join(self.project.userConfig['Resources']['macros'], self.extTexFileName)
        self.lccodeTexFile          = self.hyphenation.lccodeTexFile
        self.compHyphFile           = self.hyphenation.compHyphFile
        self.grpHyphExcTexFile      = self.hyphenation.grpHyphExcTexFile
#        self.hyphExcepTexFile       = self.hyphenation.hyphExcepTexFileName
#        self.compHyphFile           = os.path.join(self.projHyphenationFolder, self.compHyphFileName)
#        self.hyphExcepTexFile       = os.path.join(self.projHyphenationFolder, self.hyphExcepTexFileName)
        self.ptxMargVerseFile       = os.path.join(self.projMacPackFolder, self.ptxMargVerseFileName)
        self.watermarkFile          = os.path.join(self.projIllustrationsFolder, self.watermarkFileName)
        self.linesFile              = os.path.join(self.projIllustrationsFolder, self.linesFileName)

        # Make any dependent folders if needed
        if not os.path.isdir(self.gidFolder) :
            os.mkdir(self.gidFolder)

        # Check to see if the PDF viewer is ready to go
        if not self.pdfViewer :
            defaultViewer = self.project.userConfig['System']['pdfDefaultViewerCommand']
            self.pdfViewer = defaultViewer
            self.projConfig['Managers'][self.manager]['pdfViewerCommand'] = defaultViewer
            writeConfFile(self.projConfig)

        # Record some error codes
        # FIXME: much more needs to be done with this
        self.xetexErrorCodes =  {
            0   : 'Rendering succeful.',
            256 : 'Something really awful happened.'
                                }


###############################################################################
############################ Manager Level Functions ##########################
###############################################################################

    def rtnBoolDepend (self, bdep) :
        '''Return the boolean value of a boolDepend target. This assumes that
        the format is config:section:key, or config:section:section:key, if
        it ever becomes different, this breaks. The config is expected to be 
        the common internal reference so consitency is absolutly necessary for 
        this to work.'''

        parts = bdep.split(':')
        ptn = len(parts)
        cfg = getattr(self, parts[0])
        if ptn == 3 :
            sec = parts[1]
            key = parts[2]
            if self.configTools.hasPlaceHolder(sec) :
                (holderType, holderKey) = self.configTools.getPlaceHolder(sec)
                # system (self) delclaired value
                if holderType == 'self' :
                    sec = self.configTools.insertValue(sec, getattr(self, holderKey))
            return cfg[sec][key]
        if ptn == 4 :
            secA = parts[1]
            secB = parts[2]
            key = parts[3]
            if self.configTools.hasPlaceHolder(secB) :
                (holderType, holderKey) = self.configTools.getPlaceHolder(secB)
                # system (self) delclaired value
                if holderType == 'self' :
                    secB = self.configTools.insertValue(secB, getattr(self, holderKey))
            return cfg[secA][secB][key]


    def copyInMargVerse (self) :
        '''Copy in the marginalverse macro package.'''

        # Copy in to the process folder the macro package for this component
        if not os.path.isdir(self.projMacPackFolder) :
            os.makedirs(self.projMacPackFolder)

        if not os.path.isfile(self.ptxMargVerseFile) :
            shutil.copy(os.path.join(self.rapumaMacPackFolder, fName(self.ptxMargVerseFile)), self.ptxMargVerseFile)
            self.project.log.writeToLog('XTEX-070', [fName(self.ptxMargVerseFile)])
            return True


    def removeMargVerse (self) :
        '''Remove the marginal verse macro package from the project.'''

        if os.path.isfile(self.ptxMargVerseFile) :
            os.remove(self.ptxMargVerseFile)
            return True


    def makeTexSettingsDict (self, xmlFile) :
        '''Create a dictionary object from a layout xml file. This will track two kinds of
        bool settings for both True and False so setting output can be determined depending
        on what kind of bool it is. boolDependFalse is a very rare case though. Nonetheless
        those are tracked for each setting regardless of their use.'''

        if  os.path.exists(xmlFile) :
            # Read in our XML file
            doc = ElementTree.parse(xmlFile)
            # Create an empty dictionary
            data = {}
            # Extract the section/key/value data
            thisSection = ''; thisTex = ''; thisBoolDepTrue = ''; thisBoolDepFalse = ''
            for event, elem in ElementTree.iterparse(xmlFile):
                if elem.tag == 'setting' :
                    if thisTex or thisBoolDepTrue or thisBoolDepFalse:
                        data[thisSection] = {self.macroPackage : thisTex, 'boolDependTrue' : thisBoolDepTrue, 'boolDependFalse' : thisBoolDepFalse}
                    thisSection = ''
                    thisTex = ''
                    thisBoolDepTrue = ''
                    thisBoolDepFalse = ''
                if elem.tag == 'key' :
                    thisSection = elem.text
                elif elem.tag == self.macroPackage :
                    thisTex = elem.text
                elif elem.tag == 'boolDependTrue' :
                    thisBoolDepTrue = elem.text
                elif elem.tag == 'boolDependFalse' :
                    thisBoolDepFalse = elem.text
            # Ship it!
            return data
        else :
            raise IOError, "Can't open " + xmlFile


    def copyInMacros (self) :
        '''Copy in the right macro set for this component and renderer combination.'''

        if self.cType.lower() == 'usfm' :

            # Copy in to the process folder the macro package for this component
            if not os.path.isdir(self.projMacPackFolder) :
                os.makedirs(self.projMacPackFolder)

            mCopy = False
            for root, dirs, files in os.walk(self.rapumaMacPackFolder) :
                for f in files :
                    fTarget = os.path.join(self.projMacPackFolder, f)
                    if not os.path.isfile(fTarget) :
                        shutil.copy(os.path.join(self.rapumaMacPackFolder, f), fTarget)
                        mCopy = True
                        self.project.log.writeToLog('XTEX-070', [fName(fTarget)])

            return mCopy
        else :
            self.project.log.writeToLog('XTEX-075', [self.cType])


    def displayPdfOutput (self) :
        '''Display a PDF XeTeX output file if that is turned on.'''

#        import pdb; pdb.set_trace()
        if self.usePdfViewer :
            # Build the viewer command
            self.pdfViewer.append(self.gidPdfFile)
            # Run the XeTeX and collect the return code for analysis
            try :
                subprocess.Popen(self.pdfViewer)
                # FIXME: We need to pop() the last item (pdfFile)
                # to avoid it somehow being writen out to the proj.conf
                self.pdfViewer.pop()
                return True
            except Exception as e :
                # If we don't succeed, we should probably quite here
                self.project.log.writeToLog('XTEX-105', [str(e)])


    def makeGrpHyphExcTexFile (self) :
        '''Create a TeX hyphenation file. There must be a texWordList for this
        to work properly.'''

        description = 'This is an auto-generated hyphenation exceptions word list for this group. \
             Please refer to the documentation for details on how to make changes.'

        # Try to get dependent files in place
        if not os.path.isfile(self.compHyphFile) :
            # Call the Hyphenation manager to create a sorted file of hyphenated words
            self.hyphenation.updateHyphenation()

        # Create the output file here
        with codecs.open(self.grpHyphExcTexFile, "w", encoding='utf_8') as hyphenTexObject :
            hyphenTexObject.write(makeFileHeader(fName(self.grpHyphExcTexFile), description))
            hyphenTexObject.write('\hyphenation{\n')
            with codecs.open(self.compHyphFile, "r", encoding='utf_8') as hyphenWords :
                for word in hyphenWords :
                    # Strip out commented lines/words
                    if word[:1] != '#' and word != '' :
                        # Swap the generic hyphen markers out if they are there
                        hyphenTexObject.write(re.sub(u'<->', u'-', word))

            hyphenTexObject.write('}\n')

        return True


    def makeLccodeTexFile (self) :
        '''Make a simple starter lccode file to be used with TeX hyphenation.'''

        description = 'This is an auto-generated lccode rules file for this project. \
            Please refer to the documentation for details on how to make changes.'

        # Create the file and put default settings in it
        with codecs.open(self.lccodeTexFile, "w", encoding='utf_8') as lccodeObject :
            lccodeObject.write(makeFileHeader(fName(self.lccodeTexFile), description))
            lccodeObject.write('\lccode "2011 = "2011	% Allow TeX hyphenation to ignore a Non-break hyphen\n')
            # Add in all our non-word-forming characters as found in our PT project
            for c in self.pt_tools.getNWFChars() :
                uv = rtnUnicodeValue(c)
                # We handel these chars special in this context
                if not uv in ['2011', '002D'] :
                    lccodeObject.write('\lccode "' + uv + ' = "' + uv + '\n')

            # Add special exceptions
            lccodeObject.write('\catcode "2011 = 11	% Changing the catcode here allows the \lccode above to work\n')

        return True



###############################################################################
############################# DEPENDENCY FUNCTIONS ############################
###############################################################################

    def makeMacLinkFile (self) :
        '''Check for the exsistance of or the age of the macLink dependent file.
        Create or refresh if needed. If there are any problems, report and die.'''

        description = 'This file provides a link between XeTeX and the project macro \
            package. It should be one of the first TeX files to be read when XeTeX \
            starts the rendering process.'

        # Set some file names
        if self.macroPackage == 'usfmTex' :
            mainMacroFile = os.path.join(self.projMacPackFolder, 'paratext2.tex')
        elif self.macroPackage == 'usfmTex-auto' :
            mainMacroFile = os.path.join(self.projMacPackFolder, 'paratext2.tex')
        else :
            self.project.log.writeToLog('XTEX-115', [self.macroPackage])

        # Check to see if our macros are there
        if not os.path.isdir(self.projMacPackFolder) :
            self.copyInMacros()

        # Check for existance and age. List any files in this next list that
        # could require the rebuilding of the link file
        makeLinkFile = False
        dep = [mainMacroFile, self.fontConfFile, self.layoutConfFile, self.projConfFile]
        if not os.path.isfile(self.macLinkFile) :
            makeLinkFile = True
            self.project.log.writeToLog('XTEX-065', [fName(self.macLinkFile)])
        else :
            for f in dep :
                if isOlder(self.macLinkFile, f) :
                    makeLinkFile = True
                    self.project.log.writeToLog('XTEX-060', [fName(f),fName(self.macLinkFile)])

        if makeLinkFile :
            with codecs.open(self.macLinkFile, "w", encoding='utf_8') as writeObject :
                writeObject.write(makeFileHeader(fName(self.macLinkFile), description))
                writeObject.write('\\input ' + quotePath(mainMacroFile) + '\n')
                # If we are using marginal verses then we will need this
                if self.useMarginalVerses :
                    self.copyInMargVerse()
                    writeObject.write('\\input ' + quotePath(self.ptxMargVerseFile) + '\n')
                else :
                    self.removeMargVerse()

        return True


    def makeSetTexFile (self) :
        '''Create the main settings file that XeTeX will use in gidTex to render 
        gidPdf. This is a required file so it will run every time. However, it
        may not need to be remade. We will look for its exsistance and then compare 
        it to its primary dependents to see if we actually need to do anything.'''

        description = 'This is the main settings file that XeTeX will use to configure \
            the rendered output. It can be overridden by other TeX macro files that \
            are added in down-stream.'

        # Set vals
        dep = [self.layoutConfFile, self.fontConfFile, self.projConfFile]
        makeIt = False

        # Check for existance and age
#        import pdb; pdb.set_trace()
        if os.path.isfile(self.setTexFile) :
            for f in dep :
                if isOlder(self.setTexFile, f) :
                    # Something changed in a conf file this is dependent on
                    makeIt = True
                    break
        else :
            makeIt = True

        # Bail out here if necessary, return True because everything seems okay
        if not makeIt :
            return True
        else :
            # Otherwise make/remake the file
            macTexVals = dict(self.makeTexSettingsDict(self.layoutXmlFile))

            writeObject = codecs.open(self.setTexFile, "w", encoding='utf_8')
            writeObject.write(makeFileHeader(fName(self.setTexFile), description))

            # Bring in the settings from the layoutConfig
            for section in self.layoutConfig.keys() :
                writeObject.write('\n% ' + section + '\n')
                vals = {}

                # Do a precheck here for input order that could affect the section.
                # Be on the look out for an input ordering field. If there is one
                # it should have two or more items in the list this becomes the
                # base for our inputsOrder list used for output
                try :
                    # This setting must have a boolDepend, check what it is here
                    if str2bool(self.rtnBoolDepend(macTexVals['inputsOrder']['boolDependTrue'])) :
                        inputsOrder = self.layoutConfig[section]['inputsOrder']
                    else :
                        inputsOrder = []
                except :
                    inputsOrder = []

                # Start gathering up all the items in this section now
                for k, v in self.layoutConfig[section].iteritems() :
                    # This will prevent output on empty fields, never output when
                    # there is no value
                    if not v :
                        continue
                    # Gather each macro package line we need to output
                    if testForSetting(macTexVals, k, self.macroPackage) :
                        macVal = (macTexVals[k][self.macroPackage])
                        # Test for boolDepend True and False. If there is a boolDepend
                        # then we don't need to output just yet. These next two if/elif
                        # statements insure that output happens in the proper condition.
                        # In some cases we want output only if a certain bool is set to
                        # true, but in a few rare cases we want output when a certain
                        # bool is set to false. These will screen for both cases.
                        if testForSetting(macTexVals, k, 'boolDependTrue') and not str2bool(self.rtnBoolDepend(macTexVals[k]['boolDependTrue'])) :
                            continue
                        elif testForSetting(macTexVals, k, 'boolDependFalse') and not str2bool(self.rtnBoolDepend(macTexVals[k]['boolDependFalse'])) == False :
                            continue
                        # After having made it past the previous two tests, we can ouput now.
                        else :
                            # Here we will build a dictionary for this section made up
                            # of all the k, v, and macVals needed. We also build a
                            # list of keys to be used for ordered output
                            vals[k] = [v, macVal]
                            if not k in inputsOrder :
                                # In case there was an inputsOrder list in the config,
                                # this will prepend the value to that list. The idea is
                                # that the ordered output goes last (or at the bottom)
                                inputsOrder.insert(0, k)

                # Write the lines out according to the inputsOrder
                for key in inputsOrder :
                    writeObject.write(self.configTools.processLinePlaceholders(vals[key][1], vals[key][0]) + '\n')

            # Move on to Fonts, add all the font def commands
            def addParams (writeObject, pList, line) :
                for k,v in pList.iteritems() :
                    if v :
                        line = line.replace(k, v)
                    else :
                        line = line.replace(k, '')
                # Clean out unused placeholders
                line = re.sub(u"\^\^[a-z]+\^\^", "", line)
                # Remove unneeded colon from the end of the string
                line = re.sub(u":\"", "\"", line)
                # Write it out
                writeObject.write(line + '\n')

            writeObject.write('\n% Font Definitions\n')
            for f in self.projConfig['Managers'][self.cType + '_Font']['installedFonts'] :
                fInfo = self.fontConfig['Fonts'][f]
                fontPath            = os.path.join(self.projFontsFolder, f)
                useMapping          = self.projConfig['Managers'][self.cType + '_Font']['useMapping']
                if useMapping :
                    useMapping      = os.path.join(fontPath, useMapping)
                useRenderingSystem  = self.projConfig['Managers'][self.cType + '_Font']['useRenderingSystem']

                useLanguage         = self.projConfig['Managers'][self.cType + '_Font']['useLanguage']
                params              = {}
                if useMapping :
                    params['^^mapping^^'] = ':mapping=' + useMapping
                if useRenderingSystem :
                    params['^^renderer^^'] = '/' + useRenderingSystem
                if useLanguage :
                    params['^^language^^'] = ':language=' + useLanguage
                if fontPath :
                    params['^^path^^'] = fontPath

    #            import pdb; pdb.set_trace()
                # Create the fonts settings that will be used with TeX
                if self.projConfig['Managers'][self.cType + '_Font']['primaryFont'] == f :
                    # Primary
                    writeObject.write('\n% These are normal use fonts for this type of component.\n')
                    for k, v in fInfo['UsfmTeX']['PrimaryFont'].iteritems() :
                        addParams(writeObject, params, v)

                    # Secondary
                    writeObject.write('\n% These are font settings for other custom uses.\n')
                    for k, v in fInfo['UsfmTeX']['SecondaryFont'].iteritems() :
                        addParams(writeObject, params, v)

                # There maybe additional fonts for this component. Their secondary settings need to be captured
                # At this point it would be difficult to handle a full set of parms with a secondary
                # font. For this reason, we take them all out. Only the primary font will support
                # all font features.
                params              = {'^^mapping^^' : '', '^^renderer^^' : '', '^^language^^' : '', '^^path^^' : fontPath}
                if self.project.projConfig['Managers'][self.cType + '_Font']['primaryFont'] != f :
                    # Secondary (only)
                    writeObject.write('\n% These are non-primary extra font settings for other custom uses.\n')
                    for k, v in fInfo['UsfmTeX']['SecondaryFont'].iteritems() :
                        addParams(writeObject, params, v)

            # Add special custom commands (may want to parameterize and move 
            # these to the config XML at some point)
            writeObject.write('\n% Special commands\n')

            # This will insert a code that allows the use of numbers in the source text
            writeObject.write(u'\\catcode`@=11\n')
            writeObject.write(u'\\def\\makedigitsother{\\m@kedigitsother}\n')
            writeObject.write(u'\\def\\makedigitsletters{\\m@kedigitsletters}\n')
            writeObject.write(u'\\catcode `@=12\n')

            # Special space characters
            writeObject.write(u'\\def\\nbsp{\u00a0}\n')
            writeObject.write(u'\\def\\zwsp{\u200b}\n')

            ## Baselineskip Adjustment Hook
            # This hook provides a means to adjust the baselineskip on a
            # specific style. It provides a place to put the initial 
            # setting so the hook can make the change and then go back
            # to the initial setting when done.
            # Usage Example:
            #   \sethook{start}{s1}{\remblskip=\baselineskip \baselineskip=10pt}
            #   \sethook{after}{s1}{\baselineskip=\remblskip}
            writeObject.write(u'\\newdimen\\remblskip \\remblskip=\\baselineskip\n')

            # WORKING TEXT LINE SPACING
            # Take out a little space between lines in working text
            writeObject.write(u'\\def\\suckupline{\\vskip -\\baselineskip}\n')
            writeObject.write(u'\\def\\suckuphalfline{\\vskip -0.5\\baselineskip}\n')
            writeObject.write(u'\\def\\suckupqline{\\vskip -0.25\\baselineskip}\n')

            # Skip some space in the working text
            writeObject.write(u'\\def\\skipline{\\vskip\\baselineskip}\n')
            writeObject.write(u'\\def\\skiphalfline{\\vskip 0.5\\baselineskip}\n')
            writeObject.write(u'\\def\\skipqline{\\vskip 0.25\\baselineskip}\n')

            # End here
            writeObject.close()
            self.project.log.writeToLog('XTEX-040', [fName(self.setTexFile)])
            return True


    def makeGrpExtTexFile (self) :
        '''Create/copy a group TeX extentions file to the project for specified group.'''

        description = 'This is the group extention file which overrides settings in \
        the main TeX settings files and the component TeX settings.'

        # First look for a user file, if not, then make a blank one
        if not os.path.isfile(self.grpExtTexFile) :
            if os.path.isfile(self.usrGrpExtTexFile) :
                shutil.copy(self.usrGrpExtTexFile, self.grpExtTexFile)
            else :
                # Create a blank file
                with codecs.open(self.grpExtTexFile, "w", encoding='utf_8') as writeObject :
                    writeObject.write(makeFileHeader(fName(self.grpExtTexFile), description, False))
                self.project.log.writeToLog('XTEX-040', [fName(self.grpExtTexFile)])

        # Need to return true here even if nothing was done
        return True


    def makeExtTexFile (self) :
        '''Create/copy a TeX extentions file that has custom code for a project component
        type. This will go in before the group extentions file.'''

        description = 'This the component TeX macro settings file. The settings \
            in this file can override the main TeX settings and these settings \
            can be overridden by the group-level settings file.'

        # First look for a user file, if not, then one 
        # from Rapuma, worse case, make a blank one
        if not os.path.isfile(self.extTexFile) :
            if os.path.isfile(self.usrExtTexFile) :
                shutil.copy(self.usrExtTexFile, self.extTexFile)
            elif os.path.isfile(self.rpmExtTexFile) :
                shutil.copy(self.rpmExtTexFile, self.extTexFile)
            else :
                # Create a blank file
                with codecs.open(self.extTexFile, "w", encoding='utf_8') as writeObject :
                    writeObject.write(makeFileHeader(fName(self.extTexFileName), description, False))
                self.project.log.writeToLog('XTEX-040', [fName(self.extTexFile)])

        # Need to return true here even if nothing was done
        return True


    def makeGidTexFile (self, cidList) :
        '''Create the main gid TeX control file.'''

        description = 'This is the group TeX control file. XeTeX will \
            read this file to get all of links to other instructions (macros) \
            needed to render the group, or a component of a group.'

        # Since a render run could contain any number of components
        # in any order, we will remake this file on every run. No need
        # for dependency checking
        if os.path.exists(self.gidTexFile) :
            os.remove(self.gidTexFile)

        # Start writing out the gid.tex file. Check/make dependencies as we go.
        # If we fail to make a dependency it will die and report during that process.
        with codecs.open(self.gidTexFile, "w", encoding='utf_8') as gidTexObject :
            gidTexObject.write(makeFileHeader(self.gidTexFileName, description))
            if self.makeMacLinkFile() :
                gidTexObject.write('\\input \"' + self.macLinkFile + '\"\n')
            if self.makeSetTexFile() :
                gidTexObject.write('\\input \"' + self.setTexFile + '\"\n')
            if self.makeExtTexFile() :
                gidTexObject.write('\\input \"' + self.extTexFile + '\"\n')
            if self.makeGrpExtTexFile() :
                gidTexObject.write('\\input \"' + self.grpExtTexFile + '\"\n')
            if self.hyphenation.checkGrpHyphExcTexFile() :
                gidTexObject.write('\\input \"' + self.grpHyphExcTexFile + '\"\n')
            if self.style.checkDefaultStyFile() :
                gidTexObject.write('\\stylesheet{' + self.defaultStyFile + '}\n')
            if self.style.checkDefaultExtStyFile() :
                gidTexObject.write('\\stylesheet{' + self.defaultExtStyFile + '}\n')
            if self.style.checkGrpExtStyFile() :
                gidTexObject.write('\\stylesheet{' + self.grpExtStyFile + '}\n')
            for cid in cidList :
                cidSource = os.path.join(self.projComponentsFolder, cid, self.component.makeFileName(cid))
                gidTexObject.write('\\ptxfile{' + cidSource + '}\n')
            # This can only hapen once in the whole process, this marks the end
            gidTexObject.write('\\bye\n')

        return True


    def checkGrpHyphExcTexFile (self) :
        '''If hyphenation is used, check for the exsistance of the group TeX Hyphenation 
        exception file. If not found, kindly ask the appropreate function to make it.'''

        if self.useHyphenation :
            # The TeX group hyphen exceptions file
            if not os.path.isfile(self.grpHyphExcTexFile) or isOlder(self.grpHyphExcTexFile, self.compHyphFile) :
                if self.makeGrpHyphExcTexFile() :
                    self.project.log.writeToLog('XTEX-130', [fName(self.grpHyphExcTexFile)])
                else :
                    # If we can't make it, we return False
                    self.project.log.writeToLog('XTEX-170', [fName(self.grpHyphExcTexFile)])
                    return False
            # The TeX lccode file
            if not os.path.exists(self.lccodeTexFile) or isOlder(self.lccodeTexFile, self.grpHyphExcTexFile) :
                if self.makeLccodeTexFile() :
                    self.project.log.writeToLog('XTEX-130', [fName(self.lccodeTexFile)])
                else :
                    # If we can't make it, we return False
                    self.project.log.writeToLog('XTEX-170', [fName(self.lccodeTexFile)])
                    return False
            return True
        else :
            # If Hyphenation is turned off, we return True and don't need to worry about it.
            return True


###############################################################################
################################# Main Function ###############################
###############################################################################

    def run (self, renderParams) :
        '''This will check all the dependencies for a group and then
        use XeTeX to render it.'''

        cidList = renderParams['cidList']
        # This is the file we will make. If force is set, delete the old one.
        if renderParams['force'] :
            if os.path.isfile(self.gidPdfFile) :
                os.remove(self.gidPdfFile)

        # Create, if necessary, the gid.tex file
        # First, go through and make/update any dependency files
        self.makeMacLinkFile()
        self.makeSetTexFile()
        self.makeExtTexFile()
        self.checkGrpHyphExcTexFile()
        # Now make the gid main setting file
        self.makeGidTexFile(cidList)

        # Dynamically create a dependency list for the render process
        dep = [self.gidTexFile, self.extTexFile]
        for cid in cidList :
            cidUsfm = self.project.groups[self.gid].getCidPath(cid)
            cidAdj = self.project.groups[self.gid].getCidAdjPath(cid)
            cidIlls = self.project.groups[self.gid].getCidPiclistPath(cid)
            dep.append(cidUsfm)
            if os.path.isfile(cidAdj) :
                dep.append(cidAdj)
            if os.path.isfile(cidIlls) :
                dep.append(cidIlls)

        # Render if gidPdf is older or is missing
        render = False
        if not os.path.isfile(self.gidPdfFile) :
            render = True
        else :
            for d in dep :
                if isOlder(self.gidPdfFile, d) :
                    render = True
                    break

        # Call the renderer
        if render :
            # Create the environment that XeTeX will use. This will be temporarily set
            # by subprocess.call() just before XeTeX is run.
            texInputsLine = self.project.local.projHome + ':' \
                            + self.projMacPackFolder + ':' \
                            + self.projMacrosFolder + ':' \
                            + self.gidFolder + ':.'

            # Create the environment dictionary that will be fed into subprocess.call()
            envDict = dict(os.environ)
            envDict['TEXINPUTS'] = texInputsLine

            # Create the XeTeX command argument list that subprocess.call()
            # will run with
            cmds = ['xetex', '-output-directory=' + self.gidFolder, self.gidTexFile]

            # Run the XeTeX and collect the return code for analysis
#                dieNow()
            rCode = subprocess.call(cmds, env = envDict)

            # Analyse the return code
            if rCode == int(0) :
                self.project.log.writeToLog('XTEX-025', [fName(self.gidTexFile)])
            elif rCode in self.xetexErrorCodes :
                self.project.log.writeToLog('XTEX-030', [fName(self.gidTexFile), self.xetexErrorCodes[rCode], str(rCode)])
            else :
                self.project.log.writeToLog('XTEX-035', [str(rCode)])
                dieNow()

        # Add lines background for composition work
        if self.useLines :
            cmd = [self.pdfUtilityCommand, gidPdf, 'background', linesFile, 'output', tempName(gidPdf)]
            try :
                subprocess.call(cmd)
                shutil.copy(tempName(gidPdf), gidPdf)
                os.remove(tempName(gidPdf))
                self.project.log.writeToLog('XTEX-165')
            except Exception as e :
                # If we don't succeed, we should probably quite here
                self.project.log.writeToLog('XTEX-160', [str(e)])
                dieNow()

        # Add a watermark if required
        if self.useWatermark :
            cmd = [self.pdfUtilityCommand, self.gidPdfFile, 'background', self.watermarkFile, 'output', tempName(self.gidPdfFile)]
            try :
                subprocess.call(cmd)
                shutil.copy(tempName(self.gidPdfFile), self.gidPdfFile)
                os.remove(tempName(self.gidPdfFile))
                self.project.log.writeToLog('XTEX-145')
            except Exception as e :
                # If we don't succeed, we should probably quite here
                self.project.log.writeToLog('XTEX-140', [str(e)])
                dieNow()

        # Review the results if desired
        if os.path.isfile(self.gidPdfFile) :
            if self.displayPdfOutput() :
                self.project.log.writeToLog('XTEX-095', [fName(self.gidPdfFile)])
            else :
                self.project.log.writeToLog('XTEX-100', [fName(self.gidPdfFile)])




