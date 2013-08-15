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

import os, codecs
from configobj import ConfigObj, Section
#from functools import partial

# Load the local classes
from rapuma.core.tools                  import Tools
from rapuma.core.paratext               import Paratext
from rapuma.group.group                 import Group
from rapuma.project.proj_font           import ProjFont
from rapuma.project.proj_illustration   import ProjIllustration
from rapuma.project.proj_config         import Config
from rapuma.project.proj_background     import ProjBackground


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
        self.pid                    = project.projectIDCode
        self.gid                    = project.gid
        self.cType                  = 'usfm'
        self.Ctype                  = self.cType.capitalize()
        self.project                = project
        self.local                  = project.local
        self.tools                  = Tools()
        self.pt_tools               = Paratext(self.pid, self.gid)
        self.proj_font              = ProjFont(self.pid, self.gid)
        self.proj_illustration      = ProjIllustration(self.pid, self.gid)
        self.proj_config            = Config(self.pid, self.gid)
        self.pg_background          = ProjBackground(self.pid, self.gid)
        self.projConfig             = project.projConfig
        self.log                    = project.log
        self.cfg                    = cfg
        self.mType                  = project.projectMediaIDCode
        self.csid                   = project.projConfig['Groups'][self.gid]['csid']
        self.renderer               = project.projConfig['CompTypes'][self.Ctype]['renderer']
        self.sourceEditor           = project.projConfig['CompTypes'][self.Ctype]['sourceEditor']
        self.macPack                = project.projConfig['CompTypes'][self.Ctype]['macroPackage']
        # If adjustments are needed in the macPack we insert into local here for down-stream use
        self.adjustmentConfig       = self.proj_config.adjustmentConfig
        self.adjustmentConfFile     = self.proj_config.adjustmentConfFile
        # Get the comp settings
        self.compSettings           = project.projConfig['CompTypes'][self.Ctype]
        # Get macro package settings
        self.macPackConfig          = self.proj_config.macPackConfig
        # Build a tuple of managers this component type needs to use
        self.usfmManagers = ('text', self.renderer)

        # Init the general managers
        for mType in self.usfmManagers :
            self.project.createManager(mType)

        # Create the internal ref names we use in this module
        self.text                   = self.project.managers[self.cType + '_Text']
        # File names

        # Folder paths
        self.projScriptFolder       = self.local.projScriptFolder
        self.projComponentFolder    = self.local.projComponentFolder
        self.gidFolder              = os.path.join(self.projComponentFolder, self.gid)
        # File names with folder paths
        self.rapumaXmlCompConfig    = os.path.join(self.project.local.rapumaConfigFolder, self.xmlConfFile)

        # Get persistant values from the config if there are any
        newSectionSettings = self.tools.getPersistantSettings(self.projConfig['CompTypes'][self.Ctype], self.rapumaXmlCompConfig)
        if newSectionSettings != self.projConfig['CompTypes'][self.Ctype] :
            self.projConfig['CompTypes'][self.Ctype] = newSectionSettings
        # Set them here
        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)

        # Check if there is a primary font installed
        if not self.proj_font.varifyFont() :
            # If a PT project, use that font, otherwise, install default

