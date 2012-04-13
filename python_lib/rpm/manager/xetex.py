#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This manager class will handle component rendering with XeTeX.

# History:
# 20120113 - djd - Started with intial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil


# Load the local classes
from tools import *
from manager import Manager


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
        self.cfg                    = cfg
        self.cType                  = cType
        self.tcfDependents          = {}
        self.tcfDependOrder         = {}
        self.manager                = self.cType + '_Xetex'
        self.usePdfViewer           = self.project.projConfig['Managers'][self.manager]['usePdfViewer']
        self.pdfViewer              = self.project.projConfig['Managers'][self.manager]['viewerCommand']
        self.macroPackage           = self.project.projConfig['Managers'][self.manager]['macroPackage']
        self.macLayoutValFile       = os.path.join(self.project.local.rpmConfigFolder, 'layout_' + self.macroPackage + '.xml')
        self.projMacPackFolder      = os.path.join(self.project.local.projMacrosFolder, self.macroPackage)
        self.macPackFile            = os.path.join(self.projMacPackFolder, self.macroPackage + '.tex')
        self.ptxMargVerseFile       = os.path.join(self.projMacPackFolder, 'ptxplus-marginalverses.tex')
        self.xetexOutputFolder      = os.path.join(self.project.local.projProcessFolder, 'Output')

        # This manager is dependent on usfm_Layout. Load it if needed.
        if 'usfm_Layout' not in self.project.managers :
            self.project.createManager(self.cType, 'layout')

        # Get persistant values from the config if there are any
        # We assume at this point that if the merge has already taken place,
        # we do not need to do it again. We will check for a version number 
        # under the General Settings section to tell if it has been merged
        # already. FIXME: This may not be the best way to do this but we cannot
        # be writing this file out every time as it causes the PDF to get
        # rendered every time, which is not helpful.
        try :
            version = self.project.managers[self.cType + '_Layout'].layoutConfig['GeneralSettings']['usfmTexVersion']
            writeToLog(self.project.local, self.project.userConfig, 'LOG', 'Version number present, not running persistant values: layout.__init__()')
        except :
            # No version number means we need to merge the default and usfmTex layout settings
            newSectionSettings = getPersistantSettings(project.managers['usfm_Layout'].layoutConfig, self.macLayoutValFile)
            if newSectionSettings != self.project.managers['usfm_Layout'].layoutConfig :
                project.managers['usfm_Layout'].layoutConfig = newSectionSettings

            macVals = ConfigObj(getXMLSettings(self.macLayoutValFile))
            layoutCopy = ConfigObj(self.project.local.layoutConfFile)
            layoutCopy.merge(macVals)
            self.project.managers[self.cType + '_Layout'].layoutConfig = layoutCopy
            writeConfFile(self.project.managers[self.cType + '_Layout'].layoutConfig)
            writeToLog(self.project.local, self.project.userConfig, 'LOG', 'Write out new layout config: layout.__init__()')

        # Get settings for this component
        self.managerSettings = self.project.projConfig['Managers'][self.manager]
        for k, v in self.managerSettings.iteritems() :
            if v == 'True' or v == 'False' :
                setattr(self, k, str2bool(v))
            else :
                setattr(self, k, v)

        self.xetexErrorCodes =  {
            0   : 'Rendering succeful.',
            256 : 'Something really awful happened.'
                                }

