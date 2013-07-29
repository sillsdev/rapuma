
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

#        import pdb; pdb.set_trace()

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
        self.log                        = ProjLog(pid)
        self.tools_path                 = ToolsPath(self.local, self.projConfig, self.userConfig)
        self.tools_group                = ToolsGroup(self.local, self.projConfig, self.userConfig)
        self.cType                      = self.projConfig['Groups'][self.gid]['cType']
        self.Ctype                      = self.cType.capitalize()
        # Folder paths
        self.projConfFolder             = self.local.projConfFolder
        self.projMacrosFolder           = self.local.projMacrosFolder
        self.rapumaMacrosFolder         = self.local.rapumaMacrosFolder

        # Some vars that are handled separately
        if self.proj_config.macPack :
            self.macPack                = self.proj_config.macPack
            # File names
            self.macPackFileName        = self.macPack + '.zip'
            # Folder paths
            self.projMacPackFolder      = os.path.join(self.local.projMacrosFolder, self.macPack)
            # File names with paths
            self.macPackXmlConfFile     = self.proj_config.macPackXmlConfFile
            self.rapumaMacPackFile      = os.path.join(self.rapumaMacrosFolder, self.macPackFileName)
            self.macPackConfig          = self.proj_config.macPackConfig

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

            '1100' : ['ERR', 'Macro package: [<<1>>] already exists in the project. Use force (-f) to reinstall.'],
            '1250' : ['ERR', 'Failed to install macro package: [<<1>>]'],

            '2100' : ['MSG', 'Force set to True. Removed macro package configuration file: [<<1>>]'],
            '2200' : ['MSG', 'Removed macro package [<<1>>] folder and all files contained.']

        }


###############################################################################
################################ Add Functions ################################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################

#    def initMacPackVals (self) :
#        '''It is necessary to be able to call this at different times during
#        the process to initialize these values.'''

#        self.macPack                = self.proj_config.macPack
#        # File names
#        self.macPackFileName        = self.macPack + '.zip'
#        # Folder paths
#        self.projMacPackFolder      = os.path.join(self.local.projMacrosFolder, self.macPack)
#        # File names with paths
#        self.macPackXmlConfFile     = self.proj_config.macPackXmlConfFile
#        self.rapumaMacPackFile      = os.path.join(self.rapumaMacrosFolder, self.macPackFileName)
#        self.macPackConfig          = self.proj_config.macPackConfig


#    def addMacPack (self, package, force = False) :
#        '''Add a macro package to the project. If force is set to True
#        remove the old macPack and install. Otherwise, do not touch
#        the existing macPack.'''

#        import pdb; pdb.set_trace()

#        # Set the projConf to the new/same package
#        self.projConfig['CompTypes'][self.Ctype]['macroPackage'] = package
#        self.tools.writeConfFile(self.projConfig)

#        # Re-init to be sure all the settings are right
#        self.__init__(self.pid, self.gid)

#        # Clear out existing macPack (but not conf file)
#        if os.path.exists(self.projMacPackFolder) :
#            if force :
#                self.removeMacPack(package)
#            else :
#                self.log.writeToLog(self.errorCodes['1100'], [package])

#        # If we got this far, install the a fresh copy of the macPack
#        if not self.tools.pkgExtract(self.rapumaMacPackFile, self.projMacrosFolder, self.macPackXmlConfFile) :
#            self.log.writeToLog(self.errorCodes['1250'], [self.macPack])


###############################################################################
############################## Remove Functions ###############################
###############################################################################
######################## Error Code Block Series = 2000 #######################
###############################################################################

#    def removeMacPack (self, package, force = False) :
#        '''Remove a macro package from a project. Using this will break a project
#        as installed font information will be lost from the macro config file
#        when it is deleted if force is used. However, there may be times this
#        is necessary. If force is not used it will retain the macro config file.
#        This is useful when you want to freshen the macro package but bad in
#        that custom style and TeX code.'''

#        # Set names and path for specified package
#        macPackConfFile     = os.path.join(self.local.projConfFolder, package + '.conf')
#        macPackFolder       = os.path.join(self.proj_config.projMacrosFolder, package)

#        # Remove the macPack config file if required
#        if os.path.exists(macPackConfFile) and force :
#            os.remove(macPackConfFile)
#            self.log.writeToLog(self.errorCodes['2100'], [self.tools.fName(macPackConfFile)])

#        # Now remove the macro folder (with all its contents)
#        if os.path.exists(macPackFolder) :
#            shutil.rmtree(macPackFolder)
#            self.log.writeToLog(self.errorCodes['2200'], [package])

#        # Remove the reference for this macro package from any component type
#        # that uses it. Normally that would probably be just be one of them.
#        for comp in self.projConfig['CompTypes'].keys() :
#            if self.projConfig['CompTypes'][comp]['macroPackage'] == package :
#                self.projConfig['CompTypes'][comp]['macroPackage'] = ''
#                self.tools.writeConfFile(self.projConfig)

###############################################################################
############################## Update Functions ###############################
###############################################################################
######################## Error Code Block Series = 3000 #######################
###############################################################################

    def updateMacPack (self, package, force = False) :
        '''Update a macro package with the latest version from Rapuma.'''

        pass


###############################################################################
########################### TeX Handling Functions ############################
###############################################################################
######################## Error Code Block Series = 4000 #######################
###############################################################################





###############################################################################
######################## User Macro Handling Functions ########################
###############################################################################
######################## Error Code Block Series = 5000 #######################
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





