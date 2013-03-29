#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111203
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project infrastructure tasks.

# History:
# 20110823 - djd - Started with intial file from Rapuma project
# 20111203 - djd - Begin changing over to new manager model


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, sys, shutil, imp, subprocess, zipfile, StringIO, filecmp
from configobj import ConfigObj, Section


# Load the local classes
from rapuma.core.tools import *
import rapuma.project.manager as mngr
import rapuma.core.user_config as userConfig
#from rapuma.component.usfm import PT_Tools
from rapuma.group.usfm import PT_Tools
from importlib import import_module

###############################################################################
################################## Begin Class ################################
###############################################################################

class Project (object) :

    def __init__(self, userConfig, projConfig, local, log, systemVersion, gid = None) :
        '''Instantiate this class.'''

#        import pdb; pdb.set_trace()
#        self.pt_tools               = PT_Tools(self)
        self.local                  = local
        self.userConfig             = userConfig
        self.projConfig             = projConfig
        self.log                    = log
        self.systemVersion          = systemVersion
        self.groups                 = {}
        self.components             = {}
#        self.componentType          = {}
        self.managers               = {}
        self.projectMediaIDCode     = self.projConfig['ProjectInfo']['projectMediaIDCode']
        self.projectIDCode          = self.projConfig['ProjectInfo']['projectIDCode']
        self.projectName            = self.projConfig['ProjectInfo']['projectName']
        # The gid cannot generally be set yet but we will make a placeholder
        # for it here and the functions below will set it. (I'm just say'n)
        self.gid                    = gid

#        import pdb; pdb.set_trace()

        m = import_module('rapuma.project.' + self.projectMediaIDCode)
#       or you could use:
#        m = import_module('..' + self.projectMediaIDCode, mngr.__name__)
        self.__class__ = getattr(m, self.projectMediaIDCode[0].upper() + self.projectMediaIDCode[1:])

        # Update the existing config file with the project type XML file
        # if needed
        newXmlDefaults = os.path.join(self.local.rapumaConfigFolder, self.projectMediaIDCode + '.xml')
        xmlConfig = getXMLSettings(newXmlDefaults)
        newConf = ConfigObj(xmlConfig.dict(), encoding='utf-8').override(self.projConfig)
        for s,v in self.projConfig.items() :
            if s not in newConf :
                newConf[s] = v

        # Replace with new conf if new is different from old
        # Rem new conf doesn't have a filename, give it one
        if self.projConfig != newConf :
            self.projConfig = newConf
            self.projConfig.filename = self.local.projConfFile

        # Up the creatorVersion on the project if needed
        if not testForSetting(self.projConfig, 'ProjectInfo', 'projectCreatorVersion') :
            self.projConfig['ProjectInfo']['projectCreatorVersion'] = self.systemVersion
            writeConfFile(self.projConfig)
        else :
            if self.projConfig['ProjectInfo']['projectCreatorVersion'] != self.systemVersion :
                self.projConfig['ProjectInfo']['projectCreatorVersion'] = self.systemVersion
                writeConfFile(self.projConfig)

        # If this is a valid project we might as well put in the folders
        for folder in self.local.projFolders :
            if not os.path.isdir(getattr(self.local, folder)) :
                os.makedirs(getattr(self.local, folder))

        # Go ahead and set this as the current project
        self.setProjCurrent(self.projectIDCode)

        # Log messages for this module
        self.errorCodes     = {
            'PROJ-000' : ['MSG', 'Project module messages'],
            'PROJ-010' : ['LOG', 'Wrote out [<<1>>] settings to the project configuration file.'],
            'PROJ-011' : ['ERR', 'Failed to write out project [<<1>>] settings to the project configuration file.'],
            'PROJ-030' : ['MSG', 'Changed  [<<1>>][<<2>>][<<3>>] setting from \"<<4>>\" to \"<<5>>\".'],
            'PROJ-040' : ['ERR', 'Problem making setting change. Section [<<1>>] missing from configuration file.'],
            'PROJ-050' : ['ERR', 'Component [<<1>>] working text file was not found in the project configuration.'],
            'PROJ-060' : ['ERR', 'Component [<<1>>] was not found in the project configuration.'],
            'PROJ-070' : ['ERR', 'Source file not found: [<<1>>].'],
            'PROJ-080' : ['MSG', 'Successful copy of [<<1>>] to [<<2>>].'],
            'PROJ-090' : ['ERR', 'Target file [<<1>>] already exists. Use force (-f) to overwrite.'],

            '205' : ['LOG', 'Created the [<<1>>] manager object.'],
        }

