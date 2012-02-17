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

import os


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

        # Set values for this manager
        self.project            = project
        self.cfg                = cfg
        self.cType              = cType
        
        # Get persistant values from the config if there are any
        manager = self.cType + '_Xetex'
        newSectionSettings = getPersistantSettings(self.project._projConfig['Managers'][manager], os.path.join(self.project.rpmConfigFolder, self.xmlConfFile))
        if newSectionSettings != self.project._projConfig['Managers'][manager] :
            self.project._projConfig['Managers'][manager] = newSectionSettings
            self.project.writeOutProjConfFile = True

        self.compSettings = self.project._projConfig['Managers'][manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)

        # Set values for this manager
        self._formatConfig              = {}
        self.formatConfigFileName       = 'format.conf'
        self.formatConfFile             = os.path.join(self.project.projConfFolder, self.formatConfigFileName)
        self.defaultFormatValuesFile    = os.path.join(self.project.rpmConfigFolder, 'format_values.xml')
        self.macroFormatValuesFile      = os.path.join(self.project.rpmConfigFolder, 'format_values-' + self.project._projConfig['Managers'][manager]['macroPackage'] + '.xml')

###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def run (self, cid) :
        '''This will render a component using the XeTeX rendering enging.'''

        # Using the information passed to this module created by other managers
        # it will create all the final forms of files needed to render the
        # current component with the XeTeX renderer.

        # Start by making the main format config file that will control
        # how Xetex will behave. Depending on the macro package that is
        # used, this will bring in the default settings that all projects
        # use, then merge in specific settings for the macro package being
        # used for this in this instance.
        if not os.path.isfile(self.formatConfFile) :
            self._formatConfig = mergeConfig(getXMLSettings(self.defaultFormatValuesFile), self.macroFormatValuesFile)
            writeConfFile(self._formatConfig, self.formatConfFile)
        else :
            self._formatConfig = ConfigObj(self.formatConfFile)

        # The fonts should all be in place but a TeX specific font control
        # needs to be created. That is done here by drawing off of the font
        # manager.
        if self.makeFontInfoTexFile() :
            self.project.writeToLog('MSG', 'Created font information file.')
        # Create the main control file that XeTeX will use for processing components
        if self.makeCompTypeSettingsFile() :
            self.project.writeToLog('MSG', 'Created the XeTeX settings file.')
        # Create the component control file
        if self.makeTexControlFile(cid) :
            self.project.writeToLog('MSG', 'Created control file for: ' + cid + ' component.')
        
        # Create the system call that will render this component
        
        # Run XeTeX to render
        
        # Report/record any errors encountered


    def makeTexControlFile (self, cid) :
        '''Create the control file that will be used for rendering this
        component.'''

        # Create the control file
        ctrlTex = os.path.join(self.project.processFolder, cid + '.tex')

        if not os.path.isfile(ctrlTex) :
            writeObject = codecs.open(ctrlTex, "w", encoding='utf_8')
            writeObject.write('# ' + cid + '.tex created: ' + tStamp() + '\n')

            # Finish the process
            writeObject.close()
            return True


    def makeCompTypeSettingsFile (self) :
        '''Create the TeX settings file for this component type.'''

        compTypeSettingsFileName = 'xetex_settings_' + self.cType + '.tex'
        compTypeSettings = os.path.join(self.project.processFolder, compTypeSettingsFileName)

        if not os.path.isfile(compTypeSettings) :
            writeObject = codecs.open(compTypeSettings, "w", encoding='utf_8')
            writeObject.write('# ' + compTypeSettingsFileName + ' created: ' + tStamp() + '\n')

            # Finish the process
            writeObject.close()
            return True


    def makeFontInfoTexFile (self) :
        '''Create a TeX info font file that TeX will use for rendering.'''

        # We will not make this file if it is already there
        fontInfoFileName = os.path.join(self.project.processFolder,'fonts.tex')
        # The rule is that we only create this file if it is not there,
        # otherwise it will silently fail.  If one already exists the file will
        # need to be removed by some other process before it can be recreated.
        sCType = self.cType.capitalize()
        if not os.path.isfile(fontInfoFileName) :
            writeObject = codecs.open(fontInfoFileName, "w", encoding='utf_8')
            writeObject.write('# fonts.tex' + ' created: ' + tStamp() + '\n')
            for f in self.project._projConfig['CompTypes'][sCType]['installedFonts'] :
                fInfo = self.project._projConfig['Fonts'][f]
                # Create the primary fonts that will be used with TeX
                if self.project._projConfig['CompTypes'][sCType]['primaryFont'] == f :
                    writeObject.write('\n# These are normal use fonts for this type of component.\n')
                    features = fInfo['FontInformation']['features']
                    for tf in fInfo :
                        if tf[:8] == 'Typeface' :
                            # Make all our line components (More will need to be added)
                            startDef    = '\\def\\' + fInfo[tf]['texMapping'] + '{'
                            fpath       = "\"[" + os.path.join('..', self.project.fontsFolder, fInfo[tf]['file']) + "]\""
                            endDef      = "}\n"
                            featureString = ''
                            for i in features :
                                featureString += ':' + i

                            writeObject.write(startDef + fpath + featureString + endDef)

                # Create defs with secondary fonts for special use with TeX in publication
                else :
                    writeObject.write('\n# These are special use fonts for this type of component.\n')
                    features = fInfo['FontInformation']['features']
                    for tf in fInfo :
                        if tf[:8] == 'Typeface' :
                            # Make all our line components (More will need to be added)
                            startDef    = '\\def\\' + f.lower() + tf[8:].lower() + '{'
                            fpath       = "\"[" + os.path.join('..', self.project.fontsFolder, fInfo[tf]['file']) + "]\""
                            endDef      = "}\n"
                            featureString = ''
                            for i in features :
                                featureString += ':' + i

                            writeObject.write(startDef + fpath + featureString + endDef)

            # Finish the process
            writeObject.close()
            return True



