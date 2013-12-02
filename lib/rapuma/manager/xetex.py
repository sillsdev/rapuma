#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

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

# Load the local classes
from rapuma.core.tools                  import Tools
from rapuma.manager.manager             import Manager
from rapuma.core.paratext               import Paratext
from rapuma.project.proj_config         import Config
from rapuma.project.proj_maps           import ProjMaps
from rapuma.project.proj_toc            import ProjToc
from rapuma.project.proj_background     import ProjBackground
from rapuma.project.proj_hyphenation    import ProjHyphenation
from rapuma.project.proj_illustration   import ProjIllustration
from rapuma.group.usfmTex               import UsfmTex


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
        self.pt_tools               = Paratext(self.pid, self.gid)
        self.pg_back                = ProjBackground(self.pid, self.gid)
        self.proj_config            = Config(self.pid, self.gid)
        self.proj_config.getProjectConfig()
        self.proj_config.getLayoutConfig()
        # Bring in some manager objects we will need
        self.proj_hyphenation       = ProjHyphenation(self.pid, self.gid)
        self.proj_illustration      = ProjIllustration(self.pid, self.gid)
        # Get config objs
        self.projectConfig          = self.proj_config.projectConfig
        self.layoutConfig           = self.proj_config.layoutConfig
        self.userConfig             = self.project.userConfig
        self.macPack                = None
        self.macPackConfig          = None
        if self.projectConfig['CompTypes'][self.Ctype].has_key('macroPackage') and self.projectConfig['CompTypes'][self.Ctype]['macroPackage'] != '' :
            self.macPack            = self.projectConfig['CompTypes'][self.Ctype]['macroPackage']
            self.proj_config.getMacPackConfig(self.macPack)
            self.proj_config.loadMacPackFunctions(self.macPack)
            self.macPackConfig      = self.proj_config.macPackConfig
            self.macPackFunctions   = self.proj_config.macPackFunctions
        # Some config settings
        self.pdfViewerCmd           = self.project.userConfig['System']['pdfViewerCommand']
        self.pdfUtilityCmd          = self.project.userConfig['System']['pdfUtilityCommand']
        self.sourceEditor           = self.projectConfig['CompTypes'][self.Ctype]['sourceEditor']
        self.macroPackage           = self.projectConfig['CompTypes'][self.Ctype]['macroPackage']

        # Get settings for this component
        self.managerSettings = self.projectConfig['Managers'][self.manager]
        for k, v in self.managerSettings.iteritems() :
            if v == 'True' or v == 'False' :
                setattr(self, k, self.tools.str2bool(v))
            else :
                setattr(self, k, v)

        # Set some Booleans (this comes after persistant values are set)
        self.useHyphenation         = self.proj_hyphenation.useHyphenation
        self.chapNumOffSingChap     = self.tools.str2bool(self.macPackConfig['ChapterVerse']['omitChapterNumberOnSingleChapterBook'])

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

            'XTEX-000' : ['MSG', 'XeTeX module messages'],
            'XTEX-005' : ['TOD', 'The ParaTExt SSF file could not be found. Check the project folder to see if it exsits.'],
            'XTEX-010' : ['LOG', 'Version number: [<<1>>], was found. Assumed persistent values have been merged.'],
            'XTEX-015' : ['LOG', 'Version number present, not running persistant values.'],
            'XTEX-020' : ['LOG', 'Wrote out new layout configuration file.'],
            'XTEX-045' : ['TOD', 'File <<1>> is missing. Check the error log for an import error for this required file. The system cannot render without it.'],
            'XTEX-050' : ['ERR', 'USFM working text not found: <<1>>. This is required in order to render.'],
            'XTEX-055' : ['ERR', 'make<<1>>() failed to properly create: <<2>>. This is a required file in order to render.'],
            'XTEX-080' : ['LOG', 'There has been a change in [<<1>>], [<<2>>] needs to be rerendered.'],
            'XTEX-085' : ['MSG', 'The file: <<1>> was not found, XeTeX will now try to render it.'],
            'XTEX-110' : ['MSG', 'The file <<1>> was removed so it could be rerendered.'],
            'XTEX-120' : ['ERR', 'Global style file [<<1>>] is missing! This is a required file that should have been installed with the component. We have to stop here, sorry about that.'],

            '1005' : ['ERR', 'PDF viewer failed with error: [<<1>>]'],
            '1010' : ['ERR', 'Style file [<<1>>] could not be created.'],
            '1040' : ['LOG', 'Created: [<<1>>]'],


            '0420' : ['WRN', 'TeX settings file has been frozen for debugging purposes.'],
            '0430' : ['LOG', 'TeX hyphenation dependent file [<<1>>] has been recreated.'],
            '0440' : ['LOG', 'Created: [<<1>>]'],
            '0460' : ['LOG', 'Settings changed in [<<1>>], [<<2>>] needed to be recreated.'],
            '0465' : ['LOG', 'File: [<<1>>] missing, created a new one.'],
            '0470' : ['ERR', 'Macro package [<<1>>] is not recognized by the system.'],
            '0480' : ['ERR', 'Cannot create critical hyphenation file: [<<1>>]'],

            '0600' : ['MSG', '<<1>> cannot be viewed, PDF viewer turned off.'],
            '0610' : ['LOG', 'Recorded [<<1>>] rendered pages in the [<<2>>] group.'],
            '0615' : ['ERR', 'XeTeX failed to execute with error: <<1>>'],
            '0617' : ['ERR', 'XeTeX failed to execute with this error: [<<1>>]'],
            '0620' : ['DBG', 'xetex command in <<1>>: <<2>> <<3>>'],
            '0625' : ['MSG', 'Rendering of [<<1>>] successful.'],
            '0630' : ['ERR', 'Rendering [<<1>>] was unsuccessful. <<2>> (<<3>>)'],
            '0635' : ['ERR', 'XeTeX error code [<<1>>] not understood by Rapuma.'],
            '0640' : ['ERR', 'Failed to add background to [<<1>>]. Ended with error: [<<2>>]'],
            '0645' : ['LOG', 'Successfully added watermark to [<<1>>].'],
            '0650' : ['ERR', 'Component type [<<1>>] not supported!'],
            '0665' : ['LOG', 'Successfully added [<<1>>] background to [<<2>>].'],
            '0670' : ['LOG', 'Successfully rendered [<<1>>] group for binding.'],
            '0690' : ['MSG', 'Dependent files unchanged, rerendering of [<<1>>] un-necessary.'],
            '0695' : ['MSG', 'Routing <<1>> to PDF viewer.'],
            '0700' : ['ERR', 'Rendered file not found: <<1>>'],
            '0710' : ['WRN', 'PDF viewing is disabled.'],

        }


