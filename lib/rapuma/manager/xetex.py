#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (sparkycbr at gmail dot com)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This manager class will handle component rendering with XeTeX.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, re, codecs, subprocess
from configobj                          import ConfigObj
from pyPdf                              import PdfFileReader

# Load the local classes
from rapuma.core.tools                  import Tools
from rapuma.manager.manager             import Manager
from rapuma.project.proj_config         import Config
from rapuma.project.proj_macro          import Macro
from rapuma.project.proj_background     import ProjBackground
from rapuma.project.proj_diagnose       import ProjDiagnose
from rapuma.project.proj_font           import ProjFont
from rapuma.project.proj_illustration   import ProjIllustration
from rapuma.project.proj_hyphenation    import ProjHyphenation
from rapuma.group.usfmTex               import UsfmTex
from rapuma.group.usfm_data             import UsfmData


###############################################################################
################################## Begin Class ################################
###############################################################################

class Xetex (Manager) :

    # Shared values
    xmlConfFile     = 'xetex.xml'

    def __init__(self, project, cfg, cType) :
        '''Do the primary initialization for this manager.'''

        super(Xetex, self).__init__(project, cfg)

#        import pdb; pdb.set_trace()

        # Create all the values we can right now for this manager.
        # Others will be created at run time when we know the cid.
        self.tools                  = Tools()
        self.project                = project
        self.local                  = project.local
        self.log                    = project.log
        self.cfg                    = cfg
        self.pid                    = project.projectIDCode
        self.gid                    = project.gid
        self.cType                  = cType
        self.Ctype                  = cType.capitalize()
        self.mType                  = project.projectMediaIDCode
        self.renderer               = 'xetex'
        self.manager                = self.cType + '_' + self.renderer.capitalize()
        self.managers               = project.managers
        self.pg_back                = ProjBackground(self.pid, self.gid)
        self.fmt_diagnose           = ProjDiagnose(self.pid, self.gid)
        self.proj_config            = Config(self.pid, self.gid)
        self.proj_config.getProjectConfig()
        self.proj_config.getLayoutConfig()
        self.proj_config.getFontConfig()
        self.proj_config.getMacroConfig()
        # Bring in some manager objects we will need
        self.proj_font              = ProjFont(self.pid)
        self.proj_illustration      = ProjIllustration(self.pid, self.gid)
        self.proj_hyphenation       = ProjHyphenation(self.pid, self.gid)
        self.usfmData               = UsfmData()
        self.cidChapNumDict         = self.usfmData.cidChapNumDict()
        self.cidPtIdDict            = self.usfmData.cidPtIdDict()
        # Get config objs
        self.projectConfig          = self.proj_config.projectConfig
        self.layoutConfig           = self.proj_config.layoutConfig
        self.fontConfig             = self.proj_config.fontConfig
        self.macroConfig            = self.proj_config.macroConfig
        self.userConfig             = self.project.userConfig
        self.macPackId              = self.projectConfig['CompTypes'][self.Ctype]['macroPackage']
        # Some config settings

        self.pdfViewerCmd           = self.tools.getPdfViewerCommand(self.userConfig, self.projectConfig)
        self.sourceEditor           = self.projectConfig['CompTypes'][self.Ctype]['sourceEditor']
        self.useBackground          = self.tools.str2bool(self.layoutConfig['DocumentFeatures']['useBackground'])
        self.useDiagnostic          = self.tools.str2bool(self.layoutConfig['DocumentFeatures']['useDiagnostic'])
        self.useDocInfo             = self.tools.str2bool(self.layoutConfig['DocumentFeatures']['useDocInfo'])

        # Get settings for this component
        self.managerSettings = self.projectConfig['Managers'][self.manager]
        for k, v in self.managerSettings.iteritems() :
            if v == 'True' or v == 'False' :
                setattr(self, k, self.tools.str2bool(v))
            else :
                setattr(self, k, v)

        # Set some Booleans (this comes after persistant values are set)
        # In case the macro is not installed we need to skip over this
        try :
            self.useHyphenation         = self.tools.str2bool(self.projectConfig['ProjectInfo']['hyphenationOn'])
            self.chapNumOffSingChap     = self.tools.str2bool(self.macroConfig['Macros'][self.macPackId]['ChapterVerse']['omitChapterNumberOnSingleChapterBook'])
        except :
            self.useHyphenation         = None
            self.chapNumOffSingChap     = None
        # Make any dependent folders if needed
        if not os.path.isdir(self.local.projGidFolder) :
            os.makedirs(self.local.projGidFolder)

        # Record some error codes
        # FIXME: much more needs to be done with this
        self.xetexErrorCodes =  {
            0   : 'Rendering succeful.',
            256 : 'Something really awful happened.'
                                }

        # Log messages for this module
        self.errorCodes     = {

            '1005' : ['ERR', 'PDF viewer failed with error: [<<1>>]'],
            '1010' : ['ERR', 'Style file [<<1>>] could not be created.'],
            '1040' : ['LOG', 'Created: [<<1>>]'],

            '0420' : ['WRN', 'TeX settings file has been frozen for debugging purposes.'],
            '0440' : ['LOG', 'Created: [<<1>>]'],
            '0460' : ['LOG', 'Settings changed in [<<1>>], [<<2>>] needed to be recreated.'],
            '0465' : ['LOG', 'File: [<<1>>] missing, created a new one.'],
            '0470' : ['ERR', 'Macro package [<<1>>] is not recognized by the system.'],

            '0600' : ['MSG', '<<1>> cannot be viewed, PDF viewer turned off.'],
            '0610' : ['LOG', 'Recorded [<<1>>] rendered pages in the [<<2>>] group.'],
            '0615' : ['ERR', 'XeTeX failed to execute with error: <<1>>'],
            '0617' : ['ERR', 'XeTeX failed to execute with this error: [<<1>>]'],
            '0620' : ['DBG', 'xetex command in <<1>>: <<2>> <<3>>'],
            '0625' : ['MSG', 'Rendering of [<<1>>] successful.'],
            '0630' : ['ERR', 'Rendering [<<1>>] was unsuccessful. <<2>> (<<3>>)'],
            '0635' : ['ERR', 'XeTeX error code [<<1>>] not understood by Rapuma.'],
            '0650' : ['ERR', 'Component type [<<1>>] not supported!'],
            '0690' : ['MSG', 'Dependent files unchanged, rerendering of [<<1>>] un-necessary.'],
            '0695' : ['MSG', 'Routing <<1>> to PDF viewer.'],
            '0700' : ['ERR', 'Rendered file not found: <<1>>'],
            '0710' : ['WRN', 'PDF viewing is disabled.'],
            '0720' : ['MSG', 'Saved rendered file to: [<<1>>]'],
            '0730' : ['ERR', 'Failed to save rendered file to: [<<1>>]'],

            '1000' : ['WRN', 'XeTeX debugging is set to [<<1>>]. These are the paths XeTeX is seeing: [<<2>>]'],
            '1090' : ['ERR', 'Invalid value [<<1>>] used for XeTeX debugging. Must use an integer of 0, 1, 2, 4, 8, 16, or 32']

        }

        # FIXME: It would be good if we could do a check for dependent files here


