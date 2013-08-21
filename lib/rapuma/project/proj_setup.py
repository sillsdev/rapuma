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

import codecs, os, sys, unicodedata, subprocess, shutil, re, tempfile
from configobj                      import ConfigObj
from importlib                      import import_module
from functools                      import partial

import palaso.sfm as sfm
from palaso.sfm                             import usfm, style, element, text

# Load the local classes
from rapuma.core.tools                      import Tools, ToolsPath
from rapuma.core.user_config                import UserConfig
from rapuma.core.proj_local                 import ProjLocal
from rapuma.core.proj_process               import ProjProcess
from rapuma.core.proj_log                   import ProjLog
from rapuma.core.proj_compare               import ProjCompare
from rapuma.core.proj_data                  import ProjData
from rapuma.core.paratext                   import Paratext
from rapuma.manager.project                 import Project
from rapuma.project.proj_commander          import ProjCommander
from rapuma.project.proj_config             import Config


class ProjSetup (object) :

    def __init__(self, pid) :
        '''Intitate the whole class and create the object.'''

        self.user                           = UserConfig()
        self.userConfig                     = self.user.userConfig
        self.tools                          = Tools()
        self.pid                            = pid
        self.projHome                       = None
        self.projectMediaIDCode             = None
        self.local                          = None
        self.log                            = None
        self.groups                         = {}

        self.errorCodes     = {

            '0200' : ['ERR', 'No source path exists. Cannot update group. Use -s (source) to indicate where the source files are for this component source ID.'],
            '0201' : ['ERR', 'Source path given for source ID [<<1>>] group not valid! Use -s (source) to indicate where the source files are for this component source ID.'],
            '0203' : ['ERR', 'Component group source path not valid. Use -s (source) to provide a valid source path.'],
            '0205' : ['ERR', 'Component type [<<1>>] is not supported by the system.'],
            '0210' : ['ERR', 'The [<<1>>] group is locked. It must be unlocked before any modifications can be made or use (-f) force to override the lock.'],
            '0212' : ['ERR', 'Component [<<1>>] not found.'],
            '0215' : ['ERR', 'Source file name could not be built because the Name Form ID for [<<1>>] is missing or incorrect. Double check to see which editor created the source text.'],
            '0220' : ['MSG', 'Removed the [<<1>>] component group from the project configuation.'],
            '0230' : ['MSG', 'Added the [<<1>>] component to the project.'],
            '0232' : ['LOG', 'Force switch was set (-f). Added the [<<1>>] component to the project.'],
            '0240' : ['MSG', 'Added the [<<1>>] component group to the project.'],
            '0250' : ['ERR', 'Component group [<<1>>] not found. Cannot remove component.'],
            '0260' : ['ERR', 'Sorry, cannot delete [<<1>>] from the [<<2>>] group. This component is shared by another group group.'],
            '0265' : ['ERR', 'Unable to complete working text installation for [<<1>>]. May require \"force\" (-f).'],
            '0270' : ['LOG', 'The [<<1>>] compare file was created for component [<<2>>]. - project.uninstallGroupComponent()'],
            '0272' : ['MSG', 'Update for [<<1>>] component is unnecessary. Source is the same as the group source copy.'],
            '0273' : ['ERR', 'The compont [<<1>>] is not a part of the [<<2>>] group.'],
            '0274' : ['MSG', 'Force set to true, component [<<1>>] has been overwritten in the [<<2>>] group.'],
            '0280' : ['LOG', 'The [<<1>>] file was removed from component [<<2>>]. - project.uninstallGroupComponent()'],
            '0290' : ['LOG', 'Removed the [<<1>>] component group folder and all its contents.'],

            '0300' : ['ERR', 'Failed to set source path. Error given was: [<<1>>]'],
            '0320' : ['MSG', 'Set/reset source path to: [<<1>>]'],

            '1060' : ['LOG', 'Text validation succeeded on USFM file: [<<1>>]'],
            '1070' : ['ERR', 'Text validation failed on USFM file: [<<1>>] It reported this error: [<<2>>]'],
            '1080' : ['LOG', 'Normalizing Unicode text to the [<<1>>] form.'],
            '1090' : ['ERR', 'USFM file: [<<1>>] did NOT pass the validation test. Because of an encoding conversion, the terminal output is from the file [<<2>>]. Please only edit [<<1>>].'],
            '1095' : ['WRN', 'Validation for USFM file: [<<1>>] was turned off.'],
            '1100' : ['MSG', 'Source file editor [<<1>>] is not recognized by this system. Please double check the name used for the source text editor setting.'],
            '1110' : ['ERR', 'Source file name could not be built because the Name Form ID for [<<1>>] is missing or incorrect. Double check to see which editor created the source text.'],
            '1120' : ['ERR', 'Source file: [<<1>>] not found! Cannot copy to project. Process halting now.'],
            '1130' : ['ERR', 'Failed to complete preprocessing on component [<<1>>]'],
            '1140' : ['MSG', 'Completed installation on [<<1>>] component working text.'],
            '1150' : ['ERR', 'Unable to copy [<<1>>] to [<<2>>] - error in text.'],

            '2810' : ['ERR', 'Configuration file [<<1>>] not found. Setting change could not be made.'],
            '2840' : ['ERR', 'Problem making setting change. Section [<<1>>] missing from configuration file.'],
            '2860' : ['MSG', 'Changed  [<<1>>][<<2>>][<<3>>] setting from \"<<4>>\" to \"<<5>>\".'],

        }

        # Because this function can be called elsewhere in the module we call it here too
        self.finishInit()

    def finishInit (self) :
        '''If this is a new project (or system) we need to handle these settings special.'''

