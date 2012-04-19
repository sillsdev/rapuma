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
        self.manager                = self.cType + '_Xetex'
        self.usePdfViewer           = self.project.projConfig['Managers'][self.manager]['usePdfViewer']
        self.pdfViewer              = self.project.projConfig['Managers'][self.manager]['viewerCommand']
        self.xetexOutputFolder      = os.path.join(self.project.local.projProcessFolder, 'Output')
        self.layoutConfig           = {}

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
            writeToLog(self.project.local, self.project.userConfig, 'LOG', 'Version number present, not running persistant values: layout.__init__()')
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

    def makeCidPdf (self) :
        # When this is called all the files necessary to render this component 
        # should be in place. Here we do the rendering process. The result 
        # should be a PDF file.

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
                writeObject.write('% ' + self.extFileName + ' created: ' + tStamp() + '\n')
                writeObject.close()
                writeToLog(self.project.local, self.project.userConfig, 'LOG', 'Created: ' + fName(self.extFile))

#####################################################################################################

    def makeMacPackFile (self) :
        '''Install the macro package we need to render this component.'''

        # Copy in the standard package
        self.copyInMacros()

        # If we are using marginal verses then we will need this
        if str2bool(self.layoutConfig['ChapterVerse']['useMarginalVerses']) :
            self.copyInMargVerse()
        else :
            self.removeMargVerse()

        # Make the usfmTex.tex file that will link the project with
        # the macro package. Customize it as needed.
        
        # FIXME: We will need some way to know what the possible files are
        # then look for them and add them as we find them.

        return True

#######################################################################################################

    def makeGlobSty (self) :
        '''The Global style file is required for rendering but it is created/aquired
        by the component type manager. This will check to see if it is there, and
        try to quite gracefully if it is not.'''

        if os.path.isfile(self.cidUsfm) :
            return True
        else :
            writeToLog(self.project.local, self.project.userConfig, 'ERR', 'USFM working text not found: ' + fName(self.cidUsfm) + ' This is required, system should halt.')


    def makeCidUsfm (self) :
        '''The USFM source text needs to be handled by the text manager and component type.
        This file is required so if it has not been created and the system got this far
        this function will report the missing file and try to quite gracefully.'''

        if os.path.isfile(self.cidUsfm) :
            return True
        else :
            writeToLog(self.project.local, self.project.userConfig, 'ERR', 'USFM working text not found: ' + fName(self.cidUsfm) + ' This is required, system should halt.')


    def makeCidTex (self) :
        '''Create the control file that will be used for rendering this
        component. This is run every time rendering is called on.'''

        def setLine (fileName) :
            '''Internal function to return the file name in a formated 
            line according to the type it is.'''

            if self.files[fileName][0] == 'input' :
                if os.path.isfile(getattr(self, fileName)) :
                    return '\\input \"' + getattr(self, fileName) + '\"\n'

            elif self.files[fileName][0] in ['stylesheet', 'ptxfile'] :
                if os.path.isfile(getattr(self, fileName)) :
                    return '\\' + self.files[fileName][0] + '{' + getattr(self, fileName) + '}\n'

        # Create or refresh any required files
        for f in self.primOut['cidTex'] :
            # This is for required files, if something fails here we should die
            if str2bool(self.files[f][1]) :
                if not getattr(self, 'make' + f[0].upper() + f[1:])() :
                    writeToLog(self.project.local, self.project.userConfig, 'ERR', 'Failed to create: ' + fName(getattr(self, f)) + ' This file is required.')
                    return
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
        writeObject = codecs.open(self.cidTex, "w", encoding='utf_8')
        writeObject.write('% ' + fName(self.cidTex) + ' created: ' + tStamp() + '\n')
        writeObject.write('% This file is auto-generated. Do not bother editing it.\n')
        # We allow for a number of different types of lines
        for f in self.primOut['cidTex'] :
            if setLine(f) :
                writeObject.write(setLine(f))

        # Finish the process
        writeObject.write('\\bye\n')
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

        # Start the main part of the function here

        # Check for existance and age
        if os.path.isfile(self.setFile) :
            if isOlder(self.setFile, self.layoutConfFile) :
                # Something changed in the layout conf file
                makeIt()
                writeToLog(self.project.local, self.project.userConfig, 'LOG', 'Layout settings changed, ' + fName(self.setFile) + ' recreated.')
            elif isOlder(self.setFile, self.fontConfFile) :
                # Something changed in the font conf file
                makeIt()
                writeToLog(self.project.local, self.project.userConfig, 'LOG', 'Font settings changed, ' + fName(self.setFile) + ' recreated.')
        else :
            makeIt()
            writeToLog(self.project.local, self.project.userConfig, 'LOG', fName(self.setFile) + ' missing, created a new one.')

        return True


