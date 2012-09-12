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
import subprocess

# Load the local classes
from tools import *
from pt_tools import *
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
        self.Ctype                  = cType.capitalize()
        self.manager                = self.cType + '_Xetex'
        self.usePdfViewer           = self.project.projConfig['Managers'][self.manager]['usePdfViewer']
        self.pdfViewer              = self.project.projConfig['Managers'][self.manager]['pdfViewerCommand']
        self.macroPackage           = self.project.projConfig['Managers'][self.manager]['macroPackage']
        self.macLayoutValFile       = os.path.join(self.project.local.rpmConfigFolder, 'layout_' + self.macroPackage + '.xml')
        self.projMacPackFolder      = os.path.join(self.project.local.projMacrosFolder, self.macroPackage)
        self.macPackFile            = os.path.join(self.projMacPackFolder, self.macroPackage + '.tex')
        self.ptxMargVerseFile       = os.path.join(self.projMacPackFolder, 'ptxplus-marginalverses.tex')
        self.sourceEditor           = self.project.projConfig['CompTypes'][self.Ctype]['sourceEditor']
        self.layoutConfig           = {}
        self.ptSSFConf              = {}
        # Make a PT settings dictionary
        if self.sourceEditor.lower() == 'paratext' :
            self.ptSSFConf = getPTSettings(self.project.local.projHome)
            if not len(self.ptSSFConf) :
                self.project.log.writeToLog('XTEX-005')


        # This manager is dependent on usfm_Layout. Load it if needed.
        if 'usfm_Layout' not in self.project.managers :
            self.project.createManager(self.cType, 'layout')

        self.layoutConfig           = self.project.managers[self.cType + '_Layout'].layoutConfig

        # Get persistant values from the config if there are any
        # We assume at this point that if the merge has already taken place,
        # we do not need to do it again. We will check for a version number 
        # under the General Settings section to tell if it has been merged
        # already. FIXME: This may not be the best way to do this but we cannot
        # be writing this file out every time as it causes the PDF to get
        # rendered every time, which is not helpful.
        try :
            version = self.layoutConfig['GeneralSettings']['usfmTexVersion']
            self.project.log.writeToLog('XTEX-010', [version])
        except :
            # No version number means we need to merge the default and usfmTex layout settings
            newSectionSettings = getPersistantSettings(self.layoutConfig, self.macLayoutValFile)
            if newSectionSettings != self.layoutConfig :
                self.project.managers[self.cType + '_Layout'].layoutConfig = newSectionSettings

            macVals = ConfigObj(getXMLSettings(self.macLayoutValFile))
            layoutCopy = ConfigObj(self.project.local.layoutConfFile)
            layoutCopy.merge(macVals)
            self.project.managers[self.cType + '_Layout'].layoutConfig = layoutCopy
            self.layoutConfig = layoutCopy
            if writeConfFile(self.project.managers[self.cType + '_Layout'].layoutConfig) :
                self.project.log.writeToLog('XTEX-020')

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

    def makeCidPdf (self) :
        '''When this is called all the files necessary to render this component 
        should be in place. Here we do the rendering process. The result 
        should be a PDF file.'''

        # Be sure the file names for this component are good
        self.buildCidFileNames(self.cid)

        # Create the environment that XeTeX will use. This will be temporarily set
        # by subprocess.call() just before XeTeX is run.
        texInputsLine = self.project.local.projHome + ':' \
                        + self.projMacPackFolder + ':' \
                        + self.project.local.projProcessFolder + ':' \
                        + os.path.join(self.project.local.projProcessFolder, self.cid) + ':.'

        # Create the environment dictionary that will be fed into subprocess.call()
        envDict = dict(os.environ)
        envDict['TEXINPUTS'] = texInputsLine

        # Create the XeTeX command argument list that subprocess.call()
        # will run with
        cmds = ['xetex', '-output-directory=' + self.cidFolder, self.masterTex]

        # Run the XeTeX and collect the return code for analysis
        rCode = subprocess.call(cmds, env = envDict)

        # Analyse the return code
        if rCode == int(0) :
            self.project.log.writeToLog('XTEX-025', [fName(self.cidTex)])
        elif rCode in self.xetexErrorCodes :
            self.project.log.writeToLog('XTEX-030', [fName(self.cidTex), self.xetexErrorCodes[rCode], str(rCode)])
        else :
            self.project.log.writeToLog('XTEX-035', [str(rCode)])

        # Change the masterPDF file name to the cidPdf file name to make it easier to track
        if os.path.isfile(self.masterPdf) :
            os.rename(self.masterPdf, self.cidPdf)


    def texFileHeader (self, fName) :
        '''Create a generic file header for a non-editable .tex file.'''

        return '% ' + fName + ' created: ' + tStamp() + '\n' \
            + '% This file is auto-generated, do not bother editing it\n\n'

    def makeExtFile (self) :
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
                writeObject.write(self.texFileHeader(self.extFileName))
                writeObject.close()
                self.project.log.writeToLog('XTEX-040', [fName(self.extFile)])


    def makeUsfmMacLinkFile (self) :
        '''Create the main macro link file for the USFM macro package 
        and install the package we need to render this component. This
        function is hard coded for this macro package. A more generalized
        way may be needed.'''

        # Copy in the standard package
        self.copyInMacros(self.cType)

        mainMacroFile = os.path.join(self.projMacPackFolder, 'paratext2.tex')

        # Make the macLinkFile file that will link the project with
        # the macro package. Customize it as needed.

        macLinkFile = getattr(self, self.cType + 'MacLinkFile')
        writeObject = codecs.open(macLinkFile, "w", encoding='utf_8')
        writeObject.write(self.texFileHeader(fName(macLinkFile)))
        writeObject.write('\\input ' + escapePath(mainMacroFile) + '\n')

        # If we are using marginal verses then we will need this
        if str2bool(self.layoutConfig['ChapterVerse']['useMarginalVerses']) :
            self.copyInMargVerse()
            writeObject.write('\\input ' + escapePath(self.ptxMargVerseFile) + '\n')
        else :
            self.removeMargVerse()

        writeObject.close()
        self.project.log.writeToLog('XTEX-040', [fName(macLinkFile)])

        return True


    def makeGlobSty (self) :
        '''This actually doesn't make anything.  The Global style file is
        required for rendering but is dependent on the USFM working file.  This
        will check to see if it is there, and try to quite gracefully if it is
        not.  The exception to this would be if this is a meta component, then
        it doesn't worry about it.'''

        if not self.cidMeta :
            if os.path.isfile(self.cidUsfm) :
                return True
            else :
                self.project.log.writeToLog('XTEX-045', [fName(self.cidUsfm)])


    def makeCidUsfm (self) :
        '''The USFM source text needs to be handled by the text manager and component type.
        This file is required so if it has not been created and the system got this far
        this function will report the missing file and try to quite gracefully.'''

        if os.path.isfile(self.cidUsfm) :
            return True
        else :
            self.project.log.writeToLog('XTEX-050', [fName(self.cidUsfm)])


    def makeControlTex (self, typeID) :
        '''Create a TeX control file (global or component) that will be used for 
        rendering a component or meta component. This is run every time rendering
        is called on.'''

        if typeID == 'masterTex' :
            ctrlFile = self.masterTex
        else :
            ctrlFile = getattr(self, typeID)

        def setLine (fileID) :
            '''Internal function to return the file name in a formated 
            line according to the type it is.'''

            output = ''
            if not fileID == 'cidTex' :
                if self.files[fileID][0] == 'input' :
                    if os.path.isfile(getattr(self, fileID)) :
                        output = '\\input ' + escapePath(getattr(self, fileID)) + '\n'

                elif self.files[fileID][0] in ['stylesheet', 'ptxfile'] :
                    if os.path.isfile(getattr(self, fileID)) :
                        output = '\\' + self.files[fileID][0] + '{' + getattr(self, fileID) + '}\n'
            else :
                output = '\\input ' + escapePath(getattr(self, 'cidTex')) + '\n'

            return output


        # Create or refresh any required files
        for f in self.primOut[typeID] :
            # This is for required files, if something fails here we should die
            if str2bool(self.files[f][1]) :
                try :
                    getattr(self, 'make' + f[0].upper() + f[1:])()
                except :
                    self.project.log.writeToLog('XTEX-055', [f[0].upper() + f[1:], fName(getattr(self, f))])

            # Non required files are handled different we will look for
            # each one and try to make it if it is not there but will 
            # not complain if we cannot do it
            else :
                if not os.path.isfile(getattr(self, f)) :
                    try :
                        getattr(self, 'make' + f[0].upper() + f[1:])()
                    except :
                        pass

        # Create the control file 
        writeObject = codecs.open(ctrlFile, "w", encoding='utf_8')
        writeObject.write(self.texFileHeader(fName(ctrlFile)))
        # We allow for a number of different types of lines
        for f in self.primOut[typeID] :
            if setLine(f) :
                writeObject.write(setLine(f))
        # If this is a global file, then put in the links to the component(s) to render
        if typeID == 'masterTex' :
            if self.cidMeta :
                for c in self.project.projConfig['Components'][self.cid]['list'] :
                    # Make sure we are working with the right cid file names
                    # This needs to be done for meta components
                    self.buildCidFileNames(c)
                    writeObject.write(setLine('cidTex'))
            else :
                    writeObject.write(setLine('cidTex'))
            writeObject.write('\\bye\n')

        # Finish the process
        writeObject.close()
        return True


    def makeSetFile (self) :
        '''Create the main settings file that XeTeX will use in cidTex to render 
        cidPdf. This is a required file so it will run every time. However, it
        may not need to be remade. We will look for its exsistance and then compare 
        it to its primary dependents to see if we actually need to do anything.'''

        def makeIt () :
            '''Internal function to build the setFile.'''

            # Get the default and TeX macro values and merge them into one dictionary
            x = self.makeTexSettingsDict(self.project.local.rpmLayoutDefaultFile)
            y = self.makeTexSettingsDict(self.macLayoutValFile)
            macTexVals = dict(y.items() + x.items())

            writeObject = codecs.open(self.setFile, "w", encoding='utf_8')
            writeObject.write(self.texFileHeader(fName(self.setFile)))

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


