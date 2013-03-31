#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class handles USFM component type tasks for book projects.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, dircache, unicodedata
from configobj import ConfigObj, Section
from functools import partial

# Load the local classes
from rapuma.core.tools import *
#from rapuma.component.component import Component
from rapuma.group.group import Group
import palaso.sfm as sfm
from palaso.sfm import usfm, style, element, text


###############################################################################
################################## Begin Class ################################
###############################################################################

# As we load the module we will bring in all the common information about all the
# components this type will handle.



class Usfm (Group) :
    '''This class contains information about a type of component 
    used in a type of project.'''

    # Shared values
    xmlConfFile     = 'usfm.xml'

    def __init__(self, project, cfg) :
        super(Usfm, self).__init__(project, cfg)

        # Set values for this manager
        self.project                = project
        self.projConfig             = project.projConfig
        self.local                  = project.local
        self.log                    = project.log
        self.cfg                    = cfg
        self.gid                    = project.gid
        self.cType                  = 'usfm'
        self.Ctype                  = self.cType.capitalize()
        self.mType                  = project.projectMediaIDCode
        self.renderer               = project.projConfig['CompTypes'][self.Ctype]['renderer']
        self.sourceEditor           = project.projConfig['CompTypes'][self.Ctype]['sourceEditor']
        # Get the comp settings
        self.compSettings           = project.projConfig['CompTypes'][self.Ctype]

        # Build a tuple of managers this component type needs to use
        self.usfmManagers = ('component', 'text', 'style', 'font', 'layout', 'hyphenation', 'illustration', self.renderer)

        # Init the general managers
        for mType in self.usfmManagers :
            self.project.createManager(self.cType, mType)

        # Create the internal ref names we use in this module
        self.font                   = self.project.managers[self.cType + '_Font']
        self.component              = self.project.managers[self.cType + '_Component']
        self.layout                 = self.project.managers[self.cType + '_Layout']
        self.illustration           = self.project.managers[self.cType + '_Illustration']
        self.text                   = self.project.managers[self.cType + '_Text']
        self.style                  = self.project.managers[self.cType + '_Style']

        # File names
        self.adjustmentConfFile     = project.local.adjustmentConfFile
        # Folder paths
        self.projScriptsFolder      = self.local.projScriptsFolder
        self.projComponentsFolder   = self.local.projComponentsFolder
        self.gidFolder              = os.path.join(self.projComponentsFolder, self.gid)
        # File names with folder paths
        self.rapumaXmlCompConfig    = os.path.join(self.project.local.rapumaConfigFolder, self.xmlConfFile)
        self.grpPreprocessFile      = self.text.grpPreprocessFile

        # Pick up some init settings that come after the managers have been installed
        self.macroPackage           = self.projConfig['Managers'][self.cType + '_' + self.renderer.capitalize()]['macroPackage']
        self.layoutConfig           = self.layout.layoutConfig
        if not os.path.isfile(self.adjustmentConfFile) :
            if self.createProjAdjustmentConfFile() :
                self.log.writeToLog('COMP-240', [fName(self.adjustmentConfFile)])
            else :
                self.updateCompAdjustmentConf()
        # Now get the adj config
        self.adjustmentConfig       = ConfigObj(self.adjustmentConfFile, encoding='utf-8')

        # Get persistant values from the config if there are any
        newSectionSettings = getPersistantSettings(self.projConfig['CompTypes'][self.Ctype], self.rapumaXmlCompConfig)
        if newSectionSettings != self.projConfig['CompTypes'][self.Ctype] :
            self.projConfig['CompTypes'][self.Ctype] = newSectionSettings
        # Set them here
        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)


        # Check if there is a font installed
        if not self.font.varifyFont() :
            # If a PT project, use that font, otherwise, install default
            if self.sourceEditor.lower() == 'paratext' :
                font = self.project.projConfig['Managers'][self.cType + '_Font']['ptDefaultFont']
            else :
                font = 'DefaultFont'

            self.font.installFont(font)

        # Connect to the PT tools class
        self.pt_tools = PT_Tools(self.project)

        # Module Error Codes
        self.errorCodes     = {
            '000' : ['MSG', 'Messages for the USFM module.'],
            '005' : ['MSG', 'Unassigned error message ID.'],
            '010' : ['ERR', 'Could not process character pair. This error was found: [<<1>>]. Process could not complete. - usfm.pt_tools.getNWFChars()'],
            '020' : ['ERR', 'Improper character pair found: [<<1>>].  Process could not complete. - usfm.pt_tools.getNWFChars()'],
            '025' : ['WRN', 'No non-word-forming characters were found in the PT settings file. - usfm.pt_tools.getNWFChars()'],
            '030' : ['WRN', 'Problems found in hyphenation word list. They were reported in [<<1>>].  Process continued but results may not be right. - usfm.pt_tools.checkForBadWords()'],
            '040' : ['ERR', 'Hyphenation source file not found: [<<1>>]. Process halted!'],
            '050' : ['LOG', 'Updated project file: [<<1>>]'],
            '055' : ['LOG', 'Did not update project file: [<<1>>]'],
            '060' : ['MSG', 'Force switch was set. Removed hyphenation source files for update proceedure.'],
            '070' : ['ERR', 'Text validation failed on USFM file: [<<1>>] It reported this error: [<<2>>]'],
            '080' : ['LOG', 'Normalizing Unicode text to the [<<1>>] form.'],
            '090' : ['ERR', 'USFM file: [<<1>>] did NOT pass the validation test. Because of an encoding conversion, the terminal output is from the file [<<2>>]. Please only edit [<<1>>].'],
            '095' : ['WRN', 'Validation for USFM file: [<<1>>] was turned off.'],
            '100' : ['MSG', 'Source file editor [<<1>>] is not recognized by this system. Please double check the name used for the source text editor setting.'],
            '120' : ['ERR', 'Source file: [<<1>>] not found! Cannot copy to project. Process halting now.'],
            '130' : ['ERR', 'Failed to complete preprocessing on component [<<1>>]'],
            '140' : ['MSG', 'Completed installation on [<<1>>] component working text.'],
            '150' : ['ERR', 'Unable to copy [<<1>>] to [<<2>>] - error in text.'],

            '210' : ['ERR', 'Source file name could not be built because the Name Form ID for [<<1>>] is missing or incorrect. Double check to see which editor created the source text.'],
        }

###############################################################################
############################ Functions Begin Here #############################
###############################################################################

    def getCidPath (self, cid) :
        '''Return the full path of the cName working text file. This assumes
        the cid is valid.'''

        return os.path.join(self.local.projComponentsFolder, cid, self.component.makeFileNameWithExt(cid))


    def getCidAdjPath (self, cid) :
        '''Return the full path of the cName working text adjustments file. 
        This assumes the cName is valid.'''

        return os.path.join(self.local.projComponentsFolder, cid, self.component.makeFileName(cid) + '.adj')


    def getCidPiclistPath (self, cid) :
        '''Return the full path of the cName working text illustrations file. 
        This assumes the cName is valid.'''

        return os.path.join(self.local.projComponentsFolder, cid, self.component.makeFileName(cid) + '.piclist')


    def render(self, renderParams) :
        '''Does USFM specific rendering of a USFM component'''