###############################################################################
############################ Manager Level Functions ##########################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################

    def displayPdfOutput (self, fileName) :
        '''Display a PDF XeTeX output file if that is turned on.'''

#        import pdb; pdb.set_trace()

        # Add the file to the viewer command
        self.pdfViewerCmd.append(fileName)
        # Run the XeTeX and collect the return code for analysis
        try :
            subprocess.Popen(self.pdfViewerCmd)
            return True
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.log.writeToLog(self.errorCodes['1005'], [str(e)])


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


    def makeGrpHyphExcTexFile (self) :
        '''Create a TeX hyphenation file. There must be a texWordList for this
        to work properly.'''

        description = 'This is an auto-generated hyphenation exceptions word list for this group. \
             Please refer to the documentation for details on how to make changes.'

        # Try to get dependent files in place
        if not os.path.isfile(self.local.compHyphFile) :
            # Call the Hyphenation manager to create a sorted file of hyphenated words
            # We will not use force (set to False) for this.
            self.proj_hyphenation.updateHyphenation(False)

        # Create the output file here
        with codecs.open(self.grpHyphExcTexFile, "w", encoding='utf_8') as hyphenTexObject :
            hyphenTexObject.write(self.tools.makeFileHeader(self.tools.fName(self.grpHyphExcTexFile), description))
            hyphenTexObject.write('\hyphenation{\n')
            with codecs.open(self.local.compHyphFile, "r", encoding='utf_8') as hyphenWords :
                for word in hyphenWords :
                    # Strip out commented lines/words
                    if word[:1] != '#' and word != '' :
                        # Swap the generic hyphen markers out if they are there
                        hyphenTexObject.write(re.sub(u'<->', u'-', word))

            hyphenTexObject.write('}\n')

        return True


    def makeLccodeTexFile (self) :
        '''Make a simple starter lccode file to be used with TeX hyphenation.'''

        description = 'This is an auto-generated lccode rules file for this project. \
            Please refer to the documentation for details on how to make changes.'

        # Create the file and put default settings in it
        with codecs.open(self.local.lccodeTexFile, "w", encoding='utf_8') as lccodeObject :
            lccodeObject.write(self.tools.makeFileHeader(self.local.lccodeTexFileName, description))
            lccodeObject.write('\lccode "2011 = "2011	% Allow TeX hyphenation to ignore a Non-break hyphen\n')
            # Add in all our non-word-forming characters as found in our PT project
            for c in self.pt_tools.getNWFChars() :
                uv = self.tools.rtnUnicodeValue(c)
                # We handel these chars special in this context
                if not uv in ['2011', '002D'] :
                    lccodeObject.write('\lccode "' + uv + ' = "' + uv + '\n')

            # Add special exceptions
            lccodeObject.write('\catcode "2011 = 11	% Changing the catcode here allows the \lccode above to work\n')

        return True