###############################################################################
############################ Manager Level Functions ##########################
###############################################################################
######################## Error Code Block Series = 200 ########################
###############################################################################

    def createManager (self, cType, mType) :
        '''Check to see if a manager is listed in the config and load it if
        it is not already.'''

        fullName = cType + '_' + mType.capitalize()
        if fullName not in self.managers :
            self.addManager(cType, mType)
            self.loadManager(cType, mType)
            self.log.writeToLog(self.errorCodes['205'], [fullName])


    def loadManager (self, cType, mType) :
        '''Do basic load on a manager.'''

#        if mType == 'component' :
#            import pdb; pdb.set_trace()

        fullName = cType + '_' + mType.capitalize()
        cfg = self.projConfig['Managers'][fullName]
        module = import_module('rapuma.manager.' + mType)
        ManagerClass = getattr(module, mType.capitalize())
        manobj = ManagerClass(self, cfg, cType)
        self.managers[fullName] = manobj


    def addManager (self, cType, mType) :
        '''Create a manager reference in the project config that components
        will point to.'''

#        import pdb; pdb.set_trace()

        fullName = cType + '_' + mType.capitalize()
        managerDefaults = None
        # Insert the Manager section if it is not already there
        buildConfSection(self.projConfig, 'Managers')
        if not testForSetting(self.projConfig['Managers'], fullName) :
            buildConfSection(self.projConfig['Managers'], fullName)

        # Update settings if needed
        update = False
        managerDefaults = getXMLSettings(os.path.join(self.local.rapumaConfigFolder, mType + '.xml'))
        for k, v, in managerDefaults.iteritems() :
            # Do not overwrite if a value is already there
            if not testForSetting(self.projConfig['Managers'][fullName], k) :
                self.projConfig['Managers'][fullName][k] = v
                # If we are dealing with an empty string, don't bother writing out
                # Trying to avoid needless conf updating here. Just in case we are
                # working with a list, we'll use len()
                if len(v) > 0 :
                    update = True
        # Update the conf if one or more settings were changed
        if update :
            if writeConfFile(self.projConfig) :
                self.log.writeToLog('PROJ-010',[fullName])
            else :
                self.log.writeToLog('PROJ-011',[fullName])


###############################################################################
############################ Group Level Functions ############################
###############################################################################

    def getGroupSourcePath (self, gid) :
        '''Get the source path for a specified group.'''

#        import pdb; pdb.set_trace()
        csid = self.projConfig['Groups'][gid]['csid']

        try :
            return self.userConfig['Projects'][self.projectIDCode][csid + '_sourcePath']
        except Exception as e :
            # If we don't succeed, we should probably quite here
            terminal('No source path found for: [' + str(e) + ']')
            terminal('Please add a source path for this component type.')
            dieNow()


    def renderGroup (self, gid, cidList = None, force = False) :
        '''Render a group of subcomponents or any number of components
        in the group specified in the cidList.'''

#        import pdb; pdb.set_trace()

        # Just in case, set the gid here.
        self.gid = gid

        # Do a basic test for exsistance
        if isConfSection(self.projConfig['Groups'], gid) :
            # Check for cidList, use std group if it isn't there
            if cidList :
                if isinstance(cidList, str) :
                    cidList = cidList.split()
            else :
                cidList = self.projConfig['Groups'][gid]['cidList']

            # Make a dictionary of the rendering params for this run
            # We do this to both protect the params and perhaps expand
            # them in the future
            renderParams = {'cidList' : cidList, 'force' : force}
            # Now create the group and pass the param on
            self.createGroup(gid).render(renderParams)
            return True


    def isGroup (self, gid) :
        '''Return True if this gid is found in the project config.'''

        return isConfSection(self.projConfig['Groups'], gid)


    def createGroup (self, gid) :
        '''Create a group object that can be acted on. It is assumed
        this only happens for one group per session. This group
        will contain one or more compoenents. The information for
        each one will be contained in the group object.'''

        # Just in case, set the gid here.
        self.gid = gid

        # If the object already exists just return it
        if gid in self.groups: return self.groups[gid]

