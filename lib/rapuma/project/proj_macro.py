
#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle macros in book projects.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, codecs

# Load the local classes
from rapuma.core.tools                  import Tools, ToolsPath, ToolsGroup
from rapuma.core.user_config            import UserConfig
from rapuma.core.proj_local             import ProjLocal
from rapuma.core.proj_log               import ProjLog
from rapuma.project.proj_config         import ProjConfig


###############################################################################
################################## Begin Class ################################
###############################################################################

class ProjMacro (object) :

    def __init__(self, pid, gid) :
        '''Do the primary initialization for this class.'''

        self.pid                        = pid
        self.gid                        = gid
        self.tools                      = Tools()
        self.user                       = UserConfig()
        self.userConfig                 = self.user.userConfig
        self.projHome                   = self.userConfig['Projects'][self.pid]['projectPath']
        self.mType                      = self.userConfig['Projects'][self.pid]['projectMediaIDCode']
        self.local                      = ProjLocal(pid)
        self.proj_config                = ProjConfig(pid, gid)
        self.projConfig                 = self.proj_config.projConfig
        
        
# FIXME: If proj_config doesn't give us the macPackConfig, what do we do?
        
        
        self.macPackConfig              = self.proj_config.macPackConfig
        
        
        self.log                        = ProjLog(pid)
        self.tools_path                 = ToolsPath(self.local, self.projConfig, self.userConfig)
        self.tools_group                = ToolsGroup(self.local, self.projConfig, self.userConfig)
        self.cType                      = self.projConfig['Groups'][self.gid]['cType']
        self.Ctype                      = self.cType.capitalize()
        self.macPack                    = self.projConfig['CompTypes'][self.Ctype]['macroPackage']
        # File names
        self.macPackFileName            = self.macPack + '.zip'
        # Folder paths
        self.projConfFolder             = self.local.projConfFolder
        self.projMacrosFolder           = self.local.projMacrosFolder
        self.rapumaMacrosFolder         = self.local.rapumaMacrosFolder
        self.projMacPackFolder          = os.path.join(self.local.projMacrosFolder, self.macPack)
        # File names with paths
        self.macPackXmlConfFile         = self.proj_config.macPackXmlConfFile
#        self.macPackFile                = os.path.join(self.projMacPackFolder, self.macPackFileName)
        self.rapumaMacPackFile          = os.path.join(self.rapumaMacrosFolder, self.macPackFileName)

        # Log messages for this module
        self.errorCodes     = {

            '0050' : ['MSG', 'Placeholder message'],

            'MCRO-000' : ['MSG', 'Messages for user macro issues (mainly found in project.py)'],
            'MCRO-010' : ['ERR', 'This macro [<<1>>] is already registered for this project. Use force -f to overwrite it.'],
            'MCRO-020' : ['ERR', 'The macro file [<<1>>] already exsists in this project. Use force -f to overwrite it.'],
            'MCRO-030' : ['MSG', 'The macro file [<<1>>] has been installed into this project.'],
            'MCRO-050' : ['MSG', 'Running macro command: [<<1>>]'],
            'MCRO-060' : ['ERR', 'Macro file not found: [<<1>>]'],
            '1000' : ['MSG', 'Placeholder message'],

            '0250' : ['ERR', 'Failed to install macro package: [<<1>>]']

        }



###############################################################################
################################ Add Functions ################################
###############################################################################
######################## Error Code Block Series = 0200 #######################
###############################################################################

    def addMacPack (self, force = False) :
        '''Add a macro package to the project.'''

        if os.path.exists(self.projMacPackFolder) and force :
            self.removeMacPack(force)

        if not self.tools.pkgExtract(self.rapumaMacPackFile, self.projMacrosFolder, self.macPackXmlConfFile) :
            self.log.writeToLog(self.errorCodes['0250'], [self.macPack])


    def getAdjustmentConfFile (self) :
        '''Return the full path and name of the adjustment file if the
        macro package requires it. Return null if not required.'''
        
        adjustmentConfFile     = ''
        if self.macPack in ['usfmTex', 'ptx2pdf'] :
            adjustmentConfFileName = self.macPackConfig['ParagraphAdjustments']['paragraphAdjustmentsFile']
            adjustmentConfFile = os.path.join(self.projConfFolder, adjustmentConfFileName)

        return adjustmentConfFile


###############################################################################
############################## Remove Functions ###############################
###############################################################################
######################## Error Code Block Series = 0400 #######################
###############################################################################

    def removeMacPack (self, package, force = False) :
        '''Remove a macro package from a project.'''

        return True