#            import pdb; pdb.set_trace()

        # Catch if we have a Projects key sooner than later
        if not self.userConfig.has_key('Projects') :
            self.tools.buildConfSection(self.userConfig, 'Projects')
            self.tools.writeConfFile(self.userConfig)

        if self.userConfig['Projects'].has_key(self.pid) :
            self.data               = ProjData(self.pid)
            self.projHome           = self.userConfig['Projects'][self.pid]['projectPath']
            self.projectMediaIDCode = self.userConfig['Projects'][self.pid]['projectMediaIDCode']
            # These could be initialized above but because it might be necessary
            # to reinitialize, we put them here
            self.log                = ProjLog(self.pid)
            self.proj_config        = Config(self.pid)
            self.proj_config.getProjectConfig()
            self.projectConfig      = self.proj_config.projectConfig
            self.local              = ProjLocal(self.pid)
            self.tools_path         = ToolsPath(self.pid)
            self.compare            = ProjCompare(self.pid)
            return True
        else :
            return False


###############################################################################
############################ Group Setup Functions ############################
###############################################################################
####################### Error Code Block Series = 0200 ########################
###############################################################################

    def updateAllGroups (self, force = False) :
        '''Run the update on all the groups in a project.'''

        for gid in self.projectConfig['Groups'].keys() :
            self.updateGroup(gid, force)


    def updateGroup (self, gid, cidList = None, force = False) :
        '''Update a group, --source is optional but if given it will
        overwrite the current setting. Normal behavior is to have it 
        check if there is any difference between the cid project backup
        copy and the proposed source. If there is, then it will perform
        the update. If not, it will require force to do the update.'''

        # Just in case there are any problems with the source path
        # Reset the local mod first
        self.local = ProjLocal(self.pid, gid, self.projectConfig)
        # Look for it now
        if not self.local.sourcePath :
            self.log.writeToLog(self.errorCodes['0200'])

        # Sort out the list
        if not cidList :
            cidList = self.projectConfig['Groups'][gid]['cidList']
        else :
            if type(cidList) != list :
                 cidList = cidList.split()
                 # Do a quick validity test
                 for cid in cidList :
                    if not cid in self.projectConfig['Groups'][gid]['cidList'] :
                        self.log.writeToLog(self.errorCodes['0273'], [cid,gid], 'proj_setup.updateGroup():0273')

        # Unlock the group so it can be worked on
        self.lockUnlock(gid, False)

        # Process each cid
        for cid in cidList :
            target          = self.getWorkingFile(gid, cid)
            targetSource    = self.getWorkingSourceFile(gid, cid)
            source          = self.getSourceFile(gid, cid)
            workingComp     = self.getWorkCompareFile(gid, cid)
            # Set aside a tmp backup of the target
            targetBackup    = tempfile.NamedTemporaryFile(delete=True)
            if os.path.exists(target) :
                shutil.copy(target, targetBackup.name)

            # The use of force is for if the group is locked or source is
            # matching but you want to rerun a preprocess on the text to update it.
            # In the past the component was pretty much removed with the function
            # uninstallGroupComponent() that practice has been discontinued as it
            # doesn't seem to make sense anymore
            if force or self.compare.isDifferent(source, targetSource) :
                self.installUsfmWorkingText(gid, cid, force)
                # Update our compare for next time
                if os.path.isfile(workingComp) :
                    self.tools.makeWriteable(workingComp)
                shutil.copy(targetBackup.name, workingComp)
                self.tools.makeReadOnly(workingComp)
                if force :
                    self.log.writeToLog(self.errorCodes['0274'], [cid,gid])
                self.compare.compare(source, target)
            else :
                self.log.writeToLog(self.errorCodes['0272'], [cid])

        # Now be sure the group is locked down before we go
        if not self.isLocked(gid) :
            self.lockUnlock(gid, True)


    def addGroup (self, cType, gid, cidList, csid, sourcePath = None, force = False) :
        '''This handels adding a group which can contain one or more components. 
        Most of the prechecking was done in the calling script so we can assume that
        the vars here are pretty good.'''

        # Do not want to add this group, non-force, if it already exsists.
        self.tools.buildConfSection(self.projectConfig, 'Groups')
        if self.projectConfig['Groups'].has_key(gid) and not force :
            self.log.writeToLog(self.errorCodes['0210'], [gid])

        sourceKey = csid + '_sourcePath'

        # If the new source is valid, we will add that to the config now
        # so that processes to follow will have that setting available.
        if sourcePath :
            self.addCompGroupSourcePath(gid, csid, sourcePath)
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
            del self.projectConfig['Groups'][gid]
        except :
            pass

        # Get persistant values from the config
        self.tools.buildConfSection(self.projectConfig, 'Groups')
        self.tools.buildConfSection(self.projectConfig['Groups'], gid)
        newSectionSettings = self.tools.getPersistantSettings(self.projectConfig['Groups'][gid], os.path.join(self.local.rapumaConfigFolder, 'group.xml'))
        if newSectionSettings != self.projectConfig['Groups'][gid] :
            self.projectConfig['Groups'][gid] = newSectionSettings

        # Add/Modify the info to the group config info
        self.projectConfig['Groups'][gid]['cType']                 = cType
        self.projectConfig['Groups'][gid]['csid']                  = csid
        self.projectConfig['Groups'][gid]['cidList']               = cidList
        self.projectConfig['Groups'][gid]['bindingOrder']          = 0

        # Here we need to "inject" cType information into the config
        # If we don't createGroup() will fail badly.
        self.cType = cType

