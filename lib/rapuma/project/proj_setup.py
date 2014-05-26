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
from configobj                              import ConfigObj
from importlib                              import import_module
from functools                              import partial

import palaso.sfm as sfm
from palaso.sfm                             import usfm, style, element, text

# Load the local classes
from rapuma.core.tools                      import Tools
from rapuma.core.user_config                import UserConfig
from rapuma.core.proj_local                 import ProjLocal
from rapuma.core.proj_process               import ProjProcess
from rapuma.core.proj_log                   import ProjLog
from rapuma.core.proj_compare               import ProjCompare
from rapuma.core.proj_data                  import ProjData
from rapuma.manager.project                 import Project
from rapuma.project.proj_commander          import ProjCommander
from rapuma.project.proj_config             import Config
from rapuma.group.usfm_data                 import UsfmData


class ProjSetup (object) :

    def __init__(self, sysConfig, pid) :
        '''Intitate the whole class and create the object.'''

        self.pid                            = pid
        self.user                           = UserConfig()
        self.userConfig                     = self.user.userConfig
        self.projHome                       = os.path.join(os.path.expanduser(self.userConfig['Resources']['projects']), self.pid)
        self.tools                          = Tools()
        self.log                            = ProjLog(self.pid)
        self.systemVersion                  = sysConfig['Rapuma']['systemVersion']
        self.projectConfig                  = self.loadUpProjConfig(self.pid)
        self.local                          = ProjLocal(self.pid)
        self.groups                         = {}
        self.usfmData                       = UsfmData()
        self.ntCidList                      = self.usfmData.ntCidList()
        self.otCidList                      = self.usfmData.otCidList()
        self.wholeCannonList                = self.usfmData.wholeCannonList()
        self.cidNameDict                    = self.usfmData.cidNameDict()

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
            '0250' : ['MSG', 'Importing: [<<1>>]'],
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
            '1999' : ['WRN', 'Collect end notes is not fully implemented yet. The following note was removed from the working text, but not saved: [<<1>>]'],

            '2810' : ['ERR', 'Configuration file [<<1>>] not found. Setting change could not be made.'],
            '2840' : ['ERR', 'Problem making setting change. Section [<<1>>] missing from configuration file.'],
            '2860' : ['MSG', 'Changed  [<<1>>][<<2>>][<<3>>] setting from \"<<4>>\" to \"<<5>>\".'],

        }

        ## Because this function can be called elsewhere in the module we call it here too
        #self.finishInit()

    #def finishInit (self) :
        #'''If this is a new project (or system) we need to handle these settings special.'''

##        import pdb; pdb.set_trace()

        #self.data               = ProjData(self.pid)
        ## These could be initialized above but because it might be necessary 
        ## to reinitialize, we put them here
        #self.log                = ProjLog(self.pid)
        #self.proj_config        = Config(self.pid)
        #self.proj_config.getProjectConfig()
        #self.projectConfig      = self.proj_config.projectConfig
        #self.local              = ProjLocal(self.pid)
        #self.compare            = ProjCompare(self.pid)
        #return True

    def loadUpProjConfig (self, pid) :
        '''Load up the project config.'''







#        import pdb; pdb.set_trace()




        self.proj_config        = Config(pid)
        self.proj_config.getProjectConfig()
        return self.proj_config.projectConfig


###############################################################################
############################ Group Setup Functions ############################
###############################################################################
####################### Error Code Block Series = 0200 ########################
###############################################################################

    def makeCVOne (self, workingBak, workingCVOne) :
        '''Create a .cv1 backup of the current working file (source), if
        one exists. If not, do nothing.'''

        # Check for the target (working file)
        if os.path.exists(workingCVOne) :
            self.tools.makeWriteable(workingCVOne)
        shutil.copy(workingBak, workingCVOne)
        self.tools.makeReadOnly(workingCVOne)

        return True

# FIXME: Cannot have this here unless we can feed it all the file path info.
    #def updateAllGroups (self, force = False) :
        #'''Run the update on all the groups in a project.'''

        #for gid in self.projectConfig['Groups'].keys() :
            #self.updateGroup(gid, force)


    def updateGroup (self, gid, sourceList, force = False) :
        '''Update a group by providing a list of source files. This
        will check to see if the incoming source coresponds to cids
        listed for the group. If not, it will log a warning. If one or
        more cids are missing, it will throw an error and quite before
        doing the actual update. All the source needs to be in place
        for this to work. Otherwise, the user should be just updating
        a single component.'''

