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

import os


# Load the local classes
from tools import *
from manager import Manager
import font_command as fntCmd


###############################################################################
################################## Begin Class ################################
###############################################################################

class Font (Manager) :

    def __init__(self, project) :
        '''Do the primary initialization for this manager.'''

        super(Font, self).__init__(project)

        terminal("Initializing Font Manager")

        # Add commands for this manager
        project.addCommand("font_add", fntCmd.AddFont(self))

        # Set values for this manager
        self.fontFileName       = 'fonts.conf'
        self.fontFolderName     = 'Fonts'
        self.fontFolder         = os.path.join(self.project.projHome, self.fontFolderName)
        self.fontConfFile       = os.path.join(self.project.projConfFolder, self.fontFileName)
        self.rpmXmlFontConfig   = os.path.join(self.project.rpmConfigFolder, 'font.xml')
        self.fontInitFile       = os.path.join(self.project.rpmConfigFolder, 'font_init.xml')

        # Start with default settings
        if os.path.isfile(self.fontInitFile) :
            self._initConfig = getXMLSettings(self.fontInitFile)
            self.runBasicManagerInit(self._initConfig)


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


    def initFonts (self) :
        '''Initialize the fonts for this auxiliary component by finding and
        copying the fonts into the project from the source.  Of course this only
        works if there are any fonts set for a given aux.'''

        for font in self.project._projConfig['FontInformation']['installedFonts'] :
            fontInfo = self._fontConfig['Fonts'][font]
            # Make the font family folder for this typeface
            fontFamilyFolder = os.path.join(self.fontFolder, fontInfo['FontInformation']['fontFolder'])
            if not os.path.isdir(fontFamilyFolder) :
                os.mkdir(fontFamilyFolder)
                
            # Now loop through all the typefaces in this family and copy over the files
            for tf in fontInfo.keys() :
                if tf[:8] == 'Typeface' :
                    # Find the source font file name and path, always use the user's version
                    fontFileName = fontInfo[tf]['file']
                    fontSource = None
                    # System version
                    if os.path.isfile(os.path.join(self.project.rpmFonts, font, fontFileName)) :
                        fontSource = os.path.join(self.project.rpmFonts, font, fontFileName)
                    # User version
                    if os.path.isfile(os.path.join(self.project.userFonts, font, fontFileName)) :
                        fontSource = os.path.join(self.project.userFonts, font, fontFileName)
                    # Crash and burn if the font file is not found
                    if not fontSource :
                        self.project.writeToLog('ERR', 'Halt! ' + fontSource + 'not found.', 'fontsTex.initAuxiliary()')
                        return False
                    # Copy the font file if need be
                    fontFilePath = os.path.join(self.fontFolder, font, fontFileName)
                    if not os.path.isfile(fontFilePath) :
                        shutil.copy(fontSource, fontFilePath)

        return True


    def addFont (self, ftype, font, rank='None') :
        '''Setup a font for a specific typeface and create a fonts.conf file in
        the process folder.'''

        # First, delete the existing font info TeX file.  Everything changes if
        # we add a font to this aux
        if os.path.isfile(os.path.join(self.processFolder, self.aid + '.tex')) :
            os.remove(os.path.join(self.processFolder, self.aid + '.tex'))

        # It is expected that all the necessary meta data for this font is in
        # a file located with the font. The system expects to find it in:
        # ~/lib_share/Fonts/[FontID]
        # There will be a minimal number of fonts in the system but we will look
        # in the user area first. That is where the fonts really should be kept.
        # If it is unable to find the font in either the user area or the system
        # resources shared area, it will fail.
        if os.path.isfile(os.path.join(self.project.userFonts, font, font + '.xml')) :
            self.project.writeToLog('LOG', 'Found ' + font + '.xml in user resources.')
            fontDir = os.path.join(self.project.userFonts, font)
            fontInfo = os.path.join(self.project.userFonts, font, font + '.xml')
        elif os.path.isfile(os.path.join(self.project.rpmFonts, font, font + '.xml')) :
            self.project.writeToLog('LOG', 'Found ' + font + '.xml in RPM resources.')
            fontDir = os.path.join(self.project.rpmFonts, font)
            fontInfo = os.path.join(self.project.rpmFonts, font, font + '.xml')
        else :
            self.project.writeToLog('ERR', 'Halt! ' + font + '.xml not found.')
            return False

        # Inject the font info into the project format config file.
        fInfo = getXMLSettings(fontInfo)
        buildConfSection (self._fontConfig['Fonts'], font)
        self._fontConfig['Fonts'][font] = fInfo.dict()

        # Add to installed fonts list for this auxiliary type, only one instance allowed
        if font not in self.project._projConfig['AuxiliaryTypes'][self.type]['installedFonts'] :
            listOrder = []
            listOrder = self.project._projConfig['AuxiliaryTypes'][self.type]['installedFonts']
            listOrder.append(font)
            self.project._projConfig['AuxiliaryTypes'][self.type]['installedFonts'] = listOrder

        if font not in self.project._projConfig['Auxiliaries'][self.aid]['installedFonts'] :
            listOrder = []
            listOrder = self.project._projConfig['Auxiliaries'][self.aid]['installedFonts']
            listOrder.append(font)
            self.project._projConfig['Auxiliaries'][self.aid]['installedFonts'] = listOrder

        # Check to see if the primary font has been set
        if rank.lower() == 'primary' :
            self.project._projConfig['Auxiliaries'][self.aid]['primaryFont'] = self._fontConfig['Fonts'][font]['FontInformation']['fontID']

        # Add any features that this aux needs to have with this specific font.
        buildConfSection(self.project._projConfig['Auxiliaries'][self.aid], font)
        self.project._projConfig['Auxiliaries'][self.aid][font]['features'] = self._fontConfig['Fonts'][font]['FontInformation']['features']

        # Set conf write flag and report
        self.project._projConfig['Auxiliaries'][self.aid]['remakeTexFile'] = True
        self.project.writeOutProjConfFile = True
        writeConfFile(self._fontConfig, self.fontFileName, self.processFolder)
        self.project.writeToLog('MSG', font + ' font setup information added to [' + ftype + '] component')     
        return True


    def removeAuxFont (self, ftype, font) :
        '''Remove a font from only this aux.'''

        # FIXME: This will work at the aux level but needs expanding to work
        # more globally

        # Remove from aux font listing
        if font in self.project._projConfig['Auxiliaries'][self.aid]['installedFonts'] :
            listOrder = []
            listOrder = self.project._projConfig['Auxiliaries'][self.aid]['installedFonts']
            listOrder.pop(listOrder.index(font))
            self.project._projConfig['Auxiliaries'][self.aid]['installedFonts'] = listOrder

        # Remove any features that this aux needed to have with this specific font.
        if font in self.project._projConfig['Auxiliaries'][self.aid] :
            del self.project._projConfig['Auxiliaries'][self.aid][font]

        # Change the primary font setting if needed
        if self.project._projConfig['Auxiliaries'][self.aid]['primaryFont'] == font :
            self.project._projConfig['Auxiliaries'][self.aid]['primaryFont'] = self.project._projConfig['Auxiliaries'][self.aid]['installedFonts'][0]
        else :
            self.project._projConfig['Auxiliaries'][self.aid]['primaryFont'] = 'None'

        # Set conf write flag and report
        self.project._projConfig['Auxiliaries'][self.aid]['remakeTexFile'] = True
        self.project.writeOutProjConfFile = True
        self.project.writeToLog('MSG', font + ' font setup information removed from [' + ftype + '] component')
        return True


