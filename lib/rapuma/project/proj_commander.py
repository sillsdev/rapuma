#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (sparkycbr at gmail dot com)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project command helper scripts creation.

###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, re
from configobj import ConfigObj

# Load the local classes
from rapuma.core.tools                  import Tools
from rapuma.core.user_config            import UserConfig
from rapuma.core.proj_local             import ProjLocal
from rapuma.project.proj_config         import Config
from rapuma.project.proj_macro          import Macro


class ProjCommander (object) :

    def __init__(self, pid) :
        '''Intitate the whole class and create the object.'''

        self.pid                    = pid
        self.tools                  = Tools()
        self.user                   = UserConfig()
        self.userConfig             = self.user.userConfig
        self.projHome               = os.path.join(os.environ['RAPUMA_PROJECTS'], self.pid)
        self.local                  = ProjLocal(self.pid)
        self.proj_config            = Config(pid)
        self.proj_config.getProjectConfig()
        self.projectConfig          = self.proj_config.projectConfig
        self.projectMediaIDCode     = self.projectConfig['ProjectInfo']['projectMediaIDCode']

        # Log messages for this module
        self.errorCodes     = {
            '0000' : ['MSG', 'Placeholder message'],
        }


###############################################################################
########################## Command Creation Functions #########################
###############################################################################

    def removeScripts (self) :
        '''Remove any unnecessary group control scripts from the project.'''

        self.tools.dieNow('removeScripts() not implemented yet.')


    def updateScripts (self) :
        '''Update all the helper command scripts in a project.'''

        self.makeStaticScripts()
        self.makeGrpScripts()


    def makeGrpScripts (self) :
        '''Create scripts that process specific group components.'''

        if not os.path.isdir(self.local.projHelpScriptFolder) :
            os.mkdir(self.local.projHelpScriptFolder)

        # Output the scripts (If this is a new project we need to pass)
        if self.projectConfig.has_key('Groups') :
            for gid in self.projectConfig['Groups'].keys() :
                allScripts = self.getGrpScripInfo(gid)
                for key in allScripts.keys() :
                    fullFile = os.path.join(self.local.projHelpScriptFolder, key) + gid
                    with codecs.open(fullFile, "w", encoding='utf_8') as writeObject :
                        writeObject.write(self.makeScriptHeader(allScripts[key][0], allScripts[key][1]))
                        # Strip out extra spaces from command
                        cmd = re.sub(ur'\s+', ur' ', allScripts[key][1])
                        writeObject.write(cmd + '\n\n')

                    # Make the script executable
                    self.tools.makeExecutable(fullFile)
            
            self.tools.terminal('\nCompleted creating/recreating group helper scripts.\n')
        else :
            pass


    def makeStaticScripts (self) :
        '''Create helper scripts for a project to help with repetitive tasks.
        If any scripts are present with the same name they will be overwritten.
        Note: This is only for temporary use due to the lack of an interface at
        this time (20130306140636). It assumes the cType is usfm which, at some point
        may not be the case.'''

        if not os.path.isdir(self.local.projHelpScriptFolder) :
            os.mkdir(self.local.projHelpScriptFolder)

        # Output the scripts
        allScripts = self.getStaticScripInfo()
        for key in allScripts.keys() :
            fullFile = os.path.join(self.local.projHelpScriptFolder, key)
            with codecs.open(fullFile, "w", encoding='utf_8') as writeObject :
                writeObject.write(self.makeScriptHeader(allScripts[key][0], allScripts[key][1]))
                writeObject.write(allScripts[key][1] + '\n\n')

            # Make the script executable
            self.tools.makeExecutable(fullFile)

        self.tools.terminal('\nCompleted creating/recreating static helper scripts.\n')


    def makeScriptHeader (self, desc, cmd) :
        '''Make a helper script header.'''

        return '#!/bin/sh\n\n# Description: ' + desc + '\n\necho \necho Rapuma helper script: ' + desc + '\n\necho \necho command: ' + self.echoClean(cmd) + '\n\n'


    def echoClean (self, cmdStr) :
        '''Clean up a string for an echo statement in a shell script.'''

        clean = re.sub(ur'\;', ur'\\;', cmdStr)
        clean = re.sub(ur'\s+', ur' ', clean)

        return clean


    def getStaticScripInfo (self) :
        '''Create a dictionary of all the static auxillary script information used in
        most projects.'''

        pid                 = self.pid
        mid                 = self.projectMediaIDCode

        return {
                'addBible'      : ['Add Scripture components for a Bible group.',   'rapuma group '         + pid + ' BIBLE group add --source_path $1 '], 
                'addNT'         : ['Add Scripture components for an NT group.',     'rapuma group '         + pid + ' NT    group add --source_path $1 '], 
                'addOT'         : ['Add Scripture components for an OT group.',     'rapuma group '         + pid + ' OT    group add --source_path $1 '], 
                'archive'       : ['Archive this project',                          'rapuma project '       + pid + ' archive   save '], 
                'backup'        : ['Backup this project',                           'rapuma project '       + pid + ' backup    save '], 
                'cloudPull'     : ['Pull data for this project from the cloud',     'rapuma project '       + pid + ' cloud     restore '], 
                'cloudPush'     : ['Push data from this project to the cloud',      'rapuma project '       + pid + ' cloud     save $1 '], 
                'restore'       : ['Restore a backup.',                             'rapuma project '       + pid + ' backup    restore '], 
                'template'      : ['Create a template of the project.',             'rapuma project '       + pid + ' template  save --id $1 '], 
                'updateScripts' : ['Update the project scripts.',                   'rapuma project '       + pid + ' project update --update_type helper '], 
                'bind'          : ['Create the binding PDF file',                   'if [ "$1" ]; then CMD=" $1"; fi; if [ "$2" ]; then CMD=" $1 $2"; fi; rapuma project ' + pid + ' project bind $CMD '], 
                'placeholdOff'  : ['Turn off illustration placeholders.',           'rapuma settings '      + pid + ' ' + mid + '_layout Illustrations useFigurePlaceHolders False '], 
                'placeholdOn'   : ['Turn on illustration placeholders.',            'rapuma settings '      + pid + ' ' + mid + '_layout Illustrations useFigurePlaceHolders True '] 
            }


    def getGrpScripInfo (self, gid) :
        '''Create a dictionary of the auxillary group script information used in
        most projects.'''

