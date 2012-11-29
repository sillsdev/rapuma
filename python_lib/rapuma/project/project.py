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

import codecs, os, sys, shutil, imp, subprocess, zipfile, StringIO
#from configobj import ConfigObj, Section


# Load the local classes
from rapuma.core.tools import *
from rapuma.core.pt_tools import *
import rapuma.project.manager as mngr
import rapuma.component.component as cmpt
import rapuma.core.user_config as userConfig
from importlib import import_module

###############################################################################
################################## Begin Class ################################
###############################################################################

class Project (object) :

    def __init__(self, userConfig, projConfig, local, log) :
        '''Instantiate this class.'''

        self.local                  = local
        self.userConfig             = userConfig
        self.projConfig             = projConfig
        self.log                    = log
        self.components             = {}
        self.componentType          = {}
        self.managers               = {}
        self.projectMediaIDCode     = self.projConfig['ProjectInfo']['projectMediaIDCode']
        self.projectIDCode          = self.projConfig['ProjectInfo']['projectIDCode']
        self.projectName            = self.projConfig['ProjectInfo']['projectName']

        # Do some cleanup like getting rid of the last sessions error log file.
        try :
            if os.path.isfile(self.local.projErrorLogFile) :
                os.remove(self.local.projErrorLogFile)
        except :
            pass

        # Initialize the project type
        # FIXME: some additional work needs to be done to simplify this
        # This will have to do for now.
        m = import_module('rapuma.project.' + self.projectMediaIDCode)
#       or you could use:
#        m = import_module('..' + self.projectMediaIDCode, mngr.__name__)
        self.__class__ = getattr(m, self.projectMediaIDCode[0].upper() + self.projectMediaIDCode[1:])

        # Update the existing config file with the project type XML file
        # if needed
        newXmlDefaults = os.path.join(self.local.rapumaConfigFolder, self.projectMediaIDCode + '.xml')
        xmlConfig = getXMLSettings(newXmlDefaults)
        newConf = ConfigObj(xmlConfig.dict()).override(self.projConfig)
        for s,v in self.projConfig.items() :
            if s not in newConf :
                newConf[s] = v

        if self.projConfig != newConf :
            self.projConfig = newConf

        # If this is a valid project we might as well put in the folders
        for folder in self.local.projFolders :
            if not os.path.isdir(getattr(self.local, folder)) :
                os.makedirs(getattr(self.local, folder))


###############################################################################
############################ Manager Level Functions ##########################
###############################################################################

    def createManager (self, cType, mType) :
        '''Check to see if a manager is listed in the config and load it if
        it is not already.'''

        fullName = cType + '_' + mType.capitalize()
        if fullName not in self.managers :
            self.addManager(cType, mType)
            self.loadManager(cType, mType)
            self.log.writeToLog('PROJ-005', [fullName])
#            return self.managers[fullName]


    def loadManager (self, cType, mType) :
        '''Do basic load on a manager.'''

#        import pdb; pdb.set_trace()

        fullName = cType + '_' + mType.capitalize()
        cfg = self.projConfig['Managers'][fullName]
        module = import_module('rapuma.manager.' + mType)
        ManagerClass = getattr(module, mType.capitalize())
        manobj = ManagerClass(self, cfg, cType)
        self.managers[fullName] = manobj


    def addManager (self, cType, mType) :
        '''Create a manager reference in the project config that components will point to.'''
#        import pdb; pdb.set_trace()

        fullName = cType + '_' + mType.capitalize()
        managerDefaults = None
        # Insert the Manager section if it is not already there
        buildConfSection(self.projConfig, 'Managers')
        if not testForSetting(self.projConfig['Managers'], fullName) :
            buildConfSection(self.projConfig['Managers'], fullName)
            managerDefaults = getXMLSettings(os.path.join(self.local.rapumaConfigFolder, mType + '.xml'))
            for k, v, in managerDefaults.iteritems() :
                # Do not overwrite if a value is already there
                if not testForSetting(self.projConfig['Managers'][fullName], k) :
                    self.projConfig['Managers'][fullName][k] = v

            if writeConfFile(self.projConfig) :
                self.log.writeToLog('PROJ-010',[fullName])
            else :
                self.log.writeToLog('PROJ-011',[fullName])


