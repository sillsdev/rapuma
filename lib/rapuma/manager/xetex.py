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
from rapuma.component.usfm import PT_Tools
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
        self.cType                  = cType
        self.Ctype                  = cType.capitalize()
        self.cName                  = project.cName
        self.renderer               = 'xetex'
        self.manager                = self.cType + '_' + self.renderer.capitalize()
        self.managers               = project.managers
        self.pt_tools               = PT_Tools(project)
        self.configTools            = ConfigTools(project)
        self.hy_tools               = self.managers[self.cType + '_Hyphenation']
        # ConfigObjs
        self.projConfig             = project.projConfig
        if self.cType + '_Layout' not in self.managers :
            self.project.createManager(self.cType, 'layout')
        self.layoutConfig           = self.managers[self.cType + '_Layout'].layoutConfig
        if self.cType + '_Font' not in self.managers :
            self.project.createManager(self.cType, 'font')
        self.fontConfig             = self.managers[self.cType + '_Font'].fontConfig
        self.userConfig             = self.project.userConfig
        # Config Settings
        self.macroPackage           = self.projConfig['Managers'][self.manager]['macroPackage']
        self.pdfViewer              = self.projConfig['Managers'][self.manager]['pdfViewerCommand']
        self.pdfUtilityCommand      = self.projConfig['Managers'][self.manager]['pdfUtilityCommand']
        self.sourceEditor           = self.projConfig['CompTypes'][self.Ctype]['sourceEditor']
        self.macroPackage           = self.projConfig['Managers'][self.manager]['macroPackage']
        self.mainStyleFile          = self.projConfig['Managers'][self.cType + '_Style']['mainStyleFile']
        self.customStyleFile        = self.projConfig['Managers'][self.cType + '_Style']['customStyleFile']
        # Note: a little slight-of-hand goes on here with the processLinePlaceholders()
        # function when we send it the same value in two places. One acts as the line value
        # with a placeholder while acts as the value itself, which happens to need converting.
        lccodeValue                 = self.layoutConfig['Hyphenation']['lccodeFile']
        self.lccodeFile             = self.configTools.processLinePlaceholders(lccodeValue, lccodeValue)
        hyphenExceptValue           = self.layoutConfig['Hyphenation']['hyphenExceptionsFile']
        self.hyphenExceptionsFile   = self.configTools.processLinePlaceholders(hyphenExceptValue, hyphenExceptValue)
        compHyphenValue             = self.layoutConfig['Hyphenation']['compHyphenFile']
        self.compHyphenFile         = self.configTools.processLinePlaceholders(compHyphenValue, compHyphenValue)
        self.useIllustrations       = self.layoutConfig['Illustrations']['useIllustrations']
        # Folder paths
        self.rapumaMacrosFolder     = self.local.rapumaMacrosFolder
        self.rapumaConfigFolder     = self.local.rapumaConfigFolder
        self.projConfFolder         = self.local.projConfFolder
        self.projComponentsFolder   = self.local.projComponentsFolder
        self.projHyphenationFolder  = self.local.projHyphenationFolder
        self.projFontsFolder        = self.local.projFontsFolder
        self.projStylesFolder       = self.local.projStylesFolder
        self.projMacrosFolder       = self.local.projMacrosFolder
        self.cNameFolder            = os.path.join(self.projComponentsFolder, self.cName)
        self.projMacPackFolder      = os.path.join(self.local.projMacrosFolder, self.macroPackage)
        self.sourcePath             = getattr(self.project, self.cType + '_sourcePath')
        # File names
        self.ptxMargVerseFile       = os.path.join(self.projMacPackFolder, 'ptxplus-marginalverses.tex')
        self.macLinkFile            = 'xetex_macLink' + self.cType + '.tex'
        self.setFileName            = 'xetex_settings_' + self.cType + '.tex'
        self.extFileName            = 'xetex_settings_' + self.cType + '-ext.tex'

        # Get settings for this component
        self.managerSettings = self.projConfig['Managers'][self.manager]
        for k, v in self.managerSettings.iteritems() :
            if v == 'True' or v == 'False' :
                setattr(self, k, str2bool(v))
            else :
                setattr(self, k, v)

        # Set some Booleans (this comes after persistant values are set)
        self.usePdfViewer           = str2bool(self.projConfig['Managers'][self.manager]['usePdfViewer'])
        self.useHyphenation         = str2bool(self.projConfig['Managers'][self.cType + '_Hyphenation']['useHyphenation'])
        self.useMarginalVerses      = str2bool(self.layoutConfig['ChapterVerse']['useMarginalVerses'])

        # Set file names with full path (this after booleans are set)
        self.layoutXmlFile          = os.path.join(self.rapumaConfigFolder, self.project.projectMediaIDCode + '_layout.xml')
        self.layoutConfFile         = os.path.join(self.projConfFolder, self.project.projectMediaIDCode + '_layout.conf')
        self.fontConfFile           = os.path.join(self.projConfFolder, 'font.conf')
        self.illustrationConfFile   = os.path.join(self.projConfFolder, 'illustration.conf')
        self.projConfFile           = os.path.join(self.projConfFolder, 'project.conf')
        self.macLink                = os.path.join(self.projMacrosFolder, self.macroPackage, self.macLinkFile)
        self.setFile                = os.path.join(self.projMacrosFolder, self.macroPackage, self.setFileName)
        self.extFile                = os.path.join(self.projMacrosFolder, self.macroPackage, self.extFileName)
        self.globSty                = os.path.join(self.projStylesFolder, self.mainStyleFile)
        self.lccodeTex              = os.path.join(self.local.projHyphenationFolder, self.lccodeFile)
        if os.path.isfile(os.path.join(self.projStylesFolder, self.customStyleFile)) :
            self.custSty            = os.path.join(self.projStylesFolder, self.customStyleFile)
        else :
            self.custSty            = ''
        if self.useHyphenation :
            self.hyphenTex          = os.path.join(self.local.projHyphenationFolder, self.hyphenExceptionsFile)
            self.compHyphen         = os.path.join(self.projHyphenationFolder, self.compHyphenFile)
        else :
            self.hyphenTex          = ''
            self.compHyphen         = ''

        # Make any dependent folders if needed
        if not os.path.isdir(self.cNameFolder) :
            os.mkdir(self.cNameFolder)

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


    def texFileHeader (self, fName) :
        '''Create a generic file header for a non-editable .tex file.'''

        return '% ' + fName + ' created: ' + tStamp() + '\n' \
            + '% This file is auto-generated, do not bother editing it\n\n'


    def copyInMargVerse (self) :
        '''Copy in the marginalverse macro package.'''

        macrosTarget    = os.path.join(self.local.projMacrosFolder, self.macroPackage)
        macrosSource    = os.path.join(self.local.rapumaMacrosFolder, self.macroPackage)

        # Copy in to the process folder the macro package for this component
        if not os.path.isdir(macrosTarget) :
            os.makedirs(macrosTarget)

        if not os.path.isfile(self.ptxMargVerseFile) :
            shutil.copy(os.path.join(macrosSource, fName(self.ptxMargVerseFile)), self.ptxMargVerseFile)
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


    def copyInMacros (self, cType) :
        '''Copy in the right macro set for this component and renderer combination.'''

        if cType.lower() == 'usfm' :
            macrosTarget    = os.path.join(self.projMacrosFolder, self.macroPackage)
            macrosSource    = os.path.join(self.rapumaMacrosFolder, self.macroPackage)
            copyExempt      = [fName(self.extFile), fName(self.ptxMargVerseFile)]

            # Copy in to the process folder the macro package for this component
            if not os.path.isdir(macrosTarget) :
                os.makedirs(macrosTarget)

            mCopy = False
            for root, dirs, files in os.walk(macrosSource) :
                for f in files :
                    fTarget = os.path.join(macrosTarget, f)
                    if fName(f) not in copyExempt :
                        if not os.path.isfile(fTarget) :
                            shutil.copy(os.path.join(macrosSource, f), fTarget)
                            mCopy = True
                            self.project.log.writeToLog('XTEX-070', [fName(fTarget)])

            return mCopy
        else :
            self.project.log.writeToLog('XTEX-075', [cType])


    def displayPdfOutput (self, pdfFile) :
        '''Display a PDF XeTeX output file if that is turned on.'''