#        import pdb; pdb.set_trace()

        # Just in case there are any problems with the source path
        # Reset the local mod first
        self.local = ProjLocal(self.pid, gid, self.projectConfig)

# FIXME: This all needs to be rewriten

        # Sort out the list
        #if not cidList :
            #cidList = self.projectConfig['Groups'][gid]['cidList']
        #else :
            #if type(cidList) != list :
                 #cidList = cidList.split()
            ## Do a quick validity test
            #for cid in cidList :
                #if not cid in self.projectConfig['Groups'][gid]['cidList'] :
                    #self.log.writeToLog(self.errorCodes['0273'], [cid,gid], 'proj_setup.updateGroup():0273')

        ## Unlock the group so it can be worked on
        #self.lockUnlock(gid, False)

        ## Process each cid
        #for cid in cidList :
            #target              = self.getWorkingFile(gid, cid)
            #targetSource        = self.getWorkingSourceFile(gid, cid)
            #source              = self.getSourceFile(gid, cid)
            #workingBak          = tempfile.NamedTemporaryFile(delete=True).name
            #workingCVOne        = self.getWorkCompareFile(gid, cid)

            ## Create temp backup of working file
            #if os.path.exists(target) :
                #shutil.copy(target, workingBak)
                
            ## Don't do this unless it is different or forced
            #if force or self.compare.isDifferent(source, targetSource) :
                ## Delete the existing working file
                #if os.path.exists(target) :
                    #os.remove(target)
                ## Create the backup for comparison
                #if os.path.exists(workingBak) :
                    #self.makeCVOne(workingBak, workingCVOne)
                ## Install the new text
                #self.importWorkingText(gid, cid, force)
                ## Report if this was forced
                #if force :
                    #self.log.writeToLog(self.errorCodes['0274'], [cid,gid])
                ## Compare the new working file with the previous
                #if os.path.exists(workingCVOne) :
                    #self.compare.compare(workingCVOne, target)
            #else :
                #self.log.writeToLog(self.errorCodes['0272'], [cid])

        ## Now be sure the group is locked down before we go
        #if not self.isLocked(gid) :
            #self.lockUnlock(gid, True)


    def addGroup (self, cType, gid, sourceList, force = False) :
        '''Add a group by providing a component type, group ID and a 
        list of source files. This will check to see if the incoming 
        source is valid. If not, it will throw an error and quite 
        before doing the actual import. All the source needs to be 
        in place for this to work. Force will cause the function to 
        overwrite any exsisting group meta data or source data.'''

        # Do not want to add this group, non-force, if it already exsists.
        self.tools.buildConfSection(self.projectConfig, 'Groups')
        if self.projectConfig['Groups'].has_key(gid) and not force :
            self.log.writeToLog(self.errorCodes['0210'], [gid])
        else :
            # Otherwise we may need to remove the group from the config
            try :
                del self.projectConfig['Groups'][gid]
            except :
                pass

        # Set some vars
        cidList = []
        sources = {}

        # Do the importing first, then write the changes to the config
        for f in sourceList :
            cid = self.tools.discoverCIDFromFile(f)
            if cid in self.wholeCannonList :
                # Add CID to cidList
                cidList.append(cid)
                sources[cid] = f
        
#        import pdb; pdb.set_trace()

        # Get persistant values from the config
        self.tools.buildConfSection(self.projectConfig, 'Groups')
        self.tools.buildConfSection(self.projectConfig['Groups'], gid)
        newSectionSettings = self.tools.getPersistantSettings(self.projectConfig['Groups'][gid], os.path.join(self.local.rapumaConfigFolder, 'group.xml'))
        if newSectionSettings != self.projectConfig['Groups'][gid] :
            self.projectConfig['Groups'][gid] = newSectionSettings
        # Add/Modify the info to the group config info
        self.projectConfig['Groups'][gid]['cType']                 = cType
        self.projectConfig['Groups'][gid]['cidList']               = cidList
        self.projectConfig['Groups'][gid]['bindingOrder']          = 0
        # Here we need to "inject" cType information into the config
        # If we don't createGroup() will fail badly.
        self.cType = cType
        self.tools.addComponentType(self.projectConfig, self.local, cType)
        # Initialize the project now to get settings into the project config
        # This might help to overcome other module initialization problems.
        aProject = Project(self.pid, gid)
        aProject.createGroup()
        if self.tools.writeConfFile(self.projectConfig) :
            self.log.writeToLog(self.errorCodes['0240'], [gid])

        # Install the components now, if successful, we can update the
        # project config. If not, the user will need to sort out why
        if self.installGroupComps(gid, cType, sources, force) :
            # Sort the cidList to cannonical order
            cidList = self.usfmData.cannonListSort(cidList)



            # Update helper scripts
            #if self.tools.str2bool(self.userConfig['System']['autoHelperScripts']) :
                #ProjCommander(self.pid).updateScripts()
                
            return True