###############################################################################
########################## Component Level Functions ##########################
###############################################################################


    def hasCidFile (self, cid) :
        '''Check to see if a file exists for a given cid.'''

        return os.path.isfile(os.path.join(self.local.projComponentsFolder, cid, cid + '.' + self.projConfig['Components'][cid]['type']))


    def isComponent (self, cid) :
        '''Simple test to see if a component exsists. Return True if it is.
        If it is a meta component then test for the exsistance of every
        cid in the group. Note: This assumes that because the component
        has been installed through the system, it is a valid type ID so
        no testin of component type ID is being done.'''

        def testComponent(cid) :
            if testForSetting(self.projConfig, 'Components', cid) :
                if self.hasCidFile(cid) :
                    return True
                else :
                    self.log.writeToLog('COMP-050', [cid])
            else :
                self.log.writeToLog('COMP-060', [cid])

        # Check first to see if this is a meta component
        if self.isMetaComponent(cid) :
            for c in self.projConfig['Components'][cid]['list'] :
                if testComponent(c) :
                    return True
        else :
            if testComponent(cid) :
                return True


    def findBadComp (self, cid) :
        '''Much like isComponent() but it returns the first offending
        cid ID it finds.'''

        if self.isMetaComponent(cid) :
            for i in self.projConfig['Components'][cid]['list'] :
                if not hasUsfmCidInfo(i) :
                    return i
        else :
            if not hasUsfmCidInfo(cid) :
                return cid


    def isMetaComponent (self, cid) :
        '''Return True if this component has a list of component in it.'''

        try :
            if testForSetting(self.projConfig['Components'][cid], 'list') :
                return True
            else :
                return False
        except :
            return False

    def isComponentType (self, cType) :
        '''Simple test to see if a component type exsists. Return True if it is.'''

        Ctype = cType.capitalize()
        if testForSetting(self.projConfig, 'CompTypes', Ctype) :
            return True


    def renderComponent (self, cid, force = False) :
        '''Render a single component. This will ensure there is a component
        object, then render it. However, just because the object exsists
        does not mean all the parts of the componet are in place. Rendering
        could fail if something is missing.'''

#        import pdb; pdb.set_trace()

        # Check for cid in config
        if self.isComponent(cid) :
            self.createComponent(cid).render(force)
            return True

        else :
            bad = self.findBadComp(cid)
            if bad :
                if bad == cid :
                    self.log.writeToLog('COMP-011', [cid])
                else :
                    self.log.writeToLog('COMP-012', [bad,cid])
                return False
            return True


    def validateComponent (self, cid) :
        '''Validate a component (cannot be a group) return True if it is good.
        If not, output the errors and return False.'''

        self.log.writeToLog('COMP-080')


    def createComponent (self, cid) :
        '''Create a component object that can be acted on.'''

        # If the object already exists just return it
        if cid in self.components : return self.components[cid]