#        import pdb; pdb.set_trace()
        self.tools.addComponentType(self.projectConfig, self.local, cType)

        # Lock and save our config settings
        self.projectConfig['Groups'][gid]['isLocked']  = True
        if self.tools.writeConfFile(self.projectConfig) :
            self.log.writeToLog(self.errorCodes['0240'], [gid])

        # Update helper scripts
        if self.tools.str2bool(self.userConfig['System']['autoHelperScripts']) :
            ProjCommander(self.pid).updateScripts()

        # Initialize the project now to get settings into the project config
        # This might help to overcome other module initialization problems.
        aProject = Project(self.pid, gid)
        aProject.createGroup()
        if cType == 'usfm' :
            aProject.managers['usfm_Text'].updateManagerSettings(gid)

        # In case all the vars are not set
        self.finishInit()

        # Install the components
        self.installGroupComps(gid, cidList, force)


    def removeGroup (self, gid, force = False) :
        '''Handler to remove a group. If it is not found return True anyway.'''

        cidList     = self.projectConfig['Groups'][gid]['cidList']
        cType       = self.projectConfig['Groups'][gid]['cType']
        groupFolder = os.path.join(self.local.projComponentFolder, gid)

        # First test for lock
        if self.isLocked(gid) and force == False :
            self.log.writeToLog(self.errorCodes['0210'], [gid])

        # Remove subcomponents from the target if there are any
        self.tools.buildConfSection(self.projectConfig, 'Groups')
        if self.projectConfig['Groups'].has_key(gid) :
            for cid in cidList :
                self.uninstallGroupComponent(gid, cid, self.projectConfig, force)
            if os.path.exists(groupFolder) :
                shutil.rmtree(groupFolder)
                self.log.writeToLog(self.errorCodes['0290'], [gid])
        else :
            self.log.writeToLog(self.errorCodes['0250'], [gid])
            
        # Now remove the config entry
        del self.projectConfig['Groups'][gid]
        if self.tools.writeConfFile(self.projectConfig) :
            self.log.writeToLog(self.errorCodes['0220'], [gid])


    def uninstallGroupComponent (self, gid, cid, force = False) :
        '''This will remove a component (files) from a group in the project.
        However, a backup will be made of the working text for comparison purposes. 
       This does not return anything. We trust it worked.'''

