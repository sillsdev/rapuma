#!/usr/bin/python
# -*- coding: utf_8 -*-
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project data editing operations.

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


class ProjEdit (object) :

    def __init__(self, pid) :
        '''Intitate the whole class and create the object.'''

        self.pid            = pid
        self.tools          = Tools()
        self.rapumaHome     = os.environ.get('RAPUMA_BASE')
        self.userHome       = os.environ.get('RAPUMA_USER')
        self.user           = UserConfig(self.rapumaHome, self.userHome)
        self.userConfig     = self.user.userConfig
        self.projConfig     = ProjConfig(pid).projConfig
        self.projHome       = None
        self.local          = None

        self.finishInit()

        # Log messages for this module
        self.errorCodes     = {
            'EDIT-000' : ['MSG', 'Messages for editing project and setting files.'],
            'EDIT-005' : ['MSG', 'Unassigned error message ID.'],
            'EDIT-010' : ['ERR', 'The component [<<1>>] has multiple subcomponents and cannot be opened for editing. Please work with the individual subcomponents.'],
            'EDIT-020' : ['ERR', 'Working text file [<<1>>] not found.'],
            'EDIT-030' : ['ERR', 'No files found to edit with the commands supplied.'],
            'EDIT-040' : ['MSG', 'Component files for [<<1>>] have been opened in your file editor.'],

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


###############################################################################
################################ Edit Functions ###############################
###############################################################################
####################### Error Code Block Series = 0200 ########################
###############################################################################


# FIXME: Still lots to do on this next function

    def edit (self, cName = None, glob = False, sys = False) :
        '''Call editing application to edit various project and system files.'''

        editDocs = ['gedit']
        # If a subcomponent is called, pull it up and its dependencies
        # This will not work with components that have more than one
        # subcomponent.
        if cName :
            # Probably need to create the component object now
            self.createComponent(cName)

            cid = self.components[cName].getUsfmCid(cName)

            cType = self.groups[gid].getComponentType(gid)
            self.buildComponentObject(cType, cid)
            cidList = self.groups[gid].getSubcomponentList(gid)
            if len(cidList) > 1 :
                self.log.writeToLog('EDIT-010', [cid])
                self.tools.dieNow()

            self.createManager('text')
            compWorkText = self.groups[gid].getCidPath(cid)
            if os.path.isfile(compWorkText) :
                editDocs.append(compWorkText)
                compTextAdj = self.components[cName].getCidAdjPath(cid)
                compTextIlls = self.components[cName].getCidPiclistPath(cid)
                dep = [compTextAdj, compTextIlls]
                for d in dep :
                    if os.path.isfile(d) :
                        editDocs.append(d)
            else :
                self.log.writeToLog('EDIT-020', [self.tools.fName(compWorkText)])
                self.tools.dieNow()

        # Look at project global settings
        if glob :
            for files in os.listdir(self.local.projConfFolder):
                if files.endswith(".conf"):
                    editDocs.append(os.path.join(self.local.projConfFolder, files))

            globSty = os.path.join(self.local.projStyleFolder, self.projConfig['Managers']['usfm_Style']['mainStyleFile'])
            custSty = os.path.join(self.local.projStyleFolder, self.projConfig['Managers']['usfm_Style']['customStyleFile'])
            if os.path.isfile(globSty) :
                editDocs.append(globSty)
            if os.path.isfile(custSty) :
                editDocs.append(custSty)

            # FIXME: This next part is hard-wired, be nice to do better
            fileName = 'xetex_settings_usfm-ext.tex'
            macExt = os.path.join(self.local.projMacroFolder, 'usfmTex', fileName)
            editDocs.append(macExt)

        # Look at system setting files
        if sys :
            editDocs.append(self.local.userConfFile)

        # Pull up our docs in the editor
        if len(editDocs) > 1 :
            subprocess.call(editDocs)
            self.log.writeToLog('EDIT-040', [cName])
        else :
            self.log.writeToLog('EDIT-030')




