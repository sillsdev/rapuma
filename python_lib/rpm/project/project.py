#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111203
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project infrastructure tasks.

# History:
# 20110823 - djd - Started with intial file from RPM project
# 20111203 - djd - Begin changing over to new manager model


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, sys, shutil, imp, subprocess, zipfile
#from configobj import ConfigObj, Section


# Load the local classes
from tools import *
from pt_tools import *
import manager as mngr
import component as cmpt
import user_config as userConfig

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
        self.projectType            = self.projConfig['ProjectInfo']['projectType']
        self.projectIDCode          = self.projConfig['ProjectInfo']['projectIDCode']

        # Do some cleanup like getting rid of the last sessions error log file.
        try :
            if os.path.isfile(self.local.projErrorLogFile) :
                os.remove(self.local.projErrorLogFile)
        except :
            pass

        # Initialize the project type
        m = __import__(self.projectType)
        self.__class__ = getattr(m, self.projectType[0].upper() + self.projectType[1:])

        # Update the existing config file with the project type XML file
        # if needed
        newXmlDefaults = os.path.join(self.local.rpmConfigFolder, self.projectType + '.xml')
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
        return self.managers[fullName]


    def loadManager (self, cType, mType) :
        '''Do basic load on a manager.'''

        fullName = cType + '_' + mType.capitalize()
        cfg = self.projConfig['Managers'][fullName]
        module = __import__(mType)
        manobj = getattr(module, mType.capitalize())(self, cfg, cType)
        self.managers[fullName] = manobj


    def addManager (self, cType, mType) :
        '''Create a manager reference in the project config that components will point to.'''

        fullName = cType + '_' + mType.capitalize()
        # Insert the Manager section if it is not already there
        buildConfSection(self.projConfig, 'Managers')
        if not testForSetting(self.projConfig['Managers'], fullName) :
            buildConfSection(self.projConfig['Managers'], fullName)
            managerDefaults = getXMLSettings(os.path.join(self.local.rpmConfigFolder, mType + '.xml'))
            for k, v, in managerDefaults.iteritems() :
                # Do not overwrite if a value is already there
                if not testForSetting(self.projConfig['Managers'][fullName], k) :
                    self.projConfig['Managers'][fullName][k] = v

            if writeConfFile(self.projConfig) :
                self.log.writeToLog('PROJ-010')
            else :
                self.log.writeToLog('PROJ-011')