#            import pdb; pdb.set_trace()

            if not self.sourceEditor :
                self.sourceEditor = self.pt_tools.getSourceEditor()
            if self.sourceEditor.lower() == 'paratext' :
                font = ''
                if self.macPackConfig['FontSettings'].has_key('ptDefaultFont') \
                    and self.macPackConfig['FontSettings']['ptDefaultFont'] :
                    font = self.macPackConfig['FontSettings']['ptDefaultFont']
                else :
                    font = self.pt_tools.getDefaultFont(self.macPackConfig)
            else :
                font = 'DefaultFont'

            self.proj_font.installFont(font)

        # Module Error Codes
        self.errorCodes     = {
            'USFM-000' : ['MSG', 'Messages for the USFM module.'],
            'USFM-005' : ['MSG', 'Unassigned error message ID.'],
            'USFM-010' : ['ERR', 'Could not process character pair. This error was found: [<<1>>]. Process could not complete. - usfm.pt_tools.getNWFChars()'],
            'USFM-020' : ['ERR', 'Improper character pair found: [<<1>>].  Process could not complete. - usfm.pt_tools.getNWFChars()'],
            'USFM-025' : ['WRN', 'No non-word-forming characters were found in the PT settings file. - usfm.pt_tools.getNWFChars()'],
            'USFM-040' : ['ERR', 'Hyphenation source file not found: [<<1>>]. Process halted!'],
            'USFM-070' : ['ERR', 'Text validation failed on USFM file: [<<1>>] It reported this error: [<<2>>]'],
            'USFM-080' : ['LOG', 'Normalizing Unicode text to the [<<1>>] form.'],
            'USFM-090' : ['ERR', 'USFM file: [<<1>>] did NOT pass the validation test. Because of an encoding conversion, the terminal output is from the file [<<2>>]. Please only edit [<<1>>].'],
            'USFM-095' : ['WRN', 'Validation for USFM file: [<<1>>] was turned off.'],
            'USFM-100' : ['MSG', 'Source file editor [<<1>>] is not recognized by this system. Please double check the name used for the source text editor setting.'],
            'USFM-110' : ['ERR', 'Source file name could not be built because the Name Form ID for [<<1>>] is missing or incorrect. Double check to see which editor created the source text.'],
            'USFM-120' : ['ERR', 'Source file: [<<1>>] not found! Cannot copy to project. Process halting now.'],
            'USFM-130' : ['ERR', 'Failed to complete preprocessing on component [<<1>>]'],
            'USFM-140' : ['MSG', 'Completed installation on [<<1>>] component working text.'],
            'USFM-150' : ['ERR', 'Unable to copy [<<1>>] to [<<2>>] - error in text.'],

            '0010' : ['LOG', 'Created the [<<1>>] master adjustment file.'],
            '0220' : ['ERR', 'Cannot find: [<<1>>] working file, unable to complete preprocessing for rendering.'],
            '0230' : ['LOG', 'Created the [<<1>>] component adjustment file.'],
            '0240' : ['LOG', 'Could not find adjustments for [<<1>>], created place holder setting.'],
            '0255' : ['LOG', 'Illustrations not being used. The piclist file has been removed from the [<<1>>] illustrations folder.'],
            '0260' : ['LOG', 'Piclist file for [<<1>>] has been created.'],
            '0265' : ['ERR', 'Failed to create piclist file for [<<1>>]!'],
        }


###############################################################################
############################ Functions Begin Here #############################
###############################################################################
######################## Error Code Block Series = 0200 #######################
###############################################################################

    def makeFileName(self, cid) :
        '''From what we know, return the full file name.'''

        return cid + '_' + self.csid


    def makeFileNameWithExt(self, cid) :
        '''From what we know, return the full file name.'''

        return self.makeFileName(cid) + '.' + self.cType


    def getCidPath (self, cid) :
        '''Return the full path of the cName working text file. This assumes
        the cid is valid.'''

        return os.path.join(self.local.projComponentFolder, cid, self.makeFileNameWithExt(cid))


    def getCidAdjPath (self, cid) :
        '''Return the full path of the cName working text adjustments file. 
        This assumes the cName is valid.'''

        return os.path.join(self.local.projComponentFolder, cid, self.makeFileName(cid) + '.adj')


#    def getCidPiclistFile (self, cid) :
#        '''Return the full path of the cName working text illustrations file. 
#        This assumes the cName is valid.'''

#        return os.path.join(self.local.projComponentFolder, cid, self.makeFileName(cid) + '.piclist')


    def render(self, gid, mode, cidList, force) :
        '''Does USFM specific rendering of a USFM component'''