###############################################################################
############################# DEPENDENCY FUNCTIONS ############################
###############################################################################
######################## Error Code Block Series = 0400 #######################
###############################################################################


    def makeSettingsTexFile (self) :
        '''Create the primary TeX settings file.'''

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
                                    realVal = self.macPackConfig[sections['sectionID']][setting['key']]
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
            installedFonts = self.macPackConfig['Fonts'].keys()
            primaryFont = self.macPackConfig['FontSettings']['primaryFont']
            for font in installedFonts :
                if font == primaryFont :
                    # Output the primary font
                    for key in self.macPackConfig['Fonts'][font]['TexMapping']['PrimaryFont'].keys() :
                        writeObject.write(self.proj_config.processNestedPlaceholders(self.macPackConfig['Fonts'][font]['TexMapping']['PrimaryFont'][key]) + '\n')
                    # Output the seconday settings as well for this font
                    for key in self.macPackConfig['Fonts'][font]['TexMapping']['SecondaryFont'].keys() :
                        writeObject.write(self.proj_config.processNestedPlaceholders(self.macPackConfig['Fonts'][font]['TexMapping']['SecondaryFont'][key]) + '\n')
                if not font == primaryFont :
                    # There can only be one primary font, this is not it
                    for key in self.macPackConfig['Fonts'][font]['TexMapping']['SecondaryFont'].keys() :
                        writeObject.write(self.proj_config.processNestedPlaceholders(self.macPackConfig['Fonts'][font]['TexMapping']['SecondaryFont'][key]) + '\n')

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


#        try :
#            realBool = str(self.returnConfRefValue(boolDependInfo['#text']))
#            print realBool, type(realBool)
#            if boolDependInfo['@state'].lower() == realBool.lower() :
#                return True
#        except Exception as e :
#            print str(e)
#            print boolDependInfo
#            print type(self.returnConfRefValue(boolDependInfo['#text']))
#            print type(boolDependInfo['@state'])
#            print type(boolDependInfo)
#            self.tools.dieNow()



    def returnConfRefValue (self, ref) :
        '''Return the value of a given config reference. The ref syntax is
        as follows: [config:configObj|section|key]. This should be able to
        recuse as deep as necessary.'''

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

        # Get some cid info we will need below
        cidInfo = self.pt_tools.usfmCidInfo()

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
                gidTexObject.write('\\input \"' + self.local.lccodeTexFile + '\"\n')
                gidTexObject.write('\\input \"' + self.local.grpHyphExcTexFile + '\"\n')
            # If this is less than a full group render, just go with default pg num (1)
            if cidList == self.projectConfig['Groups'][self.gid]['cidList'] :
                startPageNumber = int(self.projectConfig['Groups'][self.gid]['startPageNumber'])
                if startPageNumber > 1 :
                    gidTexObject.write('\\pageno = ' + str(startPageNumber) + '\n')
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
                    if self.chapNumOffSingChap and cidInfo[cid][3] == 1 :
                        gidTexObject.write('\\OmitChapterNumbertrue\n') 
                    # Add the working file here
                    gidTexObject.write('\\ptxfile{' + cidSource + '}\n')
                    # Check again for short books turn off omit statement
                    if self.chapNumOffSingChap and cidInfo[cid][3] == 1 :
                        gidTexObject.write('\\OmitChapterNumberfalse\n') 
                    # Check for for style override and add the "Off" style file here
                    if self.projectConfig['Groups'][self.gid].has_key('compStyOverrideList') and cid in self.projectConfig['Groups'][self.gid]['compStyOverrideList'] :
                        self.makeCmpExtStyFileOn(cidStyFileOff)
                        gidTexObject.write('\\stylesheet{' + cidStyFileOff + '}\n')
                    # Check for for TeX macro override and add the "Off" TeX file here
                    if self.projectConfig['Groups'][self.gid].has_key('compTexOverrideList') and cid in self.projectConfig['Groups'][self.gid]['compTexOverrideList'] :
                        self.makeCmpExtTexFileOff(cidTexFileOff)
                        gidTexObject.write('\\input \"' + cidTexFileOff + '\"\n')
                # Output files and commands for map cType
                elif self.cType == 'map' :
                    gidTexObject.write('\\ptxfile{' + ProjMaps(self.pid, self.gid).getGidContainerFile() + '}\n')
                # Output files and commands for toc cType
                elif self.cType == 'toc' :
                    gidTexObject.write('\\ptxfile{' + ProjToc(self.pid, self.gid).getGidContainerFile() + '}\n')
                else :
                    self.log.writeToLog(self.errorCodes['0650'], [self.cType])
            # This can only hapen once in the whole process, this marks the end
            gidTexObject.write('\\bye\n')

        return True


    def checkGrpHyphExcTexFile (self) :
        '''If hyphenation is used, check for the exsistance of the group TeX Hyphenation 
        exception file. If not found, kindly ask the appropreate function to make it.'''

        if self.useHyphenation :
            # The TeX group hyphen exceptions file
            if not os.path.isfile(self.local.grpHyphExcTexFile) or self.tools.isOlder(self.local.grpHyphExcTexFile, self.local.compHyphFile) :
                if self.makeGrpHyphExcTexFile() :
                    self.log.writeToLog(self.errorCodes['0430'], [self.local.grpHyphExcTexFileName])
                else :
                    # If we can't make it, we return False
                    self.log.writeToLog(self.errorCodes['0480'], [self.local.grpHyphExcTexFile])
                    return False
            # The TeX lccode file
            if not os.path.exists(self.local.lccodeTexFile) or self.tools.isOlder(self.local.lccodeTexFile, self.local.grpHyphExcTexFile) :
                if self.makeLccodeTexFile() :
                    self.log.writeToLog(self.errorCodes['0430'], [self.local.lccodeTexFileName])
                else :
                    # If we can't make it, we return False
                    self.log.writeToLog(self.errorCodes['0480'], [self.local.lccodeTexFileName])
                    return False
            return True
        else :
            # If Hyphenation is turned off, we return True and don't need to worry about it.
            return True