###############################################################################
############################ Project Level Functions ##########################
###############################################################################

    def setDependCheck (self) :
        # Dependency check for the main TeX settings file
        # The setFile is dependent on:
        # fontConfFile
        # layoutConfFile
        if os.path.isfile(self.setFile) :
            if isOlder(self.setFile, self.layoutConfFile) :
                # Something changed in the layout conf file
                self.makeSetTex()
                writeToLog(self.project.local, self.project.userConfig, 'LOG', 'Layout settings changed, ' + fName(self.setFile) + ' recreated.')
            elif isOlder(self.setFile, self.fontConfFile) :
                # Something changed in the font conf file
                self.makeSetTex()
                writeToLog(self.project.local, self.project.userConfig, 'LOG', 'Font settings changed, ' + fName(self.setFile) + ' recreated.')
        else :
            self.makeSetTex()
            writeToLog(self.project.local, self.project.userConfig, 'LOG', fName(self.setFile) + ' missing, created a new one.')


    def controlDependCheck (self) :
        '''Dependency check for the main TeX control file. The cidTex is dependent on 
        files that are listed in self.tcfDependOrder. If any have changed since the
        last time the cidTex was created, it will be recreated. If it is missing, it
        will be created.'''

        if os.path.isfile(self.cidTex) :
            for r in self.tcfDependOrder :
                if os.path.isfile(self.tcfDependOrder[r][2]) :
                    if isOlder(self.cidTex, self.tcfDependOrder[r][2]) :
                        # Something changed in this dependent file
                        self.makeTexControlFile()
                        writeToLog(self.project.local, self.project.userConfig, 'LOG', 'There has been a change in , ' + fName(self.tcfDependOrder[r][2]) + ' the ' + fName(self.cidTex) + ' has been recreated.')
        else :
            self.makeTexControlFile()
            writeToLog(self.project.local, self.project.userConfig, 'LOG', fName(self.cidTex) + ' was not found, created a new one.')


    def pdfDependCheck (self) :
        '''This will check to see if all the dependents of the cidPdf
        file are younger than itself. If not, the cidPdf will be rendered.'''

        # The cidPdf is the final product it is dependent on:
        # cidTex
        # FIXME: These need to be added yet
        # cidAdj
        # cidPics
        # cidUsfm
        
        # Create the PDF (if needed)
        if os.path.isfile(self.cidPdf) :
            if isOlder(self.cidTex, self.cidPdf) :
                self.renderCidPdf()
        else :
            self.renderCidPdf()


    def makeTexControlDependents (self) :
        # Using the information passed to this module created by other managers
        # it will create all the final forms of files needed to render the
        # current component with the XeTeX renderer. The final file made is
        # the cidTex file which is needed to control rendering of the source.

        # Create (if needed) the above files in the order they are listed.
        # These files are dependents of the cidTex file
        for r in self.tcfDependents :
            if not os.path.isfile(self.tcfDependents[r][2]) :
                if self.tcfDependents[r][0] == 'mac' :
                    self.copyInMacros()
                    continue

                elif self.tcfDependents[r][0] == 'mar' :
                    self.copyInMargVerse()
                    continue

                elif self.tcfDependents[r][0] == 'set' :
                    self.makeSetTex()
                    continue

                elif self.tcfDependents[r][0] == 'ext' :
                    self.makeTexExtentionsFile()
                    continue

                elif self.tcfDependents[r][0] == 'sty' :
                    self.project.managers[self.cType + '_Style'].createCompOverrideUsfmStyles(self.cid)
                    continue

                elif self.tcfDependents[r][0] == 'cus' :
                    self.project.managers[self.cType + '_Style'].installCompTypeOverrideStyles()
                    continue

                elif self.tcfDependents[r][0] == 'glo' :
                    self.project.managers[self.cType + '_Style'].installCompTypeGlobalStyles()
                    continue

                elif self.tcfDependents[r][0] == 'hyp' :
                    writeToLog(self.project.local, self.project.userConfig, 'ERR', 'Hyphenation file creation not supported yet.')
                    continue

                elif self.tcfDependents[r][0] == 'non' :
                    # This is being added in the Usfm compType too, do we want that?
                    # I think we probably should but the function will need to be reworked.
                    continue

                else :
                    writeToLog(self.project.local, self.project.userConfig, 'ERR', 'Type: [' + self.tcfDependents[r][0] + '] not supported')