#        import pdb; pdb.set_trace()

        # Otherwise, create a new one and return it
        if testForSetting(self.projConfig, 'Components', cid) :
            cfg = self.projConfig['Components'][cid]
            cType = cfg['type']
            module = import_module('rapuma.component.' + cType)
            ManagerClass = getattr(module, cType.capitalize())
            compobj = ManagerClass(self, cfg)
            self.components[cid] = compobj
        else :
            self.log.writeToLog('COMP-040', [cid])
            return False

        return compobj


    def hasSourcePath (self, cType) :
        '''Check to see if there is a pre-exsisting path.'''

        Ctype = cType.capitalize()
        if testForSetting(self.projConfig['CompTypes'][Ctype], 'sourcePath') :
            if self.projConfig['CompTypes'][Ctype]['sourcePath'] != '' :
                return True


    def sourceIsSame (self, cType, source) :
        '''Check to see if the existing path is the same as the
        new proposed path.'''

        curPath = self.projConfig['CompTypes'][cType.capitalize()]['sourcePath']
        if curPath == source :
            return True


    def addCompTypeSourcePath (self, cType, source) :
        '''Add a source path for a component type if one does not
        already exsist. If one exists, replace anyway. Last in wins!
        The assumption is only one path per component type.'''

        Ctype = cType.capitalize()
        # Path has been resolved in Rapuma, we assume it should be valid.
        # But it could be a full file name. We need to sort that out.
        try :
            if os.path.isdir(source) :
                self.projConfig['CompTypes'][Ctype]['sourcePath'] = source
            else :
                self.projConfig['CompTypes'][Ctype]['sourcePath'] = os.path.split(source)[0]

            writeConfFile(self.projConfig)
        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.project.log.writeToLog('PROJ-100', [str(e)])
            dieNow()


    def addComponentGroup (self, cType, gid, thisList, source, force = False) :
        '''Add a component group to the project. If any of the individual
        components are missing, it will try to add them to the project.'''

        # Make sure the source path is there for this component type
        if force :
            self.addCompTypeSourcePath(cType, source)
        else :
            if not self.hasSourcePath(cType) :
                self.addCompTypeSourcePath(cType, source)
            else :
                if not self.sourceIsSame(cType, source) :
                    current = self.projConfig['CompTypes'][cType.capitalize()]['sourcePath']
                    self.log.writeToLog('COMP-090', [cType,current,source])
                    dieNow()

        # Add/check individual components
        cidList = thisList.split()
        for cid in cidList :
            self.addComponent(cid, cType, source, force)

        # Add the info to the components
        buildConfSection(self.projConfig, 'Components')
        buildConfSection(self.projConfig['Components'], gid)
        self.projConfig['Components'][gid]['name'] = gid
        self.projConfig['Components'][gid]['type'] = cType
        self.projConfig['Components'][gid]['list'] = cidList

        # Save our config settings
        if writeConfFile(self.projConfig) :
            self.log.writeToLog('GRUP-015', [gid])

        # We should be done at this point. Preprocesses should have
        # been run on any of the individual components added above
        return True


    def addComponent (self, cid, cType, source, force = False) :
        '''This will add a component to the object we created 
        above in createComponent(). If the component is already
        listed in the project configuration it will not proceed
        unless force is set to True. Then it will remove the
        component listing, along with its files so a fresh
        copy can be added to the project.'''

        # Current thinking is that a locked component cannot be touched,
        # not even by force (-f) Check here to see if that is the case
        # and quite if it is.
        if self.isLocked(cid) :
            self.log.writeToLog('TEXT-040', [cid])
            dieNow()

        # Make sure the source path is there for this component type
        if force :
            self.addCompTypeSourcePath(cType, source)
        else :
            if not self.hasSourcePath(cType) :
                self.addCompTypeSourcePath(cType, source)
            else :
                if not self.sourceIsSame(cType, source) :
                    current = self.projConfig['CompTypes'][cType.capitalize()]['sourcePath']
                    self.log.writeToLog('COMP-090', [cType,current,source])
                    dieNow()

        def insertComponent () :
            buildConfSection(self.projConfig, 'Components')
            buildConfSection(self.projConfig['Components'], cid)
            self.projConfig['Components'][cid]['name'] = cid
            self.projConfig['Components'][cid]['type'] = cType
            # This will load the component type manager and put
            # a lot of different settings into the proj config
            cfg = self.projConfig['Components'][cid]
            module = import_module('rapuma.component.' + cType)
            ManagerClass = getattr(module, cType.capitalize())
            compobj = ManagerClass(self, cfg)
            self.components[cid] = compobj
            # Save our config settings
            if writeConfFile(self.projConfig) :
                return True

        # Force on add always means we delete the component first
        # before we do anything else
        if force :
            self.removeComponent(cid, force)

        # See if the working text is present, quite if it is not
        if cType == 'usfm' :
            self.createManager(cType, 'text')
            if self.managers[cType + '_Text'].installUsfmWorkingText(cid, force) :
                # Run any working text preprocesses on the new component text
                if self.runPreprocess(cType, cid) :
                    self.log.writeToLog('TEXT-060', [cid])
                # Finish the install by adding to config
                if not testForSetting(self.projConfig, 'Components', cid) :
                    insertComponent()
                    self.lockUnlock(cid, True)
                    if force :
                        self.log.writeToLog('COMP-022', [cid])
                    else :
                        self.log.writeToLog('COMP-020', [cid])
                    return True
                else :
                    self.log.writeToLog('COMP-025', [cid])
                    return False
            else :
                self.log.writeToLog('TEXT-160', [cid])
                return False
        else :
            self.project.log.writeToLog('COMP-005', [self.cType])
            dieNow()


    def removeGroupComponent (self, gid, force = False) :
        '''This will remove a component group from a project 
        If force is set to True, the configuration entries
        as well as the physical files will be removed. Otherwise
        only the group configuration will be removed. The
        group component must be unlocked before this can
        be done.'''

        # Test for group lock
        if isLocked() :
            self.log.writeToLog('GRUP-070', [gid])
            return False

        # Check for force flag
        if force :
            if testForSetting(self.projConfig['Components'][gid], 'list') :
                cidList = self.projConfig['Components'][gid]['list']
            else :
                self.log.writeToLog('GRUP-071', [gid])
                return False
            for cid in cidList :
                self.removeComponent(cid, force)
            del self.projConfig['Components'][gid]
            self.log.writeToLog('GRUP-073', [gid])
        # Just a normal setting delete
        else :
            del self.projConfig['Components'][gid]
            self.log.writeToLog('GRUP-075', [gid])

        # Write and report
        if writeConfFile(self.projConfig) :
            self.log.writeToLog('GRUP-077')
            return True


    def removeComponent (self, cid, force = False) :
        '''This will remove a specific component from a project
        configuration. However, if force is set to True both the
        configuration entry and the physical files will be removed.
        If the component is locked, the function will abort.'''

        # We will not bother if it is not in the config file.
        # Otherwise, delete both the config and physical files
        buildConfSection(self.projConfig, 'Components')
        if isConfSection(self.projConfig['Components'], cid) :
            del self.projConfig['Components'][cid]
            # Sanity check
            if not isConfSection(self.projConfig['Components'], cid) :
                writeConfFile(self.projConfig)
                self.log.writeToLog('COMP-030', [cid])
            # Hopefully all went well with config delete, now on to the files
            compFolder = os.path.join(self.local.projComponentsFolder, cid)
            if os.path.isdir(compFolder) :
                shutil.rmtree(compFolder)
                self.log.writeToLog('COMP-031', [cid])
            else :
                self.log.writeToLog('COMP-032', [cid])

            self.log.writeToLog('COMP-033', [cid])
        else :
            self.log.writeToLog('COMP-035', [cid])


    def addComponentType (self, cType) :
        '''Add (register) a component type to the config if it 
        is not there already.'''

        Ctype = cType.capitalize()
        if not self.isComponentType(cType) :
            # Build the comp type config section
            buildConfSection(self.projConfig, 'CompTypes')
            buildConfSection(self.projConfig['CompTypes'], Ctype)

            # Get persistant values from the config if there are any
            newSectionSettings = getPersistantSettings(self.projConfig['CompTypes'][Ctype], os.path.join(self.local.rapumaConfigFolder, cType + '.xml'))
            if newSectionSettings != self.projConfig['CompTypes'][Ctype] :
                self.projConfig['CompTypes'][Ctype] = newSectionSettings
                # Save the setting rightaway
                writeConfFile(self.projConfig)
            
            # Sanity check
            if self.isComponentType(cType) :
                self.log.writeToLog('COMP-060', [cType])
                return True
            else :
                self.log.writeToLog('COMP-065', [cType])
                return False
        else :
            # Bow out gracefully
            return False


