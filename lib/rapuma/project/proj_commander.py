#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project command helper scripts creation.

###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os
from configobj import ConfigObj

# Load the local classes
from rapuma.core.tools                  import Tools
from rapuma.core.user_config            import UserConfig
from rapuma.core.proj_local             import ProjLocal
from rapuma.project.proj_config         import Config


class ProjCommander (object) :

    def __init__(self, pid) :
        '''Intitate the whole class and create the object.'''

        self.pid                    = pid
        self.tools                  = Tools()
        self.user                   = UserConfig()
        self.userConfig             = self.user.userConfig
        self.projHome               = self.userConfig['Projects'][self.pid]['projectPath']
        self.projectMediaIDCode     = self.userConfig['Projects'][self.pid]['projectMediaIDCode']
        self.local                  = ProjLocal(self.pid)
        self.proj_config            = Config(pid)
        self.proj_config.getProjectConfig()
        self.projectConfig          = self.proj_config.projectConfig

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

        if not os.path.isdir(self.local.projHelpScriptFolder) :
            os.mkdir(self.local.projHelpScriptFolder)

        self.makeStaticScripts()
        self.makeGrpScripts()


    def makeGrpScripts (self) :
        '''Create scripts that process specific group components.'''

        # Output the scripts (If this is a new project we need to pass)
        if self.projectConfig.has_key('Groups') :
            for gid in self.projectConfig['Groups'].keys() :
                allScripts = self.getGrpScripInfo(gid)
                for key in allScripts.keys() :
                    fullFile = os.path.join(self.local.projHelpScriptFolder, key) + gid
                    with codecs.open(fullFile, "w", encoding='utf_8') as writeObject :
                        writeObject.write(self.makeScriptHeader(allScripts[key][0], allScripts[key][1]))
                        writeObject.write(allScripts[key][1] + '\n\n')

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

        return '#!/bin/sh\n\n# Description: ' + desc + '\n\necho \necho Rapuma helper script: ' + desc + '\n\necho \necho command: ' + cmd + '\n\n'


    def getStaticScripInfo (self) :
        '''Create a dictionary of all the static auxillary script information used in
        most projects.'''

        pid     = self.pid
        mid     = self.projectMediaIDCode

        return {
                'addBible'      : ['Add Scripture components for a Bible group.',   'rapuma group '         + pid + ' Bible group add --component_type usfm --source_id base --source_path $1 --cid_list "gen exo lev num deu jos jdg rut 1sa 2sa 1ki 2ki 1ch 2ch ezr neh est job psa pro ecc sng isa jer lam ezk dan hos jol amo oba jon mic nam hab zep hag zec mal mat mrk luk jhn act rom 1co 2co gal eph php col 1th 2th 1ti 2ti tit phm heb jas 1pe 2pe 1jn 2jn 3jn jud rev"'], 
                'addNT'         : ['Add Scripture components for an NT group.',     'rapuma group '         + pid + ' NT    group add --component_type usfm --source_id base --source_path $1 --cid_list "mat mrk luk jhn act rom 1co 2co gal eph php col 1th 2th 1ti 2ti tit phm heb jas 1pe 2pe 1jn 2jn 3jn jud rev"'], 
                'addOT'         : ['Add Scripture components for an OT group.',     'rapuma group '         + pid + ' OT    group add --component_type usfm --source_id base --source_path $1 --cid_list "gen exo lev num deu jos jdg rut 1sa 2sa 1ki 2ki 1ch 2ch ezr neh est job psa pro ecc sng isa jer lam ezk dan hos jol amo oba jon mic nam hab zep hag zec mal"'], 
                'archive'       : ['Archive this project',                          'rapuma project '       + pid + ' archive   save '], 
                'backup'        : ['Backup this project',                           'rapuma project '       + pid + ' backup    save '], 
                'cloudPull'     : ['Pull data for this project from the cloud',     'rapuma project '       + pid + ' cloud     restore $1 '], 
                'cloudPush'     : ['Push data from this project to the cloud',      'rapuma project '       + pid + ' cloud     save $1 '], 
                'restore'       : ['Restore a backup.',                             'rapuma project '       + pid + ' backup    restore '], 
                'template'      : ['Create a template of the project.',             'rapuma project '       + pid + ' template  save --id $1 '], 
                'updateScripts' : ['Update the project scripts.',                   'rapuma project '       + pid + ' helper    update '], 
                'updateGroups'  : ['Update all the groups in a project.',           'rapuma project '       + pid + ' groups    update $1 '], 
                'bind'          : ['Create the binding PDF file',                   'rapuma project '       + pid + ' project   bind '], 
                'placeholdOff'  : ['Turn off illustration placeholders.',           'rapuma settings '      + pid + ' ' + mid + '_layout Illustrations useFigurePlaceHolders False '], 
                'placeholdOn'   : ['Turn on illustration placeholders.',            'rapuma settings '      + pid + ' ' + mid + '_layout Illustrations useFigurePlaceHolders True '] 
            }


    def getGrpScripInfo (self, gid) :
        '''Create a dictionary of the auxillary group script information used in
        most projects.'''

        # Load local versions of the macPack config
        macPackConfig   = Config(self.pid, gid).macPackConfig
        # Set the vars for this function
        pid         = self.pid
        cType       = self.projectConfig['Groups'][gid]['cType']
        renderer    = self.projectConfig['CompTypes'][cType.capitalize()]['renderer']
        font        = ''
        if macPackConfig and macPackConfig['FontSettings'].has_key('primaryFont') :
            font    = macPackConfig['FontSettings']['primaryFont']
        macro       = self.projectConfig['CompTypes'][cType.capitalize()]['macroPackage']
        mid         = self.projectMediaIDCode
        # Return a dictionary of all the commands we generate
        return {
                'compareSource' : ['Compare component working text with source.',   'rapuma component ' + pid + ' ' + gid + ' $1 --compare source'], 
                'compareWork'   : ['Compare working text with previous version.',   'rapuma component ' + pid + ' ' + gid + ' $1 --compare working'], 
                'edit'          : ['Edit specified component file.',                'rapuma component ' + pid + ' ' + gid + ' --edit $1 '], 
                'hyphenOff'     : ['Turn off hyphenation in a group.',              'rapuma group '     + pid + ' ' + gid + ' hyphenation   remove '], 
                'hyphenOn'      : ['Turn on hyphenation in a group.',               'rapuma group '     + pid + ' ' + gid + ' hyphenation   add '], 
                'hyphenUpdate'  : ['Update hyphenation in a group.',                'rapuma group '     + pid + ' ' + gid + ' hyphenation   update $1 '], 
                'draft'         : ['Create ' + gid + ' group PDF draft file.',      'rapuma group '     + pid + ' ' + gid + ' group         draft   --cid_list \"$1\" --force '], 
                'proof'         : ['Create ' + gid + ' group PDF proof file.',      'rapuma group '     + pid + ' ' + gid + ' group         proof   --cid_list \"$1\" --force '], 
                'final'         : ['Create ' + gid + ' group PDF final file.',      'rapuma group '     + pid + ' ' + gid + ' group         final   --cid_list \"$1\" --force '], 
                'update'        : ['Update the ' + gid + ' group from its source.', 'rapuma group '     + pid + ' ' + gid + ' group         update  --cid_list \"$1\" $2 '], 
                'updateFont'    : ['Update the ' + gid + ' font.',                  'rapuma package '   + pid + ' ' + gid + ' \"' + font + '\" font update '], 
                'updateMacro'   : ['Update the ' + gid + ' macro package.',         'rapuma package '   + pid + ' ' + gid + ' \"' + macro + '\" macro update '] 
            }