#        import pdb; pdb.set_trace()

        # Preprocess all subcomponents (one or more)
        # Stop if it breaks at any point
        for cid in renderParams['cidList'] :
            if not self.preProcessGroup() :
                return False

        # With everything in place we can render the component and we pass-through
        # the force (render/view) command so the renderer will do the right thing.
        # One problem we try to get around here is that some group params are not
        # in the manager object. We get around that by passing the group object (self)
        # to the renderer run() command. This may not be the best way to do this.
        self.project.managers['usfm_' + self.renderer.capitalize()].run(renderParams)

        return True


    def preProcessGroup (self) :
        '''This will prepare a component group for rendering by checking for
        and/or creating any dependents it needs to render properly.'''

        # Get some relevant settings
        useIllustrations        = str2bool(self.cfg['useIllustrations'])
        useHyphenation          = str2bool(self.cfg['useHyphenation'])
        useWatermark            = str2bool(self.layoutConfig['PageLayout']['useWatermark'])
        useLines                = str2bool(self.layoutConfig['PageLayout']['useLines'])
        usePageBorder           = str2bool(self.layoutConfig['PageLayout']['usePageBorder'])
        useBoxBoarder           = str2bool(self.layoutConfig['PageLayout']['useBoxBoarder'])
        useManualAdjustments    = str2bool(self.projConfig['Groups'][self.gid]['useManualAdjustments'])

        # See if the working text is present for each subcomponent in the
        # component and try to install it if it is not
        for cid in self.cfg['cidList'] :
            cType = self.cfg['cType']
            cidUsfm = self.getCidPath(cid)
            # Create the working text
            if not os.path.isfile(cidUsfm) :
                self.installUsfmWorkingText(self.gid, cid)
            # Add/manage the dependent files for this cid
            if self.macroPackage == 'usfmTex' :
                # Component adjustment file
                cidAdjFile = self.getCidAdjPath(cid)
                if useManualAdjustments :
                    if not os.path.isfile(cidAdjFile) or isOlder(cidAdjFile, self.adjustmentConfFile) :
                        # Remake the adjustment file (if needed)
                        self.createCompAdjustmentFile(cid)
                else :
                    # If no adjustments, remove any exsiting file
                    if os.path.isfile(cidAdjFile) :
                        os.remove(cidAdjFile)
                # Component piclist file
                cidPiclist = self.getCidPiclistPath(cid)
                if useIllustrations :
                    if self.illustration.hasIllustrations(cidCName) :
                        if not os.path.isfile(cidPiclist) :
                            # First check if we have the illustrations we think we need
                            # and get them if we do not.
                            self.illustration.getPics(cid)
                            # Now make a fresh version of the piclist file
                            self.illustration.createPiclistFile(cName, cid)
                            self.log.writeToLog('ILUS-065', [cid])
                        else :
                            for f in [self.local.layoutConfFile, self.local.illustrationConfFile] :
                                if isOlder(cidPiclist, f) or not os.path.isfile(cidPiclist) :
                                    # Remake the piclist file
                                    self.illustration.createPiclistFile(cName, cid)
                                    self.log.writeToLog('ILUS-065', [cid])
                        # Do a quick check to see if the illustration files for this book
                        # are in the project. If it isn't, the run will be killed
                        self.illustration.getPics(cid)
                else :
                    # If we are not using illustrations then any existing piclist file will be removed
                    if os.path.isfile(cidPiclist) :
                        os.remove(cidPiclist)
                        self.log.writeToLog('ILUS-055', [cName])
            else :
                self.log.writeToLog('COMP-220', [self.macroPackage])

        # Be sure there is a watermark file listed in the conf and
        # installed if watermark is turned on (True). Fallback on the
        # the default if needed.
#        if useWatermark :
#            self.illustration.installDefaultWatermarkFile()

        # Same for lines background file used for composition
#        if useLines :
#            self.illustration.installLinesFile()

        # Same for box background file used for composition
#        if useBoxBoarder :
#            self.illustration.installBoxBoarderFile()

        # Any more stuff to run?

        return True


#    def hasAdjustments (self, cType, cid) :
#        '''Check for exsiting adjustments under a book section in
#        the adjustment.conf file. Return True if found.'''

#        try :
#            if self.adjustmentConfig[cType.upper() + ':' + cid.upper()].keys() :
#                return True
#        except  :
#            return False


    def createCompAdjustmentFile (self, cid) :
        '''Create an adjustment file for this cid. If entries exsist in
        the adjustment.conf file.'''

        description = 'Auto-generated text adjustments file for: ' + cid + '\n'

#        import pdb; pdb.set_trace()

#        if self.hasAdjustments(self.cType, cid) :
        # Check for a master adj conf file
        if os.path.exists(self.adjustmentConfFile) :
            adjFile = self.getCidAdjPath(cid)
            for c in self.adjustmentConfig[self.gid].keys() :
                try :
                    if c == 'GeneralSettings' :
                        continue
                    else :
                        comp = c.lower()
                except Exception as e :
                    # If this doesn't work, we should probably quite here
                    dieNow('Error: Malformed component ID [' + c + '] in adjustment file: ' + str(e) + '\n')
                if  comp == cid and len(self.adjustmentConfig[self.gid][c].keys()) > 0 :
                    with codecs.open(adjFile, "w", encoding='utf_8') as writeObject :
                        writeObject.write(makeFileHeader(adjFile, description, True))
                        # Output like this: JAS 1.13 +1
                        for k, v in self.adjustmentConfig[self.gid][c].iteritems() :
                            if k[0] in ['%', '#'] :
                                continue
                            adj = v
                            if int(v) > 0 : 
                                adj = '+' + str(v)
                            writeObject.write(comp.upper() + ' ' + k + ' ' + adj + '\n')

                        self.log.writeToLog('COMP-230', [fName(adjFile)])
            return True


    def createProjAdjustmentConfFile (self) :
        '''Create a project master component adjustment file that group component
        ajustment files will be created automatically from. This will run every 
        time preprocess is run but after the first time it will only add a sections
        for new groups or components.'''

        if not os.path.exists(self.adjustmentConfFile) :
            self.adjustmentConfig = ConfigObj(self.adjustmentConfFile, encoding='utf-8')
            self.adjustmentConfig.filename = self.adjustmentConfFile
            self.updateCompAdjustmentConf()
        return True


    def updateCompAdjustmentConf (self) :
        '''Update an adjustmentConfig based on changes in the projConfig.'''

        for gid in self.projConfig['Groups'].keys() :
            if gid not in self.adjustmentConfig.keys() :
                buildConfSection(self.adjustmentConfig, gid)
            for comp in self.projConfig['Groups'][gid]['cidList'] :
                if not testForSetting(self.adjustmentConfig[gid], comp) :
                    buildConfSection(self.adjustmentConfig[gid], comp)
                self.adjustmentConfig[gid][comp]['%1.1'] = '1'
        writeConfFile(self.adjustmentConfig)
        return True


