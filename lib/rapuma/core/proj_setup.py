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
from rapuma.core.paratext       import Paratext
from rapuma.project.project     import Project


class ProjSetup (object) :

    def __init__(self, pid) :
        '''Intitate the whole class and create the object.'''

        self.rapumaHome         = os.environ.get('RAPUMA_BASE')
        self.userHome           = os.environ.get('RAPUMA_USER')
        self.user               = UserConfig(self.rapumaHome, self.userHome)
        self.userConfig         = self.user.userConfig
        self.pid                = pid
        self.paratext           = Paratext(pid)
        self.projHome           = None
        self.projectMediaIDCode = None
        self.local              = None
        self.projConfig         = None
        self.log                = None
        self.groups             = {}
        self.finishInit()

        self.errorCodes     = {
            'GRUP-000' : ['MSG', 'Group processing messages'],
            'GRUP-005' : ['WRN', 'Unassigned message ID.'],
            'GRUP-040' : ['MSG', 'Added the [<<1>>] component group to the project.'],
            'GRUP-110' : ['LOG', 'Created the [<<1>>] component group folder.'],

            'COMP-000' : ['MSG', 'Component processing messages'],
            'COMP-005' : ['ERR', 'Component type [<<1>>] is not supported by the system.'],
            'COMP-010' : ['ERR', 'The component ID: [<<1>>] is not a valid for this component type. It cannot be processed by the system.'],
            'COMP-020' : ['MSG', 'Added the [<<1>>] component to the project.'],
            'COMP-022' : ['LOG', 'Force switch was set (-f). Added the [<<1>>] component to the project.'],
            'COMP-025' : ['WRN', 'The [<<1>>] component is already listed in the Rapuma project configuration and is locked. Please unlock or use the force switch (-f) to cause the sytem to install new working text or overwrite the existing working text.'],
            'COMP-040' : ['WRN', 'There is no listing in the configuration file for [<<1>>]. Please add this component to render it.'],
            'COMP-050' : ['LOG', 'Doing the preprocessing on the [<<1>>] component.'],
            'COMP-060' : ['LOG', 'The [<<1>>] component type has been added to the project.'],
            'COMP-065' : ['ERR', 'Adding the [<<1>>] component type to the project failed.'],
            'COMP-070' : ['ERR', 'Failed to render the [<<1>>] component. - project.renderComponent()'],
            'COMP-080' : ['ERR', 'Validate component is not implemented yet!'],
            'COMP-090' : ['ERR', 'Component type [<<1>>] source path is [<<2>>] cannot use [<<3>>] as a replacement. Use (-f) force to override the current setting.'],
            'COMP-100' : ['ERR', 'Failed to insert the component type [<<1>>] into the project configuration.'],
            'COMP-115' : ['WRN', 'The [<<1>>] component is locked. It must be unlocked before any modifications can be made or use (-f) force to override the lock.'],
            'COMP-120' : ['LOG', 'The component [<<1>>] has been removed from the project along with all its subcomponents.'],
            'COMP-140' : ['ERR', 'Failed to remove old component for [<<1>>] on force install.'],
            'COMP-180' : ['ERR', 'Failed to compare files with error: [<<1>>]'],
            'COMP-185' : ['ERR', 'Cannot compare component [<<1>>] because a coresponding subcomponent could not be found.'],
            'COMP-190' : ['ERR', 'Compare test: [<<1>>] is not valid.'],
            'COMP-195' : ['MSG', 'Comparing: [<<1>>] with [<<2>>] Close the viewer to return to the terminal prompt.'],
            'COMP-198' : ['MSG', 'Comparison not needed, files seem to be the same.'],
            'COMP-200' : ['ERR', 'Process failed with error: [<<1>>]'],
            'COMP-220' : ['ERR', 'Component macro package [<<1>>] not supported.'],
            'COMP-230' : ['LOG', 'Created the [<<1>>] component adjustment file.'],
            'COMP-240' : ['LOG', 'Created the [<<1>>] master adjustment file.'],
            'LOCK-100' : ['MSG', 'Messages for project and component locking.'],

            'USFM-000' : ['MSG', 'Messages for the USFM module.'],
            'USFM-005' : ['MSG', 'Unassigned error message ID.'],
            'USFM-010' : ['ERR', 'Could not process character pair. This error was found: [<<1>>]. Process could not complete. - usfm.pt_tools.getNWFChars()'],
            'USFM-020' : ['ERR', 'Improper character pair found: [<<1>>].  Process could not complete. - usfm.pt_tools.getNWFChars()'],
            'USFM-025' : ['WRN', 'No non-word-forming characters were found in the PT settings file. - usfm.pt_tools.getNWFChars()'],
            'USFM-030' : ['WRN', 'Problems found in hyphenation word list. They were reported in [<<1>>].  Process continued but results may not be right. - usfm.pt_tools.checkForBadWords()'],
            'USFM-040' : ['ERR', 'Hyphenation source file not found: [<<1>>]. Process halted!'],
            'USFM-050' : ['LOG', 'Updated project file: [<<1>>]'],
            'USFM-055' : ['LOG', 'Did not update project file: [<<1>>]'],
            'USFM-060' : ['MSG', 'Force switch was set. Removed hyphenation source files for update proceedure.'],
            'USFM-070' : ['ERR', 'Text validation failed on USFM file: [<<1>>] It reported this error: [<<2>>]'],
            'USFM-080' : ['LOG', 'Normalizing Unicode text to the [<<1>>] form.'],
            'USFM-090' : ['ERR', 'USFM file: [<<1>>] did NOT pass the validation test. Because of an encoding conversion, the terminal output is from the file [<<2>>]. Please only edit [<<1>>].'],
            'USFM-095' : ['WRN', 'Validation for USFM file: [<<1>>] was turned off.'],
            'USFM-120' : ['ERR', 'Source file: [<<1>>] not found! Cannot copy to project. Process halting now.'],
            'USFM-130' : ['ERR', 'Failed to complete preprocessing on component [<<1>>]'],
            'USFM-140' : ['MSG', 'Completed installation on [<<1>>] component working text.'],
            'USFM-150' : ['ERR', 'Unable to copy [<<1>>] to [<<2>>] - error in text.'],







            '0201' : ['ERR', 'Source path given for source ID [<<1>>] group not valid! Use -s (source) to indicate where the source files are for this component source ID.'],
            '0202' : ['ERR', 'No source path found for source ID [<<1>>]. Use -s (source) to indicate where the source files are for this component source ID.'],
            '0203' : ['ERR', 'Component group source path not valid. Use -s (source) to provide a valid source path.'],
            '0210' : ['ERR', 'The [<<1>>] group is locked. It must be unlocked before any modifications can be made or use (-f) force to override the lock.'],
            '0212' : ['ERR', 'Component [<<1>>] not found.'],
            '0215' : ['ERR', 'Source file name could not be built because the Name Form ID for [<<1>>] is missing or incorrect. Double check to see which editor created the source text.'],
            '0220' : ['MSG', 'Removed the [<<1>>] component group from the project configuation.'],
            '0240' : ['MSG', 'Added the [<<1>>] component group to the project.'],
            '0250' : ['ERR', 'Component group [<<1>>] not found. Cannot remove component.'],
            '0260' : ['ERR', 'Sorry, cannot delete [<<1>>] from the [<<2>>] group. This component is shared by another group group.'],
            '0270' : ['LOG', 'The [<<1>>] compare file was created for component [<<2>>]. - project.uninstallGroupComponent()'],
            '0280' : ['LOG', 'The [<<1>>] file was removed from component [<<2>>]. - project.uninstallGroupComponent()'],
            '0290' : ['LOG', 'Removed the [<<1>>] component group folder and all its contents.'],

            '0300' : ['ERR', 'Failed to set source path. Error given was: [<<1>>]'],

            '0410' : ['ERR', 'The group lock/unlock function failed with this error: [<<1>>]'],
            '0420' : ['MSG', 'The lock setting on the [<<1>>] group has been set to [<<2>>].'],
            '0430' : ['WRN', 'The [<<1>>] group is not found. Lock NOT set to [<<2>>].'],

            '0810' : ['ERR', 'Configuration file [<<1>>] not found. Setting change could not be made.'],
            '0840' : ['ERR', 'Problem making setting change. Section [<<1>>] missing from configuration file.'],
            '0860' : ['MSG', 'Changed  [<<1>>][<<2>>][<<3>>] setting from \"<<4>>\" to \"<<5>>\".'],
            '0870' : ['ERR', 'No source path found for: [<<1>>], returned this error: [<<2>>]'],

            '1100' : ['MSG', 'Source file editor [<<1>>] is not recognized by this system. Please double check the name used for the source text editor setting.'],
            '1110' : ['ERR', 'Source file name could not be built because the Name Form ID for [<<1>>] is missing or incorrect. Double check to see which editor created the source text.'],

        }


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
####################### Error Code Block Series = 0200 ########################
###############################################################################


    def updateGroup (self, gid, cidList = None, sourcePath = None, force = False) :
        '''Update a group, --source is optional but if given it will
        overwrite the current setting. The use of this function implies
        that this is forced so no force setting is used.'''

        # Just in case there are any problems with the source path
        # resolve it here before going on.
        csid = self.projConfig['Groups'][gid]['csid']
        if not sourcePath :