###############################################################################
########################## Component Level Functions ##########################
###############################################################################

    def getPdfPathName (self, cid) :
        '''This is a crude way to create a file name and path. It may not be
        the best way.'''

        cidFolder          = os.path.join(self.local.projProcessFolder, cid)
        cidPdf             = os.path.join(cidFolder, cid + '.pdf')

        return cidPdf


    def isComponent (self, cid) :
        '''Simple test to see if a component exsists. Return True if it is.'''

        if testForSetting(self.projConfig, 'Components', cid) :
            return True


    def isComponentType (self, cType) :
        '''Simple test to see if a component type exsists. Return True if it is.'''

        Ctype = cType.capitalize()
        if testForSetting(self.projConfig, 'CompTypes', Ctype) :
            return True


    def renderComponent (self, cid, force = False) :
        '''Render a single component. This will ensure there is a component
        object, then render it.'''

        # Check for cid in config
        if isValidCID(self.projConfig, cid) :
            try :
                self.createComponent(cid).render(force)
                return True
            except :
                return False
        else :
            bad = findBadComp(self.projConfig, cid)
            if bad == cid :
                self.log.writeToLog('COMP-011', [cid])
            else :
                self.log.writeToLog('COMP-012', [bad,cid])
            return False


    def createComponent (self, cid) :
        '''Create a component object that can be acted on.'''

        # If the object already exists just return it
        if cid in self.components : return self.components[cid]

        # Otherwise, create a new one and return it
        if testForSetting(self.projConfig, 'Components', cid) :
            cfg = self.projConfig['Components'][cid]
            cType = cfg['type']
            module = __import__(cType)
            compobj = getattr(module, cType.capitalize())(self, cfg)
            self.components[cid] = compobj
        else :
            self.log.writeToLog('COMP-040', [cid])
            return False

        return compobj


    def addMetaComponent (self, cid, cidList, cType, force = False) :
        '''Add a meta component to the project'''

        # Add/check individual components
        thisList = cidList.split()
        for c in thisList :
            self.addComponent(c, cType, force)

        # Add the info to the components
        buildConfSection(self.projConfig, 'Components')
        buildConfSection(self.projConfig['Components'], cid)
        self.projConfig['Components'][cid]['name'] = cid
        self.projConfig['Components'][cid]['type'] = cType
        self.projConfig['Components'][cid]['list'] = thisList

        # Save our config settings
        if writeConfFile(self.projConfig) :
            self.log.writeToLog('PROJ-015', [cid])

        # We should be done at this point. Post processes should have
        # been run on any of the individual components added above
        return True


    def addComponent (self, cid, cType, force = False) :
        '''This will add a component to the object we created 
        above in createComponent().'''

        # See if the working text is present, quite if it is not
        self.createManager(cType, 'text')
        if not self.managers[cType + '_Text'].installUsfmWorkingText(cid, force) :
            return False

        if not testForSetting(self.projConfig, 'Components', cid) :
            buildConfSection(self.projConfig, 'Components')
            buildConfSection(self.projConfig['Components'], cid)
            self.projConfig['Components'][cid]['name'] = cid
            self.projConfig['Components'][cid]['type'] = cType
            # This will load the component type manager and put
            # a lot of different settings into the proj config
            cfg = self.projConfig['Components'][cid]
            module = __import__(cType)
            compobj = getattr(module, cType.capitalize())(self, cfg)
            self.components[cid] = compobj
            # Save our config settings
            if writeConfFile(self.projConfig) :
                self.log.writeToLog('PROJ-020', [cid])
        else :
            if force :
                self.log.writeToLog('PROJ-025', [cid])
            else :
                self.log.writeToLog('PROJ-026', [cid])

        # Run any working text post processes on the new component text
        if self.runPostProcess(cType, cid) :
            self.log.writeToLog('TEXT-060', [cid])

        return True


    def deleteComponent (self, cid) :
        '''This will delete a specific component from a project which
        includes both the configuration entry and the physical files.'''

        # We will not bother if it is not in the config file.
        # Otherwise, delete both the config and physical files
        if isConfSection(self.projConfig['Components'], cid) :
            del self.projConfig['Components'][cid]
            # Sanity check
            if not isConfSection(self.projConfig['Components'], cid) :
                writeConfFile(self.projConfig)
                self.log.writeToLog('COMP-030')
            # Hopefully all went well with config delete, now on to the files
            compFolder = os.path.join(self.local.projProcessFolder, cid)
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
            newSectionSettings = getPersistantSettings(self.projConfig['CompTypes'][Ctype], os.path.join(self.local.rpmConfigFolder, cType + '.xml'))
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

    def testIsLocked (self, item) :
        '''Test to see if a project, component type, or component are
        locked. Start at the top of the hierarchy and return True if an
        item is found that is locked above the target item or True if
        the item is locked. '''

        if str2bool(testForSetting(self.userConfig['Projects'], item, 'isLocked')) == True :
            return True
        elif str2bool(testForSetting(self.projConfig['CompTypes'], item.capitalize(), 'isLocked')) == True :
            return True
        elif str2bool(testForSetting(self.projConfig['Components'], item, 'isLocked')) == True :
            return True
        else :
            return False


    def lockProject (self) :
        '''Lock an entire project so no components in it can be processed.'''

        if not self.testIsLocked(self.projectIDCode) :
            self.userConfig['Projects'][self.projectIDCode]['isLocked'] = True
            writeConfFile(self.userConfig)
            self.log.writeToLog('LOCK-018', [self.projectIDCode])
            return True


    def unlockProject (self) :
        '''Unlock a project so all components can be processed.'''

        if self.testIsLocked(self.projectIDCode) :
            self.userConfig['Projects'][self.projectIDCode]['isLocked'] = False
            writeConfFile(self.userConfig)
            self.log.writeToLog('LOCK-028', [self.projectIDCode])
            return True


    def lockComponentType (self, cType) :
        '''Lock a component type so those components cannot be processed.
        However, if the project is locked we will not bother.'''

        Ctype = cType.capitalize()
        if not self.testIsLocked(self.projectIDCode) :
            if not self.testIsLocked(Ctype) :
                self.projConfig['CompTypes'][Ctype]['isLocked'] = True
                writeConfFile(self.projConfig)
                self.log.writeToLog('LOCK-038', [cType])
            else :
                self.log.writeToLog('LOCK-038', [cType])
            return True
        else :
            self.log.writeToLog('LOCK-007', [Ctype])
            return False


    def unlockComponentType (self, cType) :
        '''Unlock a component type so components can be processed.'''

        Ctype = cType.capitalize()
        if not self.testIsLocked(self.projectIDCode) :
            if self.testIsLocked(Ctype) :
                self.projConfig['CompTypes'][Ctype]['isLocked'] = False
                writeConfFile(self.projConfig)
                self.log.writeToLog('LOCK-048', [cType])
            else :
                self.log.writeToLog('LOCK-048', [cType])
            return True
        else :
            self.log.writeToLog('LOCK-007', [Ctype])
            return False


    def lockComponent (self, cid) :
        '''Lock a component so it cannot be processed.'''

        if self.isComponent (cid) :
            Ctype = self.projConfig['Components'][cid]['type'].capitalize()
            if not self.testIsLocked(self.projectIDCode) :
                if not self.testIsLocked(Ctype) :
                    self.projConfig['Components'][cid]['isLocked'] = True
                    writeConfFile(self.projConfig)
                    self.log.writeToLog('LOCK-058', [cid])
                    return True
                else :
                    self.log.writeToLog('LOCK-009', [cid, Ctype])
                    return False
            else :
                self.log.writeToLog('LOCK-008', [cid])
                return False
        else :
            self.log.writeToLog('LOCK-055', [cid])
            return False


    def unlockComponent (self, cid) :
        '''Unlock a component so it can be processed.'''

        if self.isComponent (cid) :
            Ctype = self.projConfig['Components'][cid]['type'].capitalize()
            if not self.testIsLocked(self.projectIDCode) :
                if not self.testIsLocked(Ctype) :
                    self.projConfig['Components'][cid]['isLocked'] = False
                    writeConfFile(self.projConfig)
                    self.log.writeToLog('LOCK-068', [cid])
                    return True
                else :
                    self.log.writeToLog('LOCK-009', [cid, Ctype])
                    return False
            else :
                self.log.writeToLog('LOCK-008', [Ctype])
                return False
        else :
            self.log.writeToLog('LOCK-055', [cid])
            return False


