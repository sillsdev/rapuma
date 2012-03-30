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

        # Set values for this manager
        self.project                = project
        self.cfg                    = cfg
        self.cType                  = cType
        self.manager                = self.cType + '_Xetex'
        self.macroPackage           = self.project.projConfig['Managers'][self.manager]['macroPackage']
        self.macroLayoutValuesFile  = os.path.join(self.project.local.rpmConfigFolder, 'layout_' + self.macroPackage + '.xml')
        self.xFiles                 = {}

        # This manager is dependent on usfm_Layout. Load it if needed.
        if 'usfm_Layout' not in self.project.managers :
            self.project.createManager(self.cType, 'layout')

        # Get persistant values from the config if there are any
        newSectionSettings = getPersistantSettings(project.managers['usfm_Layout'].layoutConfig, self.macroLayoutValuesFile)
        if newSectionSettings != self.project.managers['usfm_Layout'].layoutConfig :
            project.managers['usfm_Layout'].layoutConfig = newSectionSettings

        macVals = ConfigObj(getXMLSettings(self.macroLayoutValuesFile))
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

        # Set values for this manager
        self.macroPackage               = self.project.projConfig['Managers'][self.manager]['macroPackage']
        self.macrosTarget               = os.path.join(self.project.local.projMacrosFolder, self.macroPackage)
        self.macrosSource               = os.path.join(self.project.local.rpmMacrosFolder, self.macroPackage)

        # Copy in to the process folder the macro package for this component
        if not os.path.isdir(self.macrosTarget) :
            os.makedirs(self.macrosTarget)

        for root, dirs, files in os.walk(self.macrosSource) :
            for f in files :
                if not os.path.isfile(os.path.join(self.macrosTarget, f)) :
                    shutil.copy(os.path.join(self.macrosSource, f), os.path.join(self.project.local.projMacrosFolder, f))


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
        self.xFiles = { 1 : ['mac', 'input',       'projMacrosFolder',     self.macroPackage + '.tex',     'Macro link file'], 
                        2 : ['fnt', 'input',       'projProcessFolder',    'fonts.tex',                    'Font control file'], 
                        3 : ['set', 'input',       'projProcessFolder',    self.cType + '_xetex.tex',      'XeTeX main settings file'], 
                        4 : ['set', 'input',       'projProcessFolder',    self.cType + '_xetex-ext.tex',  'XeTeX extention settings file'], 
                        5 : ['set', 'stylesheet',  'projProcessFolder',    self.cType + '.sty',            'Primary component type styles'], 
                        6 : ['sty', 'stylesheet',  'projProcessFolder',    'custom.sty',                   'Custom project styles (from ParaTExt)'], 
                        7 : ['sty', 'stylesheet',  'projProcessFolder',    cid + '.sty',                   'Component style override'], 
                        8 : ['sty', 'input',       'projHyphenationFolder','hyphenation.tex',              'XeTeX hyphenation data file'], 
                        9 : ['mac', 'input',       'projMacrosFolder',     'ptxplus-marginalverses.tex',   'Marginal verses extention macro'],
                       10 : ['non', 'ptxfile',     'projTextFolder',       cid + '.usfm',                  'Component text file'],
                       11 : ['pro', 'input',       'projProcessFolder',    cid + '.tex',                   'XeTeX component processing commands'],
                        }

        # Create the above files in the order they are listed
        l = len(self.xFiles)
        c = 0
        while c < l :
            c +=1
            path = os.path.join(getattr(self.project.local, self.xFiles[c][2]), self.xFiles[c][3])
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
                    writeToLog(self.project.local, self.project.userConfig, 'ERR', 'Type: [' + self.xFiles[c][0] + '] not supported')

                writeToLog(self.project.local, self.project.userConfig, 'MSG', 'Created: ' + self.xFiles[c][4])


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
                    writeToLog(self.project.local, self.project.userConfig, 'ERR', 'Type not supported: ' + pieces[c][0])

                c +=1

            # Finish the process
            writeObject.write('\\bye\n')
            writeObject.close()
            return True


    def makeCompTypeSettingsFile (self) :
        '''Create the TeX settings file for this component type.'''

        compTypeSettingsFileName = 'xetex_settings_' + self.cType + '.tex'
        compTypeSettings = os.path.join(self.project.local.projProcessFolder, compTypeSettingsFileName)

        # Return now if the file is there and it is newer than the conf file
        if os.path.isfile(compTypeSettings) :
            tFileTime = 0
            tFileTime = int(os.path.getctime(compTypeSettings))
            cFileTime = int(os.path.getctime(self.project.local.projConfFile))
            fFileTime = int(os.path.getctime(self.project.local.fontConfFile))
            if tFileTime > fFileTime and tFileTime > cFileTime :
                return

        # Get the default and TeX macro values and merge them into one dictionary
        x = self.makeTexSettingsDict(self.project.local.rpmLayoutDefaultFile)
        y = self.makeTexSettingsDict(self.macroLayoutValuesFile)
        macTexVals = dict(y.items() + x.items())

        writeObject = codecs.open(compTypeSettings, "w", encoding='utf_8')
        writeObject.write('# ' + compTypeSettingsFileName + ' created: ' + tStamp() + '\n')

        # Bring in the settings from the layoutConfig
        cfg = self.project.managers[self.cType + '_Layout'].layoutConfig
        for section in cfg.keys() :
            writeObject.write('\n# ' + section + '\n')
            for k, v in cfg[section].iteritems() :
                if testForSetting(macTexVals, k, 'usfmTex') :
                    line = macTexVals[k]['usfmTex']
                    # If there is a boolDepend then we don't need to output
                    if testForSetting(macTexVals, k, 'boolDepend') and not str2bool(self.rtnBoolDepend(cfg, macTexVals[k]['boolDepend'])) :
                        continue
                    else :
                        if self.hasPlaceHolder(line) :
                            (ht, hk) = self.getPlaceHolder(line)
                            if ht == 'v' :
                                line = self.insertValue(line, v)
                            elif ht == 'path' :
                                pth = getattr(self.project.local, hk)
                                line = self.insertValue(line, pth)

                    writeObject.write(line + '\n')

        # Add all the font def commands
        writeObject.write('\n# Font Definitions\n')
        fpath = ''
        featureString = ''
        for f in self.project.projConfig['CompTypes'][self.cType.capitalize()]['installedFonts'] :
            fInfo = self.project.managers['usfm_Font'].fontConfig['Fonts'][f]
            features = fInfo['FontInformation']['features']
            # Create the primary fonts that will be used with TeX
            if self.project.projConfig['CompTypes'][self.cType.capitalize()]['primaryFont'] == f :
                writeObject.write('\n# These are normal use fonts for this type of component.\n')
                features = fInfo['FontInformation']['features']
                for tf in fInfo :
                    if tf[:8] == 'Typeface' :
                        tmc = 0
                        for tm in fInfo[tf]['texMapping'] :
                            startDef    = '\\def\\' + fInfo[tf]['texMapping'][tmc] + '{'
                            fpath       = "\"[" + os.path.join('..', self.project.local.projFontsFolder, fInfo[tf]['file']) + "]\""
                            endDef      = "}\n"
                            featureString = ''
                            for i in features :
                                featureString += ':' + i

                            modsString = ''
                            for m in fInfo[tf]['modify'] :
                                modsString += ':' + m

                            tmc +=1
                            writeObject.write(startDef + fpath + featureString + modsString + endDef)

            else :
                writeObject.write('\n# These are normal use fonts for this type of component.\n')
                features = fInfo['FontInformation']['features']
                for tf in fInfo :
                    if tf[:8] == 'Typeface' :
                        tmc = 0
                        for tm in fInfo[tf]['texMapping'] :
                            name = fInfo[tf]['name'].lower().replace(' ', '')
                            startDef    = '\\def\\' + name + fInfo[tf]['texMapping'][tmc] + '{'
                            fpath       = "\"[" + os.path.join('..', self.project.local.projFontsFolder, fInfo[tf]['file']) + "]\""
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
        writeObject.write('\n# Special commands\n')
        writeObject.write('\catcode`@=11\n')
        writeObject.write('\def\makedigitsother{\m@kedigitsother}\n')
        writeObject.write('\def\makedigitsletters{\m@kedigitsletters}\n')
        writeObject.write('\catcode `@=12\n')
        writeObject.write('\\vfuzz=2.3pt\n')

        # End here
        writeObject.close()
        return True


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
            for f in self.project.projConfig['CompTypes'][sCType]['installedFonts'] :
                fInfo = self.project.projConfig['Fonts'][f]
                # Create the primary fonts that will be used with TeX
                if self.project.projConfig['CompTypes'][sCType]['primaryFont'] == f :
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