#            try :
            sourcePath  = self.userConfig['Projects'][self.pid][csid + '_sourcePath']
            if not os.path.exists(sourcePath) :
                self.log.writeToLog(self.errorCodes['201'], [csid])
#            except :
#                self.log.writeToLog(self.errorCodes['202'], [csid])
        else :
            sourcePath = resolvePath(sourcePath)
            if not os.path.exists(sourcePath) :
                self.log.writeToLog(self.errorCodes['203'])

            # Reset the source path for this csid
            self.userConfig['Projects'][self.pid][csid + '_sourcePath'] = sourcePath
            writeConfFile(self.userConfig)

        # Sort out the list
        if not cidList :
            cidList = self.projConfig['Groups'][gid]['cidList']
        else :
            if type(cidList) != list :
                 cidList = cidList.split()

        # If force is used, just unlock by default
        if force :
            self.lockUnlock(gid, False)

        # Be sure the group is unlocked
        if self.isLocked(gid) :
            self.log.writeToLog(self.errorCodes['210'], [gid])

        # Here we essentially re-add the component(s) of the group
        self.installGroupComps(gid, cidList, force)
        # Now lock it down
        self.lockUnlock(gid, True)


    def addGroup (self, cType, gid, cidList, csid, sourcePath = None, force = False) :
        '''This handels adding a group which can contain one or more components. 
        Most of the prechecking was done in the calling script so we can assume that
        the vars here are pretty good.'''

        # Do not want to add this group, non-force, if it already exsists.
        buildConfSection(self.projConfig, 'Groups')
        if testForSetting(self.projConfig['Groups'], gid) and not force :
            self.log.writeToLog(self.errorCodes['210'], [gid])

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
            self.log.writeToLog(self.errorCodes['240'], [gid])

        # Update helper scripts
        if str2bool(self.userConfig['System']['autoHelperScripts']) :
            Commander(self.pid).updateScripts()

        # Initialize the project now to get settings into the project config
        # This might help to overcome other module initialization problems.
        aProject = Project(self.userConfig, self.projConfig, self.local, self.log, 'Testing here in proj_setup', gid)
        aProject.createGroup(gid)
        if cType == 'usfm' :
            aProject.managers['usfm_Text'].updateManagerSettings(gid)


    def removeGroup (self, gid, force = False) :
        '''Handler to remove a group. If it is not found return True anyway.'''

        cidList     = self.projConfig['Groups'][gid]['cidList']
        cType     = self.projConfig['Groups'][gid]['cType']
        groupFolder = os.path.join(self.local.projComponentsFolder, gid)

        # First test for lock
        if self.isLocked(gid) and force == False :
            self.log.writeToLog(self.errorCodes['210'], [gid])

        # Remove subcomponents from the target if there are any
        buildConfSection(self.projConfig, 'Groups')
        if isConfSection(self.projConfig['Groups'], gid) :
            for cid in cidList :
                self.uninstallGroupComponent(gid, cid, force)
            if os.path.exists(groupFolder) :
                shutil.rmtree(groupFolder)
                self.log.writeToLog(self.errorCodes['290'], [gid])
        else :
            self.log.writeToLog(self.errorCodes['250'], [gid])
            
        # Now remove the config entry
        del self.projConfig['Groups'][gid]
        if writeConfFile(self.projConfig) :
            self.log.writeToLog(self.errorCodes['220'], [gid])


    def uninstallGroupComponent (self, gid, cid, force = False) :
        '''This will remove a component (files) from a group in the project.
        However, a backup will be made of the working text for comparison purposes. 
       This does not return anything. We trust it worked.'''

        cType       = self.projConfig['Groups'][gid]['cType']
        csid        = self.projConfig['Groups'][gid]['csid']
        fileHandle  = csid + '_' + cid
        fileName    = fileHandle + '.' + cType

        # Test to see if it is shared
        if self.isSharedComponent(gid, fileHandle) :
            self.log.writeToLog(self.errorCodes['260'], [fileHandle,gid])

        # Remove the files
        if force :
            targetFolder    = os.path.join(self.local.projComponentsFolder, cid)
            source          = os.path.join(targetFolder, fileName)
            targetComp      = os.path.join(source + '.cv1')
            if os.path.isfile(source) :
                # First a comparison backup needs to be made of the working text
                if os.path.isfile(targetComp) :
                    makeWriteable(targetComp)
                shutil.copy(source, targetComp)
                makeReadOnly(targetComp)
                self.log.writeToLog(self.errorCodes['270'], [fName(targetComp), cid])
                for fn in os.listdir(targetFolder) :
                    f = os.path.join(targetFolder, fn)
                    if f != targetComp :
                        os.remove(f)
                        self.log.writeToLog(self.errorCodes['280'], [fName(f), cid])


    def isSharedComponent (self, gid, cid) :
        '''If the cid is shared by any other groups, return True.'''

        try :
            for g in self.projConfig['Groups'].keys() :
                if g != gid :
                    if cid in self.projConfig['Groups'][g]['cidList'] :
                        return True
        except :
            return False


    def installGroupComps (self, gid, cidList, force = False) :
        '''This will install components to the group we created above in createGroup().
        If a component is already installed in the project it will not proceed unless
        force is set to True. Then it will remove the component files so a fresh copy
        can be added to the project.'''