###############################################################################
############################ Post Process Functions ###########################
###############################################################################

    def runPostProcess (self, cType, cid = None) :
        '''Run a post process on a single component file or all the files
        of a specified type.'''

        # First test to see that we have a valid cType specified dive out here
        # if it is not
        if not testForSetting(self.projConfig, 'CompTypes', cType.capitalize()) :
            self.log.writeToLog('POST-010', [cType])
            return False

        # Create target file path and name
        if cid :
            target = os.path.join(self.local.projProcessFolder, cid, cid + '.' + cType)
            if os.path.isfile(target) :
                if self.postProcessComponent(target, cType, cid) :
                    return True
            else :
                self.log.writeToLog('POST-020', [target])

        # No CID means we want to do the entire set of components
        if testForSetting(self.projConfig['CompTypes'][cType.capitalize()], 'isLocked') :
            if str2bool(self.projConfig['CompTypes'][cType.capitalize()]['isLocked']) == True :
                self.log.writeToLog('POST-030', [cType])
                return False

        # If we made it this far we can assume it is okay to post process
        # everything for this component type
        for c in self.projConfig['Components'].keys() :
            if self.projConfig['Components'][c]['type'] == cType :
                target = os.path.join(self.local.projProcessFolder, c, c + '.' + cType)
                self.postProcessComponent(target, cType, c)

        return True


    def postProcessComponent (self, target, cType, cid) :
        '''Run a post process on a single component file, in place.'''
        
        
        
# We will make this look for a specific file name for this component and it will
# use that script, not a default script name.

        # First check to see if this specific component is locked
        if testForSetting(self.projConfig['Components'][cid], 'isLocked') :
            self.log.writeToLog('POST-040', [cid])

        ppFolder = 
        script = os.path.join(self.local.projProcessFolder, cType + '-post_process.py')
        if os.path.isfile(script) :
            err = subprocess.call([script, target])
            if err == 0 :
                self.log.writeToLog('POST-050', [fName(target)])
            else :
                self.log.writeToLog('POST-060', [fName(target), str(err)])
        else :
            self.log.writeToLog('POST-070', [fName(script), cid])
            self.log.writeToLog('POST-075')


    def installPostProcess (self, cType, script = None, force = None) :
        '''Install a post process script into the main components processing
        folder for a specified component type. This script will be run on 
        every file of that type that is imported into the project. Some
        projects will have their own specially developed post process
        script. Use the "script" var to specify a process (which should be
        bundled in a system compatable way). If "script" is not specified
        we will copy in a default script that the user can modify. This is
        currently limited to Python scripts only which do in-place processes
        on the target files.'''