###############################################################################
############################### Locking Functions #############################
###############################################################################

    def isLocked (self, item) :
        '''Test to see if a component is locked. Return True if the item is 
        locked. '''

        try :
            if str2bool(testForSetting(self.projConfig['Components'], item, 'isLocked')) == True :
                return True
            else :
                return False
        except :
            return False


    def lockUnlock (self, cid, lock = True) :
        '''Lock or unlock to enable or disable a cid. If the cid is a group
        then all the components will be locked/unlocked in that group as well.'''

        # Check if the component is locked
        cList = False
        if self.isComponent(cid) :
            # Lists are treated different we will lock or unlock all
            # components in a list
            if testForSetting(self.projConfig['Components'][cid], 'list') :
                cList = True
                for c in self.projConfig['Components'][cid]['list'] :
                    self.projConfig['Components'][c]['isLocked'] = lock
            
            else :
                self.projConfig['Components'][cid]['isLocked'] = lock
                
            # Update the projConfig
            writeConfFile(self.projConfig)
        else :
            # Arggg, this may not be good
            self.log.writeToLog('LOCK-010', [cid])
            return False

        # Report back
        if cList :
            self.log.writeToLog('LOCK-020', [cid,str(lock)])
        else :
            self.log.writeToLog('LOCK-030', [cid,str(lock)])
        return True


