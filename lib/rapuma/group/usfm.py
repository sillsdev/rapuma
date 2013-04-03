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

import os
from configobj import ConfigObj, Section
#from functools import partial

# Load the local classes
from rapuma.core.tools              import *
from rapuma.core.page_background    import PageBackground
from rapuma.group.group             import Group


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
        self.pg_background          = PageBackground(project.projectIDCode)
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
#        self.grpPreprocessFile      = self.text.grpPreprocessFile

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

        # Module Error Codes
        self.errorCodes     = {

            '0010' : ['LOG', 'Created the [<<1>>] master adjustment file.'],

            '0220' : ['ERR', 'Cannot find: [<<1>>] working file, unable to complete preprocessing for rendering.'],

            '0230' : ['LOG', 'Created the [<<1>>] component adjustment file.'],

        }

        # Pick up some init settings that come after the managers have been installed
        self.macroPackage           = self.projConfig['Managers'][self.cType + '_' + self.renderer.capitalize()]['macroPackage']
        self.layoutConfig           = self.layout.layoutConfig
        if not os.path.isfile(self.adjustmentConfFile) :
            if self.createProjAdjustmentConfFile() :
                self.log.writeToLog(self.errorCodes['0010'], [fName(self.adjustmentConfFile)])
            else :
                self.updateCompAdjustmentConf()
        # Now get the adj config
        self.adjustmentConfig       = ConfigObj(self.adjustmentConfFile, encoding='utf-8')


###############################################################################
############################ Functions Begin Here #############################
###############################################################################
######################## Error Code Block Series = 0200 #######################
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


    def render(self, cidList, force) :
        '''Does USFM specific rendering of a USFM component'''

#        import pdb; pdb.set_trace()

        # If the whole group is being rendered, we need to preprocess it
        cids = []
        if not cidList :
            cids = self.projConfig['Groups'][self.gid]['cidList']
        else :
            cids = cidList

        # Preprocess all subcomponents (one or more)
        # Stop if it breaks at any point
        for cid in cids :
            if not self.preProcessGroup() :
                return False

        # With everything in place we can render the component and we pass-through
        # the force (render/view) command so the renderer will do the right thing.
        # Note: We pass the cidList straight through
        self.project.managers['usfm_' + self.renderer.capitalize()].run(cidList, force)

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

        # Check if there is a font installed
        if not self.font.varifyFont() :
            # If a PT project, use that font, otherwise, install default
            if self.sourceEditor.lower() == 'paratext' :
                font = self.projConfig['Managers'][self.cType + '_Font']['ptDefaultFont']
            else :
                font = 'DefaultFont'

            self.font.installFont(font)

        # Will need the stylesheet for copy if that has not been added
        # to the project yet, we will do that now
        self.style.checkDefaultStyFile()
        self.style.checkDefaultExtStyFile()
        self.style.checkGrpExtStyFile()

        # See if the working text is present for each subcomponent in the
        # component and try to install it if it is not
        for cid in self.cfg['cidList'] :
            cType = self.cfg['cType']
            cidUsfm = self.getCidPath(cid)
            # Test for source here and die if it isn't there
            if not os.path.isfile(cidUsfm) :
                self.log.writeToLog(self.errorCodes['0220'], [cid], 'usfm.preProcessGroup():0220')

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
                self.log.writeToLog(self.errorCodes['0220'], [self.macroPackage])

        # Be sure there is a watermark file listed in the conf and
        # installed if watermark is turned on (True). Fallback on the
        # the default if needed.
        if useWatermark :
            self.pg_background.installDefaultWatermarkFile()

        # Same for lines background file used for composition
        if useLines :
            self.pg_background.installLinesFile()

        # Same for box background file used for composition
        if useBoxBoarder :
            self.pg_background.installBoxBoarderFile()

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

                        self.log.writeToLog(self.errorCodes['0230'], [fName(adjFile)])
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


