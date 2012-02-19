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
        self.manager            = self.cType + '_Xetex'
        self.macroPackage       = self.project._projConfig['Managers'][self.manager]['macroPackage']

        # Get persistant values from the config if there are any
        newSectionSettings = getPersistantSettings(self.project._projConfig['Managers'][self.manager], os.path.join(self.project.rpmConfigFolder, self.xmlConfFile))
        if newSectionSettings != self.project._projConfig['Managers'][self.manager] :
            self.project._projConfig['Managers'][self.manager] = newSectionSettings
            self.project.writeOutProjConfFile = True

        self.compSettings = self.project._projConfig['Managers'][self.manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)


###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def run (self, cid) :
        '''This will render a component using the XeTeX rendering enging.'''

        # Using the information passed to this module created by other managers
        # it will create all the final forms of files needed to render the
        # current component with the XeTeX renderer.

        # The fonts should all be in place but a TeX specific font control
        # needs to be created. That is done here by drawing off of the font
        # manager.
        if self.makeFontInfoTexFile() :
            self.project.writeToLog('LOG', 'Created font information file.')
        # Create the main control file that XeTeX will use for processing components
        if self.makeCompTypeSettingsFile() :
            self.project.writeToLog('LOG', 'Created the XeTeX settings file.')
        # Create the component control file
        if self.makeTexControlFile(cid) :
            self.project.writeToLog('LOG', 'Created control file for: ' + cid + ' component.')
        
        # Create the system call that will render this component
        
        # Run XeTeX to render
        
        # Report/record any errors encountered


    def makeTexControlFile (self, cid) :
        '''Create the control file that will be used for rendering this
        component.'''

        # List the parts the renderer will be using (in order)
        pieces = {  1 : ['input', 'macrosFolder', self.macroPackage + '.tex'], 2 : ['input', 'processFolder', 'fonts.tex'], 
                    3 : ['input', 'processFolder', 'xetex_settings_' + self.cType + '.tex'], 4 : ['stylesheet', 'processFolder', self.cType + '.sty'], 
                    5 : ['input', 'hyphenationFolder', 'hyphenation.tex'], 6 : ['input', 'macrosFolder', 'ptxplus-marginalverses.tex'],
                    7 : ['ptxfile', 'textFolder', cid + '.usfm'] }

        # Create the control file 
        ctrlTex = os.path.join(self.project.processFolder, cid + '.tex')

        if not os.path.isfile(ctrlTex) :
            writeObject = codecs.open(ctrlTex, "w", encoding='utf_8')
            writeObject.write('# ' + cid + '.tex created: ' + tStamp() + '\n')
            l = len(pieces)
            c = 1
            while c <= l :
                if pieces[c][0] == 'input' :
                    lf = '\\' + pieces[c][0] + ' \"'
                    le = '\"\n'
                elif pieces[c][0] == 'stylesheet' :
                    lf = '\\' + pieces[c][0] + ' {'
                    le = '}\n'
                elif pieces[c][0] == 'ptxfile' :
                    lf = '\\' + pieces[c][0] + ' {'
                    le = '}\n'
                else :
                    self.project.writeToLog('ERR', 'Type not supported: ' + pieces[c][0])

                # Build the path
                path =  os.path.join(setattr(self, 'project', pieces[c][1]), pieces[c][2])

                # Write out after checking to see if it is needed
                if ... :
                writeObject.write(lf + path + le)
                c +=1

            # Finish the process
            writeObject.write('\\bye\n')
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