###############################################################################
############################## Update Functions ###############################
###############################################################################
######################## Error Code Block Series = 0600 #######################
###############################################################################

    def updateMacPack (self, package, force = False) :
        '''Update a macro package with the latest version from Rapuma.'''

        pass


###############################################################################
########################### TeX Handling Functions ############################
###############################################################################
######################## Error Code Block Series = 0800 #######################
###############################################################################





###############################################################################
######################## User Macro Handling Functions ########################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################

# FIXME: All the code below is not currently working, needs rewriting

    def addUserMacro (self, name, cmd = None, path = None, force = False) :
        '''Install a user defined macro.'''

        # Define some internal vars
        oldMacro            = ''
        sourceMacro         = ''
        # FIXME: This needs to support a file extention such as .sh
        if path and os.path.isfile(os.path.join(self.tools.resolvePath(path))) :
            sourceMacro     = os.path.join(self.tools.resolvePath(path))
        macroTarget         = os.path.join(self.local.projUserMacrosFolder, name)
        if self.projConfig['GeneralSettings'].has_key('userMacros') and name in self.projConfig['GeneralSettings']['userMacros'] :
            oldMacro = name

        # First check for prexsisting macro record
        if not force :
            if oldMacro :
                self.log.writeToLog('MCRO-010', [oldMacro])
                self.tools.dieNow()

        # Make the target folder if needed (should be there already, though)
        if not os.path.isdir(self.local.projUserMacrosFolder) :
            os.makedirs(self.local.projUserMacrosFolder)

        # First check to see if there already is a macro file, die if there is
        if os.path.isfile(macroTarget) and not force :
            self.log.writeToLog('MCRO-020', [self.tools.fName(macroTarget)])

        # If force, then get rid of the file before going on
        if force :
            if os.path.isfile(macroTarget) :
                os.remove(macroTarget)

        # No script found, we can proceed
        if os.path.isfile(sourceMacro) :
            shutil.copy(sourceMacro, macroTarget)
        else :
            # Create a new user macro file
            mf = codecs.open(macroTarget, 'w', 'utf_8_sig')
            mf.write('#!/bin/sh\n\n')
            mf.write('# This macro file was auto-generated by Rapuma. Add commands as desired.\n\n')
            # FIXME: This should be done as a list so multiple commands can be added
            if cmd :
                mf.write(cmd + '\n')
            mf.close

        # Be sure that it is executable
        makeExecutable(macroTarget)

        # Record the macro with the project
        if self.projConfig['GeneralSettings'].has_key('userMacros') :
            macroList = self.projConfig['GeneralSettings']['userMacros']
            if self.tools.fName(macroTarget) not in macroList :
                self.projConfig['GeneralSettings']['userMacros'] = self.tools.addToList(macroList, self.tools.fName(macroTarget))
                self.tools.writeConfFile(self.projConfig)
        else :
                self.projConfig['GeneralSettings']['userMacros'] = [self.tools.fName(macroTarget)]
                self.tools.writeConfFile(self.projConfig)

        self.log.writeToLog('MCRO-030', [self.tools.fName(macroTarget)])
        return True


    def runUserMacro (self, name) :
        '''Run an installed, user defined macro.'''

        # In most cases we use subprocess.call() to do a process call.  However,
        # in this case it takes too much fiddling to get a these more complex Rapuma
        # calls to run from within Rapuma.  To make it easy, we use os.system() to
        # make the call out.
        macroFile = os.path.join(self.local.projUserMacrosFolder, name)
        if os.path.isfile(macroFile) :
            if self.macroRunner(macroFile) :
                return True
        else :
            self.log.writeToLog('MCRO-060', [self.tools.fName(macroFile)])


    def macroRunner (self, macroFile) :
        '''Run a macro. This assumes the macroFile includes a full path.'''

        try :
            macro = codecs.open(macroFile, "r", encoding='utf_8')
            for line in macro :
                # Clean the line, may be a BOM to remove
                line = line.replace(u'\ufeff', '').strip()
                if line[:1] != '#' and line[:1] != '' and line[:1] != '\n' :
                    self.log.writeToLog('MCRO-050', [line])
                    # FIXME: Could this be done better with subprocess()?
                    os.system(line)
            return True

        except Exception as e :
            # If we don't succeed, we should probably quite here
            terminal('Macro failed with the following error: ' + str(e))
            self.tools.dieNow()