###############################################################################
############################ Local Support Functions ##########################
###############################################################################

    def displayPdfOutput (self, pdfFile) :
        '''Display a PDF XeTeX output file if that is turned on.'''

        if str2bool(self.usePdfViewer) :
            # Build the viewer command
            command = self.pdfViewer + ' ' + pdfFile + ' &'
            rCode = os.system(command)
            # FIXME: May want to analyse the return code from viewer
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
            return True
            writeToLog(self.project.local, self.project.userConfig, 'LOG', 'Copied macro: ' + fName(self.ptxMargVerseFile))


    def removeMargVerse (self) :
        '''Remove the marginal verse macro package from the project.'''

        if os.path.isfile(self.ptxMargVerseFile) :
            os.remove(self.ptxMargVerseFile)
            return True


    def copyInMacros (self) :
        '''Copy in the right macro set for this component and renderer combination.'''

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
                        writeToLog(self.project.local, self.project.userConfig, 'LOG', 'Copied macro: ' + fName(fTarget))

        return mCopy


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


###############################################################################
################################# Main Function ###############################
###############################################################################

    def run (self, cid) :
        '''This will check all the dependencies for a component and then
        use XeTeX to render it.'''

        # Now that we know the cid, set the rest of the file/path values we need
        self.files                  = {}
        self.primOut                = {}
        self.cid                    = cid
        self.cidUsfm                = os.path.join(self.project.local.projTextFolder, self.cid + '.usfm')
        self.cidPdf                 = os.path.join(self.xetexOutputFolder, self.cid + '.pdf')
        self.cidTex                 = os.path.join(self.project.local.projProcessFolder, self.cid + '.tex')
        self.cidExt                 = os.path.join(self.project.local.projProcessFolder, self.cid + '-ext.tex')
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
        self.macroPackage           = self.project.projConfig['Managers'][self.manager]['macroPackage']
        self.macLayoutValFile       = os.path.join(self.project.local.rpmConfigFolder, 'layout_' + self.macroPackage + '.xml')
        self.projMacPackFolder      = os.path.join(self.project.local.projMacrosFolder, self.macroPackage)
        self.macPackFile            = os.path.join(self.projMacPackFolder, self.macroPackage + '.tex')
        self.ptxMargVerseFile       = os.path.join(self.projMacPackFolder, 'ptxplus-marginalverses.tex')

        # Process file information
        #   ID                      tType           Required    Description
        self.files      =   {
            'cidPdf'            : ['None',          False,       'PDF output file'],
            'cidTex'            : ['None',          True,       'Main TeX control file'],
            'cidUsfm'           : ['input',         True,       'USFM text working file'],
            'cidPics'           : ['None',          False,      'Scripture illustrations placement file'],
            'cidAdj'            : ['None',          False,      'Scripture text adjustments file'],
            'cidExt'            : ['input',         False,      'Component macro/extention and override file'],
            'cidSty'            : ['stylesheet',    False,      'Component style override file'],
            'custSty'           : ['stylesheet',    False,      'Custom project styles (from ParaTExt)'],
            'globSty'           : ['stylesheet',    True,       'Primary global component type styles'],
            'extFile'           : ['input',         False,      'XeTeX extention settings file'],
            'setFile'           : ['input',         True,       'XeTeX main settings file'],
            'macPackFile'       : ['input',         True,       'Macro package link file'],
            'hyphenTexFile'     : ['input',         False,      'XeTeX hyphenation data file'],
            'fontConfFile'      : ['None',          True,       'Project fonts configuration file'],
            'layoutConfFile'    : ['None',          True,       'Project layout configuration file'],
            'ptxMargVerseFile'  : ['None',          False,      'Marginal verses extention macro']
                            }

        # Primary output files and their Dependencies (in necessary order)
            # OrderID      FileID     Dependencies List
        self.primOut    =   {
            'cidTex' : ['macPackFile', 'setFile', 'extFile', 'cidExt', 'globSty', 'custSty', 'cidSty', 'hyphenTexFile', 'cidUsfm'],
            'cidPdf' : ['cidAdj', 'cidPics', 'cidSty', 'custSty', 'globSty', 'cidExt', 'extFile', 'setFile', 'macPackFile', 'hyphenTexFile']
                            }

        # With all the new values defined start running here
        self.makeCidTex()