#                writeToLog(self.project.local, self.project.userConfig, 'MSG', 'Created: ' + fName(self.tcfDependents[r][2]))


    def renderCidPdf (self) :
        # By this point all the files necessary to render this component should be in place
        # Here we do the rendering process. The result should be a PDF file.

        # Create the environment that XeTeX will use. This will be temporarily set
        # just before XeTeX is run.
        texInputsLine = 'TEXINPUTS=' + self.project.local.projHome + ':' + self.projMacPackFolder + ':.'

        # Create the command XeTeX will run with
        command = 'export ' + texInputsLine + ' && ' + 'xetex ' + '-output-directory=' + self.xetexOutputFolder + ' ' + self.cidTex

        # Create the output folder, XeTeX will fail without it
        if not os.path.isdir(self.xetexOutputFolder) :
            os.makedirs(self.xetexOutputFolder)

        # Run XeTeX and collect the return code for analysis
        rCode = -1
        rCode = os.system(command)

        # Analyse the return code
        if rCode == int(0) :
            writeToLog(self.project.local, self.project.userConfig, 'MSG', 'Rendering of [' + fName(self.cidTex) + '] successful.')
        elif rCode in self.xetexErrorCodes :
            writeToLog(self.project.local, self.project.userConfig, 'ERR', 'Rendering [' + fName(self.cidTex) + '] was unsuccessful. ' + self.xetexErrorCodes[rCode] + ' (' + str(rCode) + ')')
        else :
            writeToLog(self.project.local, self.project.userConfig, 'ERR', 'XeTeX error code [' + str(rCode) + '] not understood by RPM.')


    def displayPdfOutput (self, pdfFile) :
        '''Display a PDF XeTeX output file if that is turned on.'''

        if str2bool(self.usePdfViewer) :
            # Build the viewer command
            command = self.pdfViewer + ' ' + pdfFile + ' &'
            rCode = os.system(command)
            # FIXME: May want to analyse the return code from viewer
            return True


    def makeTexExtentionsFile (self) :
        '''Create/copy a TeX extentions file that has custom code for this project.'''

        rpmExtFile = os.path.join(self.project.local.rpmMacrosFolder, self.macroPackage, self.extFileName)
        userExtFile = os.path.join(self.project.userConfig['Resources']['macros'], self.extFileName)
        # First look for a user file, if not, then one 
        # from RPM, worse case, make a blank one
        if not os.path.isfile(self.extFile) :
            if os.path.isfile(userExtFile) :
                shutil.copy(userExtFile, self.extFile)
            elif os.path.isfile(rpmExtFile) :
                shutil.copy(rpmExtFile, self.extFile)
            else :
                # Create a blank file
                writeObject = codecs.open(extFile, "w", encoding='utf_8')
                writeObject.write('% ' + self.extFileName + ' created: ' + tStamp() + '\n')
                writeObject.close()
                writeToLog(self.project.local, self.project.userConfig, 'LOG', 'Created: ' + fName(self.extFile))


    def copyInMargVerse (self) :
        '''Copy in the marginalverse macro package.'''

        macrosTarget    = os.path.join(self.project.local.projMacrosFolder, self.macroPackage)
        macrosSource    = os.path.join(self.project.local.rpmMacrosFolder, self.macroPackage)

        # Copy in to the process folder the macro package for this component
        if not os.path.isdir(macrosTarget) :
            os.makedirs(macrosTarget)

        if not os.path.isfile(self.ptxMargVerseFile) :
            shutil.copy(os.path.join(macrosSource, fName(self.ptxMargVerseFile)), self.ptxMargVerseFile)
            return True
            writeToLog(self.project.local, self.project.userConfig, 'LOG', 'Copied macro: ' + fName(self.ptxMargVerseFile))


    def copyInMacros (self) :
        '''Copy in the right macro set for this component and renderer combination.'''

        macrosTarget    = os.path.join(self.project.local.projMacrosFolder, self.macroPackage)
        macrosSource    = os.path.join(self.project.local.rpmMacrosFolder, self.macroPackage)
        copyExempt      = [self.extFile]

        # Copy in to the process folder the macro package for this component
        if not os.path.isdir(macrosTarget) :
            os.makedirs(macrosTarget)

        mCopy = False
        for root, dirs, files in os.walk(macrosSource) :
            for f in files :
                fTarget = os.path.join(macrosTarget, f)
                if f not in copyExempt :
                    if not os.path.isfile(fTarget) :
                        shutil.copy(os.path.join(macrosSource, f), fTarget)
                        mCopy = True
                        writeToLog(self.project.local, self.project.userConfig, 'LOG', 'Copied macro: ' + fName(fTarget))

        return mCopy


    def makeTexControlFile (self) :
        '''Create the control file that will be used for rendering this
        component.'''

        # Create the control file 
        writeObject = codecs.open(self.cidTex, "w", encoding='utf_8')
        writeObject.write('% ' + fName(self.cidTex) + ' created: ' + tStamp() + '\n')
        # We allow for a number of different types of lines
        for r in self.tcfDependOrder :
            if self.tcfDependOrder[r][1] == 'input' :
                if os.path.isfile(self.tcfDependOrder[r][2]) :
                    writeObject.write('\\' + self.tcfDependOrder[r][1] + ' \"' + self.tcfDependOrder[r][2] + '\"\n')
            elif self.tcfDependOrder[r][1] in ['stylesheet', 'ptxfile'] :
                if os.path.isfile(self.tcfDependOrder[r][2]) :
                    writeObject.write('\\' + self.tcfDependOrder[r][1] + '{' + self.tcfDependOrder[r][2] + '}\n')
            elif self.tcfDependOrder[r][1] == 'command' :
                writeObject.write('\\' + self.tcfDependOrder[r][1] + '\n')
            else :
                writeToLog(self.project.local, self.project.userConfig, 'ERR', 'Type not supported: ' + self.tcfDependOrder[r][0])

        # Finish the process
        writeObject.write('\\bye\n')
        writeObject.close()
        writeToLog(self.project.local, self.project.userConfig, 'LOG', 'Created: ' + fName(self.cidTex))


    def makeSetTex (self) :
        '''Create the main settings file that XeTeX will use to render cidTex.'''

        # Get the default and TeX macro values and merge them into one dictionary
        x = self.makeTexSettingsDict(self.project.local.rpmLayoutDefaultFile)
        y = self.makeTexSettingsDict(self.macLayoutValFile)
        macTexVals = dict(y.items() + x.items())

        writeObject = codecs.open(self.setFile, "w", encoding='utf_8')
        writeObject.write('% ' + fName(self.setFile) + ' created: ' + tStamp() + '\n')

        # Bring in the settings from the layoutConfig
        cfg = self.project.managers[self.cType + '_Layout'].layoutConfig
        for section in cfg.keys() :
            writeObject.write('\n% ' + section + '\n')
            for k, v in cfg[section].iteritems() :
                if testForSetting(macTexVals, k, 'usfmTex') :
                    line = macTexVals[k]['usfmTex']
                    # If there is a boolDepend then we don't need to output
                    if testForSetting(macTexVals, k, 'boolDepend') and not str2bool(self.rtnBoolDepend(cfg, macTexVals[k]['boolDepend'])) :
                        continue
                    else :
                        if self.hasPlaceHolder(line) :
                            (ht, hk) = self.getPlaceHolder(line)
                            # Just a plan value
                            if ht == 'v' :
                                line = self.insertValue(line, v)
                            # A value that needs a measurement unit attached
                            elif ht == 'vm' :
                                line = self.insertValue(line, self.addMeasureUnit(v))
                            # A value that is a path
                            elif ht == 'path' :
                                pth = getattr(self.project.local, hk)
                                line = self.insertValue(line, pth)

                    writeObject.write(line + '\n')

        # Add all the font def commands
        writeObject.write('\n% Font Definitions\n')
        fpath = ''
        featureString = ''
        for f in self.project.projConfig['CompTypes'][self.cType.capitalize()]['installedFonts'] :
            fInfo = self.project.managers['usfm_Font'].fontConfig['Fonts'][f]
            features = fInfo['FontInformation']['features']
            # Create the primary fonts that will be used with TeX
            if self.project.projConfig['CompTypes'][self.cType.capitalize()]['primaryFont'] == f :
                writeObject.write('\n% These are normal use fonts for this type of component.\n')
                features = fInfo['FontInformation']['features']
                for tf in fInfo :
                    if tf[:8] == 'Typeface' :
                        tmc = 0
                        for tm in fInfo[tf]['texMapping'] :
                            startDef    = '\\def\\' + fInfo[tf]['texMapping'][tmc] + '{'
                            fpath       = "\"[" + os.path.join('..', self.project.local.projFontsFolder, fInfo[tf]['name'], fInfo[tf]['file']) + "]"
                            endDef      = "\"}\n"
                            featureString = ''
                            for i in features :
                                featureString += '/' + i

                            modsString = ''
                            for m in fInfo[tf]['modify'] :
                                modsString += ':' + m

                            tmc +=1
                            writeObject.write(startDef + fpath + featureString + modsString + endDef)

            else :
                writeObject.write('\n% These are normal use fonts for this type of component.\n')
                features = fInfo['FontInformation']['features']
                for tf in fInfo :
                    if tf[:8] == 'Typeface' :
                        tmc = 0
                        for tm in fInfo[tf]['texMapping'] :
                            name = fInfo[tf]['name'].lower().replace(' ', '')
                            startDef    = '\\def\\' + name + fInfo[tf]['texMapping'][tmc] + '{'
                            fpath       = "\"[" + os.path.join('..', self.project.local.projFontsFolder, fInfo[tf]['name'], fInfo[tf]['file']) + "]\""
                            endDef      = "}\n"
                            featureString = ''
                            for i in features :
                                featureString += ':' + i

                            modsString = ''
                            for m in fInfo[tf]['modify'] :
                                modsString += ':' + m

                            tmc +=1
                            writeObject.write(startDef + fpath + featureString + modsString + endDef)

        # Add special custom commands (may want to parameterize these at some point)
        writeObject.write('\n% Special commands\n')
        writeObject.write('\catcode`@=11\n')
        writeObject.write('\def\makedigitsother{\m@kedigitsother}\n')
        writeObject.write('\def\makedigitsletters{\m@kedigitsletters}\n')
        writeObject.write('\catcode `@=12\n')
        writeObject.write('\\vfuzz=2.3pt\n')

        # End here
        writeObject.close()
        writeToLog(self.project.local, self.project.userConfig, 'LOG', 'Created: ' + fName(self.setFile))


    def addMeasureUnit (self, val) :
        '''Return the value with the specified measurement unit attached.'''
        
        mu = self.project.managers[self.cType + '_Layout'].layoutConfig['GeneralSettings']['measurementUnit']
        return val + mu


    def rtnBoolDepend (self, cfg, bd) :
        '''Return the boolean value of a boolDepend target. This assumes that
        the format is section:key, if it ever becomes different, this breaks.'''

        bdl = bd.split(':')
        return cfg[bdl[0]][bdl[1]]


    def hasPlaceHolder (self, line) :
        '''Return True if this line has a data place holder in it.'''

        # If things get more complicated we may need to beef this up a bit
        if line.find('[') > -1 and line.find(']') > -1 :
            return True


    def getPlaceHolder (self, line) :
        '''Return place holder type and a key if one exists from a TeX setting line.'''

        begin = line.find('[')
        end = line.find(']') + 1
        cnts = line[begin + 1:end - 1]
        if cnts.find(':') > -1 :
            return cnts.split(':')
        else :
            return cnts, ''


    def insertValue (self, line, v) :
        '''Insert a value where a place holder is.'''

        begin = line.find('[')
        end = line.find(']') + 1
        ph = line[begin:end]
        return line.replace(ph, v)


    def makeTexSettingsDict (self, xmlFile) :
        '''Create a dictionary object from a layout xml file.'''

        if  os.path.exists(xmlFile) :
            # Read in our XML file
            doc = ElementTree.parse(xmlFile)
            # Create an empty dictionary
            data = {}
            # Extract the section/key/value data
            thisSection = None; thisTex = None; thisBoolDep = None
            for event, elem in ElementTree.iterparse(xmlFile):
                if elem.tag == 'setting' :
                    if thisTex or thisBoolDep :
                        data[thisSection] = {'usfmTex' : thisTex, 'boolDepend' : thisBoolDep}
                    thisSection = None
                    thisTex = None
                    thisBoolDep = None
                if elem.tag == 'key' :
                    thisSection = elem.text
                elif elem.tag == 'usfmTex' :
                    thisTex = elem.text
                elif elem.tag == 'boolDepend' :
                    thisBoolDep = elem.text

            return data
        else :
            raise IOError, "Can't open " + xmlFile


    def run (self, cid) :
        '''This will check all the dependencies for a component and then
        use XeTeX to render it.'''

        # Now that we know the cid, set the rest of the file/path values we need
        self.cid                    = cid
        self.cidUsfm                = os.path.join(self.project.local.projTextFolder, self.cid + '.usfm')
        self.cidPdf                 = os.path.join(self.xetexOutputFolder, self.cid + '.pdf')
        self.cidTex                 = os.path.join(self.project.local.projProcessFolder, self.cid + '.tex')
        self.cidSty                 = os.path.join(self.project.local.projProcessFolder, self.cid + '.sty')
        self.cidAdj                 = os.path.join(self.project.local.projTextFolder, self.cid + '.adj')
        self.cidPics                = os.path.join(self.project.local.projTextFolder, self.cid + '.piclist')
        self.custSty                = os.path.join(self.project.local.projProcessFolder, 'custom.sty')
        self.globSty                = os.path.join(self.project.local.projProcessFolder, 'usfm.sty')
        self.hyphenTexFile          = os.path.join(self.project.local.projHyphenationFolder, 'hyphenation.tex')
        self.layoutConfFile         = self.project.local.layoutConfFile
        self.fontConfFile           = self.project.local.fontConfFile
        self.setFileName            = 'xetex_settings_' + self.cType + '.tex'
        self.extFileName            = 'xetex_settings_' + self.cType + '-ext.tex'
        self.setFile                = os.path.join(self.project.local.projProcessFolder, self.setFileName)
        self.extFile                = os.path.join(self.project.local.projProcessFolder, self.extFileName)

        #   ID   pType  tType           Path & File Name            Description
        self.tcfDependents =    { 
            1 : ['mac', 'input',        self.macPackFile,           'Macro link file'], 
            2 : ['set', 'input',        self.setFile,               'XeTeX main settings file'], 
            3 : ['ext', 'input',        self.extFile,               'XeTeX extention settings file'], 
            4 : ['glo', 'stylesheet',   self.globSty,               'Primary component type styles'], 
            5 : ['cus', 'stylesheet',   self.custSty,               'Custom project styles (from ParaTExt)'], 
            6 : ['sty', 'stylesheet',   self.cidSty,                'Component style override'], 
            7 : ['hyp', 'input',        self.hyphenTexFile,         'XeTeX hyphenation data file'], 
            8 : ['mar', 'input',        self.ptxMargVerseFile,      'Marginal verses extention macro'], 
            9 : ['non', 'ptxfile',      self.cidUsfm,               'Component text file']
                                }

        # This is a list of files needed by the TeX control file in the order they need to be listed
        self.tcfDependOrder =   {
            1 : self.tcfDependents[1], 
            2 : self.tcfDependents[2], 
            3 : self.tcfDependents[3], 
            4 : self.tcfDependents[4], 
            5 : self.tcfDependents[5], 
            6 : self.tcfDependents[6], 
            7 : self.tcfDependents[7], 
            8 : self.tcfDependents[8], 
            9 : self.tcfDependents[9]
                                }

        # With all the new values defined start running here
        self.makeTexControlDependents()
        self.setDependCheck()
        self.controlDependCheck()
        self.pdfDependCheck()
        if os.path.isfile(self.cidPdf) :
            if self.displayPdfOutput(self.cidPdf) :
                writeToLog(self.project.local, self.project.userConfig, 'MSG', fName(self.cidPdf) + ' recreated, routing to PDF viewer.')
            else :
                writeToLog(self.project.local, self.project.userConfig, 'MSG', fName(self.cidPdf) + ' recreated, PDF viewer turned off.')