###############################################################################
############################# Preprocess Functions ############################
###############################################################################

# Pre and Post processes are virtually the same. The difference is that a
# preprocess will be used to prepare text for rendering. A post process will
# be used for other extra activities like round-tripping the text and creating
# associated outputs for the project. Another difference is that there can only
# be one preprocessing script associated with the project and it is run only
# on importing text. Whereas with post processing there can be a number of
# scripts associated with a project.

# At some point both types of scripts may need to be combined for unified
# management. But for now, they will stay seperate.

    def runPreprocess (self, cType, cid = None) :
        '''Run a preprocess on a single component file or all the files
        of a specified type.'''

        # First test to see that we have a valid cType specified quite if not
        if not testForSetting(self.projConfig, 'CompTypes', cType.capitalize()) :
            self.log.writeToLog('PREP-010', [cType])
            return False

        # Create target file path and name
        if cid :
            target = os.path.join(self.local.projComponentsFolder, cid, cid + '.' + cType)
            if os.path.isfile(target) :
                if self.preprocessComponent(target, cType, cid) :
                    return True
                else :
                    return False
            else :
                self.log.writeToLog('PREP-020', [target])
                return False

        # No CID means we want to do the entire set of components check for lock
        if testForSetting(self.projConfig['CompTypes'][cType.capitalize()], 'isLocked') :
            if str2bool(self.projConfig['CompTypes'][cType.capitalize()]['isLocked']) == True :
                self.log.writeToLog('PREP-030', [cType])
                return False

        # If we made it this far we can assume it is okay to preprocess
        # everything for this component type
        for c in self.projConfig['Components'].keys() :
            if self.projConfig['Components'][c]['type'] == cType :
                target = os.path.join(self.local.projComponentsFolder, c, c + '.' + cType)
                self.preprocessComponent(target, cType, c)

        return True


    def preprocessComponent (self, target, cType, cid) :
        '''Run a preprocess on a single component file, in place.'''

        scriptFileName = ''

        # First check to see if this specific component is locked
        if self.isLocked(cid) :
            self.log.writeToLog('PREP-040', [cid])
            return False

        if testForSetting(self.projConfig['CompTypes'][cType.capitalize()], 'preprocessScript') :
            if self.projConfig['CompTypes'][cType.capitalize()]['preprocessScript'] :
                scriptFileName = self.projConfig['CompTypes'][cType.capitalize()]['preprocessScript']
        else :
            self.log.writeToLog('PREP-055', [cType.capitalize()])
            return False

        if scriptFileName :
            script = os.path.join(self.local.projScriptsFolder, scriptFileName)
            if os.path.isfile(script) :
                # subprocess will fail if permissions are not set on the
                # script we want to run. The correct permission should have
                # been set when we did the installation.
                err = subprocess.call([script, target])
                if err == 0 :
                    self.log.writeToLog('PREP-050', [fName(target)])
                    # Successful completion means no more processing should
                    # be done on this component. As such, we will automatically
                    # lock it so that will not happen by accident.
                    self.lockUnlock(cid, True)
                else :
                    self.log.writeToLog('PREP-060', [fName(target), str(err)])
            else :
                self.log.writeToLog('PREP-070', [fName(script), cid])
                self.log.writeToLog('PREP-075')
        else :
            # No scriptFileName means no preprocess installed quite quietly
            return False


    def recordPreprocessScript (self, cType, script) :
        '''Record a preprocess script in the project.'''

        self.projConfig['CompTypes'][cType.capitalize()]['preprocessScript'] = fName(script)
        writeConfFile(self.projConfig)


    def installPreprocess (self, cType, script = None, force = None) :
        '''Install a preprocess script into the main components processing
        folder for a specified component type. This script will be run on 
        every file of that type that is imported into the project. 
        
        Some projects will have their own specially developed preprocess
        script. Use the "script" var to point to a script or script bundle.
        If "script" is not specified we will copy in a default script that 
        the user can modify. This is currently limited to Python scripts 
        only which do in-place processes on the target files. The script 
        needs to have the same name as the zip file it is bundled in, except 
        the extention is .py instead of the bundle .zip extention.'''

        # Define some internal vars
        if not script :
            script          = os.path.join(self.local.rapumaCompTypeFolder, cType, cType + '-preprocess.zip')
        else :
            script          = resolvePath(script)

        scriptSourceFolder  = os.path.split(script)[0]
        scriptTargetFolder  = self.local.projScriptsFolder
        scriptTarget        = os.path.join(scriptTargetFolder, fName(script).split('.')[0] + '.py')
        try :
            oldScript       = self.projConfig['CompTypes'][cType.capitalize()]['preprocessScript']
        except :
            oldScript       = ''

        # First check for prexsisting script and record, if there is,
        # just go a head and put a new one in and return
        if force :
            if os.path.isfile(scriptTarget) :
                os.remove(scriptTarget)
            if self.projConfig['CompTypes'][cType.capitalize()]['preprocessScript'] :
                self.projConfig['CompTypes'][cType.capitalize()]['preprocessScript'] = ''
                writeConfFile(self.projConfig)
            self.scriptInstall(script, scriptTarget)
            # Test the install
            if not os.path.isfile(scriptTarget) :
                dieNow('Failed to install script!: ' + fName(scriptTarget))
            else :
                self.recordPreprocessScript(cType, scriptTarget)
                # Report and end
                self.log.writeToLog('PREP-115', [fName(scriptTarget)])
                return True

        # If we made it this far, look for pre-existing script
        if oldScript == fName(scriptTarget) :
            self.log.writeToLog('PREP-081')
            return False
        elif oldScript != '' :
            self.log.writeToLog('PREP-080', [oldScript])
            return False
        elif os.path.isfile(scriptTarget) :
            self.log.writeToLog('PREP-082', [fName(scriptTarget)])
            return False

        # At this point we are looking at a fresh install
        # In case this is a new project we may need to install a component
        # type and make a process (components) folder
        if not self.isComponentType(cType) :
            self.addComponentType(cType)

        # Make the target folder if needed
        if not os.path.isdir(scriptTargetFolder) :
            os.makedirs(scriptTargetFolder)

        # No script found, we can proceed
        self.scriptInstall(script, scriptTarget)
        if not os.path.isfile(scriptTarget) :
            dieNow('Failed to install script!: ' + fName(scriptTarget))
        else :
            self.recordPreprocessScript(cType, scriptTarget)
            self.log.writeToLog('PREP-110', [fName(scriptTarget)])
            return True


    def removePreprocess (self, cType) :
        '''Remove (actually disconnect) a preprocess script from a

        component type. This will not actually remove the script. That
        would need to be done manually. Rather, this will remove the
        script name entry from the component type so the process cannot
        be accessed for this specific component type.'''

        # Get old setting
        old = self.projConfig['CompTypes'][cType.capitalize()]['preprocessScript']
        # Reset the field to ''
        if old != '' :
            self.projConfig['CompTypes'][cType.capitalize()]['preprocessScript'] = ''
            writeConfFile(self.projConfig)
            self.log.writeToLog('PREP-130', [old,cType.capitalize()])

        else :
            self.log.writeToLog('PREP-135', [cType.capitalize()])

        return True


    def scriptInstall (self, source, target) :
        '''Install a script. A script can be a collection of items in
        a zip file or a single .py script file.'''

        scriptTargetFolder, fileName = os.path.split(target)
        if isExecutable(source) :
            shutil.copy(source, target)
            makeExecutable(target)
        elif fName(source).split('.')[1].lower() == 'zip' :
            myZip = zipfile.ZipFile(source, 'r')
            for f in myZip.namelist() :
                data = myZip.read(f, source)
                # Pretty sure zip represents directory separator char as "/" regardless of OS
                myPath = os.path.join(scriptTargetFolder, f.split("/")[-1])
                try :
                    myFile = open(myPath, "wb")
                    myFile.write(data)
                    myFile.close()
                except :
                    pass
            myZip.close()
            return True
        else :
            dieNow('Script is an unrecognized type: ' + fName(scriptTarget) + ' Cannot continue with installation.')