#        import pdb; pdb.set_trace()

        # Get some group settings
        cType       = self.projConfig['Groups'][gid]['cType']
        csid        = self.projConfig['Groups'][gid]['csid']
        sourcePath  = self.userConfig['Projects'][self.pid][csid + '_sourcePath']

        for cid in cidList :
            # See if the working text is present, quite if it is not
            if cType == 'usfm' :
                # Force on add always means we delete the component first
                # before we do anything else
                if force :
                    self.uninstallGroupComponent(gid, cid, force)

                # Install our working text files
                if self.installUsfmWorkingText(gid, cid, force) :
                    # Report in context to force use or not
                    if force :
                        self.log.writeToLog('COMP-022', [cid])
                    else :
                        self.log.writeToLog('COMP-020', [cid])

                else :
                    self.log.writeToLog('TEXT-160', [cid])
                    return False
            else :
                self.log.writeToLog('COMP-005', [cType])
                dieNow()

        # If we got this far it must be okay to leave
        return True


###############################################################################
######################### Component Handling Functions ########################
###############################################################################
####################### Error Code Block Series = 0300 ########################
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
            self.log.writeToLog(self.errorCodes['300'], [str(e)])


###############################################################################
########################### Group Locking Functions ###########################
###############################################################################
####################### Error Code Block Series = 0400 ########################
###############################################################################

    def isLocked (self, gid) :
        '''Test to see if a group is locked. Return True if the group is 
        locked. However, if the group doesn't even exsist, it is assumed
        that it is unlocked and return False. :-)'''

        if not testForSetting(self.projConfig['Groups'], gid, 'isLocked') :
            return False
        elif str2bool(self.projConfig['Groups'][gid]['isLocked']) == True :
            return True
        else :
            return False


    def lockUnlock (self, gid, lock = True) :
        '''Lock or unlock to enable or disable actions to be taken on a group.'''

        try :
            self.setLock(gid, lock)
            return True
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.log.writeToLog(self.errorCodes['0410'], [gid])


    def setLock (self, gid, lock) :
        '''Set a group lock to True or False.'''

        if testForSetting(self.projConfig['Groups'], gid) :
            self.projConfig['Groups'][gid]['isLocked'] = lock
            # Update the projConfig
            if writeConfFile(self.projConfig) :
                # Report back
                self.log.writeToLog(self.errorCodes['0420'], [gid, str(lock)])
                return True
        else :
            self.log.writeToLog(self.errorCodes['0430'], [gid, str(lock)])
            return False