#        import pdb; pdb.set_trace()
        if self.usePdfViewer :
            # Build the viewer command
            self.pdfViewer.append(pdfFile)
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


    def makeHyphenExceptionFile (self) :
        '''Create a TeX hyphenation file. There must be a texWordList for this
        to work properly.'''

        # Create the output file here
        with codecs.open(self.hyphenTex, "w", encoding='utf_8') as hyphenTexObject :
            hyphenTexObject.write('% ' + fName(self.hyphenTex) + '\n')
            hyphenTexObject.write('% This is an auto-generated hyphenation rules file for this project.\n')
            hyphenTexObject.write('% Please refer to the documentation for details on how to make changes.\n\n')
            hyphenTexObject.write('\hyphenation{\n')
            # Look for the intermediate component hyphenation file, remake if needed
            # Go get the file if it is to be had
            if not os.path.isfile(self.compHyphen) :
                # Call the Hyphenation manager to create a sorted file of hyphenated words
                self.hy_tools.updateHyphenation(self.cType)
            with codecs.open(self.compHyphen, "r", encoding='utf_8') as hyphenWords :
                for word in hyphenWords :
                    # Strip out commented lines/words
                    if word[:1] != '#' and word != '' :
                        # Swap the generic hyphen markers out if they are there
                        hyphenTexObject.write(re.sub(u'<->', u'-', word))

            hyphenTexObject.write('}\n')

        return True


    def makeLccodeFile (self) :
        '''Make a simple starter lccode file to be used with TeX hyphenation.'''

        # Create the file and put default settings in it
        with codecs.open(self.lccodeTex, "w", encoding='utf_8') as lccodeObject :
            lccodeObject.write('% ' + fName(self.lccodeTex) + '\n')
            lccodeObject.write('% This is an auto-generated lccode rules file for this project.\n')
            lccodeObject.write('% Please refer to the documentation for details on how to make changes.\n\n')
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

    def makeDepMacLink (self) :
        '''Check for the exsistance of or the age of the macLink dependent file.
        Create or refresh if needed. If there are any problems, report and die.'''

        # Set some file names
        if self.macroPackage == 'usfmTex' :
            mainMacroFile = os.path.join(self.projMacPackFolder, 'paratext2.tex')
        elif self.macroPackage == 'usfmTex-auto' :
            mainMacroFile = os.path.join(self.projMacPackFolder, 'paratext2.tex')
        else :
            self.project.log.writeToLog('XTEX-115', [self.macroPackage])

        # Check to see if our macros are there
        if not os.path.isdir(self.projMacPackFolder) :
            self.copyInMacros(self.cType)

        # Check for existance and age. List any files in this next list that
        # could require the rebuilding of the link file
        makeLinkFile = False
        dep = [mainMacroFile, self.fontConfFile, self.layoutConfFile, self.projConfFile]
        if not os.path.isfile(self.macLink) :
            makeLinkFile = True
            self.project.log.writeToLog('XTEX-065', [fName(self.macLink)])
        else :
            for f in dep :
                if isOlder(self.macLink, f) :
                    makeLinkFile = True
                    self.project.log.writeToLog('XTEX-060', [fName(f),fName(self.macLink)])

        if makeLinkFile :
            with codecs.open(self.macLink, "w", encoding='utf_8') as writeObject :
                writeObject.write(self.texFileHeader(fName(self.macLink)))
                writeObject.write('\\input ' + quotePath(mainMacroFile) + '\n')
                # If we are using marginal verses then we will need this
                if self.useMarginalVerses :
                    self.copyInMargVerse()
                    writeObject.write('\\input ' + quotePath(self.ptxMargVerseFile) + '\n')
                else :
                    self.removeMargVerse()

        return True


    def makeDepSetFile (self) :
        '''Create the main settings file that XeTeX will use in cNameTex to render 
        cNamePdf. This is a required file so it will run every time. However, it
        may not need to be remade. We will look for its exsistance and then compare 
        it to its primary dependents to see if we actually need to do anything.'''

        # Set vals
        dep = [self.layoutConfFile, self.fontConfFile, self.projConfFile]
        makeIt = False

        # Check for existance and age