#        import pdb; pdb.set_trace()

        # Set the vars for this function
        pid                 = self.pid
        cType               = self.projectConfig['Groups'][gid]['cType']
        Ctype               = cType.capitalize()
        renderer            = self.projectConfig['CompTypes'][Ctype]['renderer']
        self.proj_macro     = Macro(self.pid, gid)
        macroConfig         = self.proj_macro.macroConfig
        font                = ''
        if macroConfig and macroConfig['FontSettings'].has_key('primaryFont') :
            font            = macroConfig['FontSettings']['primaryFont']
        macro               = self.projectConfig['CompTypes'][Ctype]['macroPackage']
        mid                 = self.projectMediaIDCode
        # Return a dictionary of all the commands we generate
        return {
                'compare'       : ['Compare component working text with backup.',   'if [ "$1" ]; then CMD="--cid_list $1"; fi; rapuma group ' + pid + ' ' + gid + ' group compare --compare_type backup $CMD '], 
                'render'        : ['Render ' + gid + ' group PDF file.',            'if [ "$1" ]; then CMD="--cid_list $1"; fi; if [ "$2" ]; then CMD="--cid_list $1 $2"; fi; if [ "$3" ]; then CMD="--cid_list $1 $2 $3"; fi; rapuma group ' + pid + ' ' + gid + ' group render $CMD '], 
                'update'        : ['Update the ' + gid + ' group from its source.', 'if [ "$2" ]; then CMD="--cid_list $2"; fi; rapuma group ' + pid + ' ' + gid + ' group update --source_path $1 $CMD '], 
                'background'    : ['Re/Create the project background.',             'rapuma project '   + pid + ' project update --update_type background '], 
                'transparency'  : ['Re/Create the project diagnostic layer.',       'rapuma project '   + pid + ' project update --update_type diagnostic '], 
                'addFont'       : ['Add a font to the ' + gid + ' group.',          'rapuma package '   + pid + ' ' + gid + ' $1 font add -f '],
                'removeFont'    : ['Remove a font from the ' + gid + ' group.',     'rapuma package '   + pid + ' ' + gid + ' $1 font remove -f '],
                'primaryFont'   : ['Make font primary for the ' + gid + ' group.',  'rapuma package '   + pid + ' ' + gid + ' $1 font primary -f '],
                'updateFont'    : ['Update the ' + gid + ' font.',                  'rapuma package '   + pid + ' ' + gid + ' \"' + font + '\" font update '], 
                'updateMacro'   : ['Update the ' + gid + ' macro package.',         'rapuma package '   + pid + ' ' + gid + ' \"' + macro + '\" macro update '] 
            }