#        import pdb; pdb.set_trace()

        cType = self.projConfig['Groups'][gid]['cType']
        # Create a special component object if called
        cfg = self.projConfig['Groups'][gid]
        module = import_module('rapuma.group.' + cType)
        ManagerClass = getattr(module, cType.capitalize())
        groupObj = ManagerClass(self, cfg)
        self.groups[gid] = groupObj

        return groupObj


    def installGroupComps (self, gid, cidList, force = False) :
        '''This will install components to the group we created above in createGroup().
        If a component is already installed in the project it will not proceed unless
        force is set to True. Then it will remove the component files so a fresh copy
        can be added to the project.'''

#        import pdb; pdb.set_trace()

        # Get some group settings
        cType       = self.projConfig['Groups'][gid]['cType']
        csid        = self.projConfig['Groups'][gid]['csid']
        sourcePath  = self.userConfig['Projects'][self.projectIDCode][csid + '_sourcePath']

        for cid in cidList :
            # See if the working text is present, quite if it is not
            if cType == 'usfm' :
                # Force on add always means we delete the component first
                # before we do anything else
                if force :
                    self.uninstallGroupComponent(gid, cid, force)

                # Install our working text files
                self.createManager(cType, 'text')
                if self.groups[gid].installUsfmWorkingText(gid, cid, force) :
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


    def removeGroup (self, gid, force = False) :
        '''Handler to remove a group. If it is not found return True anyway.'''

        cidList     = self.projConfig['Groups'][gid]['cidList']
        cType     = self.projConfig['Groups'][gid]['cType']
        groupFolder = os.path.join(self.local.projComponentsFolder, gid)
        # Create the group object now
        self.createGroup(gid)

        # First test for lock
        if self.isLocked(gid) and force == False :
            self.log.writeToLog('COMP-110', [gid])
            dieNow()

        # Remove subcomponents from the target if there are any
        buildConfSection(self.projConfig, 'Groups')
        if isConfSection(self.projConfig['Groups'], gid) :
            for cid in cidList :
                self.uninstallGroupComponent(gid, cid, force)
            if os.path.exists(groupFolder) :
                shutil.rmtree(groupFolder)
                self.log.writeToLog('GRUP-090', [gid])
        else :
            self.log.writeToLog('GRUP-050', [gid])
            
        # Now remove the config entry
        del self.projConfig['Groups'][gid]
        if writeConfFile(self.projConfig) :
            self.log.writeToLog('GRUP-120', [gid])


    def updateGroup (self, gid, cidList = None, sourcePath = None, force = False) :
        '''Update a group, --source is optional but if given it will
        overwrite the current setting. The use of this function implies
        that this is forced so no force setting is used.'''

        # Just in case there are any problems with the source path
        # resolve it here before going on.
        csid = self.projConfig['Groups'][gid]['csid']
        if not sourcePath :
            try :
                sourcePath  = self.userConfig['Projects'][self.projectIDCode][csid + '_sourcePath']
                if not os.path.exists(sourcePath) :
                    self.log.writeToLog('GRUP-020', [csid])
                    dieNow()
            except :
                self.log.writeToLog('GRUP-025', [csid])
                dieNow()
        else :
            sourcePath = resolvePath(sourcePath)
            if not os.path.exists(sourcePath) :
                self.log.writeToLog('GRUP-030')
                dieNow()

            # Reset the source path for this csid
            self.userConfig['Projects'][self.projectIDCode][csid + '_sourcePath'] = sourcePath
            writeConfFile(self.userConfig)

        # Create the group object now
        self.createGroup(gid)

        # Check to be sure the group exsits
        if not self.groups[gid] :
            self.log.writeToLog('COMP-210', [gid])
            dieNow()
        
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
            self.log.writeToLog('COMP-110', [gid])
            dieNow()

        # Here we essentially re-add the component(s) of the group
        self.installGroupComps(gid, cidList, force)
        # Now lock it down
        self.lockUnlock(gid, True)


    def hasValidSourcePath (self, gid, csid) :
        '''Check if there is one, see if it is valid.'''

        try :
            path = self.userConfig['Projects'][self.projectIDCode][csid + '_sourcePath']
            return os.path.isdir(resolvePath(path))
        except :
            return False


    def isValidCidList (self, gid, thisCidlist) :
        '''Check to see if all the components in the list are in the group.'''

        thisCidlist = thisCidlist.split()
        cidList = self.projConfig['Groups'][gid]['cidList']
        for cid in thisCidlist :
            if not cid in cidList :
                return False
        return True