#    def makeFontInfoTexFile (self) :
#        '''Create a TeX info font file that TeX will use for rendering.'''

#        # We will not make this file if it is already there
#        fontInfoFileName = os.path.join(self.project.processFolder,'fonts.tex')
#        # The rule is that we only create this file if it is not there,
#        # otherwise it will silently fail.  If one already exists the file will
#        # need to be removed by some other process before it can be recreated.
#        sCType = self.cType.capitalize()
#        if not os.path.isfile(fontInfoFileName) :
#            writeObject = codecs.open(fontInfoFileName, "w", encoding='utf_8')
#            writeObject.write('% fonts.tex' + ' created: ' + tStamp() + '\n')
#            for f in self.project.projConfig['CompTypes'][sCType]['installedFonts'] :
#                fInfo = self.project.projConfig['Fonts'][f]
#                # Create the primary fonts that will be used with TeX
#                if self.project.projConfig['CompTypes'][sCType]['primaryFont'] == f :
#                    writeObject.write('\n% These are normal use fonts for this type of component.\n')
#                    features = fInfo['FontInformation']['features']
#                    for tf in fInfo :
#                        if tf[:8] == 'Typeface' :
#                            # Make all our line components (More will need to be added)
#                            startDef    = '\\def\\' + fInfo[tf]['texMapping'] + '{'
#                            fpath       = "\"[" + os.path.join('..', self.project.fontsFolder, fInfo[tf]['file']) + "]\""
#                            endDef      = "}\n"
#                            featureString = ''
#                            for i in features :
#                                featureString += ':' + i

#                            writeObject.write(startDef + fpath + featureString + endDef)

#                # Create defs with secondary fonts for special use with TeX in publication
#                else :
#                    writeObject.write('\n% These are special use fonts for this type of component.\n')
#                    features = fInfo['FontInformation']['features']
#                    for tf in fInfo :
#                        if tf[:8] == 'Typeface' :
#                            # Make all our line components (More will need to be added)
#                            startDef    = '\\def\\' + f.lower() + tf[8:].lower() + '{'
#                            fpath       = "\"[" + os.path.join('..', self.project.fontsFolder, fInfo[tf]['file']) + "]\""
#                            endDef      = "}\n"
#                            featureString = ''
#                            for i in features :
#                                featureString += ':' + i

#                            writeObject.write(startDef + fpath + featureString + endDef)

#            # Finish the process
#            writeObject.close()
#            return True