#       import pdb; pdb.set_trace()

        cType       = self.projectConfig['Groups'][gid]['cType']
        csid        = self.projectConfig['Groups'][gid]['csid']
        fileHandle  = cid + '_' + csid

        # Test to see if it is shared
        if self.isSharedComponent(gid, fileHandle) :
            self.log.writeToLog(self.errorCodes['0260'], [fileHandle,gid])

        # Remove the files
        if force :
            targetFolder    = os.path.join(self.local.projComponentFolder, cid)
            workingComp     = self.getWorkCompareFile(gid, cid)
            working         = self.getWorkingFile(gid, cid)

            if os.path.isfile(working) :
                # First a comparison backup needs to be made of the working text
                if os.path.isfile(workingComp) :
                    self.tools.makeWriteable(workingComp)
                shutil.copy(working, workingComp)
                self.tools.makeReadOnly(workingComp)
                self.log.writeToLog(self.errorCodes['0270'], [self.tools.fName(workingComp), cid])
                for fn in os.listdir(targetFolder) :
                    f = os.path.join(targetFolder, fn)
                    if f != workingComp :
                        os.remove(f)
                        self.log.writeToLog(self.errorCodes['0280'], [self.tools.fName(f), cid])


    def isSharedComponent (self, gid, cid) :
        '''If the cid is shared by any other groups, return True.'''

        try :
            for g in self.projectConfig['Groups'].keys() :
                if g != gid :
                    if cid in self.projectConfig['Groups'][g]['cidList'] :
                        return True
        except :
            return False


    def installGroupComps (self, gid, cidList, force = False) :
        '''This will install components to the group we created above in createGroup().
        If a component is already installed in the project it will not proceed unless
        force is set to True. Then it will remove the component files so a fresh copy
        can be added to the project.'''

#        import pdb; pdb.set_trace()

        # Make sure our group folder is there
        if not os.path.exists(os.path.join(self.local.projComponentFolder, gid)) :
            os.makedirs(os.path.join(self.local.projComponentFolder, gid))

        # Get some group settings
        cType       = self.projectConfig['Groups'][gid]['cType']

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
                        self.log.writeToLog(self.errorCodes['0232'], [cid])
                    else :
                        self.log.writeToLog(self.errorCodes['0230'], [cid])

                else :
                    self.log.writeToLog(self.errorCodes['0265'], [cid])
                    return False
            else :
                self.log.writeToLog(self.errorCodes['0205'], [cType])

        # If we got this far it must be okay to leave
        return True


###############################################################################
######################### Component Handling Functions ########################
###############################################################################
####################### Error Code Block Series = 0300 ########################
###############################################################################

    def getSourceFile (self, gid, cid) :
        '''Get the source file name with path.'''