###############################################################################
########################### Project Setup Functions ###########################
###############################################################################
####################### Error Code Block Series = 0600 ########################
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


###############################################################################
########################## Config Setting Functions ###########################
###############################################################################
####################### Error Code Block Series = 0800 ########################
###############################################################################

    def changeConfigSetting (self, config, section, key, newValue) :
        '''Change a value in a specified config/section/key.  This will 
        write out changes immediately. If this is called internally, the
        calling function will need to reload to the config for the
        changes to take place in the current session. This is currently
        designed to work more as a single call to Rapuma.'''

#        import pdb; pdb.set_trace()

        oldValue = ''
        if config.lower() == 'rapuma' :
            confFile = os.path.join(self.local.userHome, 'rapuma.conf')
        else :
            confFile = os.path.join(self.local.projConfFolder, config + '.conf')
            
        # Test for existance
        if not os.path.exists(confFile) :
            self.log.writeToLog(self.errorCodes['0810'], [fName(confFile)])
            return

        # Load the file and make the change
        confObj = ConfigObj(confFile, encoding='utf-8')
        outConfObj = confObj
        try :
            # Walk our confObj to get to the section we want
            for s in section.split('/') :
                confObj = confObj[s]
        except :
            self.log.writeToLog(self.errorCodes['0840'], [section])
            return

        # Get the old value, if there is one, for reporting
        try :
            oldValue = confObj[key]
        except :
            pass

        # Insert the new value in its proper form
        if type(oldValue) == list :
            newValue = newValue.split(',')
            confObj[key] = newValue
        else :
            confObj[key] = newValue

        # Write out the original copy of the confObj which now 
        # has the change in it, then report what we did
        outConfObj.filename = confFile
        if writeConfFile(outConfObj) :
            self.log.writeToLog(self.errorCodes['0860'], [config, section, key, unicode(oldValue), unicode(newValue)])


    def getGroupSourcePath (self, gid) :
        '''Get the source path for a specified group.'''