#    def installUsfmWorkingText (self, gid, cid, force = False) :
#        '''Find the USFM source text and install it into the working text
#        folder of the project with the proper name. If a USFM text file
#        is not located in a PT project folder, the editor cannot be set
#        to paratext, it must be set to generic. This assumes lock checking
#        was done previous to the call.'''

##        import pdb; pdb.set_trace()

#        sourcePath = self.project.getGroupSourcePath(gid)
#        csid = self.projConfig['Groups'][gid]['csid']

#        # Check if there is a font installed
#        if not self.font.varifyFont() :
#            # If a PT project, use that font, otherwise, install default
#            if self.sourceEditor.lower() == 'paratext' :
#                font = self.projConfig['Managers'][self.cType + '_Font']['ptDefaultFont']
#            else :
#                font = 'DefaultFont'

#            self.font.installFont(font)

#        # Build the file name
#        thisFile = ''
#        if self.sourceEditor.lower() == 'paratext' :
#            thisFile = self.pt_tools.formPTName(gid, cid)
#        elif self.sourceEditor.lower() == 'generic' :
#            thisFile = self.pt_tools.formGenericName(gid, cid)
#        else :
#            self.log.writeToLog('USFM-100', [self.sourceEditor])

#        # Test, no name = no success
#        if not thisFile :
#            self.log.writeToLog(self.errorCodes['210'], [cid])
#            dieNow()

#        # Will need the stylesheet for copy if that has not been added
#        # to the project yet, we will do that now
#        self.style.checkDefaultStyFile()
#        self.style.checkDefaultExtStyFile()

#        # Start the process by building paths and file names, if we made it this far.
#        # Note the file name for the preprocess is hard coded. This will become a part
#        # of the total system and this file will be copied in when the user requests to
#        # preprocessing.

#        # Current assuption is that source text is located in a directory above the
#        # that is the default. In case that is not the case, we can override that and
#        # specify a path to the source. If that exists, then we will use that instead.
#        if sourcePath :
#            source      = os.path.join(sourcePath, thisFile)
#        else :
#            source      = os.path.join(os.path.dirname(self.local.projHome), thisFile)

#        targetFolder    = os.path.join(self.local.projComponentsFolder, cid)
#        target          = os.path.join(targetFolder, self.component.makeFileNameWithExt(cid))
#        targetSource    = os.path.join(targetFolder, thisFile + '.source')

#        # Copy the source to the working text folder. We do not want to do
#        # this if the there already is a target and it is newer than the 
#        # source text, that would indicate some edits have been done and we
#        # do not want to loose the work. However, if it is older that would
#        # indicate the source has been updated so unless the folder is locked
#        # we will want to update the target.

#        # Look for the source now, if not found, fallback on the targetSource
#        # backup file. But if that isn't there die.
#        if not os.path.isfile(source) :
#            if os.path.isfile(targetSource) :
#                source = targetSource
#            else :
#                self.log.writeToLog('USFM-120', [source])
#                dieNow()

#        # Now do the age checks and copy if source is newer than target
#        if force or not os.path.isfile(target) or isOlder(target, source) :

#            # Make target folder if needed
#            if not os.path.isdir(targetFolder) :
#                os.makedirs(targetFolder)

#            # Always save an untouched copy of the source and set to
#            # read only. We may need this to restore/reset later.
#            if os.path.isfile(targetSource) :
#                # Don't bother if we copied from it in the first place
#                if targetSource != source :
#                    # Reset permissions to overwrite
#                    makeWriteable(targetSource)
#                    shutil.copy(source, targetSource)
#                    makeReadOnly(targetSource)
#            else :
#                shutil.copy(source, targetSource)
#                makeReadOnly(targetSource)

#            # To be sure nothing happens, copy from our project source
#            # backup file. (Is self.style.defaultStyFile the best thing?)
#            if self.usfmCopy(targetSource, target, self.style.defaultStyFile) :
#                # Run any working text preprocesses on the new component text
#                if str2bool(self.projConfig['Groups'][gid]['usePreprocessScript']) :
#                    if not os.path.isfile(self.grpPreprocessFile) :
#                        self.text.installPreprocess()
#                    if not self.text.runProcessScript(target, self.grpPreprocessFile) :
#                        self.log.writeToLog('USFM-130', [cid])