###############################################################################
######################## USFM Component Text Functions ########################
###############################################################################
######################## Error Code Block Series = 200 ########################
###############################################################################


    def installUsfmWorkingText (self, gid, cid, force = False) :
        '''Find the USFM source text and install it into the working text
        folder of the project with the proper name. If a USFM text file
        is not located in a PT project folder, the editor cannot be set
        to paratext, it must be set to generic. This assumes lock checking
        was done previous to the call.'''

#        import pdb; pdb.set_trace()

        sourcePath = self.project.getGroupSourcePath(gid)
        csid = self.projConfig['Groups'][gid]['csid']

        # Check if there is a font installed
        if not self.font.varifyFont() :
            # If a PT project, use that font, otherwise, install default
            if self.sourceEditor.lower() == 'paratext' :
                font = self.projConfig['Managers'][self.cType + '_Font']['ptDefaultFont']
            else :
                font = 'DefaultFont'

            self.font.installFont(font)

        # Build the file name
        thisFile = ''
        if self.sourceEditor.lower() == 'paratext' :
            thisFile = self.pt_tools.formPTName(gid, cid)
        elif self.sourceEditor.lower() == 'generic' :
            thisFile = self.pt_tools.formGenericName(gid, cid)
        else :
            self.log.writeToLog('USFM-100', [self.sourceEditor])

        # Test, no name = no success
        if not thisFile :
            self.log.writeToLog(self.errorCodes['210'], [cid])
            dieNow()

        # Will need the stylesheet for copy if that has not been added
        # to the project yet, we will do that now
        self.style.checkDefaultStyFile()
        self.style.checkDefaultExtStyFile()

        # Start the process by building paths and file names, if we made it this far.
        # Note the file name for the preprocess is hard coded. This will become a part
        # of the total system and this file will be copied in when the user requests to
        # preprocessing.

        # Current assuption is that source text is located in a directory above the
        # that is the default. In case that is not the case, we can override that and
        # specify a path to the source. If that exists, then we will use that instead.
        if sourcePath :
            source      = os.path.join(sourcePath, thisFile)
        else :
            source      = os.path.join(os.path.dirname(self.local.projHome), thisFile)

        targetFolder    = os.path.join(self.local.projComponentsFolder, cid)
        target          = os.path.join(targetFolder, self.component.makeFileNameWithExt(cid))
        targetSource    = os.path.join(targetFolder, thisFile + '.source')

        # Copy the source to the working text folder. We do not want to do
        # this if the there already is a target and it is newer than the 
        # source text, that would indicate some edits have been done and we
        # do not want to loose the work. However, if it is older that would
        # indicate the source has been updated so unless the folder is locked
        # we will want to update the target.

        # Look for the source now, if not found, fallback on the targetSource
        # backup file. But if that isn't there die.
        if not os.path.isfile(source) :
            if os.path.isfile(targetSource) :
                source = targetSource
            else :
                self.log.writeToLog('USFM-120', [source])
                dieNow()

        # Now do the age checks and copy if source is newer than target
        if force or not os.path.isfile(target) or isOlder(target, source) :

            # Make target folder if needed
            if not os.path.isdir(targetFolder) :
                os.makedirs(targetFolder)

            # Always save an untouched copy of the source and set to
            # read only. We may need this to restore/reset later.
            if os.path.isfile(targetSource) :
                # Don't bother if we copied from it in the first place
                if targetSource != source :
                    # Reset permissions to overwrite
                    makeWriteable(targetSource)
                    shutil.copy(source, targetSource)
                    makeReadOnly(targetSource)
            else :
                shutil.copy(source, targetSource)
                makeReadOnly(targetSource)

            # To be sure nothing happens, copy from our project source
            # backup file. (Is self.style.defaultStyFile the best thing?)
            if self.usfmCopy(targetSource, target, self.style.defaultStyFile) :
                # Run any working text preprocesses on the new component text
                if str2bool(self.projConfig['Groups'][gid]['usePreprocessScript']) :
                    if not os.path.isfile(self.grpPreprocessFile) :
                        self.text.installPreprocess()
                    if not self.text.runProcessScript(target, self.grpPreprocessFile) :
                        self.log.writeToLog('USFM-130', [cid])

                # If this is a USFM component type we need to remove any \fig markers,
                # and record them in the illustration.conf file for later use
                if self.cType == 'usfm' :
                    tempFile = target + '.tmp'
                    contents = codecs.open(target, "rt", encoding="utf_8_sig").read()
                    # logUsfmFigure() logs the fig data and strips it from the working text
                    # Note: Using partial() to allows the passing of the cid param 
                    # into logUsfmFigure()
                    contents = re.sub(r'\\fig\s(.+?)\\fig\*', partial(self.project.groups[gid].logFigure, cid), contents)
                    codecs.open(tempFile, "wt", encoding="utf_8_sig").write(contents)
                    # Finish by copying the tempFile to the source
                    if not shutil.copy(tempFile, target) :
                        # Take out the trash
                        os.remove(tempFile)

                # If the text is there, we should return True so do a last check to see
                if os.path.isfile(target) :
                    self.log.writeToLog('USFM-140', [cid])
                    return True
            else :
                self.log.writeToLog('USFM-150', [source,fName(target)])
                return False
        else :
            return True


    def usfmCopy (self, source, target, projSty = None) :
        '''Copy USFM text from source to target. Decode if necessary, then
        normalize. With the text in place, validate unless that is False.'''

        # Bring in our source text
        if self.text.sourceEncode == self.text.workEncode :
            contents = codecs.open(source, 'rt', 'utf_8_sig')
            lines = contents.read()
        else :
            # Lets try to change the encoding.
            lines = self.text.decodeText(source)

        # Normalize the text
        normal = unicodedata.normalize(self.text.unicodeNormalForm, lines)
        self.log.writeToLog('USFM-080', [self.text.unicodeNormalForm])

        # Write out the text to the target
        writeout = codecs.open(target, "wt", "utf_8_sig")
        writeout.write(normal)
        writeout.close

        # Validate the target USFM text (Defalt is True)
        if str2bool(self.validateUsfm) :
            if not self.usfmTextFileIsValid(target, projSty) :
                self.log.writeToLog('USFM-090', [source,fName(target)])
                return False
        else :
            self.log.writeToLog('USFM-095', [fName(target)])

        return True


    def usfmTextFileIsValid (self, source, projSty) :
        '''Use the USFM parser to validate a style file. For now,
        if a file fails, we'll just quite right away, otherwise,
        return True.'''

        # Note: Error level reporting is possible with the usfm.parser.
        # The following are the errors it can report:
        # Note            = -1    Just give output warning, do not stop
        # Marker          =  0    Stop on any out of place marker
        # Content         =  1    Stop on mal-formed content
        # Structure       =  2    Stop on ???
        # Unrecoverable   =  100  Stop on most anything that is wrong
        # For future reference, the sfm parser will fail if TeX style
        # comment markers "%" are used to comment text rather than "#".

        try :
            fh = codecs.open(source, 'rt', 'utf_8_sig')
            stylesheet = usfm.default_stylesheet.copy()
            if projSty :
                stylesheet_extra = style.parse(open(os.path.expanduser(projSty),'r'))
                stylesheet.update(stylesheet_extra)
            doc = usfm.parser(fh, stylesheet, error_level=sfm.level.Structure)
            # With the doc text loaded up, we run a list across it
            # so the parser will either pass or fail
            testlist = list(doc)
            # Good to go
            return True

        except Exception as e :
            # If the text is not good, I think we should die here an now.
            # We may want to rethink this later but for now, it feels right.
            self.log.writeToLog('USFM-070', [source,str(e)])
            return False