# FIXME: This is where we need to do the dependency checking on all the possible
# files that could effect the rendering of the PDF file

        self.makeCidPdf()
        
        # Review the results if desired
        if os.path.isfile(self.cidPdf) :
            if self.displayPdfOutput(self.cidPdf) :
                writeToLog(self.project.local, self.project.userConfig, 'MSG', 'Routing ' + fName(self.cidPdf) + ' to PDF viewer.')
            else :
                writeToLog(self.project.local, self.project.userConfig, 'MSG', fName(self.cidPdf) + ' cannot be viewed, PDF viewer turned off.')




#    def controlDependCheck (self) :
#        '''Dependency check for the main TeX control file. The cidTex is dependent on 
#        files that are listed in self.tcfDependOrder. If any have changed since the
#        last time the cidTex was created, it will be recreated. If it is missing, it
#        will be created.'''

#        if os.path.isfile(self.cidTex) :
#            for r in self.tcfDependOrder :
#                if os.path.isfile(self.tcfDependOrder[r][2]) :
#                    if isOlder(self.cidTex, self.tcfDependOrder[r][2]) :
#                        # Something changed in this dependent file
#                        self.makeTexControlFile()
#                        writeToLog(self.project.local, self.project.userConfig, 'LOG', 'There has been a change in , ' + fName(self.tcfDependOrder[r][2]) + ' the ' + fName(self.cidTex) + ' has been recreated.')
#        else :
#            self.makeTexControlFile()
#            writeToLog(self.project.local, self.project.userConfig, 'LOG', fName(self.cidTex) + ' was not found, created a new one.')


#    def pdfDependCheck (self) :
#        '''This will check to see if all the dependents of the cidPdf
#        file are younger than itself. If not, the cidPdf will be rendered.'''

#        # Create the PDF (if needed)
#        if os.path.isfile(self.cidPdf) :
#            for r in self.pdfDependents :
#                if os.path.isfile(self.pdfDependents[r][1]) :
#                    if isOlder(self.cidPdf, self.pdfDependents[r][1]) :
#                        writeToLog(self.project.local, self.project.userConfig, 'LOG', 'There has been a change in ' + fName(self.pdfDependents[r][1]) + ' the ' + fName(self.cidPdf) + ' has been rerendered.')
#                        self.renderCidPdf()
#        else :
#            writeToLog(self.project.local, self.project.userConfig, 'LOG', fName(self.cidPdf) + ' not found, a new one has been rendered.')
#            self.renderCidPdf()


#    def makeTexControlDependents (self) :
#        '''Using the information passed to this module created by other managers
#        it will create all the final forms of files needed to render the
#        current component with the XeTeX renderer. The final file made is

#        the cidTex file which is needed to control rendering of the source.'''

#        # Create (if needed) the above files in the order they are listed.
#        # These files are dependents of the cidTex file
#        for r in self.tcfDependents :
#            if not os.path.isfile(self.tcfDependents[r][2]) :
#                if self.tcfDependents[r][0] == 'mac' :
#                    self.copyInMacros()
#                    continue

#                elif self.tcfDependents[r][0] == 'mar' :
#                    self.copyInMargVerse()
#                    continue

#                elif self.tcfDependents[r][0] == 'set' :
#                    self.makeSetTex()
#                    continue

#                elif self.tcfDependents[r][0] == 'ext' :
#                    self.makeTexExtentionsFile()
#                    continue

#                elif self.tcfDependents[r][0] == 'sty' :
#                    self.project.managers[self.cType + '_Style'].createCompOverrideUsfmStyles(self.cid)
#                    continue

#                elif self.tcfDependents[r][0] == 'cus' :
#                    self.project.managers[self.cType + '_Style'].installCompTypeOverrideStyles()
#                    continue

#                elif self.tcfDependents[r][0] == 'glo' :
#                    self.project.managers[self.cType + '_Style'].installCompTypeGlobalStyles()
#                    continue

#                elif self.tcfDependents[r][0] == 'hyp' :
#                    writeToLog(self.project.local, self.project.userConfig, 'ERR', 'Hyphenation file creation not supported yet.')
#                    continue

#                elif self.tcfDependents[r][0] == 'non' :
#                    # This is being added in the Usfm compType too, do we want that?
#                    # I think we probably should but the function will need to be reworked.
#                    continue

#                else :
#                    writeToLog(self.project.local, self.project.userConfig, 'ERR', 'Type: [' + self.tcfDependents[r][0] + '] not supported')