#                # If this is a USFM component type we need to remove any \fig markers,
#                # and record them in the illustration.conf file for later use
#                if self.cType == 'usfm' :
#                    tempFile = target + '.tmp'
#                    contents = codecs.open(target, "rt", encoding="utf_8_sig").read()
#                    # logUsfmFigure() logs the fig data and strips it from the working text
#                    # Note: Using partial() to allows the passing of the cid param 
#                    # into logUsfmFigure()
#                    contents = re.sub(r'\\fig\s(.+?)\\fig\*', partial(self.project.groups[gid].logFigure, cid), contents)
#                    codecs.open(tempFile, "wt", encoding="utf_8_sig").write(contents)
#                    # Finish by copying the tempFile to the source
#                    if not shutil.copy(tempFile, target) :
#                        # Take out the trash
#                        os.remove(tempFile)

#                # If the text is there, we should return True so do a last check to see
#                if os.path.isfile(target) :
#                    self.log.writeToLog('USFM-140', [cid])
#                    return True
#            else :
#                self.log.writeToLog('USFM-150', [source,fName(target)])
#                return False
#        else :
#            return True


#    def usfmCopy (self, source, target, projSty = None) :
#        '''Copy USFM text from source to target. Decode if necessary, then
#        normalize. With the text in place, validate unless that is False.'''

#        # Bring in our source text
#        if self.text.sourceEncode == self.text.workEncode :
#            contents = codecs.open(source, 'rt', 'utf_8_sig')
#            lines = contents.read()
#        else :
#            # Lets try to change the encoding.
#            lines = self.text.decodeText(source)

#        # Normalize the text
#        normal = unicodedata.normalize(self.text.unicodeNormalForm, lines)
#        self.log.writeToLog('USFM-080', [self.text.unicodeNormalForm])

#        # Write out the text to the target
#        writeout = codecs.open(target, "wt", "utf_8_sig")
#        writeout.write(normal)
#        writeout.close

#        # Validate the target USFM text (Defalt is True)
#        if str2bool(self.validateUsfm) :
#            if not self.usfmTextFileIsValid(target, projSty) :
#                self.log.writeToLog('USFM-090', [source,fName(target)])
#                return False
#        else :
#            self.log.writeToLog('USFM-095', [fName(target)])

#        return True


#    def usfmTextFileIsValid (self, source, projSty) :
#        '''Use the USFM parser to validate a style file. For now,
#        if a file fails, we'll just quite right away, otherwise,
#        return True.'''

#        # Note: Error level reporting is possible with the usfm.parser.
#        # The following are the errors it can report:
#        # Note            = -1    Just give output warning, do not stop
#        # Marker          =  0    Stop on any out of place marker
#        # Content         =  1    Stop on mal-formed content
#        # Structure       =  2    Stop on ???
#        # Unrecoverable   =  100  Stop on most anything that is wrong
#        # For future reference, the sfm parser will fail if TeX style
#        # comment markers "%" are used to comment text rather than "#".

#        try :
#            fh = codecs.open(source, 'rt', 'utf_8_sig')
#            stylesheet = usfm.default_stylesheet.copy()
#            if projSty :
#                stylesheet_extra = style.parse(open(os.path.expanduser(projSty),'r'))
#                stylesheet.update(stylesheet_extra)
#            doc = usfm.parser(fh, stylesheet, error_level=sfm.level.Structure)
#            # With the doc text loaded up, we run a list across it
#            # so the parser will either pass or fail
#            testlist = list(doc)
#            # Good to go
#            return True

#        except Exception as e :
#            # If the text is not good, I think we should die here an now.
#            # We may want to rethink this later but for now, it feels right.
#            self.log.writeToLog('USFM-070', [source,str(e)])
#            return False


###############################################################################
########################## USFM Component Functions ###########################
###############################################################################


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


