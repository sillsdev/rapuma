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
from rapuma.core.tools          import Tools
from rapuma.core.proj_config    import ProjConfig
from rapuma.core.user_config    import UserConfig
from rapuma.core.proj_local     import ProjLocal


class Commander (object) :

    def __init__(self, pid) :
        '''Intitate the whole class and create the object.'''

        self.pid                = pid
        self.tools              = Tools()
        self.user               = UserConfig()
        self.userConfig         = self.user.userConfig
        self.projHome           = None
        self.projectMediaIDCode = None
        self.local              = None
        self.projConfig         = None
        self.finishInit()

        # Log messages for this module
        self.errorCodes     = {
            '0000' : ['MSG', 'Placeholder message'],
        }


    def finishInit (self) :
        '''Some times not all the information is available that is needed
        but that may not be a problem for some functions. We will atempt to
        finish the init here.'''

        try :
            self.projHome           = self.userConfig['Projects'][self.pid]['projectPath']
            self.projectMediaIDCode = self.userConfig['Projects'][self.pid]['projectMediaIDCode']
            self.local              = ProjLocal(self.pid)
            self.projConfig         = ProjConfig(self.local).projConfig
        except :
            pass


###############################################################################
########################## Command Creation Functions #########################
###############################################################################

    def removeScripts (self) :
        '''Remove any unnecessary group control scripts from the project.'''

        self.tools.dieNow('removeScripts() not implemented yet.')


    def updateScripts (self) :
        '''Update all the helper command scripts in a project.'''

        if not os.path.isdir(self.local.projScriptsFolder) :
            os.mkdir(self.local.projScriptsFolder)

        self.makeStaticScripts()
        self.makeGrpScripts()
        self.makeBndScripts()


    def makeGrpScripts (self) :
        '''Create scripts that process specific group components.'''

        # Output the scripts (If this is a new project we need to pass)
        if self.tools.isConfSection(self.projConfig, 'Groups') :
            for gid in self.projConfig['Groups'].keys() :
                allScripts = self.getGrpScripInfo(gid)
                for key in allScripts.keys() :
                    fullFile = os.path.join(self.local.projScriptsFolder, key) + gid
                    with codecs.open(fullFile, "w", encoding='utf_8') as writeObject :
                        writeObject.write(self.makeScriptHeader(allScripts[key][0], allScripts[key][1]))
                        writeObject.write(allScripts[key][1] + '\n\n')

                    # Make the script executable
                    self.tools.makeExecutable(fullFile)
            
            self.tools.terminal('\nCompleted creating/recreating group helper scripts.\n')
        else :
            pass


    def makeBndScripts (self) :
        '''Create scripts that process specific group components.'''

        # Output the scripts (If this is a new project we need to pass)
        if self.tools.isConfSection(self.projConfig, 'Binding') :
            for bid in self.projConfig['Binding'].keys() :
                allScripts = self.getBndScripInfo(bid)
                for key in allScripts.keys() :
                    fullFile = os.path.join(self.local.projScriptsFolder, key) + bid
                    with codecs.open(fullFile, "w", encoding='utf_8') as writeObject :
                        writeObject.write(self.makeScriptHeader(allScripts[key][0], allScripts[key][1]))
                        writeObject.write(allScripts[key][1] + '\n\n')

                    # Make the script executable
                    self.tools.makeExecutable(fullFile)

            self.tools.terminal('\nCompleted creating/recreating binding helper scripts.\n')
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
            fullFile = os.path.join(self.local.projScriptsFolder, key)
            with codecs.open(fullFile, "w", encoding='utf_8') as writeObject :
                writeObject.write(self.makeScriptHeader(allScripts[key][0], allScripts[key][1]))
                writeObject.write(allScripts[key][1] + '\n\n')

            # Make the script executable
            self.tools.makeExecutable(fullFile)

        # Outpu scripts for project groups
        # FIXME: write the code for this

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
                'addBible'      : ['Add Scripture components for a Bible group.',       'rapuma group ' + pid + ' Bible -c usfm -m add -d base -s $1 -i "gen exo lev num deu jos jdg rut 1sa 2sa 1ki 2ki 1ch 2ch ezr neh est job psa pro ecc sng isa jer lam ezk dan hos jol amo oba jon mic nam hab zep hag zec mal mat mrk luk jhn act rom 1co 2co gal eph php col 1th 2th 1ti 2ti tit phm heb jas 1pe 2pe 1jn 2jn 3jn jud rev"'], 
                'addNT'         : ['Add Scripture components for an NT group.',         'rapuma group ' + pid + ' NT -c usfm -m add -d base -s $1 -i "mat mrk luk jhn act rom 1co 2co gal eph php col 1th 2th 1ti 2ti tit phm heb jas 1pe 2pe 1jn 2jn 3jn jud rev"'], 
                'addOT'         : ['Add Scripture components for an OT group.',         'rapuma group ' + pid + ' OT -c usfm -m add -d base -s $1 -i "gen exo lev num deu jos jdg rut 1sa 2sa 1ki 2ki 1ch 2ch ezr neh est job psa pro ecc sng isa jer lam ezk dan hos jol amo oba jon mic nam hab zep hag zec mal"'], 
                'archive'       : ['Archive this project',                              'rapuma project ' + pid + ' -p archive '], 
                'backgroundOff' : ['Turn off all backgounds on output page.',           'rapuma background ' + pid + ' none'], 
                'backup'        : ['Backup this project',                               'rapuma project ' + pid + ' -p backup '], 
                'cloudPull'     : ['Pull data for this project from the cloud',         'rapuma project ' + pid + ' -r cloud '], 
                'cloudPush'     : ['Push data from this project to the cloud',          'rapuma project ' + pid + ' -p cloud '], 
                'cropmarksOff'  : ['Turn off cropmarks on output page.',                'rapuma background ' + pid + ' cropmarks -r'], 
                'cropmarksOn'   : ['Turn on cropmarks on output page.',                 'rapuma background ' + pid + ' cropmarks -a'], 
                'linesOff'      : ['Turn off line background.',                         'rapuma background ' + pid + ' lines -r'], 
                'linesOn'       : ['Turn on line background.',                          'rapuma background ' + pid + ' lines -a'], 
                'pageBoarderOff': ['Turn off page box on output page.',                 'rapuma background ' + pid + ' boarder -r'], 
                'pageBoarderOn' : ['Turn on page box on output page.',                  'rapuma background ' + pid + ' boarder -a'], 
                'placeholdOff'  : ['Turn off illustration placeholders.',               'rapuma settings ' + pid + ' ' + mid + '_layout Illustrations useFigurePlaceHolders False '], 
                'placeholdOn'   : ['Turn on illustration placeholders.',                'rapuma settings ' + pid + ' ' + mid + '_layout Illustrations useFigurePlaceHolders True '], 
                'restore'       : ['Restore a backup.',                                 'rapuma project ' + pid + ' -r backup '], 
                'template'      : ['Create a template of the project.',                 'rapuma project ' + pid + ' -r template $1 '], 
                'updateScripts' : ['Update the project scripts.',                       'rapuma project ' + pid + ' -c '], 
                'watermarkOff'  : ['Turn off watermark background.',                    'rapuma background ' + pid + ' watermark -r'], 
                'watermarkOn'   : ['Turn on watermark background.',                     'rapuma background ' + pid + ' watermark -a']
            }


    def getGrpScripInfo (self, gid) :
        '''Create a dictionary of the auxillary group script information used in
        most projects.'''

        pid     = self.pid
        cType   = self.projConfig['Groups'][gid]['cType']
        mid     = self.projectMediaIDCode

        return {
                'compareSource' : ['Compare component working text with source.',       'rapuma component ' + pid + ' ' + gid + ' $1 -c source'], 
                'compareWork'   : ['Compare working text with previous working text.',  'rapuma component ' + pid + ' ' + gid + ' $1 -c working'], 
                'edit'          : ['Edit specified component file.',                    'rapuma edit ' + pid + ' ' + gid + ' -c $1 -g -s'], 
                'hyphenOff'     : ['Turn off hyphenation in project.',                  'rapuma group ' + pid + ' ' + gid + ' -c ' + cType + ' -y remove  '], 
                'hyphenOn'      : ['Turn on hyphenation in project.',                   'rapuma group ' + pid + ' ' + gid + ' -c ' + cType + ' -y add  '], 
                'render'        : ['Render the ' + gid + ' group PDF file.',            'rapuma group ' + pid + ' ' + gid + ' -i \"$1\" -m execute -f '], 
                'update'        : ['Update the ' + gid + ' group from its source.',     'rapuma group ' + pid + ' ' + gid + ' -i \"$1\" -m update '], 
                'view'          : ['Render the ' + gid + ' group PDF file.',            'rapuma group ' + pid + ' ' + gid + ' -i \"$1\" -m execute '], 
            }


    def getBndScripInfo (self, bid) :
        '''Create a dictionary of the group binding script information used in
        most projects.'''

        pid     = self.pid

        return {
                'bind'          : ['Bind the ' + bid + ' groups to a PDF file.',        'rapuma binding ' + pid + ' ' + bid + ' -m execute '] 
            }