# FIXME: This all needs to be refactored for importing

        ## The cList can be one or more valid component IDs
        ## It is expected that the data for this list is in
        ## this format: "id1 id2 id3 ect", unless it is coming
        ## internally which means it might alread be a proper
        ## list. We'll check first.
        #if type(cidList) != list :
            #cidList = cidList.split()


        ## The assumption is that the conf needs to be
        ## reset incase there is any residual stuff from 
        ## a previous attempt to add the same group. But if
        ## it is new, we can just pass




        ## Lock and save our config settings
        #self.projectConfig['Groups'][gid]['isLocked']  = True

        ## Update helper scripts
        #if self.tools.str2bool(self.userConfig['System']['autoHelperScripts']) :
            #ProjCommander(self.pid).updateScripts()

        ## Initialize the project now to get settings into the project config
        ## This might help to overcome other module initialization problems.
        #aProject = Project(self.pid, gid)
        #aProject.createGroup()


## FIXME: The updateManagerSettings was disabled in text.py

        ##if cType == 'usfm' :
            ##aProject.managers['usfm_Text'].updateManagerSettings(gid)




    #def removeGroup (self, gid, force = False) :
        #'''Handler to remove a group. If it is not found return True anyway.'''

        #cidList     = self.projectConfig['Groups'][gid]['cidList']
        #cType       = self.projectConfig['Groups'][gid]['cType']
        #groupFolder = os.path.join(self.local.projComponentFolder, gid)

        ## First test for lock
        #if self.isLocked(gid) and force == False :
            #self.log.writeToLog(self.errorCodes['0210'], [gid])

        ## Remove subcomponents from the target if there are any
        #self.tools.buildConfSection(self.projectConfig, 'Groups')
        #if self.projectConfig['Groups'].has_key(gid) :
            #for cid in cidList :
                #self.uninstallGroupComponent(gid, cid, force)
            #if os.path.exists(groupFolder) :
                #shutil.rmtree(groupFolder)
                #self.log.writeToLog(self.errorCodes['0290'], [gid])
        #else :
            #self.log.writeToLog(self.errorCodes['0250'], [gid])
            
        ## Now remove the config entry
        #del self.projectConfig['Groups'][gid]
        #if self.tools.writeConfFile(self.projectConfig) :
            #self.log.writeToLog(self.errorCodes['0220'], [gid])


    def uninstallGroupComponent (self, cType, gid, cid, force = False) :
        '''This will remove a component (files) from a group in the project.
        However, a backup will be made of the working text for comparison purposes. 
       This does not return anything. We trust it will work.'''

#       import pdb; pdb.set_trace()

        # In the future diglot handling will hopefully be added. Previously,
        # the ability to handle multiple working component files was
        # done with a csid (Component Source ID), this has been removed.
        # Now, all initial working components will have "base" tacked on
        # to the end of the handle. When diglot handling is implemented
        # a second source identifier will need to be added to the file
        # name and handled in the process. For now, we'll just use the
        # base ID.
        fileHandle      = cid + '_base'
        working         = fileHandle + '.' + cType
        workingComp     = working + '.cv1'
        targetFolder    = os.path.join(self.local.projComponentFolder, cid)

        # Test to see if it is shared
        if self.isSharedComponent(gid, fileHandle) :
            self.log.writeToLog(self.errorCodes['0260'], [fileHandle,gid])

        # Remove the files
        if force :
            if os.path.isfile(working) :
                self.makeCVOne(working, workingComp)
                self.log.writeToLog(self.errorCodes['0270'], [self.tools.fName(workingComp), cid])
                for fn in os.listdir(targetFolder) :
                    f = os.path.join(targetFolder, fn)
                    if f != workingComp :
                        os.remove(f)
                        self.log.writeToLog(self.errorCodes['0280'], [self.tools.fName(f), cid])

                return True


    def isSharedComponent (self, gid, cid) :
        '''If the cid is shared by any other groups, return True.'''

        try :
            for g in self.projectConfig['Groups'].keys() :
                if g != gid :
                    if cid in self.projectConfig['Groups'][g]['cidList'] :
                        return True
        except :
            return False


    def installGroupComps (self, gid, cType, sources, force = False) :
        '''This will install components to the group we created above in createGroup().
        If a component is already installed in the project it will not proceed unless
        force is set to True. Then it will remove the component files so a fresh copy
        can be added to the project.'''