# FIXME: Working here - problem with fpath, it is not the actual font folder name



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
            self.project.log.writeToLog('XTEX-040', [fName(self.setFile)])

        # Start the main part of the function here

        # Check for existance and age
        if os.path.isfile(self.setFile) :
            if isOlder(self.setFile, self.layoutConfFile) :
                # Something changed in the layout conf file
                makeIt()
                self.project.log.writeToLog('XTEX-060', [fName(self.setFile)])
            elif isOlder(self.setFile, self.fontConfFile) :
                # Something changed in the font conf file
                makeIt()
                self.project.log.writeToLog('XTEX-060', [fName(self.setFile)])
        else :
            makeIt()
            self.project.log.writeToLog('XTEX-065', [fName(self.setFile)])

        return True


###############################################################################
############################ Local Support Functions ##########################
###############################################################################

    def displayPdfOutput (self, pdfFile) :
        '''Display a PDF XeTeX output file if that is turned on.'''

        if str2bool(self.usePdfViewer) :

            # Build the viewer command
            self.pdfViewer.append(pdfFile)
            # Run the XeTeX and collect the return code for analysis
            rCode = subprocess.call(self.pdfViewer)

            # Analyse the return code
            if not rCode == int(0) :
                self.project.log.writeToLog('XTEX-105', [rCode])
            else :
                return True


    def copyInMargVerse (self) :
        '''Copy in the marginalverse macro package.'''

        macrosTarget    = os.path.join(self.project.local.projMacrosFolder, self.macroPackage)
        macrosSource    = os.path.join(self.project.local.rpmMacrosFolder, self.macroPackage)

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


    def copyInMacros (self, cType) :
        '''Copy in the right macro set for this component and renderer combination.'''

        if cType.lower() == 'usfm' :
            macrosTarget    = os.path.join(self.project.local.projMacrosFolder, self.macroPackage)
            macrosSource    = os.path.join(self.project.local.rpmMacrosFolder, self.macroPackage)
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


    def buildCidFileNames (self, thisCid) :
        '''Because it might be necessary to build cid file names multiple times
        during a session, this function will do that.  I don't know if this is
        really clever or stupid, but it works. (Maybe there is a better way to
        do this?)'''

        self.cidFolder          = os.path.join(self.project.local.projProcessFolder, thisCid)
        self.cidUsfm            = os.path.join(self.cidFolder, thisCid + '.usfm')
        self.cidTex             = os.path.join(self.cidFolder, thisCid + '.tex')
        self.masterTex          = os.path.join(self.cidFolder, 'master.tex')
        self.cidExt             = os.path.join(self.cidFolder, thisCid + '-ext.tex')
        self.cidSty             = os.path.join(self.cidFolder, thisCid + '.sty')
        self.cidAdj             = os.path.join(self.cidFolder, thisCid + '.adj')
        self.cidPics            = os.path.join(self.cidFolder, thisCid + '.piclist')
        self.cidPdf             = os.path.join(self.cidFolder, self.cid + '.pdf')
        self.masterPdf          = os.path.join(self.cidFolder, 'master.pdf')