#        import pdb; pdb.set_trace()
        if os.path.isfile(self.setFile) :
            for f in dep :
                if isOlder(self.setFile, f) :
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

            writeObject = codecs.open(self.setFile, "w", encoding='utf_8')
            writeObject.write(self.texFileHeader(fName(self.setFile)))

            # Bring in the settings from the layoutConfig
            for section in self.layoutConfig.keys() :
                writeObject.write('\n% ' + section + '\n')
                vals = {}
                # Be on the look out for an input ordering field. If there is one
                # it should have two or more items in the list this becomes the
                # base for our inputsOrder list used for output
                try :
                    inputsOrder = self.layoutConfig[section]['inputsOrder']
                except :
                    inputsOrder = []
                for k, v in self.layoutConfig[section].iteritems() :


# FIXME: Working here


                    # If there is an inputsOrder we should.......
                    if k == 'inputsOrder' :
                        # Need to be sure to check for a boolDepend and pick this up 
                        # if it is turned on
                        if testForSetting(macTexVals, k, 'boolDependTrue') and str2bool(self.rtnBoolDepend(macTexVals[k]['boolDependTrue'])) :
#                            inputsOrder = v
                            continue





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



                if section == 'Hyphenation' :
                    print inputsOrder





                # Write this line out to the TeX settings file
                for key in inputsOrder :
                    # Here we will write out the contents of the dict and becareful to
                    # put the inputsOrder keys at the end of the section in the order specified
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
            self.project.log.writeToLog('XTEX-040', [fName(self.setFile)])
            return True


    def makeDepSetExtFile (self) :
        '''Create/copy a TeX extentions file that has custom code for this project.'''

        rapumaExtFile = os.path.join(self.rapumaMacrosFolder, self.macroPackage, self.extFileName)
        userExtFile = os.path.join(self.project.userConfig['Resources']['macros'], self.extFileName)
        # First look for a user file, if not, then one 
        # from Rapuma, worse case, make a blank one
        if not os.path.isfile(self.extFile) :
            if os.path.isfile(userExtFile) :
                shutil.copy(userExtFile, self.extFile)
            elif os.path.isfile(rapumaExtFile) :
                shutil.copy(rapumaExtFile, self.extFile)
            else :
                # Create a blank file
                with codecs.open(self.extFile, "w", encoding='utf_8') as writeObject :
                    writeObject.write(self.texFileHeader(self.extFileName))
                self.project.log.writeToLog('XTEX-040', [fName(self.extFile)])

        # Need to return true here even if nothing was done
        return True


    def makeCidTexFile (self, cid) :
        '''Create the TeX control file for a subcomponent. The component control
        file will call this to process the working text.'''

        # Build necessary file names
        cidCName    = self.project.components[self.cName].getRapumaCName(cid)
        cidFolder   = os.path.join(self.projComponentsFolder, cidCName)
        cidTex      = os.path.join(cidFolder, cid + '.tex')
        cidUsfm     = os.path.join(cidFolder, cid + '.usfm')
        cidTexExt   = os.path.join(cidFolder, cid + '-ext.tex')
        cidSty      = os.path.join(cidFolder, cid + '.sty')


        # Write out the cidTex file
        with codecs.open(cidTex, "w", encoding='utf_8') as cidTexObject :
            cidTexObject.write(self.texFileHeader(fName(cidTex)))
            # User sty and macro extentions are optional at the cid level
            if os.path.isfile(os.path.join(cidTexExt)) :
                cNameTexObject.write('\\input \"' + cidTexExt + '\"\n')
            if os.path.isfile(os.path.join(cidSty)) :
                cNameTexObject.write('\\stylesheet{' + cidSty + '}\n')
            # The cid is not optional!
            if self.checkDepCidUsfm(cidUsfm) :
                cidTexObject.write('\\ptxfile{' + cidUsfm + '}\n')
            else :
                self.project.log.writeToLog('XTEX-050', [fName(cidUsfm)])
                dieNow()

        return True


    def makeCNameTexFile (self, cNameTex) :
        '''Create the main cName TeX control file.'''

        # We don't need to write this out every time so a dependency will be made to test against
        # No changes, nothing gets written out
        dep = [self.layoutConfFile, self.fontConfFile, self.projConfFile, self.globSty, self.custSty, self.hyphenTex]
        for f in dep :
            # Weed out unused files
            if f == '' :
                continue

            if isOlder(cNameTex, f) or not os.path.isfile(cNameTex) :
                # Start writing out the cName.tex file. Check/make dependencies as we go.
                # If we fail to make a dependency it will die and report during that process.
                with codecs.open(cNameTex, "w", encoding='utf_8') as cNameTexObject :
                    cNameTexObject.write(self.texFileHeader(fName(cNameTex)))
                    if self.makeDepMacLink() :
                        cNameTexObject.write('\\input \"' + self.macLink + '\"\n')
                    if self.makeDepSetFile() :
                        cNameTexObject.write('\\input \"' + self.setFile + '\"\n')
                    if self.makeDepSetExtFile() :
                        cNameTexObject.write('\\input \"' + self.extFile + '\"\n')
                    if self.checkDepGlobStyFile() :
                        cNameTexObject.write('\\stylesheet{' + self.globSty + '}\n')
                    # Custom sty file at the global level is optional as is hyphenation
                    if self.custSty :
                        cNameTexObject.write('\\stylesheet{' + self.custSty + '}\n')
                    for cid in self.projConfig['Components'][self.cName]['cidList'] :
                        cidCName = self.project.components[self.cName].getRapumaCName(cid)
                        cidTex = os.path.join(self.projComponentsFolder, cidCName, cid + '.tex')
                        if self.checkDepCidTex(cid) :
                            cNameTexObject.write('\\input \"' + cidTex + '\"\n')
                    # This can only hapen once in the whole process, this marks the end
                    cNameTexObject.write('\\bye\n')

                    # In case more than one dependency has changed,
                    # we only need to do this once
                    break

        return True


    def checkDepGlobStyFile (self) :
        '''Check for the exsistance of the Global Sty file. We need to die if 
        it is not found. This should have been installed when the components
        were brought in. To late to recover now if it is not there.'''