###############################################################################
############################ Post Process Functions ###########################
###############################################################################

    def buildPath (self, cid, cType) :
        '''Build a valid path for a component of a specific type.'''
        p = os.path.join(self.local.projComponentsFolder, cid, cid + '.' + cType)
        return os.path.realpath(os.path.expanduser(p))


    def runPostProcess (self, cType, script, cid) :
        '''Run a post process on a component. If the component is a group
        run the script on all the individual components included in the group.
        Unlike runPreprocess(), this will not do a complete cType, only
        specified components or a group of components.'''

#        import pdb; pdb.set_trace()

        Ctype = cType.capitalize()
        target = []
        # First test to see that we have a valid cType specified, quite if not
        if not testForSetting(self.projConfig, 'CompTypes', Ctype) :
            self.log.writeToLog('POST-010', [cType])
            dieNow()

        # If it is a group we will run the script across each cid individually
        # Right now this mechanizm is just basic so if a script is for collection
        # it needs to know how to handle multiple passes and output correctly.
        if not testForSetting(self.projConfig['Components'][cid], 'list') :
            target.append(self.buildPath(cid, cType))
            if not self.postProcessComponent(cType, target, script) :
                self.log.writeToLog('POST-040', [script,target])
                dieNow()
        else :
            for c in self.projConfig['Components'][cid]['list'] :
                target = []
                target.append(self.buildPath(c, cType))
                if not self.postProcessComponent(cType, target, script) :
                    self.log.writeToLog('POST-040', [script,target])
                    dieNow()

        # At this point all must have ended well
        return True


    def postProcessComponent (self, cType, target, script) :
        '''Run a post process on the target. The target could be a single file
        or a group of components.'''

        Ctype = cType.capitalize()
        if script not in self.projConfig['CompTypes'][Ctype]['postprocessScripts'] :
            self.log.writeToLog('POST-055', [script,Ctype])
            dieNow()

        script = os.path.join(self.local.projScriptsFolder, script)
        if os.path.isfile(script) :
            # subprocess will fail if permissions are not set on the
            # script we want to run. The correct permission should have
            # been set when we did the installation.
            commands = []
            commands.append(script)
            for f in target :
                 commands.append(f)
            err = subprocess.call(commands)
            if err == 0 :
                self.log.writeToLog('POST-050', [fName(f)])
                return True
            else :
                self.log.writeToLog('POST-060', [str(err)])
                dieNow()
        else :
            self.log.writeToLog('POST-070', [fName(script)])
            self.log.writeToLog('POST-075')
            dieNow()


    def installPostProcess (self, cType, script, force = None) :
        '''Install a post process script into the main components processing
        folder for a specified component type. This script will be run on 
        every file of that type that is imported into the project. Some
        projects will have their own specially developed post process
        script. Use the "script" var to specify a process (which should be
        bundled in a system compatable way). If "script" is not specified
        we will copy in a default script that the user can modify. This is
        currently limited to Python scripts only which do in-place processes
        on the target files. The script needs to have the same name as the
        zip file it is bundled in, except the extention is .py instead of
        the bundle .zip extention.'''

        # Define some internal vars
        Ctype               = cType.capitalize()
        oldScript           = ''
        scriptName          = os.path.split(script)[1]
        scriptSourceFolder  = os.path.split(script)[0]
        scriptTarget        = os.path.join(self.local.projScriptsFolder, fName(script).split('.')[0] + '.py')
        if scriptName in self.projConfig['CompTypes'][Ctype]['postprocessScripts'] :
            oldScript = scriptName

        # First check for prexsisting script record
        if not force :
            if oldScript :
                self.log.writeToLog('POST-080', [oldScript])
                return False

        # In case this is a new project we may need to install a component
        # type and make a process (components) folder
        if not self.isComponentType(cType) :
            self.addComponentType(cType)

        # Make the target folder if needed
        if not os.path.isdir(self.local.projScriptsFolder) :
            os.makedirs(self.local.projScriptsFolder)

        # First check to see if there already is a script file, return if there is
        if os.path.isfile(scriptTarget) and not force :
            self.log.writeToLog('POST-082', [fName(scriptTarget)])
            return False

        # No script found, we can proceed
        if not os.path.isfile(scriptTarget) :
            self.scriptInstall(script, scriptTarget)
            if not os.path.isfile(scriptTarget) :
                dieNow('Failed to install script!: ' + fName(scriptTarget))
            self.log.writeToLog('POST-110', [fName(scriptTarget)])
        elif force :
            self.scriptInstall(script, scriptTarget)
            if not os.path.isfile(scriptTarget) :
                dieNow('Failed to install script!: ' + fName(scriptTarget))
            self.log.writeToLog('POST-115', [fName(scriptTarget)])

        # Record the script with the cType post process scripts list
        scriptList = self.projConfig['CompTypes'][Ctype]['postprocessScripts']
        if fName(scriptTarget) not in scriptList :
            self.projConfig['CompTypes'][Ctype]['postprocessScripts'] = addToList(scriptList, fName(scriptTarget))
            writeConfFile(self.projConfig)

        return True


    def removePostProcess (self, cType) :
        '''Remove (actually disconnect) a preprocess script from a

        component type. This will not actually remove the script. That
        would need to be done manually. Rather, this will remove the
        script name entry from the component type so the process cannot
        be accessed for this specific component type.'''

        Ctype = cType.capitalize()
        # Get old setting
        old = self.projConfig['CompTypes'][Ctype]['postprocessScripts']
        # Reset the field to ''
        if old != '' :
            self.projConfig['CompTypes'][Ctype]['postprocessScripts'] = ''
            writeConfFile(self.projConfig)
            self.log.writeToLog('POST-130', [old,Ctype])

        else :
            self.log.writeToLog('POST-135', [cType.capitalize()])

        return True