#        import pdb; pdb.set_trace()

        # If the whole group is being rendered, we need to preprocess it
        cids = []
        if not cidList :
            cids = self.projConfig['Groups'][gid]['cidList']
        else :
            cids = cidList

        # Preprocess all subcomponents (one or more)
        # Stop if it breaks at any point
        for cid in cids :
            if not self.preProcessGroup(gid, mode, cids) :
                return False

        # With everything in place we can render the component and we pass-through
        # the force (render/view) command so the renderer will do the right thing.
        # Note: We pass the cidList straight through
        self.project.managers['usfm_' + self.renderer.capitalize()].run(gid, mode, cidList, force)

        return True


    def preProcessGroup (self, gid, mode, cidList) :
        '''This will prepare a component group for rendering by checking for
        and/or creating any dependents it needs to render properly.'''

        # Get some relevant settings
        # FIXME: Note page border has not really been implemented yet.
        # It is different from backgound management
        useIllustrations        = self.tools.str2bool(self.projConfig['Groups'][gid]['useIllustrations'])
        useManualAdjustments    = self.tools.str2bool(self.projConfig['Groups'][gid]['useManualAdjustments'])

        # Adjust the page number if necessary
        self.checkStartPageNumber()

        # See if the working text is present for each subcomponent in the
        # component and try to install it if it is not
        for cid in cidList :
            cType = self.cfg['cType']
            cidUsfm = self.getCidPath(cid)
            # Test for source here and die if it isn't there
            if not os.path.isfile(cidUsfm) :
                self.log.writeToLog(self.errorCodes['0220'], [cidUsfm], 'usfm.preProcessGroup():0220')

            # Add/manage the dependent files for this cid
            if self.macPack == 'usfmTex' or self.macPack == 'ptx2pdf' :
                # Component adjustment file
                cidAdjFile = self.getCidAdjPath(cid)
                if useManualAdjustments :
                    if not os.path.isfile(cidAdjFile) or self.tools.isOlder(cidAdjFile, self.adjustmentConfFile) :
                        # Remake the adjustment file (if needed)
                        self.createCompAdjustmentFile(cid)
                else :
                    # If no adjustments, remove any exsiting file
                    if os.path.isfile(cidAdjFile) :
                        os.remove(cidAdjFile)
                # Component piclist file
                cidPiclistFile = self.proj_illustration.getCidPiclistFile(cid)
                if useIllustrations :
                    if self.proj_illustration.hasIllustrations(gid, cid) :
                        # Create if not there or if the config has changed
                        if not os.path.isfile(cidPiclistFile) or self.tools.isOlder(cidPiclistFile, self.proj_config.illustrationConfFile) :
                            # First check if we have the illustrations we think we need
                            # and get them if we do not.
                            self.proj_illustration.getPics(gid, cid)
                            # Now make a fresh version of the piclist file
                            if self.proj_illustration.createPiclistFile(gid, cid) :
                                self.log.writeToLog(self.errorCodes['0260'], [cid])
                            else :
                                self.log.writeToLog(self.errorCodes['0265'], [cid])
                        else :
                            for f in [self.proj_config.layoutConfFile, self.proj_config.illustrationConfFile] :
                                if self.tools.isOlder(cidPiclistFile, f) or not os.path.isfile(cidPiclistFile) :
                                    # Remake the piclist file
                                    if self.proj_illustration.createPiclistFile(gid, cid) :
                                        self.log.writeToLog(self.errorCodes['0260'], [cid])
                                    else :
                                        self.log.writeToLog(self.errorCodes['0265'], [cid])
                        # Do a quick check to see if the illustration files for this book
                        # are in the project. If it isn't, the run will be killed
                        self.proj_illustration.getPics(gid, cid)
                    else :
                        # Does not seem to be any illustrations for this cid
                        # clean out any piclist file that might be there
                        if os.path.isfile(cidPiclistFile) :
                            os.remove(cidPiclistFile)
                else :
                    # If we are not using illustrations then any existing piclist file will be removed
                    if os.path.isfile(cidPiclistFile) :
                        os.remove(cidPiclistFile)
                        self.log.writeToLog(self.errorCodes['0255'], [cid])


# FIXME: This error message is all wrong.



            else :
                self.log.writeToLog(self.errorCodes['0220'], [self.macPack], 'usfm.preProcessGroup():0220')

        # Background management
        bgList = self.projConfig['Managers'][self.cType + '_' + self.renderer.capitalize()][mode + 'Background']
        for bg in bgList :
            self.pg_background.checkForBackground(bg, mode)

        # Any more stuff to run?

        return True


    def checkStartPageNumber (self) :
        '''Adjust page number for the current group.'''

        # Be sure settings are in place
        self.checkStartPageNumberSettings()

