#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project setup functions.

###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os
from configobj import ConfigObj
from importlib import import_module

# Load the local classes
from rapuma.core.tools          import *
from rapuma.core.proj_config    import ProjConfig
from rapuma.core.user_config    import UserConfig
from rapuma.core.proj_local     import ProjLocal
from rapuma.core.proj_commander import Commander
from rapuma.core.proj_log       import ProjLog


class ProjSetup (object) :

    def __init__(self, pid) :
        '''Intitate the whole class and create the object.'''

        self.rapumaHome         = os.environ.get('RAPUMA_BASE')
        self.userHome           = os.environ.get('RAPUMA_USER')
        self.user               = UserConfig(self.rapumaHome, self.userHome)
        self.userConfig         = self.user.userConfig
        self.pid                = pid
        self.projHome           = None
        self.projectMediaIDCode = None
        self.local              = None
        self.projConfig         = None
        self.log                = None
        self.groups             = {}
        self.finishInit()


    def finishInit (self) :
        '''Some times not all the information is available that is needed
        but that may not be a problem for some functions. We will atempt to
        finish the init here but will fail silently, which may not be a good
        idea in the long run.'''

#        import pdb; pdb.set_trace()

        try :
            self.projHome           = self.userConfig['Projects'][self.pid]['projectPath']
            self.projectMediaIDCode = self.userConfig['Projects'][self.pid]['projectMediaIDCode']
            self.local              = ProjLocal(self.rapumaHome, self.userHome, self.projHome)
            self.projConfig         = ProjConfig(self.local).projConfig
            self.log                = ProjLog(self.local, self.user)
        except :
            pass


###############################################################################
############################ Group Setup Functions ############################
###############################################################################


    def addComponentType (self, cType) :
        '''Add (register) a component type to the config if it 
        is not there already.'''

        Ctype = cType.capitalize()
        # Build the comp type config section
        buildConfSection(self.projConfig, 'CompTypes')
        buildConfSection(self.projConfig['CompTypes'], Ctype)

        # Get persistant values from the config if there are any
        newSectionSettings = getPersistantSettings(self.projConfig['CompTypes'][Ctype], os.path.join(self.local.rapumaConfigFolder, cType + '.xml'))
        if newSectionSettings != self.projConfig['CompTypes'][Ctype] :
            self.projConfig['CompTypes'][Ctype] = newSectionSettings
            # Save the setting rightaway
            writeConfFile(self.projConfig)


    def addCompGroupSourcePath (self, csid, source) :
        '''Add a source path for components used in a group if none
        exsist. If one exists, replace anyway. Last in wins! The 
        assumption is only one path per component group.'''

        # Path has been resolved in Rapuma, we assume it should be valid.
        # But it could be a full file name. We need to sort that out.
        try :
            if os.path.isdir(source) :
                self.userConfig['Projects'][self.pid][csid + '_sourcePath'] = source
            else :
                self.userConfig['Projects'][self.pid][csid + '_sourcePath'] = os.path.split(source)[0]

            writeConfFile(self.userConfig)
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.log.writeToLog('GRUP-100', [str(e)])
            dieNow()


    def addGroup (self, cType, gid, cidList, csid, sourcePath = None, force = False) :
        '''This handels adding a group which can contain one or more components. 
        Most of the prechecking was done in the calling script so we can assume that
        the vars here are pretty good.'''

        # Do not want to add this group, non-force, if it already exsists.
        buildConfSection(self.projConfig, 'Groups')
        if testForSetting(self.projConfig['Groups'], gid) and not force :
            self.log.writeToLog('GRUP-010', [gid])
            dieNow()

        sourceKey = csid + '_sourcePath'

        # If the new source is valid, we will add that to the config now
        # so that processes to follow will have that setting available.
        if sourcePath :
            self.addCompGroupSourcePath(csid, sourcePath)
            setattr(self, sourceKey, sourcePath)

        # The cList can be one or more valid component IDs
        # It is expected that the data for this list is in
        # this format: "id1 id2 id3 ect", unless it is coming
        # internally which means it might alread be a proper
        # list. We'll check first.
        if type(cidList) != list :
            cidList = cidList.split()