###############################################################################
############################## Exporting Functions ############################
###############################################################################


    def export (self, cType, cid, path = None, script = None, bundle = False, force = False) :
        '''Facilitate the exporting of project text. It is assumed that the
        text is clean and ready to go and if any extraneous publishing info
        has been injected into the text, it will be removed by an appropreate
        post-process that can be applied by this function. No validation
        will be initiated by this function.'''
        
        # FIXME - Todo: add post processing script feature

        # Figure out target path
        if path :
            path = resolvePath(path)
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
        if testForSetting(self.projConfig['Components'][cid], 'list') :
            # Process as list of components

            self.log.writeToLog('XPRT-040')
            for c in self.projConfig['Components'][cid]['list'] :
                cName = formPTName(self.projConfig, c)
                # Test, no name = no success
                if not cName :
                    self.log.writeToLog('XPRT-010')
                    dieNow()

                target = os.path.join(path, cName)
                source = os.path.join(self.local.projComponentsFolder, c, c + '.' + cType)
                # If shutil.copy() spits anything back its bad news
                if shutil.copy(source, target) :
                    self.log.writeToLog('XPRT-020', [fName(target)])
                else :
                    fList.append(target)
        else :
            # Process an individual component
            cName = formPTName(self.projConfig, cid)
            # Test, no name = no success
            if not cName :
                self.log.writeToLog('XPRT-010')
                dieNow()

            target = os.path.join(path, cName)
            source = os.path.join(self.local.projComponentsFolder, cid, cid + '.' + cType)
            # If shutil.copy() spits anything back its bad news
            if shutil.copy(source, target) :
                self.log.writeToLog('XPRT-020', [fName(target)])
            else :
                fList.append(target)

        # Start the main process here
        if bundle :
            archFile = os.path.join(path, cid + '_' + ymd() + '.zip')
            # Hopefully, this is a one time operation but if force is not True,
            # we will expand the file name so nothing is lost.
            if not force :
                if os.path.isfile(archFile) :
                    archFile = os.path.join(path, cid + '_' + fullFileTimeStamp() + '.zip')

            myzip = zipfile.ZipFile(archFile, 'w', zipfile.ZIP_DEFLATED)
            for f in fList :
                # Create a string object from the contents of the file
                strObj = StringIO.StringIO()
                for l in open(f, "rb") :
                    strObj.write(l)
                # Write out string object to zip
                myzip.writestr(fName(f), strObj.getvalue())
                strObj.close()
            # Close out the zip and report
            myzip.close()
            # Clean out the folder
            for f in fList :
                os.remove(f)
            self.log.writeToLog('XPRT-030', [fName(archFile)])
        else :
            self.log.writeToLog('XPRT-030', [path])

        return True


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
            if pid in self.userConfig['Projects'] :
                return True
        except :
            return False


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

        confObj = ConfigObj(confFile)
        outConfObj = confObj
        try :
            # Walk our confObj to get to the section we want
            for s in section.split('/') :
                confObj = confObj[s]
        except :
            self.log.writeToLog('PROJ-040', [section])
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
            self.log.writeToLog('PROJ-030', [config, section, key, str(oldValue), str(newValue)])


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