###############################################################################
############################ Manager Level Functions ##########################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################

    def checkStartPageNumber (self) :
        '''Adjust page number for the current group. The current logic is
        if there is no number in the startPageNumber setting, we can put
        one in there as a suggestion. If there is already one there, the
        user will be responsible for seeing that it is correct.'''

#        import pdb; pdb.set_trace()

        try :
            # Simply try to return anything that is in the field
            cStrPgNo = self.projectConfig['Groups'][self.gid]['startPageNumber']
            if cStrPgNo != '' :
                return cStrPgNo
        except :
            # If nothing is there, we'll make a suggestion
            pGrp = str(self.projectConfig['Groups'][self.gid]['precedingGroup'])
            if pGrp == 'None' :
                self.projectConfig['Groups'][self.gid]['startPageNumber'] = 1
                self.tools.writeConfFile(self.projectConfig)
                return '1'
            else :
                # Calculate the suggested number based on the preceeding group
                try :
                    cStrPgNo    = str(self.projectConfig['Groups'][self.gid]['startPageNumber'])
                except :
                    cStrPgNo    = 1
                    self.projectConfig['Groups'][self.gid]['startPageNumber'] = 1
                try :
                    pGrpPgs     = int(self.projectConfig['Groups'][pGrp]['totalPages'])
                    pGrpStrPgNo = int(self.projectConfig['Groups'][pGrp]['startPageNumber'])
                except :
                    # FIXME: Maybe this could go out and find out exactly how many pages were in the preceeding group
                    pGrpPgs     = 1
                    pGrpStrPgNo = 1
                    self.projectConfig['Groups'][pGrp]['totalPages'] = 1
                    self.projectConfig['Groups'][pGrp]['startPageNumber'] = 1
                # Whether this is right or wrong set it the way it is
                self.projectConfig['Groups'][self.gid]['startPageNumber'] = (pGrpStrPgNo + pGrpPgs)
                self.tools.writeConfFile(self.projectConfig)
                return self.projectConfig['Groups'][pGrp]['startPageNumber']


    def makeExtFile (self, fileName, description) :
        '''Generic function to create an extension file if one does not already exist.'''

        if not os.path.exists(fileName) :
            with codecs.open(fileName, "w", encoding='utf_8') as writeObject :
                writeObject.write(self.tools.makeFileHeader(fileName, description, False))
            self.log.writeToLog(self.errorCodes['1040'], [self.tools.fName(fileName)])
            return True


    def makeCmpExtTexFileOn (self, fileName) :
        '''Create a component TeX extention macro "on" file for a specified component. A matching "off"
        file will be created as well.'''

        description = 'This is a component (on) TeX macro extension file which may override any macros \
        which were loaded for this rendering process. This file is read just before the component \
        working file. After the component is rendered, the accompanying off TeX file will be \
        loaded which will turn off any modified macro commands that this TeX file has set. The \
        user must edit this file in order for it to work right.'

        return self.makeExtFile(fileName, description)


    def makeCmpExtTexFileOff (self, fileName) :
        '''Create a component TeX extention macro "off" file for a specified component. This is to
        match the "on" file that was created.'''

        description = 'This is a component (off) style extension file which overrides the settings \
        that were loaded for this rendering process just prior to loading the component working \
        file. The commands in this style file will off-set the "on" settings causing the macro to \
        render as it did before the "on" styles were loaded. The user must edit this file for it \
        to work properly.'

        return self.makeExtFile(fileName, description)


    def makeCmpExtStyFileOn (self, fileName) :
        '''Create a component style extentions "on" file for a specified component. A matching "off"
        file will be created as well.'''

        description = 'This is a component (on) style extension file which overrides any settings \
        which were loaded for this rendering process. This file is read just before the component \
        working file. After the component is rendered, the accompanying off style file will be \
        loaded which will turn off any modified style commands that this style file has set. The \
        user must edit this file in order for it to work right.'

        return self.makeExtFile(fileName, description)


    def makeCmpExtStyFileOff (self, fileName) :
        '''Create a component style extentions "off" file for a specified component. This is to
        match the "on" file that was created.'''

        description = 'This is a component (off) style extension file which overrides the settings \
        that were loaded for this rendering process just prior to loading the component working \
        file. The commands in this style file will off-set the "on" settings causing the macro to \
        render as it did before the "on" styles were loaded. The user must edit this file for it \
        to work properly.'

        return self.makeExtFile(fileName, description)


    def makeGrpExtTexFile (self) :
        '''Create a group TeX extentions file for a specified group.'''

        description = 'This is the group TeX extention macro file which overrides settings in \
        the global TeX extension macro file.'

        return self.makeExtFile(self.local.grpExtTexFile, description)


    def makeGrpExtStyFile (self) :
        '''Create a group Style extentions file to a specified group.'''

        description = 'This is the group style extention file which overrides settings in \
        the main default component extentions settings style file.'

        return self.makeExtFile(self.local.grpExtStyFile, description)


