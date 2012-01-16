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
        newSectionSettings = getPersistantSettings(self.project._projConfig['Managers'][self.cType + '_Xetex'], os.path.join(self.project.rpmConfigFolder, 'xetex.xml'))
        if newSectionSettings != self.project._projConfig['Managers'][self.cType + '_Xetex'] :
            self.project._projConfig['Managers'][self.cType + '_Xetex'] = newSectionSettings
            self.project.writeOutProjConfFile = True

        self.compSettings = self.project._projConfig['Managers'][self.cType + '_Xetex']

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)




###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def run (self) :
        '''This will render a component using the XeTeX rendering enging.'''

        print "Doing something..."
        
        # Using the information passed to this module created by other managers
        # it will create all the final forms of files needed to render the
        # current component with the XeTeX renderer.

 
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