#        import pdb; pdb.set_trace()

        # Just in case there are any problems with the source path
        # Reset the local mod first
        self.local = ProjLocal(self.pid, gid, self.projectConfig)
        if self.local.sourcePath :
            paratext            = Paratext(self.pid, gid)
            sourcePath          = self.local.sourcePath
            cType               = self.projectConfig['Groups'][gid]['cType']
            sourceEditor        = paratext.getSourceEditor()
            # Build the file name
            if sourceEditor.lower() == 'paratext' :
                sName = paratext.formPTName(cid)
            elif sourceEditor.lower() == 'generic' :
                sName = paratext.formGenericName(cid)
            else :
                return None

            return os.path.join(sourcePath, sName)


    def getWorkingFile (self, gid, cid) :
        '''Return the working file name with path.'''

        csid            = self.projectConfig['Groups'][gid]['csid']
        cType           = self.projectConfig['Groups'][gid]['cType']
        targetFolder    = os.path.join(self.local.projComponentFolder, cid)
        return os.path.join(targetFolder, cid + '_' + csid + '.' + cType)


    def getWorkCompareFile (self, gid, cid) :
        '''Return the working compare file (saved from last update) name with path.'''

        return self.getWorkingFile(gid, cid) + '.cv1'


    def getWorkingSourceFile (self, gid, cid) :
        '''Get the working source file name with path.'''

        # Just in case there are any problems with the source path
        # Reset the local mod first
        self.local = ProjLocal(self.pid, gid, self.projectConfig)
        if self.local.sourcePath :
            targetFolder    = os.path.join(self.local.projComponentFolder, cid)
            source          = self.getSourceFile(gid, cid)
            sName           = os.path.split(source)[1]
            return os.path.join(targetFolder, sName + '.source')


    def addCompGroupSourcePath (self, gid, csid, source) :
        '''Add a source path for components used in a group if none
        exsist. If one exists, replace anyway. Last in wins! The 
        assumption is only one path per component group.'''

#        # Get the csid
#        csid = self.projectConfig['Groups'][gid]['csid']

        # Path has been resolved in Rapuma, we assume it should be valid.
        # But it could be a full file name. We need to sort that out.
        try :
            if os.path.isdir(source) :
                self.userConfig['Projects'][self.pid][csid + '_sourcePath'] = source
            else :
                self.userConfig['Projects'][self.pid][csid + '_sourcePath'] = os.path.split(source)[0]

            self.tools.writeConfFile(self.userConfig)
            self.log.writeToLog(self.errorCodes['0320'], [source])
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.log.writeToLog(self.errorCodes['0300'], [str(e)])


###############################################################################
########################### Project Lock Functions ############################
###############################################################################
####################### Error Code Block Series = 0400 ########################
###############################################################################

    def isLocked (self, gid) :
        '''Test to see if a group is locked. Return True if the group is 
        locked. However, if the group doesn't even exsist, it is assumed
        that it is unlocked and return False. :-)'''

        if not self.projectConfig['Groups'][gid].has_key('isLocked') :
            return False
        elif self.tools.str2bool(self.projectConfig['Groups'][gid]['isLocked']) == True :
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
            sys.exit('\nERROR: The group [' + gid + '] lock/unlock function failed with this error: [' + str(e) + ']')


    def setLock (self, gid, lock) :
        '''Set a group lock to True or False.'''

        if self.projectConfig['Groups'].has_key(gid) :
            self.projectConfig['Groups'][gid]['isLocked'] = lock
            # Update the projectConfig
            if self.tools.writeConfFile(self.projectConfig) :
                return True
        else :
            return False


###############################################################################
########################### Project Setup Functions ###########################
###############################################################################
####################### Error Code Block Series = 0600 ########################
###############################################################################

    def newProject (self, projHome, pmid, pname, systemVersion, tid = None) :
        '''Create a new publishing project.'''