###############################################################################
############################# DEPENDENCY FUNCTIONS ############################
###############################################################################
######################## Error Code Block Series = 0400 #######################
###############################################################################


    def makeSettingsTexFile (self) :
        '''Create the primary TeX settings file.'''

#        import pdb; pdb.set_trace()

        description = 'This is the primary TeX settings file for the ' + self.gid + ' group. \
        It is auto-generated so editing can be a rather futile exercise. This is unless you \
        set freezeTexSettings to True in the XeTeX manager configuration of the project.conf \
        file. Doing that will prevent the file from being remade. However, no configuration \
        changes will be reflected in the static settings file. Use this with care.'

        # Setting for internal testing
        outputTest = False

        # Check for freezeTexSettings in project.conf
        if self.projectConfig['Managers'][self.cType + '_Xetex'].has_key('freezeTexSettings') and \
                self.tools.str2bool(self.projectConfig['Managers'][self.cType + '_Xetex']['freezeTexSettings']) :
            self.log.writeToLog(self.errorCodes['0420'])
            return False

        def appendLine(line, realVal) :
            '''Use this to shorten the code and look for listy things.'''
            if type(line) == list :
                for s in line :
                    linesOut.append(self.proj_config.processNestedPlaceholders(s, realVal))
            else :
                linesOut.append(self.proj_config.processNestedPlaceholders(line, realVal))

        # Open a fresh settings file
        with codecs.open(self.local.macSettingsFile, "w", encoding='utf_8') as writeObject :
            writeObject.write(self.tools.makeFileHeader(self.local.macSettingsFileName, description))
            # Build a dictionary from the default XML settings file
            # Create a dict that contains only the data we need here
            macPackDict = self.tools.xmlFileToDict(self.local.macPackConfXmlFile)

            for sections in macPackDict['root']['section'] :
                for section in sections :
                    secItem = sections[section]
                    linesOut = []
                    if type(secItem) is list :
                        if outputTest :
                            print sections['sectionID']
                        linesOut.append('% ' + sections['sectionID'].upper())
                        for setting in secItem :
                            for k in setting.keys() :
                                if k == 'texCode' :
                                    if outputTest :
                                        print '\t', setting['key']
                                    realVal = self.macroConfig['Macros'][self.macPackId][sections['sectionID']][setting['key']]
                                    # Test any boolDepends that this setting might have
                                    if setting.has_key('boolDepend') :
                                        result = []
                                        if type(setting['boolDepend']) == list :
                                            for i in setting['boolDepend'] :
                                                result.append(self.affirm(i))
                                        else :
                                            result.append(self.affirm(setting['boolDepend']))
                                        # If 'None' didn't end up in the list, that means
                                        # every bool tested good so we can output the line
                                        if None not in result :
                                            if outputTest :
                                                print '\t', setting.get(k)
                                            appendLine(setting['texCode'], realVal)
                                    # Normal setting output
                                    elif setting.get(k) :
                                        if setting.get(k) != None :
                                            # We filter out zero values here (But what if we need one of them?)
                                            if not self.proj_config.processNestedPlaceholders(realVal) == '0' :
                                                if outputTest :
                                                    print '\t', setting.get(k)
                                                appendLine(setting['texCode'], realVal)

                    # Only write out sections that have something in them
                    if len(linesOut) > 1 :
                        writeObject.write('\n')
                        for line in linesOut :
                            writeObject.write(line + '\n')


            # Continue here with injecting the font settings which are guided by
            # the config file because the XML source(s) could vary
            writeObject.write('\n% INSTALLED FONTS\n')
            installedFonts = self.fontConfig['Fonts'].keys()
            cTypeFont = self.projectConfig['CompTypes'][self.cType.capitalize()]['fontName']
            for font in installedFonts :
                if font == cTypeFont :
                    # Output the primary font
                    for key in self.fontConfig['Fonts'][font]['TexMapping']['PrimaryFont'].keys() :
                        writeObject.write(self.proj_config.processNestedPlaceholders(self.fontConfig['Fonts'][font]['TexMapping']['PrimaryFont'][key]) + '\n')
                    # Output the seconday settings as well for this font
                    for key in self.fontConfig['Fonts'][font]['TexMapping']['SecondaryFont'].keys() :
                        writeObject.write(self.proj_config.processNestedPlaceholders(self.fontConfig['Fonts'][font]['TexMapping']['SecondaryFont'][key]) + '\n')
                else :
                    # There can only be one primary font, this is not it
                    for key in self.fontConfig['Fonts'][font]['TexMapping']['SecondaryFont'].keys() :
                        writeObject.write(self.proj_config.processNestedPlaceholders(self.fontConfig['Fonts'][font]['TexMapping']['SecondaryFont'][key]) + '\n')

                writeObject.write('\n')

            # Die here if testing
            if outputTest :
                self.tools.dieNow()
            # Report finished if not
            return True


    def affirm (self, boolDependInfo) :
        '''Affirm by returning True if the actual bool matches its
        state setting. Returning 'None' will cause a setting to be skipped.'''


        realBool = self.returnConfRefValue(boolDependInfo['#text']).lower()
        if boolDependInfo['@state'].lower() == realBool.lower() :
            return True


    def returnConfRefValue (self, ref) :
        '''Return the value of a given config reference. The ref syntax is
        as follows: [config:configObj|section|key]. This should be able to
        recuse as deep as necessary.'''

