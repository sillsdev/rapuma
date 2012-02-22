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
        self.project                = project
        self.cfg                    = cfg
        self.cType                  = cType
        self.manager                = self.cType + '_Xetex'
        self.macroPackage           = self.project._projConfig['Managers'][self.manager]['macroPackage']
        self.macroLayoutValuesFile  = os.path.join(self.project.rpmConfigFolder, 'layout_' + self.macroPackage + '.xml')
        self.xFiles                 = {}

        # Get persistant values from the config if there are any
        newSectionSettings = getPersistantSettings(self.project._projConfig['Managers'][self.manager], os.path.join(self.project.rpmConfigFolder, self.xmlConfFile))
        if newSectionSettings != self.project._projConfig['Managers'][self.manager] :
            self.project._projConfig['Managers'][self.manager] = newSectionSettings
            self.project.writeOutProjConfFile = True

        # Add into layout config macro package settings
        print dir(self.project._layoutConfig)
        self.project._layoutConfig = mergeConfig(self.project._layoutConfig, self.macroLayoutValuesFile)
        writeConfFile(self.project._layoutConfig, self.project.layoutConfFile)

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

        # We can consolidate information here for files this manager needs to make
        #               ID   pType  tType          Location                FileName
        self.xFiles = { 1 : ['mac', 'input',       'macrosFolder',         self.macroPackage + '.tex',     'Macro link file'], 
                        2 : ['fnt', 'input',       'processFolder',        'fonts.tex',                    'Font control file'], 
                        3 : ['set', 'input',       'processFolder',        self.cType + '_xetex.tex',      'XeTeX main settings file'], 
                        4 : ['set', 'input',       'processFolder',        self.cType + '_xetex-ext.tex',  'XeTeX extention settings file'], 
                        5 : ['set', 'stylesheet',  'processFolder',        self.cType + '.sty',            'Primary component type styles'], 
                        6 : ['sty', 'stylesheet',  'processFolder',        'custom.sty',                   'Custom project styles (from ParaTExt)'], 
                        7 : ['sty', 'stylesheet',  'processFolder',        cid + '.sty',                   'Component style override'], 
                        8 : ['sty', 'input',       'hyphenationFolder',    'hyphenation.tex',              'XeTeX hyphenation data file'], 
                        9 : ['mac', 'input',       'macrosFolder',         'ptxplus-marginalverses.tex',   'Marginal verses extention macro'],
                       10 : ['non', 'ptxfile',     'textFolder',           cid + '.usfm',                  'Component text file'],
                       11 : ['pro', 'input',       'processFolder',        cid + '.tex',                   'XeTeX component processing commands'],
                        }

        # Create the above files in the order they are listed
        l = len(self.xFiles)
        c = 0
        while c < l :
            c +=1
            path = os.path.join(getattr(self.project, self.xFiles[c][2]), self.xFiles[c][3])
            if not os.path.isfile(path) :
                if self.xFiles[c][0] == 'mac' :
                    continue
                elif self.xFiles[c][0] == 'fnt' :
                    continue
                elif self.xFiles[c][0] == 'set' :
                    continue
                elif self.xFiles[c][0] == 'sty' :
                    continue
                elif self.xFiles[c][0] == 'pro' :
                    continue
                elif self.xFiles[c][0] == 'non' :
                    continue
                else :
                    self.project.writeToLog('ERR', 'Type: [' + self.xFiles[c][0] + '] not supported')

                self.project.writeToLog('MSG', 'Created: ' + self.xFiles[c][4])
            


        # The fonts should all be in place but a TeX specific font control
        # needs to be created. That is done here by drawing off of the font
        # manager.
#        if self.makeFontInfoTexFile() :
#            self.project.writeToLog('LOG', 'Created font information file.')
#        # Create the main control file that XeTeX will use for processing components
#        if self.makeCompTypeSettingsFile() :
#            self.project.writeToLog('LOG', 'Created the XeTeX settings file.')
#        # Create the component control file
#        if self.makeTexControlFile(cid) :
#            self.project.writeToLog('LOG', 'Created control file for: ' + cid + ' component.')
        
        # Create the system call that will render this component
        
        # Run XeTeX to render
        
        # Report/record any errors encountered


    def makeTexControlFile (self, cid) :
        '''Create the control file that will be used for rendering this
        component.'''

        # List the parts the renderer will be using (in order)
        pieces = {  1 : self.xFiles[1], 
                    2 : self.xFiles[2], 
                    3 : self.xFiles[3], 
                    4 : self.xFiles[4], 
                    5 : self.xFiles[5], 
                    6 : self.xFiles[6], 
                    7 : self.xFiles[7], 
                    8 : self.xFiles[8], 
                    9 : self.xFiles[9],
                   10 : self.xFiles[10] }

        # Create the control file 
        cidTex = os.path.join(getattr(self.project, self.xFiles[11][2]), self.xFiles[11][3])

        if not os.path.isfile(cidTex) :
            writeObject = codecs.open(cidTex, "w", encoding='utf_8')
            writeObject.write('# ' + cid + '.tex created: ' + tStamp() + '\n')
            # We allow for a number of different types of lines to
            # be created for this file. Most lines are in three parts
            # a top cookie, bottom cookie and a cream filling :-)
            l = len(pieces)
            c = 1
            while c <= l :
                filling = os.path.join(getattr(self.project, pieces[c][1]), pieces[c][2])
                if pieces[c][0] == 'input' :
                    if os.path.isfile(filling) :
                        writeObject.write('\\' + pieces[c][0] + ' \"' + filling + '\"\n')
                elif pieces[c][0] in ['stylesheet', 'ptxfile'] :
                    if os.path.isfile(filling) :
                        writeObject.write('\\' + pieces[c][0] + ' {' + filling + '}\n')
                elif pieces[c][0] == 'command' :
                    writeObject.write('\\' + pieces[c][0] + '\n')
                else :
                    self.project.writeToLog('ERR', 'Type not supported: ' + pieces[c][0])

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