#        import pdb; pdb.set_trace()

        # Make sure our group folder is there
        if not os.path.exists(os.path.join(self.local.projComponentFolder, gid)) :
            os.makedirs(os.path.join(self.local.projComponentFolder, gid))

        #print dir(sources)

        for cid, fName in sources.iteritems() :
            self.log.writeToLog(self.errorCodes['0250'], [self.cidNameDict[cid]])
            # See if the working text is present, quite if it is not
            if cType == 'usfm' :
                # Force on add always means we delete the component first
                # before we do anything else
                if force :
                    self.uninstallGroupComponent(cType, gid, cid, force)

                # Install our working text files
                if self.importWorkingText(fName, cType, gid, cid, force) :
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

    def newProject (self, pmid='book', tid=None, force=None) :
        '''Create a new publishing project.'''

#        import pdb; pdb.set_trace()

        if not pmid :
            pmid = 'book'

        # Test if this project already exists in the user's config file.
        projHome = os.path.join(os.path.expanduser(self.userConfig['Resources']['projects']), self.pid)
        if os.path.exists(projHome) :
            if force :
                self.tools.terminal('Force project delete for: ' + self.pid)
                ProjDelete().deleteProject(self.pid)
            else :
                self.tools.terminal('ERR: Halt! Project [' + self.pid + '] already exists.')
                return

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
            self.data.templateToProject(self.user, self.local.projHome, self.pid, tid)
        else :
            # If not from a template, just create a new version of the project config file
            Config(self.pid).makeNewprojectConf(self.local, self.pid, self.systemVersion, pmid) 

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

    def importWorkingText (self, source, cType, gid, cid, force = False) :
        '''Import USFM working text from source. Using force will cause
        this function to overwrite an existing version.'''

        # To prevent loading errors, bring this mod now
        proj_process        = ProjProcess(self.pid, gid, self.projectConfig)

        usePreprocessScript = self.tools.str2bool(self.projectConfig['Groups'][gid]['usePreprocessScript'])

        targetFolder        = os.path.join(self.local.projComponentFolder, cid)
        fileHandle          = cid + '_base'
        target              = os.path.join(targetFolder, fileHandle + '.' + cType)
        targetSource        = target + '.source'

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
            # Note that the groupPreprocessFile value is based on the csid,
            # not the gid. This allows for different preprocess scripts
            # to be used for the same type but use can then span groups
            if usePreprocessScript :
                proj_process.checkForPreprocessScript(gid)                
                if not proj_process.runProcessScript(target, self.local.groupPreprocessFile) :
                    self.log.writeToLog(self.errorCodes['1130'], [cid])

            self.takeOutFigMarkers(target, cType, gid, cid)
            self.takeOutFeMarkers(target, cType, gid, cid)
            # If we made it this far, return True
            return True 
        else :
            self.log.writeToLog(self.errorCodes['1150'], [source,self.tools.fName(target)])
            return False


    def takeOutFigMarkers (self, target, cType, gid, cid) :
        '''Remove \fig markers and log the information in a config file.'''

        extractFigMarkers = self.tools.str2bool(self.projectConfig['CompTypes'][cType.capitalize()]['extractFigMarkers'])
        # logUsfmFigure() logs the fig data and strips it from the working text
        # Note: Using partial() to allows the passing of the cid param 
        # into logUsfmFigure()
        if extractFigMarkers :
            tempFile = tempfile.NamedTemporaryFile()
            contents = codecs.open(target, "rt", encoding="utf_8_sig").read()
            contents = re.sub(r'\\fig\s(.+?)\\fig\*', partial(self.logFigure, gid, cid), contents)
            # Write out the remaining data to the working file
            codecs.open(tempFile.name, "wt", encoding="utf_8_sig").write(contents)
            # Finish by copying the tempFile to the source
            shutil.copy(tempFile.name, target)

        # If the text is there, we should return True so do a last check to see
        if os.path.isfile(target) :
            self.log.writeToLog(self.errorCodes['1140'], [cid])
            return True


    def takeOutFeMarkers (self, target, cType, gid, cid) :
        '''Remove \fe markers and log the information in a config file.'''

        extractFeMarkers    = self.tools.str2bool(self.projectConfig['CompTypes'][cType.capitalize()]['extractFeMarkers'])
        # collectEndNotes() removes and collects any end notes found
        # in the working text. They will be processed later and converted
        # to another end matter component.
        # Note: Using partial() to allows the passing of the cid param 
        # into collectEndNotes()
        if extractFeMarkers :
            tempFile = tempfile.NamedTemporaryFile()
            contents = codecs.open(target, "rt", encoding="utf_8_sig").read()
            