#        import pdb; pdb.set_trace()

        ref = ref.lstrip('[').rstrip(']')
        (holderType, holderKey) = ref.split(':', 1)
        if holderType.lower() == 'config' :
            val = holderKey.split('|')
            dct = ['self.' + val[0]]
            val.remove(val[0])
            for i in val :
                i = self.proj_config.processNestedPlaceholders(i, '')
                dct.append('["' + i + '"]')

            return eval(''.join(dct))


    def makeGidTexFile (self, cidList) :
        '''Create the main gid TeX control file.'''

        description = 'This is the group TeX control file. XeTeX will \
            read this file to get all of links to other instructions (macros) \
            needed to render the group, or a component of a group.'

        # Since a render run could contain any number of components
        # in any order, we will remake this file on every run. No need
        # for dependency checking
        if os.path.exists(self.local.gidTexFile) :
            os.remove(self.local.gidTexFile)

        # Create the main TeX settings file (made on every run)
        self.makeSettingsTexFile()

        # Start writing out the gid.tex file. Check/make dependencies as we go.
        # If we fail to make a dependency it will die and report during that process.
        # We bring in each element in the order necessary
        with codecs.open(self.local.gidTexFile, "w", encoding='utf_8') as gidTexObject :
            # Write out the file header
            gidTexObject.write(self.tools.makeFileHeader(self.local.gidTexFileName, description))
            # First bring in the main macro file
            gidTexObject.write('\\input \"' + self.local.primaryMacroFile + '\"\n')
            # Check for a preStyle extension file and load if it is there
            if os.path.exists(self.local.preStyTexExtFile) :
                gidTexObject.write('\\input \"' + self.local.preStyTexExtFile + '\"\n')
            ########
            # FIXME? To avoid problems with the usfmTex marginalverses macro code, we bring
            # in the stylesheets now. Will this cause any problems with other macPacks?
            ########
            # Load style files (default and extention come with the package)
            gidTexObject.write('\\stylesheet{' + self.local.defaultStyFile + '}\n')
            # Load the global style extensions
            gidTexObject.write('\\stylesheet{' + self.local.glbExtStyFile + '}\n')
            # Load the group style extensions (if needed)
            if self.projectConfig['Groups'][self.gid].has_key('useGrpStyOverride') and self.tools.str2bool(self.projectConfig['Groups'][self.gid]['useGrpStyOverride']) :
                self.makeGrpExtStyFile()
                gidTexObject.write('\\stylesheet{' + self.local.grpExtStyFile + '}\n')
            # Load the settings (usfmTex: if marginalverses, load code in this)
            gidTexObject.write('\\input \"' + self.local.macSettingsFile + '\"\n')
            # Load the TeX macro extensions for this macro package
            gidTexObject.write('\\input \"' + self.local.extTexFile + '\"\n')
            # Load the group TeX macro extensions (if needed)
            if self.projectConfig['Groups'][self.gid].has_key('useGrpTexOverride') and self.tools.str2bool(self.projectConfig['Groups'][self.gid]['useGrpTexOverride']) :
                self.makeGrpExtTexFile()
                gidTexObject.write('\\input \"' + self.local.grpExtTexFile + '\"\n')
            # Load hyphenation data if needed
            if self.useHyphenation :
                # This is the main hyphenation settings file, this must be loaded first
                gidTexObject.write('\\input \"' + self.proj_hyphenation.projHyphSetTexFile + '\"\n')
                # This is the character definition file for hyphenation, this should be loaded second
                gidTexObject.write('\\input \"' + self.proj_hyphenation.projHyphCharTexFile + '\"\n')
                # This is the exception words list (all the hyphenated words), this is loaded last
                gidTexObject.write('\\input \"' + self.proj_hyphenation.projHyphExcTexFile + '\"\n')
            # If this is less than a full group render, just go with default pg num (1)
            if cidList == self.projectConfig['Groups'][self.gid]['cidList'] :
                # Check if this setting is there
                startPageNumber = self.checkStartPageNumber()
                if startPageNumber > 1 :
                    gidTexObject.write('\\pageno = ' + str(startPageNumber) + '\n')
            # Insert Document properties and x1a compliant info if needed
            gidTexObject.write(self.makeXoneACompliant())
            # Now add in each of the components
            for cid in cidList :
                # Output files and commands for usfm cType
                if self.cType == 'usfm' :
                    cidSource       = os.path.join(self.local.projComponentFolder, cid, self.project.groups[self.gid].makeFileNameWithExt(cid))
                    cidTexFileOn    = os.path.join(self.local.projTexFolder, self.gid + '-' + cid + '-On-ext.tex')
                    cidTexFileOff   = os.path.join(self.local.projTexFolder, self.gid + '-' + cid + '-Off-ext.tex')
                    cidStyFileOn    = os.path.join(self.local.projStyleFolder, self.gid + '-' + cid + '-On-ext.sty')
                    cidStyFileOff   = os.path.join(self.local.projStyleFolder, self.gid + '-' + cid + '-Off-ext.sty')
                    # Check to see if a TeX macro override is needed
                    if self.projectConfig['Groups'][self.gid].has_key('compTexOverrideList') and cid in self.projectConfig['Groups'][self.gid]['compTexOverrideList'] :
                        self.makeCmpExtTexFileOn(cidTexFileOn)
                        gidTexObject.write('\\input \"' + cidTexFileOn + '\"\n')
                    # Check to see if a style override is needed (if so create "on" file)
                    if self.projectConfig['Groups'][self.gid].has_key('compStyOverrideList') and cid in self.projectConfig['Groups'][self.gid]['compStyOverrideList'] :
                        self.makeCmpExtStyFileOn(cidStyFileOn)
                        gidTexObject.write('\\stylesheet{' + cidStyFileOn + '}\n')
                    # Check for short books add omit statement
                    if self.chapNumOffSingChap and self.cidChapNumDict[cid] == 1 :
                        gidTexObject.write('\\OmitChapterNumbertrue\n') 
                    # Add the working file here
                    gidTexObject.write('\\ptxfile{' + cidSource + '}\n')
                    # Check again for short books turn off omit statement
                    if self.chapNumOffSingChap and self.cidChapNumDict[cid] == 1 :
                        gidTexObject.write('\\OmitChapterNumberfalse\n') 
                    # Check for for style override and add the "Off" style file here
                    if self.projectConfig['Groups'][self.gid].has_key('compStyOverrideList') and cid in self.projectConfig['Groups'][self.gid]['compStyOverrideList'] :
                        self.makeCmpExtStyFileOn(cidStyFileOff)
                        gidTexObject.write('\\stylesheet{' + cidStyFileOff + '}\n')
                    # Check for for TeX macro override and add the "Off" TeX file here
                    if self.projectConfig['Groups'][self.gid].has_key('compTexOverrideList') and cid in self.projectConfig['Groups'][self.gid]['compTexOverrideList'] :
                        self.makeCmpExtTexFileOff(cidTexFileOff)
                        gidTexObject.write('\\input \"' + cidTexFileOff + '\"\n')
                else :
                    self.log.writeToLog(self.errorCodes['0650'], [self.cType])

            # This can only hapen once in the whole process, this marks the end
            gidTexObject.write('\\bye\n')

        return True


    def makeXoneACompliant (self) :
        '''Insert the necessary TeX code into the header to give the
        appearance of being PDF x1-a compliant. If the feature is turned
        off then it will only inject relevant document properties that
        are good to have included no mater what. XeTeX output is x1-a
        for the most part, it just doesn't brag about it. The output
        here mostly works. :-) '''