###############################################################################
########################## USFM Component Functions ###########################
###############################################################################


    def logFigure (self, cid, figConts) :
        '''Log the figure data in the illustration.conf. If nothing is returned, the
        existing \fig markers with their contents will be removed. That is the default
        behavior.'''

        # Description of figKeys (in order found in \fig)
            # description = A brief description of what the illustration is about
            # file = The file name of the illustration (only the file name)
            # caption = The caption that will be used with the illustration (if turned on)
            # width = The width or span the illustration will have (span/col)
            # location = Location information that could be printed in the caption reference
            # copyright = Copyright information for the illustration
            # reference = The book ID (upper-case) plus the chapter and verse (eg. MAT 8:23)

        fig = figConts.group(1).split('|')
        figKeys = ['description', 'fileName', 'width', 'location', 'copyright', 'caption', 'reference']
        figDict = {}
        cvSep = self.layoutConfig['Illustrations']['chapterVerseSeperator']

        # Add all the figure info to the dictionary
        c = 0
        for value in fig :
            figDict[figKeys[c]] = value
            c +=1

        # Add additional information, get rid of stuff we don't need
        figDict['illustrationID'] = figDict['fileName'].split('.')[0]
        figDict['useThisIllustration'] = True
        figDict['useThisCaption'] = True
        figDict['useThisCaptionRef'] = True
        figDict['bid'] = cid.lower()
        figDict['chapter'] = re.sub(ur'[A-Z]+\s([0-9]+)[.:][0-9]+', ur'\1', figDict['reference'].upper())
        figDict['verse'] = re.sub(ur'[A-Z]+\s[0-9]+[.:]([0-9]+)', ur'\1', figDict['reference'].upper())
        figDict['scale'] = '1.0'
        if figDict['width'] == 'col' :
            figDict['position'] = 'tl'
        else :
            figDict['position'] = 't'
        if not figDict['location'] :
            figDict['location'] = figDict['chapter'] + cvSep + figDict['verse']

        illustrationConfig = self.illustration.illustrationConfig
        if not testForSetting(illustrationConfig, 'Illustrations') :
            buildConfSection(illustrationConfig, 'Illustrations')
        # Put the dictionary info into the illustration conf file
        if not testForSetting(illustrationConfig['Illustrations'], figDict['illustrationID'].upper()) :
            buildConfSection(illustrationConfig['Illustrations'], figDict['illustrationID'].upper())
        for k in figDict.keys() :
            illustrationConfig['Illustrations'][figDict['illustrationID'].upper()][k] = figDict[k]

        # Write out the conf file to preserve the data found
        writeConfFile(illustrationConfig)

        # Just incase we need to keep the fig markers intact this will
        # allow for that. However, default behavior is to strip them
        # because usfmTex does not handle \fig markers. By returning
        # them here, they will not be removed from the working text.
        if str2bool(self.projConfig['Managers'][self.cType + '_Illustration']['preserveUsfmFigData']) :
            return '\\fig ' + figConts.group(1) + '\\fig*'


    def getComponentType (self, gid) :
        '''Return the cType for a component.'''

#        import pdb; pdb.set_trace()

        try :
            cType = self.projConfig['Groups'][gid]['cType']
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.log.writeToLog('COMP-200', ['Key not found ' + str(e)])
            dieNow()

        return cType


    def isCompleteComponent (self, gid, cid) :
        '''A two-part test to see if a component has a config entry and a file.'''

        if self.hasCidFile(gid, cid) :
            return True


#    def hasCNameEntry (self, cName) :
#        '''Check for a config component entry.'''

#        buildConfSection(self.project.projConfig, 'Components')

#        if testForSetting(self.project.projConfig['Components'], cName) :
#            return True


    def hasUsfmCidInfo (self, cid) :
        '''Return True if this cid is in the PT USFM cid info dictionary.'''

        if cid in self.usfmCidInfo().keys() :
            return True


    def hasCidFile (self, gid, cid) :
        '''Return True or False depending on if a working file exists 
        for a given cName.'''

        cType = self.projConfig['Groups'][gid]['cType']
        return os.path.isfile(os.path.join(self.local.projComponentsFolder, cid, cid + '.' + cType))


###############################################################################
###############################################################################
############################## ParaTExt Classes ###############################
###############################################################################
###############################################################################

###############################################################################
########################## Hyphenation Class Functions ########################
###############################################################################

# Overview:
# A ParaTExt hyphenation word list (hyphenatedWords.txt) can potentually contain
# the following types of words:
#
#   1) abc-efg      = abc-efg   / exsiting words that contain a hyphen(s)
#   2) *abc-efg     = abc-efg   / approved words (by PT user) demarked by '*'
#   3) abc=efg      = abc-efg   / soft hyphens are added to a word
#   4) abcefg       = abcefg    / no hyphens found (may need further processing)
#
# (* Note that the "*" demarker is added by ParaTExt as a user approves a given
#   word. This character must be added manually if any processing is done outside
#   of PT so that PT can "learn" how words should be hyphenated and will make
#   better decisions in its automated hyphening. In theory, the user should be
#   teach PT to the point where no outside processing is needed.
#
# There may be some problems with words encountered. If any of the following are
# found they will be reported but it will not stop processing:
#
#   1) mixed syntax is illegal (abc-efg=hij)