# FIXME: The collectEndNotes() function doesn't really work yet.
            
            contents = re.sub(r'\\fe\s(.+?)\\fe\*', partial(self.collectEndNotes, cid), contents)
            # Write out the remaining data to the working file
            codecs.open(tempFile.name, "wt", encoding="utf_8_sig").write(contents)
            # Finish by copying the tempFile to the source
            shutil.copy(tempFile.name, target)

        # If the text is there, we should return True so do a last check to see
        if os.path.isfile(target) :
            self.log.writeToLog(self.errorCodes['1140'], [cid])
            return True


    def usfmCopy (self, source, target, gid) :
        '''Copy USFM text from source to target. Decode if necessary, then
        normalize. With the text in place, validate unless that is False.'''

        sourceEncode                = self.projectConfig['Managers']['usfm_Text']['sourceEncode']
        workEncode                  = self.projectConfig['Managers']['usfm_Text']['workEncode']
        unicodeNormalForm           = self.projectConfig['Managers']['usfm_Text']['unicodeNormalForm']
        validateSourceMarkup        = self.tools.str2bool(self.projectConfig['Groups'][gid]['validateSourceMarkup'])

#        import pdb; pdb.set_trace()

        # Validate the source markup text (Defalt is True)
        if validateSourceMarkup :
            if not self.usfmTextFileIsValid(source, gid) :
                self.log.writeToLog(self.errorCodes['1090'], [source,self.tools.fName(target)])
                return False
        else :
            # Warn that validation was turned off
            self.log.writeToLog(self.errorCodes['1095'], [self.tools.fName(target)])

        # Bring in our source text and work with the encoding if needed
        if sourceEncode == workEncode :
            contents = codecs.open(source, 'rt', 'utf_8_sig')
            lines = contents.read()
        else :
            # Lets try to change the encoding.
            lines = self.tools.decodeText(source, sourceEncode)

        # Normalize the text
        normal = unicodedata.normalize(unicodeNormalForm, lines)
        self.log.writeToLog(self.errorCodes['1080'], [unicodeNormalForm])

        # All should be okay to write out the text to the target
        writeout = codecs.open(target, "wt", "utf_8_sig")
        writeout.write(normal)
        writeout.close
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
        try :
            fh = codecs.open(source, 'rt', 'utf_8_sig')
            stylesheet = usfm.default_stylesheet.copy()
            stylesheet_extra = style.parse(open(os.path.expanduser(self.local.defaultStyFile),'r'))
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


    def collectEndNotes (self, cid, endNoteConts) :
        '''Collect the end notes from a cid.'''

