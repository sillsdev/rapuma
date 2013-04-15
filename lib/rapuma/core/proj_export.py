#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project data exporting operations.

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


class ProjExport (object) :

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
            '0000' : ['MSG', 'Placeholder message'],
            'XPRT-000' : ['MSG', 'Messages for export issues (probably only in project.py)'],
            'XPRT-005' : ['MSG', 'Unassigned error message ID.'],
            'XPRT-010' : ['ERR', 'Export file name could not be formed with available configuration information.'],
            'XPRT-020' : ['ERR', 'Unable to export: [<<1>>].'],
            'XPRT-030' : ['MSG', 'Files exported to [<<1>>].'],
            'XPRT-040' : ['MSG', 'Beginning export, please wait...'],
            'XPRT-050' : ['MSG', 'Unassigned error message ID.'],
        }


    def finishInit (self, projHome = None) :
        '''Finishing collecting settings that would be needed for most
        functions in this module.'''

        # Look for an existing project home path
        if self.isProject(self.pid) :
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


    def isProject (self, pid) :
        '''Simple test to see if a project is registered in the Rapuma config.'''

        try :
            projHome = self.userConfig['Projects'][pid]['projectPath']
            return True
        except :
            return False


###############################################################################
############################### Export Functions ##############################
###############################################################################
####################### Error Code Block Series = 0200 ########################
###############################################################################


    def export (self, cType, cName, path = None, script = None, bundle = False, force = False) :
        '''Facilitate the exporting of project text. It is assumed that the
        text is clean and ready to go and if any extraneous publishing info
        has been injected into the text, it will be removed by an appropreate
        post-process that can be applied by this function. No validation
        will be initiated by this function.'''
        
        # FIXME - Todo: add post processing script feature

        # Probably need to create the component object now
        self.createComponent(cName)

        # Figure out target path
        if path :
            path = self.tools.resolvePath(path)
        else :
            parentFolder = os.path.dirname(self.local.projHome)
            path = os.path.join(parentFolder, 'Export')

        # Make target folder if needed
        if not os.path.isdir(path) :
            os.makedirs(path)

        # Start a list for one or more files we will process
        fList = []

        # Will need the stylesheet for copy
        projSty = self.projConfig['Managers'][cType + '_Style']['mainStyleFile']
        projSty = os.path.join(self.local.projStylesFolder, projSty)
        # Process as list of components

        self.log.writeToLog('XPRT-040')
        for cid in self.components[cName].getSubcomponentList(cName) :
            cidCName = self.components[cName].getRapumaCName(cid)
            ptName = PT_Tools(self).formPTName(cName, cid)
            # Test, no name = no success
            if not ptName :
                self.log.writeToLog('XPRT-010')
                self.tools.dieNow()

            target = os.path.join(path, ptName)
            source = os.path.join(self.local.projComponentsFolder, cidCName, cid + '.' + cType)
            # If shutil.copy() spits anything back its bad news
            if shutil.copy(source, target) :
                self.log.writeToLog('XPRT-020', [self.tools.fName(target)])
            else :
                fList.append(target)

        # Start the main process here
        if bundle :
            archFile = os.path.join(path, cName + '_' + ymd() + '.zip')
            # Hopefully, this is a one time operation but if force is not True,
            # we will expand the file name so nothing is lost.
            if not force :
                if os.path.isfile(archFile) :
                    archFile = os.path.join(path, cName + '_' + fullFileTimeStamp() + '.zip')

            myzip = zipfile.ZipFile(archFile, 'w', zipfile.ZIP_DEFLATED)
            for f in fList :
                # Create a string object from the contents of the file
                strObj = StringIO.StringIO()
                for l in open(f, "rb") :
                    strObj.write(l)
                # Write out string object to zip
                myzip.writestr(self.tools.fName(f), strObj.getvalue())
                strObj.close()
            # Close out the zip and report
            myzip.close()
            # Clean out the folder
            for f in fList :
                os.remove(f)
            self.log.writeToLog('XPRT-030', [self.tools.fName(archFile)])
        else :
            self.log.writeToLog('XPRT-030', [path])

        return True