#        import pdb; pdb.set_trace()

        # Sort out some necessary vars
        self.projHome = projHome
        self.projectMediaIDCode = pmid

        # Test if this project already exists in the user's config file.
        if self.user.isRegisteredProject(self.pid) :
            self.tools.terminal('ERR: Halt! ID [' + self.pid + '] already defined for another project.')
            return

        # Add project to local Rapuma project registry
        self.user.registerProject(self.pid, pname, self.projectMediaIDCode, self.projHome)

        # Load a couple necessary modules
        self.local              = ProjLocal(self.pid)

        # Run some basic tests to see if this project can be created
        # Look for project in current folder
        if not os.path.isfile(self.local.projectConfFile) :
            # Look for locked project in current folder
            if os.path.isfile(self.local.projectConfFile + self.local.lockExt) :
                self.tools.terminal('ERR: Halt! Locked project already defined in target folder')
                return
            # Look for project in parent folder (don't want project in project)
            elif os.path.isfile(os.path.join(os.path.dirname(self.local.projHome), self.local.projectConfFileName)) :
                self.tools.terminal('ERR: Halt! Live project already defined in parent folder')
                return
            # Look for locked project in parent folder (prevent project in project)
            elif os.path.isfile(os.path.join(os.path.dirname(self.local.projHome), self.local.projectConfFileName + self.local.lockExt)) :
                self.tools.terminal('ERR: Halt! Locked project already defined in parent folder')
                return
            # Check if path to parent is valid
            elif not os.path.isdir(os.path.dirname(self.local.projHome)) :
                self.tools.terminal('ERR: Halt! Not a valid (parent) path: ' + os.path.dirname(self.local.projHome))
                return
        else :
            self.tools.terminal('ERR: Halt! A project already exsits in this location. Please remove it before continuing.')
            return

        # If we made it to this point, we need to make a new project folder
        if not os.path.exists(self.local.projConfFolder) :
            os.makedirs(self.local.projConfFolder)
            # Create all normal project folders
            for fld in self.local.projFolders :
                folder = os.path.join(self.local.projHome, fld)
                if not os.path.exists(folder) :
                    os.makedirs(folder)

        # Create the project depeding on if it is from a template or not
        if tid :
            self.data.templateToProject(self.user, self.local.projHome, self.pid, tid, pname)
        else :
            # If not from a template, just create a new version of the project config file
            Config(self.pid).makeNewprojectConf(self.local, self.pid, self.projectMediaIDCode, pname, systemVersion)

        # Add helper scripts if needed
        if self.tools.str2bool(self.userConfig['System']['autoHelperScripts']) :
            ProjCommander(self.pid).updateScripts()

        # Report what we did
        self.tools.terminal('Created new project [' + self.pid + ']')
        return True


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

        # To prevent loading errors, bring these mods now
        paratext            = Paratext(self.pid, gid)
        proj_process        = ProjProcess(self.pid)

        cType               = self.projectConfig['Groups'][gid]['cType']
        usePreprocessScript = self.tools.str2bool(self.projectConfig['Groups'][gid]['usePreprocessScript'])
        targetFolder        = os.path.join(self.local.projComponentFolder, cid)
        target              = self.getWorkingFile(gid, cid)
        targetSource        = self.getWorkingSourceFile(gid, cid)
        source              = self.getSourceFile(gid, cid)
        extractFigMarkers   = self.tools.str2bool(self.projectConfig['CompTypes'][cType.capitalize()]['extractFigMarkers'])
        extractFeMarkers    = self.tools.str2bool(self.projectConfig['CompTypes'][cType.capitalize()]['extractFeMarkers'])

        # Look for the source now, if not found, fallback on the targetSource
        # backup file. But if that isn't there die.
        if not os.path.isfile(source) :
            if os.path.isfile(targetSource) :
                source = targetSource
            else :
                self.log.writeToLog(self.errorCodes['1120'], [source])

        # Make target folder if needed
        if not os.path.isdir(targetFolder) :
            os.makedirs(targetFolder)

        # Always save an untouched copy of the source and set to
        # read only. We may need this to restore/reset later.
        if os.path.isfile(targetSource) :
            # Don't bother if we copied from it in the first place
            if targetSource != source :
                # Reset permissions to overwrite
                self.tools.makeWriteable(targetSource)
                shutil.copy(source, targetSource)
                self.tools.makeReadOnly(targetSource)
        else :
            shutil.copy(source, targetSource)
            self.tools.makeReadOnly(targetSource)

        # To be sure nothing happens, copy from our project source
        # backup file. (Is self.style.defaultStyFile the best thing?)
        if self.usfmCopy(targetSource, target, gid) :
            # Run any working text preprocesses on the new component text
            if usePreprocessScript :
                proj_process.checkForPreprocessScript(gid)
                if not proj_process.runProcessScript(target, self.local.groupPreprocessFile) :
                    self.log.writeToLog(self.errorCodes['1130'], [cid])


# FIXME: This entire next part should go out into a separate function to better
# manage the process of removing extra non-Biblical text from the source, if
# the process requires this. It should not be hard to do