#        import pdb; pdb.set_trace()

        # The assumption is that the conf needs to be
        # reset incase there is any residual stuff from 
        # a previous attempt to add the same group. But if
        # it is new, we can just pass
        try :
            del self.projConfig['Groups'][gid]
        except :
            pass

        # Get persistant values from the config
        buildConfSection(self.projConfig, 'Groups')
        buildConfSection(self.projConfig['Groups'], gid)
        newSectionSettings = getPersistantSettings(self.projConfig['Groups'][gid], os.path.join(self.local.rapumaConfigFolder, 'group.xml'))
        if newSectionSettings != self.projConfig['Groups'][gid] :
            self.projConfig['Groups'][gid] = newSectionSettings

        # Add/Modify the info to the group config info
        self.projConfig['Groups'][gid]['cType']                 = cType
        self.projConfig['Groups'][gid]['csid']                  = csid
        self.projConfig['Groups'][gid]['cidList']               = cidList

        # Here we need to "inject" cType information into the config
        # If we don't createGroup() will fail badly.
        self.cType = cType
        self.addComponentType(cType)
        # Lock and save our config settings
        self.projConfig['Groups'][gid]['isLocked']  = True
        if writeConfFile(self.projConfig) :
            self.log.writeToLog('GRUP-040', [gid])

        # Update helper scripts
        if str2bool(self.userConfig['System']['autoHelperScripts']) :
            Commander(self.pid).updateScripts()



###############################################################################
########################### Project Setup Functions ###########################
###############################################################################

    def newProject (self, projHome, pmid, pname, systemVersion, tid = None) :
        '''Create a new publishing project.'''

        # Sort out some necessary vars
        self.projHome = projHome
        self.projectMediaIDCode = pmid

        # Test if this project already exists in the user's config file.
        if self.user.isRegisteredProject(self.pid) :
            terminal('ERR: Halt! ID [' + self.pid + '] already defined for another project.')
            return

        # Add project to local Rapuma project registry
        self.user.registerProject(self.pid, pname, self.projectMediaIDCode, self.projHome)

        # At this point we should have enough to finish the module init
        self.finishInit()

        # Run some basic tests to see if this project can be created
        # Look for project in current folder
        if not os.path.isfile(self.local.projConfFile) :
            # Look for locked project in current folder
            if os.path.isfile(self.local.projConfFile + self.local.lockExt) :
                terminal('ERR: Halt! Locked project already defined in target folder')
                return
            # Look for project in parent folder (don't want project in project)
            elif os.path.isfile(os.path.join(os.path.dirname(self.local.projHome), self.local.projConfFileName)) :
                terminal('ERR: Halt! Live project already defined in parent folder')
                return
            # Look for locked project in parent folder (prevent project in project)
            elif os.path.isfile(os.path.join(os.path.dirname(self.local.projHome), self.local.projConfFileName + self.local.lockExt)) :
                terminal('ERR: Halt! Locked project already defined in parent folder')
                return
            # Check if path to parent is valid
            elif not os.path.isdir(os.path.dirname(self.local.projHome)) :
                terminal('ERR: Halt! Not a valid (parent) path: ' + os.path.dirname(self.local.projHome))
                return
        else :
            terminal('ERR: Halt! A project already exsits in this location. Please remove it before continuing.')
            return

        # If we made it to this point, we need to make a new project folder
        if not os.path.exists(self.local.projConfFolder) :
            os.makedirs(self.local.projConfFolder)

        # Create the project depeding on if it is from a template or not
        if tid :
            templateToProject(self.user, self.local.projHome, self.pid, tid, pname)
        else :
            # If not from a template, just create a new version of the project config file
            ProjConfig(self.local).makeNewProjConf(self.local, self.pid, self.projectMediaIDCode, pname, systemVersion)

        # Add helper scripts if needed
        if str2bool(self.userConfig['System']['autoHelperScripts']) :
            Commander(self.pid).updateScripts()

        # Report what we did
        terminal('Created new project [' + self.pid + ']')
        return True


    def deleteProject (self) :
        '''Delete a project fromthe Rapuma system registry and from the hard drive.'''

        # If no pid was given this fails
        if not self.pid :
            terminal('\nERROR: Project ID code not given or found. delete operation failed.\n')
            return

        # Check if project is registered with Rapuma
        if not testForSetting(self.userConfig, 'Projects', self.pid) :
            terminal('\nWarning: [' + self.pid + '] not a registered project.\n')
        else :
            # Remove references from user rapuma.conf
            if self.user.unregisterProject(self.pid) :
                terminal('Removed [' + self.pid + '] from user configuration.')
            else :
                terminal('Failed to remove [' + self.pid + '] from user configuration.')

        # Delete everything in the project path
        if self.projHome :
            if os.path.exists(self.projHome) :
                shutil.rmtree(self.projHome)
                terminal('Removed project files for [' + self.pid + '] from hard drive.')
            else :
                terminal('Warning: [' + self.pid + '] project could not be found, unable to delete project files.')
                return

        # Report the process is done
        terminal('Removal process for [' + self.pid + '] is completed.')
        return True