class PT_HyphenTools (Group) :
    '''Hyphenation-specific functions. Only called (important) when needed.'''

    def __init__(self, project) :

        self.cType                  = 'usfm'
        self.Ctype                  = self.cType.capitalize()
        self.project                = project
        self.log                    = project.log
        self.managers               = project.managers
        self.gid                    = project.gid
        self.projectIDCode          = project.projectIDCode
        self.projConfig             = project.projConfig
        self.userConfig             = project.userConfig
        self.hy_tools               = self.managers[self.cType + '_Hyphenation']
        # Bring in some manager objects we will need
        if self.cType + '_Hyphenation' not in self.managers :
            self.project.createManager(self.cType, 'hyphenation')
        self.hyphenation = self.managers[self.cType + '_Hyphenation']
        if self.cType + '_Layout' not in self.managers :
            self.project.createManager(self.cType, 'layout')
        self.layoutConfig           = self.managers[self.cType + '_Layout'].layoutConfig
        self.useHyphenation         = str2bool(self.projConfig['Managers'][self.cType + '_Hyphenation']['useHyphenation'])
        # Some hyphenation handling settings and data that might work
        # better if they were more global
        self.allPtHyphenWords       = set()
        self.goodPtHyphenWords      = set()
        self.badWords               = set()
        self.hyphenWords            = set()
        self.approvedWords          = set()
        self.softHyphenWords        = set()
        self.nonHyphenWords         = set()
        # File Names
        self.ptProjHyphErrFileName  = 'usfm_' + self.projConfig['Managers']['usfm_Hyphenation']['ptHyphErrFileName']
        self.ptHyphFileName         = self.projConfig['Managers']['usfm_Hyphenation']['ptHyphenFileName']
        self.sourcePath             = self.userConfig['Projects'][self.projectIDCode][self.projConfig['Groups'][self.gid]['csid'] + '_sourcePath']
        # Folder paths
        self.projHyphenationFolder  = self.project.local.projHyphenationFolder
        # Set file names with full path 
        self.ptHyphFile             = os.path.join(self.sourcePath, self.ptHyphFileName)
        self.ptProjHyphFile         = os.path.join(self.projHyphenationFolder, self.ptHyphFileName)
        self.ptProjHyphBakFile      = os.path.join(self.projHyphenationFolder, self.ptHyphFileName + '.bak')
        self.ptProjHyphErrFile      = os.path.join(self.projHyphenationFolder, self.ptProjHyphErrFileName)


###############################################################################

    def copyPtHyphenWords (self) :
        '''Simple copy of the ParaTExt project hyphenation words list to the project.
        We will also create a backup as well to be used for comparison or fallback.'''

        if os.path.isfile(self.ptHyphFile) :
            # Use a special kind of copy to prevent problems with BOMs
            utf8Copy(self.ptHyphFile, self.ptProjHyphFile)
            # Once copied, check if any preprocessing is needed
            self.hyphenation.preprocessSource()
        else :
            self.log.writeToLog('USFM-040', [self.ptHyphFile])
            dieNow()


    def backupPtHyphenWords (self) :
        '''Backup the ParaTExt project hyphenation words list to the project.'''

        if os.path.isfile(self.ptHyphFile) :
            # Use a special kind of copy to prevent problems with BOMs
            utf8Copy(self.ptHyphFile, self.ptProjHyphBakFile)
            makeReadOnly(self.ptProjHyphBakFile)
        else :
            self.log.writeToLog('USFM-040', [self.ptHyphFile])
            dieNow()


    def processHyphens(self, force = False) :
        '''This controls the processing of the master PT hyphenation file. The end
        result are four data sets that are ready to be handed off to the next part
        of the process. It is assumed that at this point we have a valid PT hyphen
        file that came out of PT that way or it was fixed during copy by a preprocess
        script that was made to fix specific problems.'''

        # The project source files are protected but if force is used
        # we need to delete them here.
        if force :
            if os.path.exists(self.ptProjHyphFile) :
                os.remove(self.ptProjHyphFile)
            if os.path.exists(self.ptProjHyphBakFile) :
                os.remove(self.ptProjHyphBakFile)
            self.log.writeToLog('USFM-060')

        # These calls may be order-sensitive, update local project source
        # copy only if there has been a change in the PT source
#        if not os.path.isfile(self.ptHyphFile) or isOlder(self.ptHyphFile, self.ptHyphFile) :

# FIXME: What are we looking for, why are they the same?

# Not seeing a pt source file mentioned yet


        if not os.path.isfile(self.ptProjHyphFile) or isOlder(self.ptProjHyphFile, self.ptHyphFile) :
            self.copyPtHyphenWords()
            self.backupPtHyphenWords()
            self.log.writeToLog('USFM-050', [fName(self.ptHyphFile)])
        else :
            self.log.writeToLog('USFM-055', [fName(self.ptHyphFile)])

        # Continue by processing the files located in the project
        self.getAllPtHyphenWords()
        self.getApprovedWords()
        self.getHyphenWords()
        self.getSoftHyphenWords()
        self.getNonHyhpenWords()


    def getAllPtHyphenWords (self) :
        '''Return a data set of all the words found in a ParaTExt project
        hyphated words text file. The Py set() method is used for moving
        the data because some lists can get really big. This will return the
        entire wordlist as it is found in the ptHyphenFile. That can be used
        for other processing.'''

        # Go get the file if it is to be had
        if os.path.isfile(self.ptProjHyphFile) :
            with codecs.open(self.ptProjHyphFile, "r", encoding='utf_8') as hyphenWords :
                for line in hyphenWords :
                    # Using the logic that there can only be one word in a line
                    # if the line contains more than one word it is not wanted
                    word = line.split()
                    if len(word) == 1 :
                        self.allPtHyphenWords.add(word[0])

            # Now remove any bad/mal-formed words
            self.checkForBadWords()


    def getApprovedWords (self) :
        '''Return a data set of approved words found in a ParaTExt project
        hyphen word list that have a '*' in front of them. This indicates that
        the spelling has been manually approved by the user. These words may
        or may not contain hyphens'''

        # Go get the file if it is to be had
        for word in list(self.goodPtHyphenWords) :
            if word[:1] == '*' :
                self.approvedWords.add(word[1:])
                self.goodPtHyphenWords.remove(word)


    def getHyphenWords (self) :
        '''Return a data set of pre-hyphated words found in a ParaTExt project
        hyphen words list. These are words that are spelled with a hyphen in
        them but can break on line endings.'''

        # Go get the file if it is to be had
        for word in list(self.goodPtHyphenWords) :
            if '-' in word :
                self.hyphenWords.add(word)
                self.goodPtHyphenWords.remove(word)


    def getSoftHyphenWords (self) :
        '''Return a data set of words that contain soft hyphens but have not
        been approved by the user. These are normally created by PT or some
        external process.'''

        for word in list(self.goodPtHyphenWords) :
            if '=' in word :
                self.softHyphenWords.add(word)
                self.goodPtHyphenWords.remove(word)


    def getNonHyhpenWords (self) :
        '''Return a data set of words that do not contain hyphens. These are
        words that cannot normally be broken. This process must be run after
        getApprovedWords(), getSoftHyphenWords() and getHyphenWords().'''

        self.nonHyphenWords = self.goodPtHyphenWords.copy()
        self.nonHyphenWords.difference_update(self.approvedWords)
        self.nonHyphenWords.difference_update(self.softHyphenWords)
        self.nonHyphenWords.difference_update(self.hyphenWords)


    def checkForBadWords (self) :
        '''Check the words in the master list for bad syntax. Remove them
        and put them in a hyphen error words file in the project and give
        a warning to the user.'''

        for word in list(self.allPtHyphenWords) :
            if '-' in word and '=' in word :
                self.badWords.add(word)
            else :
                # Make the good words list here
                self.goodPtHyphenWords.add(word)

        if len(self.badWords) :
            errWords = list(self.badWords)
            errWords.sort()
            with codecs.open(self.ptProjHyphErrFile, "w", encoding='utf_8') as wordErrorsObject :
                wordErrorsObject.write('# ' + fName(self.ptProjHyphErrFile) + '\n')
                wordErrorsObject.write('# This is an auto-generated file which contains errors in the hyphenation words file.\n')
                for word in errWords :
                    wordErrorsObject.write(word + '\n')

            # Report the problem to the user
            self.log.writeToLog('USFM-030', [self.ptProjHyphErrFile])


    def wordTotals (self) :
        '''Return a report on word processing totals. For accuracy this is
        dependent on getApprovedWords(), getSoftHyphenWords(), getHyphenWords()
        and getNonHyhpenWords to be run before it. If the difference is off, die
        here and report the numbers.'''

        wrds = len(self.allPtHyphenWords)
        badw = len(self.badWords)
        excp = len(self.approvedWords)
        soft = len(self.softHyphenWords)
        hyph = len(self.hyphenWords)
        pwrd = len(self.nonHyphenWords)
        diff = wrds - (badw + excp + soft + hyph + pwrd)
        
        rpt = '\tAll words = ' + str(wrds) + '\n' \
                '\tBad words = ' + str(badw) + '\n' \
                '\tException words = ' + str(excp) + '\n' \
                '\tSoft hyphen words = ' + str(soft) + '\n' \
                '\tHyphen words = ' + str(hyph) + '\n' \
                '\tProcess words = ' + str(pwrd) + '\n' \
                '\tDifference = ' + str(diff) + '\n\n' \

        # Die here if the diff is off (not 0)
        if diff != 0 :
            dieNow('\nWord totals do not balance.\n\n' + rpt + 'Rapuma halted!\n')

        return [['Total words', str(wrds)], ['Bad words', str(badw)], ['Exception words', str(excp)], ['Soft Hyphen words', str(soft)], ['Hyphen words', str(hyph)], ['Process words', str(pwrd)]]


    def pt2GenHyphens (self, hyphenWords) :
        '''Create a set of generic hyphen markers on a given list of words
        that contain hyphens or PT hyphen markers (=).'''
        
        # Make a new set to work on and pass on
        for word in list(hyphenWords) :
            soft = re.sub(u'\=', u'<->', word)
            norm = re.sub(u'\-', u'<->', word)
            if word != soft :
                hyphenWords.add(soft)
                hyphenWords.remove(word)
            elif word != norm :
                hyphenWords.add(norm)
                hyphenWords.remove(word)

        return hyphenWords