#    def addCompGroupSourcePath (self, csid, source) :
#        '''Add a source path for components used in a group if none
#        exsist. If one exists, replace anyway. Last in wins! The 
#        assumption is only one path per component group.'''

#        # Path has been resolved in Rapuma, we assume it should be valid.
#        # But it could be a full file name. We need to sort that out.
#        try :
#            if os.path.isdir(source) :
#                self.userConfig['Projects'][self.projectIDCode][csid + '_sourcePath'] = source
#            else :
#                self.userConfig['Projects'][self.projectIDCode][csid + '_sourcePath'] = os.path.split(source)[0]

#            writeConfFile(self.userConfig)
#        except Exception as e :
#            # If we don't succeed, we should probably quite here
#            self.log.writeToLog('GRUP-100', [str(e)])
#            dieNow()


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

        # First be sure this is a valid component
        if not self.groups[gid] :
            self.log.writeToLog('LOCK-010', [gid])
            dieNow()
        else :
            self.setLock(gid, lock)
            return True


    def setLock (self, gid, lock) :
        '''Set a group lock to True or False.'''

        if testForSetting(self.projConfig['Groups'], gid) :
            self.projConfig['Groups'][gid]['isLocked'] = lock
            # Update the projConfig
            if writeConfFile(self.projConfig) :
                # Report back
                self.log.writeToLog('LOCK-020', [gid, str(lock)])
                return True
        else :
            self.log.writeToLog('LOCK-030', [gid, str(lock)])
            return False


    def listAllComponents (self, cType) :
        '''Generate a list of valid component IDs and cNames for this cType.'''

        # Create the component object now with a special component caller ID
        self.createComponent('usfm_internal_caller')
        # Get the component info dictionary
        comps = self.components['usfm_internal_caller'].usfmCidInfo()
        # List and sort
        cList = list(comps.keys())
        cList.sort()
        # For now we'll output to terminal but may want to change this later.
        for c in cList :
            if c != '_z_' :
                print c, comps[c][1]


    def uninstallGroupComponent (self, gid, cid, force = False) :
        '''This will remove a component (files) from a group in the project.
        However, a backup will be made of the working text for comparison purposes. 
       This does not return anything. We trust it worked.'''

        cType       = self.projConfig['Groups'][gid]['cType']
        csid        = self.projConfig['Groups'][gid]['csid']
        fileHandle  = self.managers[cType + '_Component'].makeFileName(cid)
        self.createManager(cType, 'component')
        fileName    = self.managers[cType + '_Component'].makeFileNameWithExt(cid)

        # Test to see if it is shared
        if self.isSharedComponent(gid, fileHandle) :
            self.log.writeToLog('GRUP-060', [fileHandle,gid])
            dieNow()

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
                self.log.writeToLog('GRUP-070', [fName(targetComp), cid])
                for fn in os.listdir(targetFolder) :
                    f = os.path.join(targetFolder, fn)
                    if f != targetComp :
                        os.remove(f)
                        self.log.writeToLog('GRUP-080', [fName(f), cid])


    def isSharedComponent (self, gid, cid) :
        '''If the cid is shared by any other groups, return True.'''

        try :
            for g in self.projConfig['Groups'].keys() :
                if g != gid :
                    if cid in self.projConfig['Groups'][g]['cidList'] :
                        return True
        except :
            return False


###############################################################################
########################## Component Level Functions ##########################
###############################################################################

    def setProjCurrent (self, pid) :
        '''Compare pid with the current recored pid e rapuma.conf. If it is
        different change to the new pid. If not, leave it alone.'''

        currentPid = self.userConfig['System']['current']
        if pid != currentPid :
            self.userConfig['System']['current'] = pid
            writeConfFile(self.userConfig)


#    def addComponentType (self, cType) :
#        '''Add (register) a component type to the config if it 
#        is not there already.'''

#        Ctype = cType.capitalize()
#        if cType not in self.components :
#            # Build the comp type config section
#            buildConfSection(self.projConfig, 'CompTypes')
#            buildConfSection(self.projConfig['CompTypes'], Ctype)

#            # Get persistant values from the config if there are any
#            newSectionSettings = getPersistantSettings(self.projConfig['CompTypes'][Ctype], os.path.join(self.local.rapumaConfigFolder, cType + '.xml'))
#            if newSectionSettings != self.projConfig['CompTypes'][Ctype] :
#                self.projConfig['CompTypes'][Ctype] = newSectionSettings
#                # Save the setting rightaway
##                import pdb; pdb.set_trace()
#                writeConfFile(self.projConfig)