# Of cource this is USFM! Dah!

            # If this is a USFM component type we need to remove any \fig markers,
            # and record them in the illustration.conf file for later use
            if cType == 'usfm' :
                tempFile = tempfile.NamedTemporaryFile()
                contents = codecs.open(target, "rt", encoding="utf_8_sig").read()
                # logUsfmFigure() logs the fig data and strips it from the working text
                # Note: Using partial() to allows the passing of the cid param 
                # into logUsfmFigure()
                if extractFigMarkers :
                    contents = re.sub(r'\\fig\s(.+?)\\fig\*', partial(paratext.logFigure, gid, cid), contents)
                # Now remove end notes from the text
                if extractFeMarkers :
                    contents = re.sub(r'\\fe\s(.+?)\\fe\*', partial(paratext.collectEndNotes, cid), contents)
                # Write out the remaining data to the working file
                codecs.open(tempFile.name, "wt", encoding="utf_8_sig").write(contents)
                # Finish by copying the tempFile to the source
                shutil.copy(tempFile.name, target)

            # If the text is there, we should return True so do a last check to see
            if os.path.isfile(target) :
                self.log.writeToLog(self.errorCodes['1140'], [cid])
                return True
        else :
            self.log.writeToLog(self.errorCodes['1150'], [source,self.tools.fName(target)])
            return False


    def usfmCopy (self, source, target, gid) :
        '''Copy USFM text from source to target. Decode if necessary, then
        normalize. With the text in place, validate unless that is False.'''

        sourceEncode        = self.projectConfig['Managers']['usfm_Text']['sourceEncode']
        workEncode          = self.projectConfig['Managers']['usfm_Text']['workEncode']
        unicodeNormalForm   = self.projectConfig['Managers']['usfm_Text']['unicodeNormalForm']
        validateUsfm        = self.tools.str2bool(self.projectConfig['CompTypes']['Usfm']['validateUsfm'])

        # Bring in our source text
        if sourceEncode == workEncode :
            contents = codecs.open(source, 'rt', 'utf_8_sig')
            lines = contents.read()
        else :
            # Lets try to change the encoding.
            lines = self.tools.decodeText(source, sourceEncode)

        # Normalize the text
        normal = unicodedata.normalize(unicodeNormalForm, lines)
        self.log.writeToLog(self.errorCodes['1080'], [unicodeNormalForm])

        # Write out the text to the target
        writeout = codecs.open(target, "wt", "utf_8_sig")
        writeout.write(normal)
        writeout.close

        # Validate the target USFM text (Defalt is True)
        if validateUsfm :
            if not self.usfmTextFileIsValid(target, gid) :
                self.log.writeToLog(self.errorCodes['1090'], [source,self.tools.fName(target)])
                return False
        else :
            self.log.writeToLog(self.errorCodes['1095'], [self.tools.fName(target)])

        return True


    def usfmTextFileIsValid (self, source, gid) :
        '''Use the USFM parser to validate a style file. For now,
        if a file fails, we'll just quite right away, otherwise,
        return True.'''

#        import pdb; pdb.set_trace()

        # Note: Error level reporting is possible with the usfm.parser.
        # The following are the errors it can report:
        # Note            = -1    Just give output warning, do not stop
        # Marker          =  0    Stop on any out of place marker
        # Content         =  1    Stop on mal-formed content
        # Structure       =  2    Stop on ???
        # Unrecoverable   =  100  Stop on most anything that is wrong
        # For future reference, the sfm parser will fail if TeX style
        # comment markers "%" are used to comment text rather than "#".

        # Grab the default style file from the macPack (it better be there)
        cType           = self.projectConfig['Groups'][gid]['cType']
        Ctype           = cType.capitalize()
        macPack         = self.projectConfig['CompTypes'][Ctype]['macroPackage']
        defaultStyFile  = os.path.join(self.local.projStyleFolder, macPack + '.sty')
        try :
            fh = codecs.open(source, 'rt', 'utf_8_sig')
            stylesheet = usfm.default_stylesheet.copy()
            stylesheet_extra = style.parse(open(os.path.expanduser(defaultStyFile),'r'))
            stylesheet.update(stylesheet_extra)
            # FIXME: Keep an eye on this: error_level=sfm.level.Structure
            # gave less than helpful feedback when a mal-formed verse was
            # found. Switched to "Content" to get better error feedback
