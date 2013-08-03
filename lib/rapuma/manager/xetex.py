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
from rapuma.project.proj_config         import ProjConfig
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
        self.proj_config            = ProjConfig(self.pid, self.gid)
        # Bring in some manager objects we will need
        self.proj_hyphenation       = ProjHyphenation(self.pid, self.gid)
        self.proj_illustration      = ProjIllustration(self.pid, self.gid)
        # Get config objs
        self.projConfig             = self.proj_config.projConfig
        self.layoutConfig           = self.proj_config.layoutConfig
        self.userConfig             = self.project.userConfig
        self.macPackConfig          = self.proj_config.macPackConfig
        # Load the macPackDict for finding out all default information like file names
        self.macPackFunctions       = UsfmTex(self.layoutConfig)
        for k, v in self.proj_config.macPackFilesDict.iteritems() :
            setattr(self, k, v)
        # Some config settings
        self.pdfViewer              = self.projConfig['Managers'][self.manager]['pdfViewerCommand']
        self.pdfUtilityCommand      = self.projConfig['Managers'][self.manager]['pdfUtilityCommand']
        self.sourceEditor           = self.projConfig['CompTypes'][self.Ctype]['sourceEditor']
        self.macroPackage           = self.projConfig['CompTypes'][self.Ctype]['macroPackage']

        # Get settings for this component
        self.managerSettings = self.projConfig['Managers'][self.manager]
        for k, v in self.managerSettings.iteritems() :
            if v == 'True' or v == 'False' :
                setattr(self, k, self.tools.str2bool(v))
            else :
                setattr(self, k, v)

        # Set some Booleans (this comes after persistant values are set)
        self.usePdfViewer           = self.tools.str2bool(self.projConfig['Managers'][self.manager]['usePdfViewer'])
        self.useHyphenation         = self.proj_hyphenation.useHyphenation
        self.chapNumOffSingChap     = self.tools.str2bool(self.macPackConfig['ChapterVerse']['omitChapterNumberOnSingleChapterBook'])

        # Add the file refs that are specific to the macPack
        for k, v in self.proj_config.macPackFilesDict.iteritems() :
            setattr(self, k, v)
#            print k, ' =', getattr(self, k, v)

        # Folder paths
        self.rapumaConfigFolder     = self.local.rapumaConfigFolder
        self.projConfFolder         = self.local.projConfFolder
        self.projComponentsFolder   = self.local.projComponentsFolder
        self.projDeliverablesFolder = self.local.projDeliverablesFolder
        self.gidFolder              = os.path.join(self.projComponentsFolder, self.gid)
        self.projHyphenationFolder  = self.local.projHyphenationFolder
        self.projIllustrationsFolder= self.local.projIllustrationsFolder
        self.projFontsFolder        = self.local.projFontsFolder
        self.projMacrosFolder       = self.local.projMacrosFolder
        self.projStylesFolder       = self.local.projStylesFolder
        self.projTexFolder          = self.local.projTexFolder
        self.projMacPackFolder      = os.path.join(self.projMacrosFolder, self.macroPackage)
        # Set file names with full path 
        self.projConfFile           = self.proj_config.projConfFile
        self.layoutConfFile         = self.proj_config.layoutConfFile

        self.illustrationConfFile   = self.proj_config.illustrationConfFile
        self.macPackConfFile        = self.proj_config.macPackConfFile

        # Make any dependent folders if needed
        if not os.path.isdir(self.gidFolder) :
            os.mkdir(self.gidFolder)

        # Check to see if the PDF support is ready to go
        if not self.pdfViewer :
            self.pdfViewer = self.project.userConfig['System']['pdfDefaultViewerCommand']
            self.projConfig['Managers'][self.manager]['pdfViewerCommand'] = self.pdfViewer
            self.tools.writeConfFile(self.projConfig)
        if not self.pdfUtilityCommand :
            self.pdfUtilityCommand = self.project.userConfig['System']['pdfDefaultUtilityCommand']
            self.projConfig['Managers'][self.manager]['pdfUtilityCommand'] = self.pdfUtilityCommand
            self.tools.writeConfFile(self.projConfig)

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


            '0430' : ['LOG', 'TeX hyphenation dependent file [<<1>>] has been recreated.'],
            '0440' : ['LOG', 'Created: [<<1>>]'],
            '0460' : ['LOG', 'Settings changed in [<<1>>], [<<2>>] needed to be recreated.'],
            '0465' : ['LOG', 'File: [<<1>>] missing, created a new one.'],
            '0470' : ['ERR', 'Macro package [<<1>>] is not recognized by the system.'],
            '0480' : ['ERR', 'Cannot create critical hyphenation file: [<<1>>]'],

            '0600' : ['MSG', '<<1>> cannot be viewed, PDF viewer turned off.'],
            '0610' : ['LOG', 'Recorded [<<1>>] rendered pages in the [<<2>>] group.'],
            '0625' : ['MSG', 'Rendering of [<<1>>] successful.'],
            '0630' : ['ERR', 'Rendering [<<1>>] was unsuccessful. <<2>> (<<3>>)'],
            '0635' : ['ERR', 'XeTeX error code [<<1>>] not understood by Rapuma.'],
            '0640' : ['ERR', 'Failed to add background to [<<1>>]. Ended with error: [<<2>>]'],
            '0645' : ['LOG', 'Successfully added watermark to [<<1>>].'],
            '0650' : ['ERR', 'Component type [<<1>>] not supported!'],
            '0665' : ['LOG', 'Successfully added lines background to [<<1>>].'],
            '0670' : ['LOG', 'Successfully rendered [<<1>>] group for binding.'],
            '0690' : ['MSG', 'Dependent files unchanged, rerendering of [<<1>>] un-necessary.'],
            '0695' : ['MSG', 'Routing <<1>> to PDF viewer.'],

        }