# FIXME: This needs to link to exsisting functions to install/create a
# global style file.
        if not os.path.isfile(self.globSty) :
            self.project.log.writeToLog('XTEX-120', [fName(self.globSty)])
            dieNow()
        else :
            return True







    def checkDepHyphenFile (self) :
        '''If hyphenation is used, check for the exsistance of the TeX Hyphenation 
        files. If one of them is not found, kindly ask the appropreate function to
        make it.'''

        if self.useHyphenation :
            if not os.path.isfile(self.hyphenTex) or isOlder(self.hyphenTex, self.compHyphen):
                if self.makeHyphenExceptionFile() :
                    self.project.log.writeToLog('XTEX-130', [fName(self.hyphenTex)])
                else :
                    # If we can't make it, we return False
                    self.project.log.writeToLog('XTEX-170', [fName(self.hyphenTex)])
                    return False
# FIXME: Need a dependency filter here
            if not os.path.isfile(self.lccodeTex) :
                if self.makeLccodeFile() :
                    self.project.log.writeToLog('XTEX-130', [fName(self.lccodeTex)])
                else :
                    # If we can't make it, we return False
                    self.project.log.writeToLog('XTEX-170', [fName(self.lccodeTex)])
                    return False
            return True
        else :
            # If Hyphenation is turned off, we return True and don't need to worry about it.
            return True









    def checkDepCidTex (self, cid) :
        '''Check for the exsistance of the cidTex dependent file. Request one to
        be made if it is not there and Return True.'''

        # Build necessary file names
        cidCName    = self.project.components[self.cName].getRapumaCName(cid)
        cidFolder   = os.path.join(self.projComponentsFolder, cidCName)
        cidTex      = os.path.join(cidFolder, cid + '.tex')
        cidUsfm     = os.path.join(cidFolder, cid + '.usfm')
        cidTexExt   = os.path.join(cidFolder, cid + '-ext.tex')
        cidSty      = os.path.join(cidFolder, cid + '.sty')

        # Must be a cidUsfm file to continue
        if not os.path.isfile(cidUsfm) :
            self.project.log.writeToLog('XTEX-050', [fName(cidUsfm)])
            dieNow()

        # Just make it if it is not there
        if not os.path.isfile(cidTex) :
            if self.makeCidTexFile(cid) :
                self.project.log.writeToLog('XTEX-065', [fName(cidTex)])
                return True
        else :
            # Do not (re)make it unless a dependent has changed
            dep = [cidTexExt, cidSty, cidUsfm]
            for f in dep :
                # Weed out unused files
                if not os.path.isfile(f) :
                    continue

                if isOlder(cidTex, f) :
                    if self.makeCidTexFile(cid) :
                        self.project.log.writeToLog('XTEX-065', [fName(cidTex)])
            # Not sure if returning True here is good or not
            return True


    def checkDepCidUsfm (self, cidUsfm) :
        '''Check for the exsistance of the cidUsfm dependent file. Return

        True if it is there or report and die if it is not.'''

        if not os.path.isfile(cidUsfm) :
            self.project.log.writeToLog('XTEX-050', [fName(cidUsfm)])
            dieNow()
        else :
            return True