#        import pdb; pdb.set_trace()
        
        allLines = ''
        # Set some of the vars for the output
        title = self.projectConfig['ProjectInfo']['projectTitle']
        subject = self.projectConfig['ProjectInfo']['projectDescription']
        author = ''.join(self.projectConfig['ProjectInfo']['translators'])
        creator = ''.join(self.projectConfig['ProjectInfo']['typesetters'])
        # I don't think this next bit is not right, what does +7 mean anyway?
        # It works for CDT time anyway, which I thought was -6
        offSet = "+07\'00\'"
        # To get the date stamp right, we strip out all the non-number
        # characters so we are left with: yyyymmddhhmmss
        comp = self.projectConfig['ProjectInfo']['projectCreateDate'].replace('-', '').replace(':', '').replace(' ', '')
        cDate = 'D:' + comp + offSet
        mDate = 'D:' + self.tools.fullFileTimeStamp() + offSet
        lines = [   
                    '\special{pdf:docinfo<<',
                    '/Title(' + title + ')%',
                    '/Subject(' + subject + ')%',
                    '/Author(' + author + ')%',
                    '/Creator(' + creator + ')%',
                    '/CreationDate(' + cDate + ')%',
                    '/ModDate(' + mDate + ')%',
                    '/Producer(XeTeX with Rapuma)%',
                    '/Trapped /False',
                    '/GTS_PDFXVersion(PDF/X-1:2003)%',
                    '/GTS_PDFXConformance(PDF/X-1a:2003)%',
                    '>> }'
                ]
        # Add PDF header declairations for PDF X1-A:2003 compliance (default is True)
        if self.tools.str2bool(self.layoutConfig['DocumentFeatures']['pdfX1a']) :
            icc = os.path.join(self.local.rapumaConfigFolder, 'ps_cmyk.icc')
            # Now create the insert line list
            xtralines =  [   '\special{pdf:fstream @OBJCVR (' + icc + ')}',
                                '\special{pdf:put @OBJCVR <</N 4>>}',
                                '%\special{pdf:close @OBJCVR}',
                                '\special{pdf:docview <<',
                                '/OutputIntents [ <<',
                                '/Type/OutputIndent',
                                '/S/GTS_PDFX',
                                '/OutputCondition (An Unknown print device)',
                                '/OutputConditionIdentifier (Custom)',
                                '/DestOutputProfile @OBJCVR',
                                '/RegistryName (http://www.color.og)',
                                '>> ] >>}'
                        ]
            lines = lines + xtralines

        # Whatever our output, process the lines
        for l in lines : 
            allLines = allLines + l + ' \n'

        return allLines