#        import pdb; pdb.set_trace()

        # If none, that means it hasn't been set or it is first
        pGrp = str(self.projConfig['Groups'][self.gid]['precedingGroup'])
        if pGrp == 'None' :
            return False

        cStrPgNo = str(self.projConfig['Groups'][self.gid]['startPageNumber'])
        pGrpStrPgNo = int(self.projConfig['Groups'][pGrp]['startPageNumber'])
        pGrpPgs     = int(self.projConfig['Groups'][pGrp]['totalPages'])
        nStrPgNo    = (pGrpStrPgNo + pGrpPgs)
        if cStrPgNo != nStrPgNo :
            self.projConfig['Groups'][self.gid]['startPageNumber'] = nStrPgNo
            self.tools.writeConfFile(self.projConfig)


    def checkStartPageNumberSettings (self) :
        '''Make sure the page number settings are in place. This may be deprecated later.'''

        change = False
        if not self.projConfig['Groups'][self.gid].has_key('precedingGroup') :
            self.projConfig['Groups'][self.gid]['precedingGroup'] = None
            change = True
        if not self.projConfig['Groups'][self.gid].has_key('startPageNumber') :
            self.projConfig['Groups'][self.gid]['startPageNumber'] = 1
            change = True
        if change :
            self.tools.writeConfFile(self.projConfig)


    def createCompAdjustmentFile (self, cid) :
        '''Create an adjustment file for this cid. If entries exsist in
        the adjustment.conf file.'''

        description = 'Auto-generated text adjustments file for: ' + cid + '\n'

#        import pdb; pdb.set_trace()

        # Check for a master adj conf file
        if os.path.exists(self.adjustmentConfFile) :
            adjFile = self.getCidAdjPath(cid)
            if not self.adjustmentConfig.has_key(self.gid) :
                self.tools.buildConfSection(self.adjustmentConfig, self.gid)
                self.tools.buildConfSection(self.adjustmentConfig[self.gid], cid)
                self.adjustmentConfig[self.gid][cid]['%1.1'] = '1'
                self.tools.writeConfFile(self.adjustmentConfig)
                self.log.writeToLog(self.errorCodes['0240'], [self.gid])
                return False
            for c in self.adjustmentConfig[self.gid].keys() :
                try :
                    if c == 'GeneralSettings' :
                        continue
                    else :
                        comp = c.lower()
                except Exception as e :
                    # If this doesn't work, we should probably quite here
                    self.tools.dieNow('Error: Malformed component ID [' + c + '] in adjustment file: ' + str(e) + '\n')
                if  comp == cid and len(self.adjustmentConfig[self.gid][c].keys()) > 0 :
                    with codecs.open(adjFile, "w", encoding='utf_8') as writeObject :
                        writeObject.write(self.tools.makeFileHeader(adjFile, description, True))
                        # Output like this: JAS 1.13 +1
                        for k, v in self.adjustmentConfig[self.gid][c].iteritems() :
                            if k[0] in ['%', '#'] :
                                continue
                            adj = v
                            if int(v) > 0 : 
                                adj = '+' + str(v)
                            writeObject.write(comp.upper() + ' ' + k + ' ' + adj + '\n')

                        self.log.writeToLog(self.errorCodes['0230'], [self.tools.fName(adjFile)])
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
                self.tools.buildConfSection(self.adjustmentConfig, gid)
            for comp in self.projConfig['Groups'][gid]['cidList'] :
                if not self.adjustmentConfig[gid].has_key(comp) :
                    self.tools.buildConfSection(self.adjustmentConfig[gid], comp)
                self.adjustmentConfig[gid][comp]['%1.1'] = '1'
        self.tools.writeConfFile(self.adjustmentConfig)
        return True


###############################################################################
######################## USFM Component Text Functions ########################
###############################################################################
######################## Error Code Block Series = 0400 #######################
###############################################################################


    def getComponentType (self, gid) :
        '''Return the cType for a component.'''

#        import pdb; pdb.set_trace()

        try :
            cType = self.projConfig['Groups'][gid]['cType']
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.log.writeToLog('COMP-200', ['Key not found ' + str(e)])
            self.tools.dieNow()

        return cType


    def isCompleteComponent (self, gid, cid) :
        '''A two-part test to see if a component has a config entry and a file.'''

        if self.hasCidFile(gid, cid) :
            return True


    def hasUsfmCidInfo (self, cid) :
        '''Return True if this cid is in the PT USFM cid info dictionary.'''

        if cid in self.usfmCidInfo().keys() :
            return True


    def hasCidFile (self, gid, cid) :
        '''Return True or False depending on if a working file exists 
        for a given cName.'''

        cType = self.projConfig['Groups'][gid]['cType']
        return os.path.isfile(os.path.join(self.local.projComponentFolder, cid, cid + '.' + cType))