# Add to the confFile a post process script name that will be used for processing.
# Get rid of the default scrip name for any script that is specified

        # Define some internal vars
        scriptTargetFolder  = os.path.join(self.local.projProcessFolder, fName(script).split('.')[0])
        scriptTarget        = os.path.join(scriptTargetFolder, fName(script))
        if script :
            defaultTarget   = os.path.join(self.local.projProcessFolder, fName(script).split('.')[0], cType + '-post_process.py')
        else :
            defaultTarget   = os.path.join(self.local.projProcessFolder, cType + '-post_process', cType + '-post_process.py')
        rpmSource           = os.path.join(self.local.rpmCompTypeFolder, cType, cType + '-post_process.py')

        # In case this is a new project we may need to install a component
        # type and make a process (components) folder
        if not self.isComponentType(cType) :
            self.addComponentType(cType)

        if not os.path.isdir(self.local.projProcessFolder) :
            os.mkdir(self.local.projProcessFolder)

        # First check to see if there already is a script, return if there is
        if os.path.isfile(defaultTarget) and not force :
            self.log.writeToLog('POST-080', [fName(defaultTarget)])
            return False

        def extractScript () :
            # Now copy it in. No return from shutil.copy() is good
            if not shutil.copy(script, scriptTarget) :
                self.log.writeToLog('POST-090', [fName(script)])
                # Check if it needs to be unzipped
                if zipfile.is_zipfile(scriptTarget) :
                    myzip = zipfile.ZipFile(scriptTarget, 'r')
                    myzip.extractall(self.local.projProcessFolder)
                    os.remove(scriptTarget)
                    # A valid zip file will always contain a file named cType + '-post_process.py'
                    if os.path.isfile(defaultTarget) :
                        self.log.writeToLog('POST-100', [fName(scriptTarget)])
                    else :
                        self.log.writeToLog('POST-105', [fName(scriptTarget)])
                        return False
                    return True

        # Check to see if we have a custom post process script to use
        # If something goes wrong here we will want to quite
        if script :
            if not os.path.isfile(script) :
                self.log.writeToLog('POST-085', [fName(script)])
                return False

        # No script found, we can proceed
        if not os.path.isdir(scriptTargetFolder) :
            os.mkdir(scriptTargetFolder)
            extractScript()
            self.log.writeToLog('POST-110', [fName(scriptTarget)])
        else :
            if force :
                extractScript()
                self.log.writeToLog('POST-115', [fName(scriptTarget)])
        return True

        # No script was found, just copy in a default starter script
        # Remember, no news from shutil.copy() is good news
        if not shutil.copy(rpmSource, defaultTarget) :
            self.log.writeToLog('POST-120', [fName(defaultTarget), fName(rpmSource)])
            return True


    def removePostProcess (self, cType) :
        '''Remove (actually disconnect) a post process script from a
        component type. This will not actually remove the script. That
        would need to be done manually. Rather, this will remove the
        script name entry from the component type so the process cannot
        be accessed for this specific component.'''

        pass


###############################################################################
################################ Style Functions ##############################
###############################################################################

    def createCustomStyleFile (self, cType) :
        '''Create/copy a custom style file.'''

        self.createManager(cType, 'style')
        self.managers[cType + '_Style'].installCompTypeOverrideStyles()


    def createDefaultStyleFile (self, cType) :
        '''Create/copy the default style file.'''

        self.createManager(cType, 'style')
        self.managers[cType + '_Style'].installCompTypeGlobalStyles()


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
        is a duplicate of the function in the main rpm file.'''

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
        designed to work more as a single call to RPM.'''

        oldValue = ''
        confFile = os.path.join(self.local.projConfFolder, config + '.conf')
        confObj = ConfigObj(confFile)
        outConfObj = confObj
        # Walk our confObj to get to the section we want
        for s in section.split('/') :
            confObj = confObj[s]

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