#            doc = usfm.parser(fh, stylesheet, error_level=sfm.level.Structure)
            doc = usfm.parser(fh, stylesheet, error_level=sfm.level.Content)
            # With the doc text loaded up, we run a list across it
            # so the parser will either pass or fail
            testlist = list(doc)
            # Good to go
            self.log.writeToLog(self.errorCodes['1060'], [self.tools.fName(source)])
            return True

        except Exception as e :
            # If the text is not good, I think we should die here an now.
            # We may want to rethink this later but for now, it feels right.
            self.log.writeToLog(self.errorCodes['1070'], [source,str(e)], 'proj_setup.usfmTextFileIsValid():1070')
            return False


###############################################################################
########################## Settings Change Functions ##########################
###############################################################################
####################### Error Code Block Series = 2000 ########################
###############################################################################

    def changeConfigSetting (self, config, section, key, newValue) :
        '''Change a value in a specified config/section/key.  This will 
        write out changes immediately. If this is called internally, the
        calling function will need to reload to the config for the
        changes to take place in the current session. This is currently
        designed to work more as a single call to Rapuma.'''

        oldValue = ''
        if config.lower() == 'rapuma' :
            confFile = os.path.join(self.local.userHome, 'rapuma.conf')
        else :
            confFile = os.path.join(self.local.projConfFolder, config + '.conf')

        # Test for existance
        if not os.path.exists(confFile) :
            self.log.writeToLog(self.errorCodes['2810'], [self.tools.fName(confFile)])
            return

        # Load the file and make the change
        confObj = ConfigObj(confFile, encoding='utf-8')
        outConfObj = confObj
        try :
            # Walk our confObj to get to the section we want
            for s in section.split('/') :
                confObj = confObj[s]
        except :
            self.log.writeToLog(self.errorCodes['2840'], [section])
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
        if self.tools.writeConfFile(outConfObj) :
            self.log.writeToLog(self.errorCodes['2860'], [config, section, key, unicode(oldValue), unicode(newValue)])



###############################################################################
############################# Project Delete Class ############################
###############################################################################

# This class was created to prevent conflicts from the main class in this module.

class ProjDelete (object) :

    def __init__(self, pid) :
        '''Intitate the whole class and create the object.'''

        self.user                           = UserConfig()
        self.userConfig                     = self.user.userConfig
        self.tools                          = Tools()
        self.pid                            = pid
        self.projHome                       = None
        if self.userConfig['Projects'].has_key(pid) :
            self.projHome                   = self.userConfig['Projects'][self.pid]['projectPath']

# Currently there is only this function in this class

    def deleteProject (self) :
        '''Delete a project from the Rapuma system registry and create a 
        backup on the hard drive.'''

#        import pdb; pdb.set_trace()

        # If no pid was given this fails
        if not self.pid :
            self.tools.terminal('\nERROR: Project ID code not given or found. delete operation failed.\n')
            return

        # Check if project is registered with Rapuma
        if not self.userConfig['Projects'].get(self.pid) :
            self.tools.terminal('\nWarning: [' + self.pid + '] not a registered project.\n')
        else :
            # Remove references from user rapuma.conf
            if self.user.unregisterProject(self.pid) :
                self.tools.terminal('Removed [' + self.pid + '] from user configuration.')
            else :
                self.tools.terminal('Failed to remove [' + self.pid + '] from user configuration.')

        # Do a simple (numbered) backup.
        if self.projHome :
            self.tools.makeFolderBackup(self.projHome)
            if os.path.exists(self.projHome) :
                shutil.rmtree(self.projHome)
                self.tools.terminal('Removed project files for [' + self.pid + '] from hard drive.')
            else :
                self.tools.terminal('Warning: [' + self.pid + '] project could not be found, unable to delete project files.')
                return
        else :
            self.tools.terminal('Warning: Not enough config information to build a path to the project home. Unable to do the requested project backup.')
            return False

        # Report the process is done
        self.tools.terminal('Removal process for [' + self.pid + '] is completed.')
        return True