#            # Sanity check
#            if cType not in self.components :
#                self.log.writeToLog('COMP-060', [cType])
#                return True
#            else :
#                self.log.writeToLog('COMP-065', [cType])
#                return False
#        else :
#            # Bow out gracefully
#            return False


#    def updateComponent (self, cName, source = None, force = False) :
#        '''Update a component, --source is optional but if given it will
#        overwrite the current setting. The use of this function implies
#        that this is forced so no force setting is used.'''

#        # Create the component object now
#        self.createComponent(cName)

#        # Check to be sure the component exsits
#        if not self.components[cName] :
#            self.log.writeToLog('COMP-210', [cName])
#            dieNow()

#        # If force is used, just unlock by default
#        if force :
#            self.lockUnlock(cName, False, force)

#        # Be sure the component (and subcomponents) are unlocked
#        if self.isLocked(cName) :
#            self.log.writeToLog('COMP-110', [cName])
#            dieNow()

#        # Here we essentially re-add the component
#        cType = self.groups[gid].getComponentType(gid)
#        cidList = self.groups[gid].getSubcomponentList(gid)
#        if not source :
#            source = self.userConfig['Projects'][self.projectIDCode][cType + '_sourcePath']
##        self.addComponent(cType, cName, cidList, source, force)
#        installUsfmWorkingText (self, gid, cid, force = False)        

#        # Now do a compare between the old component and the new one
#        if str2bool(self.projConfig['Managers'][cType + '_Text']['useAutoCompare']) :
#            self.compareComponent(cName, 'working')



###############################################################################
############################## Exporting Functions ############################
###############################################################################


#    def export (self, cType, cName, path = None, script = None, bundle = False, force = False) :
#        '''Facilitate the exporting of project text. It is assumed that the
#        text is clean and ready to go and if any extraneous publishing info
#        has been injected into the text, it will be removed by an appropreate
#        post-process that can be applied by this function. No validation
#        will be initiated by this function.'''
#        
#        # FIXME - Todo: add post processing script feature

#        # Probably need to create the component object now
#        self.createComponent(cName)

#        # Figure out target path
#        if path :
#            path = resolvePath(path)
#        else :
#            parentFolder = os.path.dirname(self.local.projHome)
#            path = os.path.join(parentFolder, 'Export')

#        # Make target folder if needed
#        if not os.path.isdir(path) :
#            os.makedirs(path)

#        # Start a list for one or more files we will process
#        fList = []

#        # Will need the stylesheet for copy
#        projSty = self.projConfig['Managers'][cType + '_Style']['mainStyleFile']
#        projSty = os.path.join(self.local.projStylesFolder, projSty)
#        # Process as list of components

#        self.log.writeToLog('XPRT-040')
#        for cid in self.components[cName].getSubcomponentList(cName) :
#            cidCName = self.components[cName].getRapumaCName(cid)
#            ptName = PT_Tools(self).formPTName(cName, cid)
#            # Test, no name = no success
#            if not ptName :
#                self.log.writeToLog('XPRT-010')
#                dieNow()

#            target = os.path.join(path, ptName)
#            source = os.path.join(self.local.projComponentsFolder, cidCName, cid + '.' + cType)
#            # If shutil.copy() spits anything back its bad news
#            if shutil.copy(source, target) :
#                self.log.writeToLog('XPRT-020', [fName(target)])
#            else :
#                fList.append(target)

#        # Start the main process here
#        if bundle :
#            archFile = os.path.join(path, cName + '_' + ymd() + '.zip')
#            # Hopefully, this is a one time operation but if force is not True,
#            # we will expand the file name so nothing is lost.
#            if not force :
#                if os.path.isfile(archFile) :
#                    archFile = os.path.join(path, cName + '_' + fullFileTimeStamp() + '.zip')

#            myzip = zipfile.ZipFile(archFile, 'w', zipfile.ZIP_DEFLATED)
#            for f in fList :
#                # Create a string object from the contents of the file
#                strObj = StringIO.StringIO()
#                for l in open(f, "rb") :
#                    strObj.write(l)
#                # Write out string object to zip
#                myzip.writestr(fName(f), strObj.getvalue())
#                strObj.close()
#            # Close out the zip and report
#            myzip.close()
#            # Clean out the folder
#            for f in fList :
#                os.remove(f)
#            self.log.writeToLog('XPRT-030', [fName(archFile)])
#        else :
#            self.log.writeToLog('XPRT-030', [path])