# FIXME: Output the endnotes to a separate file in the component folder for future processing

        self.log.writeToLog(self.errorCodes['1999'], [endNoteConts.group(1)])

        pass


    def logFigure (self, gid, cid, figConts) :
        '''Log the figure data in the illustration.conf. If nothing is returned, the
        existing \fig markers with their contents will be removed. That is the default
        behavior.'''

        # Just in case this section isn't there
        self.tools.buildConfSection(self.illustrationConfig, gid)

        # Description of figKeys (in order found in \fig)
            # description = A brief description of what the illustration is about
            # file = The file name of the illustration (only the file name)
            # caption = The caption that will be used with the illustration (if turned on)
            # width = The width or span the illustration will have (span/col)
            # location = Location information that could be printed in the caption reference
            # copyright = Copyright information for the illustration
            # reference = The book ID (upper-case) plus the chapter and verse (eg. MAT 8:23)

        # We want the figConts to be a list but it comes in as a re group
        figList = figConts.group(1).split('|')

        figKeys = ['description', 'fileName', 'width', 'location', 'copyright', 'caption', 'reference']
        figDict = {}
        # FIXME: If this is for a map and no layout information has been added
        # to the project yet, the cvSep look up will fail, get around with a try
        try :
            cvSep = self.layoutConfig['Illustrations']['chapterVerseSeperator']
        except :
            cvSep = ':'

        # Add all the figure info to the dictionary
        c = 0
        for value in figList :
            figDict[figKeys[c]] = value
            c +=1

        # Add additional information, get rid of stuff we don't need
        figDict['illustrationID'] = figDict['fileName'].split('.')[0]
        figDict['useThisIllustration'] = True
        figDict['useThisCaption'] = True
        figDict['useThisCaptionRef'] = True
        figDict['bid'] = cid
        c = re.search(ur'([0-9]+)[.:][0-9]+', figDict['reference'].upper())
        if c is None :
            figDict['chapter'] = 0  # Or however you want to handle "pattern not found"
        else:
            figDict['chapter'] = c.group(1)

        v = re.search(ur'[0-9]+[.:]([0-9]+)', figDict['reference'].upper())
        if v is None :
            figDict['verse'] = 0  # Or however you want to handle "pattern not found"
        else:
            figDict['verse'] = v.group(1)

        # If this is an update, we need to keep the original settings in case the
        # default settings have been modified for this project.
        # Illustration Scale
        if self.illustrationConfig[gid].has_key(figDict['illustrationID']) :
            figDict['scale'] = self.illustrationConfig[gid][figDict['illustrationID']]['scale']
        else :
            figDict['scale'] = '1.0'
        # Illustration Position
        if self.illustrationConfig[gid].has_key(figDict['illustrationID']) :
            figDict['position'] = self.illustrationConfig[gid][figDict['illustrationID']]['position']
        else :
            if figDict['width'] == 'col' :
                figDict['position'] = 'tl'
            else :
                figDict['position'] = 't'
        # Illustration Location
        if self.illustrationConfig[gid].has_key(figDict['illustrationID']) :
            figDict['location'] = self.illustrationConfig[gid][figDict['illustrationID']]['location']
        else :
            if not figDict['location'] :
                figDict['location'] = figDict['chapter'] + cvSep + figDict['verse']
        # Now make (update) the actual illustration section
        if not self.illustrationConfig.has_key(gid) :
            self.tools.buildConfSection(self.illustrationConfig, gid)
        # Put the dictionary info into the illustration conf file
        if not self.illustrationConfig[gid].has_key(figDict['illustrationID']) :
            self.tools.buildConfSection(self.illustrationConfig[gid], figDict['illustrationID'])
        for k in figDict.keys() :
            self.illustrationConfig[gid][figDict['illustrationID']][k] = figDict[k]

        # Write out the conf file to preserve the data found
        self.tools.writeConfFile(self.illustrationConfig)

        # Just incase we need to keep the fig markers intact this will
        # allow for that. However, default behavior is to strip them
        # because usfmTex does not handle \fig markers. By returning
        # them here, they will not be removed from the working text.
        # FIXME: One issue here is that is is basicaly hard-wired for
        # usfm to be the only cType. This breaks if you are working with
        # something else. To get around it we will use a try statement
        try :
            if self.tools.str2bool(self.projectConfig['Managers'][self.cType + '_Illustration']['preserveUsfmFigData']) :
                return '\\fig ' + figConts.group(1) + '\\fig*'
        except :
            return None


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

    def __init__(self) :
        '''Intitate the whole class and create the object.'''

        self.user                           = UserConfig()
        self.userConfig                     = self.user.userConfig
        self.tools                          = Tools()

# Currently there is only this function in this class

    def deleteProject (self, pid) :
        '''Delete a project.'''

        projHome                            = os.path.join(os.path.expanduser(self.userConfig['Resources']['projects']), pid)

        # Delete project
        if os.path.exists(projHome) :
            shutil.rmtree(projHome)
            self.tools.terminal('Removed project files for [' + pid + '] from hard drive.')
            return True
        else :
            self.tools.terminal('Warning: [' + pid + '] project could not be found, unable to delete project files.')