###############################################################################
################################# Main Function ###############################
###############################################################################
######################## Error Code Block Series = 0600 #######################
###############################################################################

    def run (self, gid, cidList, pgRange, override, save) :
        '''This will check all the dependencies for a group and then
        use XeTeX to render the whole group or a subset of components
        and even a page range in a single component.'''

#        import pdb; pdb.set_trace()

        # There must be a cidList. If one was not passed, default to
        # the group list
        cidListSubFileName      = ''
        saveFile                = ''
        saveFileName            = ''
        if not cidList :
            cidList = self.projectConfig['Groups'][gid]['cidList']
        else :
            # If there is a cidList, create an alternate ouput name.
            # This is so if the file is saved it will have a unique
            # name. the name needs to be ordered by ###-cid-gid.
            # We need to do this sooner than later.
            if len(cidList) > 1 :
                cidListSubFileName = '-'.join(cidList)
            else :
                cid = cidList[0]
                # Add a filler character to the ID
                cnid = "{:0>3}".format(self.cidPtIdDict[cid])
                cidListSubFileName = cnid + '-' + cid

        # Create, if necessary, the gid.tex file
        # First, go through and make/update any dependency files
        self.makeSettingsTexFile()
        # Now make the gid main setting file
        self.makeGidTexFile(cidList)
        # Dynamically create a dependency list for the render process
        # Note: gidTexFile is remade on every run, do not test against that file
        dep = [self.local.extTexFile, self.local.projectConfFile, self.local.layoutConfFile, 
                self.local.macroConfFile, self.local.illustrationConfFile, ]
        # Add component dependency files
        for cid in cidList :
            cidUsfm = self.project.groups[gid].getCidPath(cid)
            cidIlls = self.proj_illustration.getCidPiclistFile(cid)
            for f in [cidUsfm, cidIlls] :
                if os.path.exists(f) :
                    dep.append(f)
            # Treat adjustment file separate
            if self.cType == 'usfm' :
                cidAdj = self.project.groups[gid].getCidAdjPath(cid)
                if os.path.exists(cidAdj) :
                    dep.append(cidAdj)

        # Call the renderer
        # Create the environment that XeTeX will use. This will be temporarily set
        # by subprocess.call() just before XeTeX is run.
        texInputsLine = self.project.local.projHome + ':' \
                        + self.local.projStyleFolder + ':' \
                        + self.local.projTexFolder + ':' \
                        + self.local.projMacPackFolder + ':' \
                        + self.local.projMacroFolder + ':' \
                        + self.local.projGidFolder + ':.'

        # Create the environment dictionary that will be fed into subprocess.call()
        #envDict = dict(os.environ)
        envDict={}
        # These are project environment vars
        envDict['TEXINPUTS'] = texInputsLine
        # These are XeTeX environment vars that are run if the internal (fast) version
        # of XeTeX is being run, which is the default. If runExternalXetex is set to
        # False, the following special environment vars will be run. If set to true,
        # an external version of XeTeX, provided it is installed, will run with its own
        # environment vars set elsewhere
        runExternal = self.tools.str2bool(self.projectConfig['Managers'][self.cType + '_Xetex'].get('runExternalXetex', ''))
        if not runExternal :
            envDict['PATH'] = os.path.join(self.local.rapumaXetexFolder, 'bin', 'x86_64-linux')
            envDict['TEXMFCNF'] = os.path.join(self.local.rapumaXetexFolder, 'texmf-local', 'web2c')
            envDict['TEXFORMATS'] = os.path.join(self.local.rapumaXetexFolder, 'texmf-local', 'web2c', 'xetex')
            # To help with debugging the following hook has been added. This is not
            # something the user would ever use. It is only for developer diagnostics.
            # for infomation on what integers can be used refer to this URL:
            # http://www.dcs.ed.ac.uk/home/latex/Informatics/Obsolete/html/kpathsea/kpathsea.html
            debugXetex = self.projectConfig['Managers'][self.cType + '_Xetex'].get('debugKpse', None)
            if debugXetex :
                try :
                    if int(debugXetex) > 0 :
                        envDict['KPATHSEA_DEBUG'] = debugXetex
                        self.log.writeToLog(self.errorCodes['1000'], [str(debugXetex), str(envDict)])
                except :
                    self.log.writeToLog(self.errorCodes['1090'], [debugXetex])
        else :
            envDict.update(os.environ)

        # Create the XeTeX command argument list that subprocess.call() will run with
        # the environment vars we set above
        cmds = ['xetex', '-output-directory=' + self.local.projGidFolder, self.local.gidTexFile]

        # For debugging purposes, output the following DBG message
        if self.projectConfig['Managers'][self.cType + '_Xetex'].has_key('freezeTexSettings') and \
                self.tools.str2bool(self.projectConfig['Managers'][self.cType + '_Xetex']['freezeTexSettings']) :
            self.log.writeToLog(self.errorCodes['0620'], [os.getcwd(), str(envDict), " ".join(cmds)])

        # Run the XeTeX and collect the return code for analysis
        try :
            rCode = subprocess.call(cmds, env = envDict)
            # Analyse the return code
            if rCode == int(0) :
                self.log.writeToLog(self.errorCodes['0625'], [self.local.gidTexFileName])
            elif rCode in self.xetexErrorCodes :
                self.log.writeToLog(self.errorCodes['0630'], [self.local.gidTexFileName, self.xetexErrorCodes[rCode], str(rCode)])
            else :
                self.log.writeToLog(self.errorCodes['0635'], [str(rCode)])
        except Exception as e :
            # If subprocess fails it might be because XeTeX did not execute
            # we will try to report back something useful
            self.log.writeToLog(self.errorCodes['0615'], [str(e)])

        # Collect the page count and record in group (Write out at the end of the opp.)
        self.projectConfig['Groups'][gid]['totalPages'] = str(PdfFileReader(open(self.local.gidPdfFile)).getNumPages())
        # Write out any changes made to the project.conf file that happened during this opp.
        self.tools.writeConfFile(self.projectConfig)

        # Pull out pages if requested (use the same file for output)
        if pgRange :
            self.tools.pdftkPullPages(self.local.gidPdfFile, self.local.gidPdfFile, pgRange)

        # The gidPdfFile is the residue of the last render and if approved, can be
        # used for the binding process. In regard to saving and file naming, the
        # gidPdfFile will be copied but never renamed. It must remain intact.

        # If the user wants to save this file or use a custom name, do that now
        if save and not override :
            saveFileName = self.pid + '_' + gid
            if cidListSubFileName :
                saveFileName = saveFileName + '_' + cidListSubFileName
            if pgRange :
                saveFileName = saveFileName + '_pg(' + pgRange + ')'
            # Add date stamp
            saveFileName = saveFileName + '_' + self.tools.ymd()
            # Add render file extention
            saveFileName = saveFileName + '.pdf'
            # Save this to the Deliverable folder (Make sure there is one)
            if not os.path.isdir(self.local.projDeliverableFolder) :
                os.makedirs(self.local.projDeliverableFolder)
            # Final file name and path
            saveFile = os.path.join(self.local.projDeliverableFolder, saveFileName)
            # Copy, no news is good news
            if shutil.copy(self.local.gidPdfFile, saveFile) :
                self.log.writeToLog(self.errorCodes['0730'], [saveFileName])
            else :
                self.log.writeToLog(self.errorCodes['0720'], [saveFileName])            

        # If given, the override file name becomes the file name 
        if override :
            saveFile = override
            # With shutil.copy(), no news is good news
            if shutil.copy(self.local.gidPdfFile, saveFile) :
                self.log.writeToLog(self.errorCodes['0730'], [saveFileName])
            else :
                self.log.writeToLog(self.errorCodes['0720'], [saveFileName])

        # Once we know the file is successfully generated, add a background if defined
        viewFile = ''
        if self.useBackground :
            if saveFile :
                viewFile = self.pg_back.addBackground(saveFile)
            else :
                viewFile = self.pg_back.addBackground(self.local.gidPdfFile)
                
        # Add a timestamp and doc info if requested in addition to background
        if self.useDocInfo :
            if saveFile :
                if os.path.isfile(viewFile) :
                    viewFile = self.pg_back.addDocInfo(viewFile)
                else :
                    viewFile = self.pg_back.addDocInfo(saveFile)
            else :
                if os.path.isfile(viewFile) :
                    viewFile = self.pg_back.addDocInfo(viewFile)
                else :
                    viewFile = self.pg_back.addDocInfo(self.local.gidPdfFile)

        # Add a diagnostic layer to the rendered output. Normally this is
        # not used with a normal background layer
        if self.useDiagnostic :
            if saveFile :
                viewFile = self.fmt_diagnose.addTransparency(saveFile)
            else :
                viewFile = self.fmt_diagnose.addTransparency(self.local.gidPdfFile)

        # To avoid confusion with file names, if this is a saved file,
        # and it has a background, we need to remove the original, non-
        # background file (remembering originals are kept in the group
        # Component folder), then rename the -view version to whatever
        # the saved name should be
        if save or override :
            if os.path.isfile(saveFile) and os.path.isfile(viewFile) :
                # First remove
                os.remove(saveFile)
                # Next rename
                os.rename(viewFile, saveFile)

        ##### Viewing #####
        # First get the right file name to view
        if saveFile :
            # If there was a saveFile, that will be the viewFile
            viewFile = saveFile
        else :
            # The view file in this case is just temporary
            if not os.path.isfile(viewFile) :
                viewFile = self.local.gidPdfFile.replace(gid + '.pdf', gid + '-view.pdf')
                shutil.copy(self.local.gidPdfFile, viewFile)

        # Now view it
        if os.path.isfile(viewFile) :
            if self.pdfViewerCmd :
                # Add the file to the viewer command
                self.pdfViewerCmd.append(viewFile)
                # Run the XeTeX and collect the return code for analysis
                try :
                    subprocess.Popen(self.pdfViewerCmd)
                    return True
                except Exception as e :
                    # If we don't succeed, we should probably quite here
                    self.log.writeToLog(self.errorCodes['1005'], [str(e)])
            else :
                self.log.writeToLog(self.errorCodes['0710'])
        else :
            self.log.writeToLog(self.errorCodes['0700'], [self.tools.fName(viewFile)])
            
        # If we made it this far, return True
        return True