###############################################################################
################################# Main Function ###############################
###############################################################################

    def run (self, force) :
        '''This will check all the dependencies for a component and then
        use XeTeX to render it.'''

        # This is the file we will make. If force is set, delete the old one.
        cNamePdf = os.path.join(self.cNameFolder, self.cName + '.pdf')
        if force :
            if os.path.isfile(cNamePdf) :
                os.remove(cNamePdf)

        # Create, if necessary, the cName.tex file
        cNameTex = os.path.join(self.cNameFolder, self.cName + '.tex')
        # First, go through and make/update any dependency files
        self.makeDepMacLink()
        self.makeDepSetFile()
        self.makeDepSetExtFile()
        self.checkDepHyphenFile()
        # Now make the cName main setting file
        self.makeCNameTexFile(cNameTex)

        # Dynamically create a dependency list for the render process
        dep = [cNameTex, self.extFile]
        for cid in self.projConfig['Components'][self.cName]['cidList'] :
            cidCName = self.project.components[self.cName].getRapumaCName(cid)
            cType = self.projConfig['Components'][self.cName]['type']
#            cidUsfm = self.managers[cType + '_Text'].getCompWorkingTextPath(cid)
            cidUsfm = self.project.components[self.cName].getCidPath(cid)
            cidAdj = self.project.components[self.cName].getCidAdjPath(cid)
            cidIlls = self.project.components[self.cName].getCidPiclistPath(cid)
            dep.append(cidUsfm)
            if os.path.isfile(cidAdj) :
                dep.append(cidAdj)
            if os.path.isfile(cidIlls) :
                dep.append(cidIlls)

        # Render if cNamePdf is older or is missing
        for d in dep :
            if isOlder(cNamePdf, d) or not os.path.isfile(cNamePdf) :
                # Create the environment that XeTeX will use. This will be temporarily set
                # by subprocess.call() just before XeTeX is run.
                texInputsLine = self.project.local.projHome + ':' \
                                + self.projMacPackFolder + ':' \
                                + self.projMacrosFolder + ':' \
                                + os.path.join(self.projComponentsFolder, self.cName) + ':.'

                # Create the environment dictionary that will be fed into subprocess.call()
                envDict = dict(os.environ)
                envDict['TEXINPUTS'] = texInputsLine

                # Create the XeTeX command argument list that subprocess.call()
                # will run with
                cmds = ['xetex', '-output-directory=' + self.cNameFolder, cNameTex]

                # Run the XeTeX and collect the return code for analysis