#        import pdb; pdb.set_trace()
        csid = self.projConfig['Groups'][gid]['csid']

        try :
            return self.userConfig['Projects'][self.pid][csid + '_sourcePath']
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.log.writeToLog(self.errorCodes['0870'], [gid, str(e)])


###############################################################################
######################## USFM Component Text Functions ########################
###############################################################################
######################## Error Code Block Series = 1000 #######################
###############################################################################

    def installUsfmWorkingText (self, gid, cid, force = False) :
        '''Find the USFM source text and install it into the working text
        folder of the project with the proper name. If a USFM text file
        is not located in a PT project folder, the editor cannot be set

        to paratext, it must be set to generic. This assumes lock checking
        was done previous to the call.'''

#        import pdb; pdb.set_trace()

        sourcePath      = self.getGroupSourcePath(gid)
        csid            = self.projConfig['Groups'][gid]['csid']
        cType           = self.projConfig['Groups'][gid]['cType']
        sourceEditor    = self.projConfig['CompTypes'][cType.capitalize()]['sourceEditor']


        # Build the file name
        thisFile = ''
        if sourceEditor.lower() == 'paratext' :
            thisFile = self.paratext.formPTName(gid, cid)
        elif sourceEditor.lower() == 'generic' :
            thisFile = self.paratext.formGenericName(gid, cid)
        else :
            self.log.writeToLog(self.errorCodes['1100'], [sourceEditor])

        # Test, no name = no success
        if not thisFile :
            self.log.writeToLog(self.errorCodes['1110'], [cid])

        # Will need the stylesheet for copy if that has not been added
        # to the project yet, we will do that now
        self.style.checkDefaultStyFile()
        self.style.checkDefaultExtStyFile()

        # Start the process by building paths and file names, if we made it this far.
        # Note the file name for the preprocess is hard coded. This will become a part
        # of the total system and this file will be copied in when the user requests to
        # preprocessing.

        # Current assuption is that source text is located in a directory above the
        # that is the default. In case that is not the case, we can override that and
        # specify a path to the source. If that exists, then we will use that instead.
        if sourcePath :
            source      = os.path.join(sourcePath, thisFile)
        else :
            source      = os.path.join(os.path.dirname(self.local.projHome), thisFile)

        targetFolder    = os.path.join(self.local.projComponentsFolder, cid)
        target          = os.path.join(targetFolder, self.component.makeFileNameWithExt(cid))
        targetSource    = os.path.join(targetFolder, thisFile + '.source')

        # Copy the source to the working text folder. We do not want to do
        # this if the there already is a target and it is newer than the 
        # source text, that would indicate some edits have been done and we
        # do not want to loose the work. However, if it is older that would
        # indicate the source has been updated so unless the folder is locked
        # we will want to update the target.

        # Look for the source now, if not found, fallback on the targetSource
        # backup file. But if that isn't there die.
        if not os.path.isfile(source) :
            if os.path.isfile(targetSource) :
                source = targetSource
            else :
                self.log.writeToLog('USFM-120', [source])
                dieNow()

        # Now do the age checks and copy if source is newer than target
        if force or not os.path.isfile(target) or isOlder(target, source) :

            # Make target folder if needed
            if not os.path.isdir(targetFolder) :
                os.makedirs(targetFolder)

            # Always save an untouched copy of the source and set to
            # read only. We may need this to restore/reset later.
            if os.path.isfile(targetSource) :
                # Don't bother if we copied from it in the first place
                if targetSource != source :
                    # Reset permissions to overwrite
                    makeWriteable(targetSource)
                    shutil.copy(source, targetSource)
                    makeReadOnly(targetSource)
            else :
                shutil.copy(source, targetSource)
                makeReadOnly(targetSource)

            # To be sure nothing happens, copy from our project source
            # backup file. (Is self.style.defaultStyFile the best thing?)
            if self.usfmCopy(targetSource, target, self.style.defaultStyFile) :
                # Run any working text preprocesses on the new component text
                if str2bool(self.projConfig['Groups'][gid]['usePreprocessScript']) :
                    if not os.path.isfile(self.grpPreprocessFile) :
                        self.text.installPreprocess()
                    if not self.text.runProcessScript(target, self.grpPreprocessFile) :
                        self.log.writeToLog('USFM-130', [cid])

                # If this is a USFM component type we need to remove any \fig markers,
                # and record them in the illustration.conf file for later use
                if self.cType == 'usfm' :
                    tempFile = target + '.tmp'
                    contents = codecs.open(target, "rt", encoding="utf_8_sig").read()
                    # logUsfmFigure() logs the fig data and strips it from the working text
                    # Note: Using partial() to allows the passing of the cid param 
                    # into logUsfmFigure()
                    contents = re.sub(r'\\fig\s(.+?)\\fig\*', partial(self.project.groups[gid].logFigure, cid), contents)
                    codecs.open(tempFile, "wt", encoding="utf_8_sig").write(contents)
                    # Finish by copying the tempFile to the source
                    if not shutil.copy(tempFile, target) :
                        # Take out the trash
                        os.remove(tempFile)

                # If the text is there, we should return True so do a last check to see
                if os.path.isfile(target) :
                    self.log.writeToLog('USFM-140', [cid])
                    return True
            else :
                self.log.writeToLog('USFM-150', [source,fName(target)])
                return False
        else :
            return True


    def usfmCopy (self, source, target, projSty = None) :
        '''Copy USFM text from source to target. Decode if necessary, then
        normalize. With the text in place, validate unless that is False.'''

        # Bring in our source text
        if self.text.sourceEncode == self.text.workEncode :
            contents = codecs.open(source, 'rt', 'utf_8_sig')
            lines = contents.read()
        else :
            # Lets try to change the encoding.
            lines = self.text.decodeText(source)

        # Normalize the text
        normal = unicodedata.normalize(self.text.unicodeNormalForm, lines)
        self.log.writeToLog('USFM-080', [self.text.unicodeNormalForm])

        # Write out the text to the target
        writeout = codecs.open(target, "wt", "utf_8_sig")
        writeout.write(normal)
        writeout.close

        # Validate the target USFM text (Defalt is True)
        if str2bool(self.validateUsfm) :
            if not self.usfmTextFileIsValid(target, projSty) :
                self.log.writeToLog('USFM-090', [source,fName(target)])
                return False
        else :
            self.log.writeToLog('USFM-095', [fName(target)])

        return True


    def usfmTextFileIsValid (self, source, projSty) :
        '''Use the USFM parser to validate a style file. For now,
        if a file fails, we'll just quite right away, otherwise,

        return True.'''

        # Note: Error level reporting is possible with the usfm.parser.
        # The following are the errors it can report:
        # Note            = -1    Just give output warning, do not stop
        # Marker          =  0    Stop on any out of place marker
        # Content         =  1    Stop on mal-formed content
        # Structure       =  2    Stop on ???
        # Unrecoverable   =  100  Stop on most anything that is wrong
        # For future reference, the sfm parser will fail if TeX style
        # comment markers "%" are used to comment text rather than "#".

        try :
            fh = codecs.open(source, 'rt', 'utf_8_sig')
            stylesheet = usfm.default_stylesheet.copy()
            if projSty :
                stylesheet_extra = style.parse(open(os.path.expanduser(projSty),'r'))
                stylesheet.update(stylesheet_extra)
            doc = usfm.parser(fh, stylesheet, error_level=sfm.level.Structure)
            # With the doc text loaded up, we run a list across it
            # so the parser will either pass or fail
            testlist = list(doc)
            # Good to go
            return True

        except Exception as e :
            # If the text is not good, I think we should die here an now.
            # We may want to rethink this later but for now, it feels right.
            self.log.writeToLog('USFM-070', [source,str(e)])
            return False




