#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project macro operations.

###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os
from configobj                  import ConfigObj

# Load the local classes
from rapuma.core.tools          import Tools
from rapuma.core.proj_config    import ProjConfig
from rapuma.core.user_config    import UserConfig
from rapuma.core.proj_local     import ProjLocal
from rapuma.core.proj_log       import ProjLog


class ProjMacro (object) :

    def __init__(self, pid) :
        '''Intitate the whole class and create the object.'''

        self.pid            = pid
        self.tools          = Tools()
        self.rapumaHome     = os.environ.get('RAPUMA_BASE')
        self.userHome       = os.environ.get('RAPUMA_USER')
        self.user           = UserConfig(self.rapumaHome, self.userHome)
        self.userConfig     = self.user.userConfig
        self.projHome       = None
        self.local          = None
        self.projConfig     = None
        self.finishInit()

        # Log messages for this module
        self.errorCodes     = {
            'MCRO-000' : ['MSG', 'Messages for user macro issues (mainly found in project.py)'],
            'MCRO-010' : ['ERR', 'This macro [<<1>>] is already registered for this project. Use force -f to overwrite it.'],
            'MCRO-020' : ['ERR', 'The macro file [<<1>>] already exsists in this project. Use force -f to overwrite it.'],
            'MCRO-030' : ['MSG', 'The macro file [<<1>>] has been installed into this project.'],
            'MCRO-050' : ['MSG', 'Running macro command: [<<1>>]'],
            'MCRO-060' : ['ERR', 'Macro file not found: [<<1>>]'],

            '0000' : ['MSG', 'Placeholder message'],
        }


    def finishInit (self, projHome = None) :
        '''Finishing collecting settings that would be needed for most
        functions in this module.'''

        # Look for an existing project home path
        if self.tools.isProject(self.pid) :
            localProjHome   = self.userConfig['Projects'][self.pid]['projectPath']
        else :
            localProjHome   = ''
        # Testing: The local project home wins over a user provided one
        if localProjHome and not projHome :
            self.projHome   = localProjHome
        elif projHome :
            self.projHome   = projHome
        
        # If a projHome was succefully found, we can go on
        if self.projHome : 
            self.local      = ProjLocal(self.rapumaHome, self.userHome, self.projHome)
            self.projConfig = ProjConfig(self.local).projConfig


###############################################################################
############################### Macro Functions ###############################
###############################################################################
####################### Error Code Block Series = 0200 ########################
###############################################################################


    def addMacro (self, name, cmd = None, path = None, force = False) :
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


    def runMacro (self, name) :
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