#        return True


###############################################################################
############################ System Level Functions ###########################
###############################################################################

    def run (self, command, opts, userConfig) :
        '''Run a command'''

        if command in self.commands :
            self.commands[command].run(opts, self, userConfig)
        else :
            terminalError('The command: [' + command + '] failed to run with these options: ' + str(opts))


    def isProject (self, pid) :
        '''Look up in the user config to see if a project is registered. This
        is a duplicate of the function in the main rapuma file.'''

        try :
            if pid in self.userConfig['Projects'].keys() :
                pass
        except :
            sys.exit('\nERROR: Project ID given is not valid! Process halted.\n')


    def installFile (self, source, path, force) :
        '''Install a file into a project. Overwrite if force is set to True.'''

        source = resolvePath(source)
        target = os.path.join(resolvePath(path), fName(source))
        if not os.path.isfile(source) :
            self.log.writeToLog('PROJ-070', [source])

        if os.path.isfile(target) :
            if force :
                if not shutil.copy(source, target) :
                    self.log.writeToLog('PROJ-080', [source,target])
            else :
                self.log.writeToLog('PROJ-090', [source,target])
        else :
            if not shutil.copy(source, target) :
                self.log.writeToLog('PROJ-080', [source,target])


    def addMacro (self, name, cmd = None, path = None, force = False) :
        '''Install a user defined macro.'''

        # Define some internal vars
        oldMacro            = ''
        sourceMacro         = ''
        # FIXME: This needs to support a file extention such as .sh
        if path and os.path.isfile(os.path.join(resolvePath(path))) :
            sourceMacro     = os.path.join(resolvePath(path))
        macroTarget         = os.path.join(self.local.projUserMacrosFolder, name)
        if testForSetting(self.projConfig['GeneralSettings'], 'userMacros') and name in self.projConfig['GeneralSettings']['userMacros'] :
            oldMacro = name

        # First check for prexsisting macro record
        if not force :
            if oldMacro :
                self.log.writeToLog('MCRO-010', [oldMacro])
                dieNow()

        # Make the target folder if needed (should be there already, though)
        if not os.path.isdir(self.local.projUserMacrosFolder) :
            os.makedirs(self.local.projUserMacrosFolder)

        # First check to see if there already is a macro file, die if there is
        if os.path.isfile(macroTarget) and not force :
            self.log.writeToLog('MCRO-020', [fName(macroTarget)])
            dieNow()
            
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
        if testForSetting(self.projConfig['GeneralSettings'], 'userMacros') :
            macroList = self.projConfig['GeneralSettings']['userMacros']
            if fName(macroTarget) not in macroList :
                self.projConfig['GeneralSettings']['userMacros'] = addToList(macroList, fName(macroTarget))
                writeConfFile(self.projConfig)
        else :
                self.projConfig['GeneralSettings']['userMacros'] = [fName(macroTarget)]
                writeConfFile(self.projConfig)

        self.log.writeToLog('MCRO-030', [fName(macroTarget)])
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
            self.log.writeToLog('MCRO-060', [fName(macroFile)])


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
            dieNow()


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
                dieNow()

            self.createManager(cType, 'text')
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
                self.log.writeToLog('EDIT-020', [fName(compWorkText)])
                dieNow()

        # Look at project global settings
        if glob :
            for files in os.listdir(self.local.projConfFolder):
                if files.endswith(".conf"):
                    editDocs.append(os.path.join(self.local.projConfFolder, files))

            globSty = os.path.join(self.local.projStylesFolder, self.projConfig['Managers']['usfm_Style']['mainStyleFile'])
            custSty = os.path.join(self.local.projStylesFolder, self.projConfig['Managers']['usfm_Style']['customStyleFile'])
            if os.path.isfile(globSty) :
                editDocs.append(globSty)
            if os.path.isfile(custSty) :
                editDocs.append(custSty)

            # FIXME: This next part is hard-wired, be nice to do better
            fileName = 'xetex_settings_usfm-ext.tex'
            macExt = os.path.join(self.local.projMacrosFolder, 'usfmTex', fileName)
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