###############################################################################
################################# Main Function ###############################
###############################################################################

    def run (self, cid, force) :
        '''This will check all the dependencies for a component and then
        use XeTeX to render it.'''

        # Now that we know the cid, set the rest of the file/path values we need
        self.files                  = {}
        self.primOut                = {}
        self.cid                    = cid
        self.cidMeta                = False
        self.custSty                = os.path.join(self.project.local.projProcessFolder, 'custom.sty')
        self.globSty                = os.path.join(self.project.local.projProcessFolder, 'usfm.sty')
        self.hyphenTexFile          = os.path.join(self.project.local.projHyphenationFolder, 'hyphenation.tex')
        self.layoutConfFile         = self.project.local.layoutConfFile
        self.fontConfFile           = self.project.local.fontConfFile
        self.setFileName            = 'xetex_settings_' + self.cType + '.tex'
        self.extFileName            = 'xetex_settings_' + self.cType + '-ext.tex'
        self.setFile                = os.path.join(self.project.local.projProcessFolder, self.setFileName)
        self.extFile                = os.path.join(self.project.local.projProcessFolder, self.extFileName)
        if self.sourceEditor.lower() == 'paratext' :
            self.mainStyleFile      = self.ptSSFConf['ScriptureText']['StyleSheet']
            self.globSty            = os.path.join(self.project.local.projProcessFolder, self.mainStyleFile)

        # Set this flag to True if it is a meta component
        self.cidMeta                = isMetaComponent(self.project.projConfig, self.cid)

        # Build the initial cid names/paths
        self.buildCidFileNames(self.cid)

        # Make sure we have a component folder in place before we do anything
        if not os.path.isdir(self.cidFolder) :
            os.makedirs(self.cidFolder)

        # The macro link file is named according to the type of component
        setattr(self, self.cType + 'MacLinkFile', os.path.join(self.project.local.projProcessFolder, self.cType + 'MacLinkFile.tex'))
        macLinkFile = self.cType + 'MacLinkFile'

        # Process file information
        #   ID                      tType           Required    Description
        self.files      =   {
            'cidPdf'            : ['None',          False,      'Final PDF output file'],
            'masterPdf'         : ['None',          False,      'Initial PDF output file to be renamed to cidPdf'],
            'masterTex'         : ['None',          True,       'Main TeX control file for a component or meta-component'],
            'cidTex'            : ['None',          True,       'TeX control file for an individual component'],
            'cidUsfm'           : ['ptxfile',       True,       'USFM text working file'],
            'cidPics'           : ['None',          False,      'Scripture illustrations placement file'],
            'cidAdj'            : ['None',          False,      'Scripture text adjustments file'],
            'cidExt'            : ['input',         False,      'Component macro/extention and override file'],
            'cidSty'            : ['stylesheet',    False,      'Component style override file'],
            'custSty'           : ['stylesheet',    False,      'Custom project styles (from ParaTExt)'],
            'globSty'           : ['stylesheet',    True,       'Primary global component type styles'],
            'extFile'           : ['input',         False,      'XeTeX extention settings file'],
            'setFile'           : ['input',         True,       'XeTeX main settings file'],
             macLinkFile        : ['input',         True,       'Macro package link file'],
            'macPackFile'       : ['input',         True,       'Macro package link file'],
            'hyphenTexFile'     : ['input',         False,      'XeTeX hyphenation data file'],
            'fontConfFile'      : ['None',          True,       'Project fonts configuration file'],
            'layoutConfFile'    : ['None',          True,       'Project layout configuration file'],
            'ptxMargVerseFile'  : ['None',          False,      'Marginal verses extention macro']
                            }

        # Primary output files and their Dependencies (in necessary order)
        # FIXME: for meta comps and the cidPdf we may need to embed a list that
        # represents each of the subcomponents for a cid, that would be processed
        # to see if any changes were made causing a rerendering of the PDF comp.
        # For now we just need to get it working.
        self.primOut    =   {
            'masterTex'     : [macLinkFile, 'setFile', 'extFile', 'globSty', 'custSty', 'hyphenTexFile'],
            'cidTex'        : ['cidExt', 'cidSty', 'cidUsfm'],
            'cidPdf'        : ['cidAdj', 'cidPics', 'cidSty', 'custSty', 'globSty', 'cidExt', 'extFile', 'setFile', 'hyphenTexFile']
                            }

        # With all the new values defined start running here

        # Check if this is a meta component, preprocess all subcomponents
        if self.cidMeta :
            for c in self.project.projConfig['Components'][self.cid]['list'] :
                # Adjust the file names for this cid
                self.buildCidFileNames(c)
                self.makeControlTex('cidTex')
        else :
            self.makeControlTex('cidTex')

        # Create the global TeX file that will link to the cidTex file(s) we just made
        self.buildCidFileNames(self.cid)
        self.makeControlTex('masterTex')

        # If the user gave the render (-r) command we will force the rendering
        # of this component here by deleting any previously rendered PDF. However,
        # if the view (-v) command was given, we will pass and just view, or, if
        # needed, render the PDF.
        # Adjust the cidPdf path if this is a meta component because it got
        # messed with by the makeControlTex() processes. FIXME: This could
        # probably be better.
        self.buildCidFileNames(self.cid)
        if force :
            if os.path.isfile(self.cidPdf) :
                os.remove(self.cidPdf)
                self.project.log.writeToLog('XTEX-110', [fName(self.cidPdf)])

        # Create the PDF (if needed)
        render = False
        if os.path.isfile(self.cidPdf) :
            fList = self.primOut['cidPdf']
            # Add the cidUsfm into the list here so 
            # that file is covered as a dependent
            fList.append('cidUsfm')
            for k in fList :
                thisFile = getattr(self, k)
                if os.path.isfile(thisFile) :
                    if isOlder(self.cidPdf, thisFile) :
                        self.project.log.writeToLog('XTEX-080', [fName(thisFile), fName(self.cidPdf)])
                        render = True
        else :
            self.project.log.writeToLog('XTEX-085', [fName(self.cidPdf)])
            render = True

        if render :
            self.makeCidPdf()
        else :
            self.project.log.writeToLog('XTEX-090', [fName(self.cidPdf)])

        # Review the results if desired
        if os.path.isfile(self.cidPdf) :
            if self.displayPdfOutput(self.cidPdf) :
                self.project.log.writeToLog('XTEX-095', [fName(self.cidPdf)])
            else :
                self.project.log.writeToLog('XTEX-100', [fName(self.cidPdf)])