###############################################################################
############################ PT Data Class Functions ##########################
###############################################################################

class PT_Tools (Group) :
    '''This class contains functions for working with general USFM data in ParaTExt.'''

    def __init__(self, project) :

        self.cType                  = 'usfm'
        self.Ctype                  = self.cType.capitalize()
        self.project                = project
        self.gid                    = project.gid
        self.managers               = project.managers
        self.projConfig             = project.projConfig
        self.userConfig             = project.userConfig


    def getUsfmCidInfo (self, cid) :
        '''Return a list of info about a specific cid used in the PT context.'''

#        import pdb; pdb.set_trace()

        try :
            return self.usfmCidInfo()[cid]
        except :
            return False


    def getNWFChars (self) :
        '''Return a list of non-word-forming characters from the PT settings
        field [ValidPunctuation] in the translation project.'''

        ptSet = self.getPTSettings(self.gid)
        chars = []
        if testForSetting(ptSet['ScriptureText'], 'ValidPunctuation') :
            for c in ptSet['ScriptureText']['ValidPunctuation'].split() :
                # Leave it a lone if it is a single character
                if len(c) == 1 :
                    chars.append(c)
                # A pair is what we expect
                elif len(c) == 2 :
                    # We expect "_" to be part of the pair
                    try :
                        if c.find('_') > 0 :
                            chars.append(c.replace('_', ''))
                    except Exception as e :
                        # If we don't succeed, we should probably quite here
                        self.log.writeToLog('USFM-010', [str(e)])
                        dieNow()
                else :
                    # Something really strange happened
                    self.log.writeToLog('USFM-020', [c])
                    dieNow()
        else :
            self.log.writeToLog('USFM-025')
        return chars


    def formPTName (self, gid, cid) :
        '''Using valid PT project settings from the project configuration, form
        a valid PT file name that can be used for a number of operations.'''

        # Assumed that this is for a ParaTExt USFM file, there should be
        # a nameFormID setting. If not, try updating the manager. If there
        # still is not a nameFormID, die in a very spectacular way.
        if not self.projConfig['Managers']['usfm_Text']['nameFormID'] :
            self.project.managers['usfm_Text'].updateManagerSettings(gid)

        # Hopefully all is well now
        nameFormID = self.projConfig['Managers']['usfm_Text']['nameFormID']
        postPart = self.projConfig['Managers']['usfm_Text']['postPart']
        prePart = self.projConfig['Managers']['usfm_Text']['prePart']

        # Sanity test
        if not nameFormID :
            dieNow('ERROR: usfm.PT_Tools.formPTName() could not determine the nameFormID. All is lost! Please crawl under your desk and wait for a large explosion. (Just kidding!)')