###############################################################################
############################ Manager Level Functions ##########################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################

    def displayPdfOutput (self, fileName) :
        '''Display a PDF XeTeX output file if that is turned on.'''

#        import pdb; pdb.set_trace()

        if self.usePdfViewer :
            # Add the file to the viewer command
            self.pdfViewer.append(fileName)
            # Run the XeTeX and collect the return code for analysis
            try :
                subprocess.Popen(self.pdfViewer)
                return True
            except Exception as e :
                # If we don't succeed, we should probably quite here
                self.log.writeToLog(self.errorCodes['1005'], [str(e)])


    def makeGrpExtStyFile (self) :
        '''Create a group Style extentions file to a specified group.'''

        description = 'This is the group style extention file which overrides settings in \
        the main default component extentions settings style file.'

        # Create a blank file (only if there is none)
        if not os.path.exists(self.grpExtStyFile) :
            with codecs.open(self.grpExtStyFile, "w", encoding='utf_8') as writeObject :
                writeObject.write(self.tools.makeFileHeader(self.tools.fName(self.grpExtStyFile), description, False))
            self.log.writeToLog(self.errorCodes['1040'], [self.tools.fName(self.grpExtStyFile)])

        # Need to return true here even if nothing was done
        return True


    def makeGrpHyphExcTexFile (self) :
        '''Create a TeX hyphenation file. There must be a texWordList for this
        to work properly.'''

        description = 'This is an auto-generated hyphenation exceptions word list for this group. \
             Please refer to the documentation for details on how to make changes.'

        # Try to get dependent files in place
        if not os.path.isfile(self.compHyphFile) :
            # Call the Hyphenation manager to create a sorted file of hyphenated words
            # We will not use force (set to False) for this.
            self.proj_hyphenation.updateHyphenation(False)

        # Create the output file here
        with codecs.open(self.grpHyphExcTexFile, "w", encoding='utf_8') as hyphenTexObject :
            hyphenTexObject.write(self.tools.makeFileHeader(self.tools.fName(self.grpHyphExcTexFile), description))
            hyphenTexObject.write('\hyphenation{\n')
            with codecs.open(self.compHyphFile, "r", encoding='utf_8') as hyphenWords :
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
        with codecs.open(self.lccodeTexFile, "w", encoding='utf_8') as lccodeObject :
            lccodeObject.write(self.tools.makeFileHeader(self.tools.fName(self.lccodeTexFile), description))
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
######################## Error Code Block Series = 400 ########################
###############################################################################


    def makeSettingsTexFile (self) :
        '''Create the primary TeX settings file.'''

        description = 'This is the primary TeX settings file for the ' + self.gid + ' group. \
        It is auto-generated so editing can be a rather futile exercise.'

        # Setting for internal testing
        outputTest = False

        def appendLine(line, realVal) :
            '''Use this to shorten the code and look for listy things.'''
            if type(line) == list :
                for s in line :
                    linesOut.append(self.proj_config.processNestedPlaceholders(s, realVal))
            else :
                linesOut.append(self.proj_config.processNestedPlaceholders(line, realVal))

        # Open a fresh settings file
        with codecs.open(self.macSettingsFile, "w", encoding='utf_8') as writeObject :
            writeObject.write(self.tools.makeFileHeader(self.tools.fName(self.macSettingsFile), description))
            # Build a dictionary from the default XML settings file
            # Create a dict that contains only the data we need here
            for sections in self.proj_config.macPackDict['root']['section'] :
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
            for font in installedFonts :
                for key in self.macPackConfig['Fonts'][font]['TexMapping']['PrimaryFont'].keys() :
                    writeObject.write(self.proj_config.processNestedPlaceholders(self.macPackConfig['Fonts'][font]['TexMapping']['PrimaryFont'][key]) + '\n')
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
        if boolDependInfo['@state'].lower() == realBool :
            return True


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


    def makeGrpExtTexFile (self) :
        '''Create/copy a group TeX extentions file to the project for specified group.'''

        description = 'This is the group extention file which overrides settings in \
        the main TeX settings files and the component TeX settings.'

        # First look for a user file, if not, then make a blank one
        if not os.path.isfile(self.grpExtTexFile) :
            with codecs.open(self.grpExtTexFile, "w", encoding='utf_8') as writeObject :
                writeObject.write(self.tools.makeFileHeader(self.tools.fName(self.grpExtTexFile), description, False))
            self.log.writeToLog(self.errorCodes['0440'], [self.tools.fName(self.grpExtTexFile)])

            # Need to return true here even if nothing was done
            return True


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
        if os.path.exists(self.gidTexFile) :
            os.remove(self.gidTexFile)

        # Create (if needed) dependent files
        self.makeSettingsTexFile()
        self.makeGrpExtTexFile()
        self.makeGrpExtStyFile()

        # Start writing out the gid.tex file. Check/make dependencies as we go.
        # If we fail to make a dependency it will die and report during that process.
        # We bring in each element in the order necessary
        with codecs.open(self.gidTexFile, "w", encoding='utf_8') as gidTexObject :
            # Write out the file header
            gidTexObject.write(self.tools.makeFileHeader(self.tools.fName(self.gidTexFile), description))
            # First bring in the main macro file
            gidTexObject.write('\\input \"' + self.primaryMacroFile + '\"\n')
            # Load the settings
            gidTexObject.write('\\input \"' + self.macSettingsFile + '\"\n')
            # Load the settings extensions
            gidTexObject.write('\\input \"' + self.extTexFile + '\"\n')
            # Load the group settings extensions
            gidTexObject.write('\\input \"' + self.grpExtTexFile + '\"\n')
            # Load hyphenation data if needed
            if self.useHyphenation :
                gidTexObject.write('\\input \"' + self.lccodeTexFile + '\"\n')
                gidTexObject.write('\\input \"' + self.grpHyphExcTexFile + '\"\n')
            # Load style files (default and extention come with the package)
            gidTexObject.write('\\stylesheet{' + self.defaultStyFile + '}\n')
            # Load the global style extensions
            gidTexObject.write('\\stylesheet{' + self.glbExtStyFile + '}\n')
            # Load the group style extensions
            gidTexObject.write('\\stylesheet{' + self.grpExtStyFile + '}\n')
            # If this is less than a full group render, just go with default pg num (1)
            if cidList == self.projConfig['Groups'][self.gid]['cidList'] :
                startPageNumber = int(self.projConfig['Groups'][self.gid]['startPageNumber'])
                if startPageNumber > 1 :
                    gidTexObject.write('\\pageno = ' + str(startPageNumber) + '\n')
            # Now add in each of the components
            for cid in cidList :
                if self.cType == 'usfm' :
                    cidSource = os.path.join(self.projComponentsFolder, cid, self.project.groups[self.gid].makeFileNameWithExt(cid))
                    if self.chapNumOffSingChap and cidInfo[cid][3] == 1 :
                        gidTexObject.write('\\OmitChapterNumbertrue\n') 
                        gidTexObject.write('\\ptxfile{' + cidSource + '}\n')
                        gidTexObject.write('\\OmitChapterNumberfalse\n') 
                    else :
                        gidTexObject.write('\\ptxfile{' + cidSource + '}\n')
                elif self.cType == 'map' :
                    gidTexObject.write('\\ptxfile{' + ProjMaps(self.pid, self.gid).getGidContainerFile() + '}\n')
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
            if not os.path.isfile(self.grpHyphExcTexFile) or self.tools.isOlder(self.grpHyphExcTexFile, self.compHyphFile) :
                if self.makeGrpHyphExcTexFile() :
                    self.log.writeToLog(self.errorCodes['0430'], [self.tools.fName(self.grpHyphExcTexFile)])
                else :
                    # If we can't make it, we return False
                    self.log.writeToLog(self.errorCodes['0480'], [self.tools.fName(self.grpHyphExcTexFile)])
                    return False
            # The TeX lccode file
            if not os.path.exists(self.lccodeTexFile) or self.tools.isOlder(self.lccodeTexFile, self.grpHyphExcTexFile) :
                if self.makeLccodeTexFile() :
                    self.log.writeToLog(self.errorCodes['0430'], [self.tools.fName(self.lccodeTexFile)])
                else :
                    # If we can't make it, we return False
                    self.log.writeToLog(self.errorCodes['0480'], [self.tools.fName(self.lccodeTexFile)])
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


    def run (self, gid, mode, cidList, force) :
        '''This will check all the dependencies for a group and then
        use XeTeX to render it.'''

        # Get our list of cids
        # Check for cidList, use std group if it isn't there
        # If there is a cidList, create an alternate ouput name
        pdfSubFileName = ''
        if cidList :
            pdfSubFileName = gid + '-' + '-'.join(cidList) + '.pdf'
        else :
            cidList = self.projConfig['Groups'][gid]['cidList']

        # Background management (Phase one)
        # Much of the backgound handeling happens after rendering but
        # if cropmarks are desired, they must be turned on before the
        # document is rendered. We turn that on here before and turn
        # it off below when backgounds are being added.
        if 'cropmarks' in self.projConfig['Managers'][self.manager][mode + 'Background'] :
            if not self.tools.str2bool(self.layoutConfig['PageLayout']['useCropmarks']) :
                self.layoutConfig['PageLayout']['useCropmarks'] = True
                self.tools.writeConfFile(self.layoutConfig)

        # This is the file we will make. If force is set, delete the old one.
        if force :
            if os.path.isfile(self.gidPdfFile) :
                os.remove(self.gidPdfFile)

        # Create, if necessary, the gid.tex file
        # First, go through and make/update any dependency files
