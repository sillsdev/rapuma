#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project tasks.

# History:
# 20111207 - djd - Started with intial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil


# Load the local classes
from tools import *
from manager import Manager
import font_command as fntCmd


###############################################################################
################################## Begin Class ################################
###############################################################################

class Font (Manager) :

    # Shared values
    xmlConfFile     = 'font.xml'
    xmlInitFile     = 'font_init.xml'

    def __init__(self, project, cfg) :
        '''Do the primary initialization for this manager.'''

        super(Font, self).__init__(project, cfg)

        # Set values for this manager
        self.project            = project
        self.cfg                = cfg
        self.fontFileName       = 'fonts.conf'
        self.fontFolderName     = 'Fonts'
        self.fontFolder         = os.path.join(self.project.projHome, self.fontFolderName)
        self.fontConfFile       = os.path.join(self.project.projConfFolder, self.fontFileName)
        self.rpmXmlFontConfig   = os.path.join(self.project.rpmConfigFolder, self.xmlConfFile)
        self.fontInitFile       = os.path.join(self.project.rpmConfigFolder, self.xmlInitFile)

        # These are constant values that are in the XML file
        self.fontDefaults = getXMLSettings(os.path.join(self.project.rpmConfigFolder, self.xmlConfFile))

# FIXME: This next part is not right at all, is it?
        self.fontConfig = self.fontDefaults
        for k, v in self.fontDefaults.iteritems() :
            setattr(self, k, v)


        # Start with default settings
        if os.path.isfile(self.fontInitFile) :
            self._initConfig = getXMLSettings(self.fontInitFile)


###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def makeFontInfoTexFile (self) :
        '''Create a TeX info font file that TeX will use for rendering.'''

        # We will not make this file if it is already there
        fontInfoFileName = os.path.join(self.processFolder, self.aid + '.tex')

        # The rule is that we only create this file if it is not there,
        # otherwise it will silently fail.  If one already exists the file will
        # need to be removed by some other process before it can be recreated.
        if not os.path.isfile(fontInfoFileName) or self.project._projConfig['Auxiliaries'][self.aid]['remakeTexFile'] == 'True' :
            writeObject = codecs.open(fontInfoFileName, "w", encoding='utf_8')
            writeObject.write('# ' + self.aid + '.tex' + ' created: ' + tStamp() + '\n')
            auxFonts = self.project._projConfig['Auxiliaries'][self.aid]['installedFonts']
            for f in auxFonts :
                fInfo = self._fontConfig['Fonts'][f]
                # Create the primary fonts that will be used with TeX
                if self.project._projConfig['Auxiliaries'][self.aid]['primaryFont'] == f :
                    writeObject.write('\n# These are normal use fonts for this type of component.\n')
                    features = self.project._projConfig['Auxiliaries'][self.aid][f]['features']
                    for tf in fInfo :
                        if tf[:8] == 'Typeface' :
                            # Make all our line components (More will need to be added)
                            startDef    = '\\def\\' + fInfo[tf]['texMapping'] + '{'
                            fpath       = "\"[" + os.path.join('..', self.fontFolderName, fInfo[tf]['file']) + "]\""
                            endDef      = "}\n"
                            featureString = ''
                            for i in features :
                                featureString += ':' + i

                            writeObject.write(startDef + fpath + featureString + endDef)

                # Create defs with secondary fonts for special use with TeX in publication
                else :
                    writeObject.write('\n# These are special use fonts for this type of component.\n')
                    features = self.project._projConfig['Auxiliaries'][self.aid][f]['features']
                    for tf in fInfo :
                        if tf[:8] == 'Typeface' :
                            # Make all our line components (More will need to be added)
                            startDef    = '\\def\\' + f.lower() + tf[8:].lower() + '{'
                            fpath       = "\"[" + os.path.join('..', self.fontFolderName, fInfo[tf]['file']) + "]\""
                            endDef      = "}\n"
                            featureString = ''
                            for i in features :
                                featureString += ':' + i

                            writeObject.write(startDef + fpath + featureString + endDef)

            # Finish the process
            writeObject.close()
            self.project._projConfig['Auxiliaries'][self.aid]['remakeTexFile'] = False
            self.project.writeOutProjConfFile = True
            return True


    def recordFont (self, font, manager) :
        '''Check for the exsitance of a font in the project conf file.
        If there is one, return, if not add it.'''

        # It is expected that all the necessary meta data for this font is in
        # a file located with the font. The system expects to find it in:
        # ~/resources/lib_share/Fonts/[FontID]
        fontDir = os.path.join(self.project.rpmFontsFolder, font)
        fontInfo = os.path.join(self.project.rpmFontsFolder, font, font + '.xml')
        if not os.path.isfile(fontInfo) :
            self.project.writeToLog('ERR', 'Halt! ' + font + '.xml not found.')
            return False

        # Inject the font info into the project format config file.
        fInfo = getXMLSettings(fontInfo)
        buildConfSection (self.project._projConfig, 'Fonts')
        buildConfSection (self.project._projConfig['Fonts'], font)
        self.project._projConfig['Fonts'][font] = fInfo.dict()

        # Record the font with the font manager that called it
        if not self.project._projConfig['Managers'][manager]['primaryFont'] :
            self.project._projConfig['Managers'][manager]['primaryFont'] = font
            self.project._projConfig['Managers'][manager]['installedFonts'] = [font]
        else :
            fontList = self.project._projConfig['Managers'][manager]['installedFonts']
            self.project._projConfig['Managers'][manager]['installedFonts'] = addToList(fontList, font)

        self.project.writeOutProjConfFile = True
        self.project.writeToLog('LOG', font + ' font setup information added to project config')
        return True


    def installFont (self, font, manager) :
        '''Install (copy) a font into a project.'''

        for font in self.project._projConfig['Managers'][manager]['installedFonts'] :
            fontInfo = self.project._projConfig['Fonts'][font]
            # Make the font family folder for this typeface
            fontFamilyFolder = os.path.join(self.fontFolder, fontInfo['FontInformation']['fontFolder'])
            if not os.path.isdir(fontFamilyFolder) :
                os.makedirs(fontFamilyFolder)

            # Now loop through all the typefaces in this family and copy over the files
            for tf in fontInfo.keys() :
                if tf[:8] == 'Typeface' :
                    # Find the source font file name and path, always use the user's version
                    fontFileName = fontInfo[tf]['file']
                    fontSource = None
                    # System version
                    if os.path.isfile(os.path.join(self.project.rpmFontsFolder, font, fontFileName)) :
                        fontSource = os.path.join(self.project.rpmFontsFolder, font, fontFileName)
                    # Crash and burn if the font file is not found
                    if not fontSource :
                        self.project.writeToLog('ERR', 'Halt! ' + fontSource + 'not found.', 'fontsTex.initAuxiliary()')
                        return False
                    # Copy the font file if need be
                    fontFilePath = os.path.join(self.fontFolder, font, fontFileName)
                    if not os.path.isfile(fontFilePath) :
                        shutil.copy(fontSource, fontFilePath)

        return True