#        import pdb; pdb.set_trace()

        thisFile = ''

        if nameFormID == '41MAT' :
            mainName = self.getUsfmCidInfo(cid)[2] + cid.upper()
            if prePart and prePart != 'None' :
                thisFile = prePart + mainName + postPart
            else :
                thisFile = mainName + postPart
                
        if thisFile != '' :
            return thisFile
        else :
            return None


    def formGenericName (self, gid, cid) :
        '''Figure out the best way to form a valid file name given the
        source is not coming from a PT project. In the end, this is almost
        impossible to do because of all the different possibilities. We
        will just try to make our best guess. A better way will be needed.'''

        postPart = self.projConfig['Managers']['usfm_Text']['postPart']
        if postPart == '' :
            postPart = self.projConfig['Groups'][gid]['cType']

        return cid + '.' + postPart


    def mapPTTextSettings (self, sysSet, ptSet, force=False) :
        '''Map the text settings from a PT project SSF file into the text
        manager's settings. If no setting is present in the config, add
        what is in the PT SSF. If force is True, replace any exsisting
        settings.'''

        # A PT to Rapuma text mapping dictionary
        mapping   = {
                    'FileNameBookNameForm'      : 'nameFormID',
                    'FileNameForm'              : 'nameFormID',
                    'FileNamePrePart'           : 'prePart',
                    'FileNamePostPart'          : 'postPart',
                    'DefaultFont'               : 'ptDefaultFont'
                    }

        # Loop through all the PT settings and check against the mapping
        for k in mapping.keys() :
            try :
                if sysSet[mapping[k]] == '' or sysSet[mapping[k]] == 'None' :
                    # This is for getting rid of "None" settings in the config
                    if not ptSet['ScriptureText'][k] :
                        sysSet[mapping[k]] = ''
                    else :
                        sysSet[mapping[k]] = ptSet['ScriptureText'][k]
                elif force :
                    sysSet[mapping[k]] = ptSet['ScriptureText'][k]
            except :
                pass

        return sysSet


    def findSsfFile (self, gid) :
        '''Look for the ParaTExt project settings file. The immediat PT project
        is the parent folder and the PT environment that the PT projet is found
        in, if any, is the grandparent folder. the .ssf (settings) file in the
        grandparent folder takes presidence over the one found in the parent folder.
        This function will determine where the primary .ssf file is and return the
        .ssf path/file and the PT path. If not found, return None.'''

        # Not sure where the PT SSF file might be or even what its name is.
        # Starting in parent, we should find the first .ssf file. That will
        # give us the name of the file. Then we will look in the grandparent
        # folder and if we find the same named file there, that will be
        # harvested for the settings. Otherwise, the settings will be taken
        # from the parent folder.
        # Note: Starting with PT 7 the "gather" folder was introduced to
        # projects. We will need to look in that folder as well for the 
        # .ssf file.
        ssfFileName = ''
        ptPath = ''
        parentFolder = self.project.getGroupSourcePath(gid)
        grandparentFolder = os.path.dirname(parentFolder)
        gatherFolder = os.path.join(parentFolder, 'gather')

        # For now, we will assume that if there is a gather folder, it must have a .ssf file in it
        if os.path.isdir(gatherFolder) :
            parentFolder = gatherFolder
        # Get a file list from the parent folder and look for a .ssf/.SSF file
        # This assumes there is (has to be) only one ssf/SSF file in the folder.
        # The main problem at this point is we don't really know the name of
        # the file, only the extention.
        parentFileList = dircache.listdir(parentFolder)
        grandparentFileList = dircache.listdir(grandparentFolder)

        # Parent first to find the actual settings file name. Right now, there
        # can only be 2 possibilities, either ssf or SSF. (No one in their right
        # mind would ever use mixed case on an extention. That would be stupid!)
        for f in parentFileList :
            if os.path.isfile(os.path.join(parentFolder, f)) :
                # Not every file we test has an extention, look first
                if len(f.split('.')) > 1 :
                    if f.split('.')[1] == 'ssf' or f.split('.')[1] == 'SSF' :
                        ssfFileName = f
                        ptPath = parentFolder

        # At this point we need a sanity test. If no ssfFileName is present
        # then there probably isn't one and we should just return False now
        if not ssfFileName :
            return False

        # Now now look in the grandparent folder and change to override settings
        # file if there is one
        for f in grandparentFileList :
            if os.path.isfile(os.path.join(grandparentFolder, f)) :
                ucn = ssfFileName.split('.')[0] + '.' + ssfFileName.split('.')[1].upper()
                lcn = ssfFileName.split('.')[0] + '.' + ssfFileName.split('.')[1].lower()
                if f == (ucn or lcn) :
                    ssfFileName = f
                    ptPath = grandparentFolder

        return os.path.join(ptPath, ssfFileName)


    def getPTSettings (self, gid) :
        '''Return the data into a dictionary for the system to use.'''

        sourcePath = self.project.getGroupSourcePath(gid)

        # Return the dictionary
        if os.path.isdir(sourcePath) :
            ssfFile = self.findSsfFile(gid)
            if ssfFile :
                if os.path.isfile(ssfFile) :
                    return xmlFileToDict(ssfFile)


    def getSourceEditor (self, gid) :
        '''Return the sourceEditor if it is set. If not try to
        figure out what it should be and return that. Unless we
        find we are in a PT project, we'll call it generic.'''

    #    import pdb; pdb.set_trace()
        se = 'generic'
        # FIXME: This may need expanding as more use cases arrise
        if testForSetting(self.projConfig['CompTypes'][self.Ctype], 'sourceEditor') :
            se = self.projConfig['CompTypes'][self.Ctype]['sourceEditor']
        else :
            if self.findSsfFile(gid) :
                se = 'paratext'

        return se


    def usfmCidInfo (self) :
        '''Return a dictionary of all valid information about USFMs used in PT.'''

    #            ID     Comp Name                               Comp ID                         PT ID  Chps
        return {
                '_z_' : ['USFM InternalCaller',                 'usfm_internal_caller',         '00',   0], 
                'gen' : ['Genesis',                             'genesis',                      '01',  50], 
                'exo' : ['Exodus',                              'exodus',                       '02',  40], 
                'lev' : ['Leviticus',                           'leviticus',                    '03',  27], 
                'num' : ['Numbers',                             'numbers',                      '04',  36], 
                'deu' : ['Deuteronomy',                         'deuteronomy',                  '05',  34], 
                'jos' : ['Joshua',                              'joshua',                       '06',  24], 
                'jdg' : ['Judges',                              'judges',                       '07',  21], 
                'rut' : ['Ruth',                                'ruth',                         '08',   4], 
                '1sa' : ['1 Samuel',                            '1_samuel',                     '09',  31], 
                '2sa' : ['2 Samuel',                            '2_samuel',                     '10',  24], 
                '1ki' : ['1 Kings',                             '1_kings',                      '11',  22], 
                '2ki' : ['2 Kings',                             '2_kings',                      '12',  25], 
                '1ch' : ['1 Chronicles',                        '1_chronicles',                 '13',  29], 
                '2ch' : ['2 Chronicles',                        '2_chronicles',                 '14',  36], 
                'ezr' : ['Ezra',                                'ezra',                         '15',  10], 
                'neh' : ['Nehemiah',                            'nehemiah',                     '16',  13], 
                'est' : ['Esther',                              'esther',                       '17',  10], 
                'job' : ['Job',                                 'job',                          '18',  42], 
                'psa' : ['Psalms',                              'psalms',                       '19', 150], 
                'pro' : ['Proverbs',                            'proverbs',                     '20',  31], 
                'ecc' : ['Ecclesiastes',                        'ecclesiastes',                 '21',  12], 
                'sng' : ['Song of Songs',                       'song_of_songs',                '22',   8], 
                'isa' : ['Isaiah',                              'isaiah',                       '23',  66], 
                'jer' : ['Jeremiah',                            'jeremiah',                     '24',  52], 
                'lam' : ['Lamentations',                        'lamentations',                 '25',   5], 
                'ezk' : ['Ezekiel',                             'ezekiel',                      '26',  48], 
                'dan' : ['Daniel',                              'daniel',                       '27',  12], 
                'hos' : ['Hosea',                               'hosea',                        '28',  14], 
                'jol' : ['Joel',                                'joel',                         '29',   3], 
                'amo' : ['Amos',                                'amos',                         '30',   9], 
                'oba' : ['Obadiah',                             'obadiah',                      '31',   1], 
                'jon' : ['Jonah',                               'jonah',                        '32',   4], 
                'mic' : ['Micah',                               'micah',                        '33',   7], 
                'nam' : ['Nahum',                               'nahum',                        '34',   3], 
                'hab' : ['Habakkuk',                            'habakkuk',                     '35',   3], 
                'zep' : ['Zephaniah',                           'zephaniah',                    '36',   3], 
                'hag' : ['Haggai',                              'haggai',                       '37',   2], 
                'zec' : ['Zechariah',                           'zechariah',                    '38',  14], 
                'mal' : ['Malachi',                             'malachi',                      '39',   4],
                'mat' : ['Matthew',                             'matthew',                      '41',  28], 
                'mrk' : ['Mark',                                'mark',                         '42',  16], 
                'luk' : ['Luke',                                'luke',                         '43',  24], 
                'jhn' : ['John',                                'john',                         '44',  21], 
                'act' : ['Acts',                                'acts',                         '45',  28], 
                'rom' : ['Romans',                              'romans',                       '46',  16], 
                '1co' : ['1 Corinthians',                       '1_corinthians',                '47',  16], 
                '2co' : ['2 Corinthians',                       '2_corinthians',                '48',  13], 
                'gal' : ['Galatians',                           'galatians',                    '49',   6], 
                'eph' : ['Ephesians',                           'ephesians',                    '50',   6], 
                'php' : ['Philippians',                         'philippians',                  '51',   4], 
                'col' : ['Colossians',                          'colossians',                   '52',   4], 
                '1th' : ['1 Thessalonians',                     '1_thessalonians',              '53',   5], 
                '2th' : ['2 Thessalonians',                     '2_thessalonians',              '54',   3], 
                '1ti' : ['1 Timothy',                           '1_timothy',                    '55',   6], 
                '2ti' : ['2 Timothy',                           '2_timothy',                    '56',   4], 
                'tit' : ['Titus',                               'titus',                        '57',   3], 
                'phm' : ['Philemon',                            'philemon',                     '58',   1], 
                'heb' : ['Hebrews',                             'hebrews',                      '59',  13], 
                'jas' : ['James',                               'james',                        '60',   5], 
                '1pe' : ['1 Peter',                             '1_peter',                      '61',   5], 
                '2pe' : ['2 Peter',                             '2_peter',                      '62',   3], 
                '1jn' : ['1 John',                              '1_john',                       '63',   5], 
                '2jn' : ['2 John',                              '2_john',                       '64',   1], 
                '3jn' : ['3 John',                              '3_john',                       '65',   1], 
                'jud' : ['Jude',                                'jude',                         '66',   1], 
                'rev' : ['Revelation',                          'revelation',                   '67',  22], 
                'tob' : ['Tobit',                               'tobit',                        '68', '?'], 
                'jdt' : ['Judith',                              'judith',                       '69', '?'], 
                'esg' : ['Esther',                              'esther',                       '70', '?'], 
                'wis' : ['Wisdom of Solomon',                   'wisdom_of_solomon',            '71', '?'], 
                'sir' : ['Sirach',                              'sirach',                       '72', '?'], 
                'bar' : ['Baruch',                              'baruch',                       '73', '?'], 
                'lje' : ['Letter of Jeremiah',                  'letter_of_jeremiah',           '74', '?'], 
                's3y' : ['Song of the Three Children',          'song_3_children',              '75', '?'], 
                'sus' : ['Susanna',                             'susanna',                      '76', '?'], 
                'bel' : ['Bel and the Dragon',                  'bel_dragon',                   '77', '?'], 
                '1ma' : ['1 Maccabees',                         '1_maccabees',                  '78', '?'], 
                '2ma' : ['2 Maccabees',                         '2_maccabees',                  '79', '?'], 
                '3ma' : ['3 Maccabees',                         '3_maccabees',                  '80', '?'], 
                '4ma' : ['4 Maccabees',                         '4_maccabees',                  '81', '?'], 
                '1es' : ['1 Esdras',                            '1_esdras',                     '82', '?'], 
                '2es' : ['2 Esdras',                            '2_esdras',                     '83', '?'], 
                'man' : ['Prayer of Manasses',                  'prayer_of_manasses',           '84', '?'], 
                'ps2' : ['Psalms 151',                          'psalms_151',                   '85', '?'], 
                'oda' : ['Odae',                                'odae',                         '86', '?'], 
                'pss' : ['Psalms of Solomon',                   'psalms_of_solomon',            '87', '?'], 
                'jsa' : ['Joshua A',                            'joshua_a',                     '88', '?'], 
                'jdb' : ['Joshua B',                            'joshua_b',                     '89', '?'], 
                'tbs' : ['Tobit S',                             'tobit_s',                      '90', '?'], 
                'sst' : ['Susannah (Theodotion)',               'susannah_t',                   '91', '?'], 
                'dnt' : ['Daniel (Theodotion)',                 'daniel_t',                     '92', '?'], 
                'blt' : ['Bel and the Dragon (Theodotion)',     'bel_dragon_t',                 '93', '?'], 
                'frt' : ['Front Matter',                        'front_matter',                 'A0',   0], 
                'int' : ['Introductions',                       'introductions',                'A7',   0], 
                'bak' : ['Back Matter',                         'back_matter',                  'A1',   0], 
                'cnc' : ['Concordance',                         'concordance',                  'A8',   0], 
                'glo' : ['Glossary',                            'glossary',                     'A9',   0], 
                'tdx' : ['Topical Index',                       'topical_index',                'B0',   0], 
                'ndx' : ['Names Index',                         'names_index',                  'B1',   0], 
                'xxa' : ['Extra A',                             'extra_a',                      '94',   0], 
                'xxb' : ['Extra B',                             'extra_b',                      '95',   0], 
                'xxc' : ['Extra C',                             'extra_c',                      '96',   0], 
                'xxd' : ['Extra D',                             'extra_d',                      '97',   0],
                'xxe' : ['Extra E',                             'extra_e',                      '98',   0], 
                'xxf' : ['Extra F',                             'extra_f',                      '99',   0], 
                'xxg' : ['Extra G',                             'extra_g',                      '100',  0], 
                'oth' : ['Other',                               'other',                        'A2',   0], 
                'eza' : ['Apocalypse of Ezra',                  'apocalypse_of_ezra',           'A4', '?'], 
                '5ez' : ['5 Ezra',                              '5_ezra_lp',                    'A5', '?'], 
                '6ez' : ['6 Ezra (Latin Epilogue)',             '6_ezra_lp',                    'A6', '?'], 
                'dag' : ['Daniel Greek',                        'daniel_greek',                 'B2', '?'], 
                'ps3' : ['Psalms 152-155',                      'psalms_152-155',               'B3', '?'], 
                '2ba' : ['2 Baruch (Apocalypse)',               '2_baruch_apocalypse',          'B4', '?'], 
                'lba' : ['Letter of Baruch',                    'letter_of_baruch',             'B5', '?'], 
                'jub' : ['Jubilees',                            'jubilees',                     'B6', '?'], 
                'eno' : ['Enoch',                               'enoch',                        'B7', '?'], 
                '1mq' : ['1 Meqabyan',                          '1_meqabyan',                   'B8', '?'], 
                '2mq' : ['2 Meqabyan',                          '2_meqabyan',                   'B9', '?'], 
                '3mq' : ['3 Meqabyan',                          '3_meqabyan',                   'C0', '?'], 
                'rep' : ['Reproof (Proverbs 25-31)',            'reproof_proverbs_25-31',       'C1', '?'], 
                '4ba' : ['4 Baruch (Rest of Baruch)',           '4_baruch',                     'C2', '?'], 
                'lao' : ['Laodiceans',                          'laodiceans',                   'C3', '?'] 

               }