###############################################################################
################################# Main Function ###############################
###############################################################################
######################## Error Code Block Series = 0600 #######################
###############################################################################


    def run (self, gid, mode, cidList, pgRange, override) :
        '''This will check all the dependencies for a group and then
        use XeTeX to render it.'''

#        import pdb; pdb.set_trace()

        # Get our list of cids
        # Check for cidList, use std group if it isn't there
        # If there is a cidList, create an alternate ouput name.
        # The file name needs to be ordered by ###-cid-gid.
        pdfSubFileName = ''
        if cidList :
            cid = cidList[0]
            cidInfo = self.pt_tools.usfmCidInfo()
            cnid = "{:03}".format(int(cidInfo[cid][2]))
            pdfSubFileName = cnid + '-' + '-'.join(cidList) + '-' + gid + '.pdf'
        else :
            cidList = self.projectConfig['Groups'][gid]['cidList']

        # Background management (Phase one)
        # Much of the backgound handeling happens after rendering but
        # if cropmarks are desired, they must be turned on before the
        # document is rendered. We turn that on here before and turn
        # it off below when backgounds are being added.
        if 'cropmarks' in self.projectConfig['Managers'][self.manager][mode + 'Background'] :
            if not self.tools.str2bool(self.macPackConfig['PageLayout']['useCropmarks']) :
                # Note that the value is set as a string because internally 
                # incoming bool values are assumed to be strings a real boolean
                # value will really throw a wrench in the works
                self.macPackConfig['PageLayout']['useCropmarks'] = 'True'
                # This is more of an internal value change so it will
                # not be written out 

        # Create, if necessary, the gid.tex file
        # First, go through and make/update any dependency files
        self.makeSettingsTexFile()
        self.checkGrpHyphExcTexFile()
        # Now make the gid main setting file
        self.makeGidTexFile(cidList)
        # Dynamically create a dependency list for the render process
        # Note: gidTexFile is remade on every run, do not test against that file
        dep = [self.local.extTexFile, self.local.projectConfFile, self.local.layoutConfFile, 
                self.local.macPackConfFile, self.local.illustrationConfFile, ]
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

        # Render if gidPdf is older or is missing
        render = False
        if not os.path.isfile(self.local.gidPdfFile) :
            render = True
        else :
            for d in dep :
                if self.tools.isOlder(self.local.gidPdfFile, d) :
                    render = True
                    break

        # Call the renderer
        if render :
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
            if not self.projectConfig['Managers'][self.cType + '_Xetex'].has_key('runExternalXetex') or \
                    not self.tools.str2bool(self.projectConfig['Managers'][self.cType + '_Xetex']['runExternalXetex']) :
                envDict['PATH'] = os.path.join(self.local.rapumaXetexFolder, 'bin')
                envDict['TEXMFCNF'] = os.path.join(self.local.rapumaXetexFolder, 'texmf-local', 'web2c')
                envDict['TEXFORMATS'] = os.path.join(self.local.rapumaXetexFolder, 'texmf-local', 'web2c', 'xetex')
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

            # Background management (Phase 2)
            bgList = self.projectConfig['Managers'][self.manager][mode + 'Background']
            for bg in bgList :
                # Special handling for cropmarks happened before rendering
                # To clean up, turn off cropmarks here because it is done already
                if bg == 'cropmarks' :
                    if self.tools.str2bool(self.macPackConfig['PageLayout']['useCropmarks']) :
                        # Note that the value is set as a string because internally 
                        # incoming bool values are assumed to be strings a real boolean
                        # value will really throw a wrench in the works
                        self.macPackConfig['PageLayout']['useCropmarks'] = 'False'
                    continue
                bgFile = os.path.join(self.local.projIllustrationFolder, bg + '.pdf')
                cmd = self.pdfUtilityCmd + [self.local.gidPdfFile, 'background', bgFile, 'output', self.tools.tempName(self.local.gidPdfFile)]
                try :
                    subprocess.call(cmd)
                    shutil.copy(self.tools.tempName(self.local.gidPdfFile), self.local.gidPdfFile)
                    os.remove(self.tools.tempName(self.local.gidPdfFile))
                    self.log.writeToLog(self.errorCodes['0665'], [self.tools.fName(bgFile), self.tools.fName(self.local.gidPdfFile)])
                except Exception as e :
                    # If we don't succeed, we should probably quite here
                    self.log.writeToLog(self.errorCodes['0640'], [self.local.gidPdfFile, str(e)])

            # Collect the page count and record in group
            newPages = self.tools.pdftkTotalPages(self.local.gidPdfFile)
            if self.projectConfig['Groups'][gid].has_key('totalPages') :
                oldPages = int(self.projectConfig['Groups'][gid]['totalPages'])
                if oldPages != newPages or oldPages == 'None' :
                    self.projectConfig['Groups'][gid]['totalPages'] = newPages
                    self.tools.writeConfFile(self.projectConfig)
                    self.log.writeToLog(self.errorCodes['0610'], [str(newPages),gid])
            else :
                self.projectConfig['Groups'][gid]['totalPages'] = newPages
                self.tools.writeConfFile(self.projectConfig)
                self.log.writeToLog(self.errorCodes['0610'], [str(newPages),gid])

            # If we are in bind mode we will finish up here
            if mode == 'bind' :
                self.log.writeToLog(self.errorCodes['0670'], [gid])
                return True
        else :
            self.log.writeToLog(self.errorCodes['0690'], [self.local.gidPdfFileName])

        # Move to the output folder according to mode for easier access
        if os.path.isfile(self.local.gidPdfFile) :
            # For override requests just use that
            if override :
                outputPdfFile = override
            # Otherwise, for normal output build the name and location
            else :
                outputFolder = os.path.join(self.local.projHome, mode.capitalize())
                if pdfSubFileName :
                    outputPdfFile = self.tools.modeFileName(outputFolder, pdfSubFileName, mode, pgRange)
                else :
                    outputPdfFile = self.tools.modeFileName(outputFolder, self.local.gidPdfFile, mode, pgRange)
                # Make sure there is a folder there to put it in
                if not os.path.exists(outputFolder) :
                    os.makedirs(outputFolder)

            # Pull out pages if requested (use the same file for output)
            if pgRange :
                self.tools.pdftkPullPages(self.local.gidPdfFile, self.local.gidPdfFile, pgRange)

            # Deliver to final target folder
            if os.path.exists(self.local.gidPdfFile) :
                shutil.move(self.local.gidPdfFile, outputPdfFile)

#        import pdb; pdb.set_trace()

        # Review the results if desired
        if os.path.isfile(outputPdfFile) :
            if not len(self.pdfViewerCmd) == 0 :
                if self.displayPdfOutput(outputPdfFile) :
                    self.log.writeToLog(self.errorCodes['0695'], [self.tools.fName(outputPdfFile)])
                else :
                    self.log.writeToLog(self.errorCodes['0600'], [self.tools.fName(outputPdfFile)])
            else :
                self.log.writeToLog(self.errorCodes['0710'])
        else :
            self.log.writeToLog(self.errorCodes['0700'], [self.tools.fName(outputPdfFile)])

        return True