#        self.makeMacLinkFile()
        self.makeSettingsTexFile()
        self.checkGrpHyphExcTexFile()
        # Now make the gid main setting file
        self.makeGidTexFile(cidList)
        # Dynamically create a dependency list for the render process
        # Note: gidTexFile is remade on every run, do not test against that file
        dep = [self.extTexFile, self.projConfFile, self.layoutConfFile, 
                self.macPackConfFile, self.illustrationConfFile, ]
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
        if not os.path.isfile(self.gidPdfFile) :
            render = True
        else :
            for d in dep :
                if self.tools.isOlder(self.gidPdfFile, d) :
                    render = True
                    break

        # Call the renderer
        if render :
            # Create the environment that XeTeX will use. This will be temporarily set
            # by subprocess.call() just before XeTeX is run.
            texInputsLine = self.project.local.projHome + ':' \
                            + self.projStylesFolder + ':' \
                            + self.projTexFolder + ':' \
                            + self.projMacPackFolder + ':' \
                            + self.projMacrosFolder + ':' \
                            + self.gidFolder + ':.'

            # Create the environment dictionary that will be fed into subprocess.call()
            envDict = dict(os.environ)
            envDict['TEXINPUTS'] = texInputsLine

            # Create the XeTeX command argument list that subprocess.call()
            # will run with
            cmds = ['xetex', '-output-directory=' + self.gidFolder, self.gidTexFile]

            # Run the XeTeX and collect the return code for analysis