#                dieNow()
                rCode = subprocess.call(cmds, env = envDict)

                # Analyse the return code
                if rCode == int(0) :
                    self.project.log.writeToLog('XTEX-025', [fName(cNameTex)])
                elif rCode in self.xetexErrorCodes :
                    self.project.log.writeToLog('XTEX-030', [fName(cNameTex), self.xetexErrorCodes[rCode], str(rCode)])
                else :
                    self.project.log.writeToLog('XTEX-035', [str(rCode)])
                    dieNow()

        # Add lines background for composition work
        if str2bool(self.layoutConfig['PageLayout']['useLines']) :
            linesFileName       = self.layoutConfig['PageLayout']['linesFile']
            linesFile           = os.path.join(self.local.projIllustrationsFolder, linesFileName)
            cmd = [self.pdfUtilityCommand, cNamePdf, 'background', linesFile, 'output', tempName(cNamePdf)]
            try :
                subprocess.call(cmd)
                shutil.copy(tempName(cNamePdf), cNamePdf)
                os.remove(tempName(cNamePdf))
                self.project.log.writeToLog('XTEX-165')
            except Exception as e :
                # If we don't succeed, we should probably quite here
                self.project.log.writeToLog('XTEX-160', [str(e)])
                dieNow()

        # Add a watermark if required
        if str2bool(self.layoutConfig['PageLayout']['useWatermark']) :
            watermarkFileName   = self.layoutConfig['PageLayout']['watermarkFile']
            watermarkFile       = os.path.join(self.local.projIllustrationsFolder, watermarkFileName)
            cmd = [self.pdfUtilityCommand, cNamePdf, 'background', watermarkFile, 'output', tempName(cNamePdf)]
            try :
                subprocess.call(cmd)
                shutil.copy(tempName(cNamePdf), cNamePdf)
                os.remove(tempName(cNamePdf))
                self.project.log.writeToLog('XTEX-145')
            except Exception as e :
                # If we don't succeed, we should probably quite here
                self.project.log.writeToLog('XTEX-140', [str(e)])
                dieNow()

        # Review the results if desired
        if os.path.isfile(cNamePdf) :
            if self.displayPdfOutput(cNamePdf) :
                self.project.log.writeToLog('XTEX-095', [fName(cNamePdf)])
            else :
                self.project.log.writeToLog('XTEX-100', [fName(cNamePdf)])