#                self.tools.dieNow()
            rCode = subprocess.call(cmds, env = envDict)

            # Analyse the return code
            if rCode == int(0) :
                self.log.writeToLog(self.errorCodes['0625'], [self.tools.fName(self.gidTexFile)])
            elif rCode in self.xetexErrorCodes :
                self.log.writeToLog(self.errorCodes['0630'], [self.tools.fName(self.gidTexFile), self.xetexErrorCodes[rCode], str(rCode)])
            else :
                self.log.writeToLog(self.errorCodes['0635'], [str(rCode)])

            # Background management (Phase 2)
            bgList = self.projConfig['Managers'][self.manager][mode + 'Background']
            for bg in bgList :
                # Special handling for cropmarks happened before rendering
                # Turn off cropmarks here because it is done already
                if bg == 'cropmarks' :
                    if self.tools.str2bool(self.layoutConfig['PageLayout']['useCropmarks']) :
                        self.layoutConfig['PageLayout']['useCropmarks'] = False
                        self.tools.writeConfFile(self.layoutConfig)
                    continue
                bgFile = os.path.join(self.projIllustrationsFolder, bg + '.pdf')
                cmd = self.pdfUtilityCommand + [self.gidPdfFile, 'background', bgFile, 'output', self.tools.tempName(self.gidPdfFile)]
                try :
                    subprocess.call(cmd)
                    shutil.copy(self.tools.tempName(self.gidPdfFile), self.gidPdfFile)
                    os.remove(self.tools.tempName(self.gidPdfFile))
                    self.log.writeToLog(self.errorCodes['0665'])
                except Exception as e :
                    # If we don't succeed, we should probably quite here
                    self.log.writeToLog(self.errorCodes['0640'], [self.gidPdfFile, str(e)])

            # Collect the page count and record in group
            newPages = self.tools.getPdfPages(self.gidPdfFile)
            if self.projConfig['Groups'][gid].has_key('totalPages') :
                oldPages = int(self.projConfig['Groups'][gid]['totalPages'])
                if oldPages != newPages or oldPages == 'None' :
                    self.projConfig['Groups'][gid]['totalPages'] = newPages
                    self.tools.writeConfFile(self.projConfig)
                    self.log.writeToLog(self.errorCodes['0610'], [str(newPages),gid])
            else :
                self.projConfig['Groups'][gid]['totalPages'] = newPages
                self.tools.writeConfFile(self.projConfig)
                self.log.writeToLog(self.errorCodes['0610'], [str(newPages),gid])

            # If we are in bind mode we will finish up here
            if mode == 'bind' :
                self.log.writeToLog(self.errorCodes['0670'], [gid])
                return True
        else :
            self.log.writeToLog(self.errorCodes['0690'], [self.tools.fName(self.gidPdfFile)])

        # Move to the Deliverables folder for easier access
        if os.path.isfile(self.gidPdfFile) :
            if pdfSubFileName :
                deliverablePdfFile = self.tools.modeFileName(os.path.join(self.projDeliverablesFolder, pdfSubFileName), mode)
            else :
                deliverablePdfFile = self.tools.modeFileName(os.path.join(self.projDeliverablesFolder, self.tools.fName(self.gidPdfFile)), mode)

            shutil.move(self.gidPdfFile, deliverablePdfFile)

        # Review the results if desired
        if os.path.isfile(deliverablePdfFile) :
            if self.displayPdfOutput(deliverablePdfFile) :
                self.log.writeToLog(self.errorCodes['0695'], [self.tools.fName(deliverablePdfFile)])
            else :
                self.log.writeToLog(self.errorCodes['0600'], [self.tools.fName(deliverablePdfFile)])

        return True


