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

import codecs, os, sys, shutil, imp, subprocess
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


    def renderComponent (self, cid, force = False) :
        '''Render a single component. This will ensure there is a component
        object, then render it.'''


        import pdb; pdb.set_trace()

        # Check for cid in config
        if isValidCID(self.projConfig, cid) :
            self.createComponent(cid).render(force)
#            try :
#                self.createComponent(cid).render(force)
#                return True
#            except :
#                return False
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



# FIXME: we need to stop this next process (adding to the conf) if the 
# comp type is locked or maybe even if the source doesn't exsist. How do we do that?
# We also should add folders and working text at this point so it is ready to render later.

    def addComponent (self, cid, cType, force = False) :
        '''This will add a component to the object we created 
        above in createComponent().'''

        # Inject the component type into the config file.
        self.addComponentType(cType)

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
        if self.postProcessComponent(cid) :
            self.log.writeToLog('TEXT-060', [cid])

        return True


    def lockComponent (self, cid, ctype = None) :
        '''Create a component lock so that the working text cannot be updated
        by newer source files. If the component type code is included, install
        a lock file in the process folder that will prevent all components of
        the same type from being updated.'''

        compLockFile = os.path.join(self.local.projProcessFolder, cid, cid + self.local.lockExt)
        if ctype :
            typeLockFile = os.path.join(self.local.projProcessFolder, ctype + self.local.lockExt)

        def writeLock (fn) :
            writeout = codecs.open(fn, "w", "utf-8")
            writeout.write(fn)
            writeout.close

        if cid and ctype :
            writeLock(typeLockFile)
            self.log.writeToLog('COMP-021', [ctype])
        else :
            writeLock(compLockFile)
            self.log.writeToLog('COMP-020', [cid])


    def unlockComponent (self, cid, ctype = None) :
        '''Unlock (delete the lock file) of a specific component or a set of
        components of the same type.'''

        compLockFile = os.path.join(self.local.projProcessFolder, cid, cid + self.local.lockExt)
        if ctype :
            typeLockFile = os.path.join(self.local.projProcessFolder, ctype + self.local.lockExt)

        if cid and ctype :
            try :
                os.remove(typeLockFile)
                self.log.writeToLog('COMP-026', [ctype])
            except :
                self.log.writeToLog('COMP-028', [ctype])
        else :
            try :
                os.remove(compLockFile)
                self.log.writeToLog('COMP-025', [cid])
            except :
                self.log.writeToLog('COMP-027', [cid])


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
        # Build the comp type config section
        if not testForSetting(self.projConfig, 'CompTypes', Ctype) :
            buildConfSection(self.projConfig, 'CompTypes')
            buildConfSection(self.projConfig['CompTypes'], Ctype)

        # Get persistant values from the config if there are any
        newSectionSettings = getPersistantSettings(self.projConfig['CompTypes'][Ctype], os.path.join(self.local.rpmConfigFolder, 'usfm.xml'))
        if newSectionSettings != self.projConfig['CompTypes'][Ctype] :
            self.projConfig['CompTypes'][Ctype] = newSectionSettings
            # Save the setting rightaway
            writeConfFile(self.projConfig)


    def postProcessComponent (self, cid) :
        '''Run a post process on the working text of a single component file.'''

        # Create target file path and name
        cType = self.projConfig['Components'][cid]['type']
        target = os.path.join(self.local.projProcessFolder, cid, cid + '.' + cType)
        if os.path.isfile(target) :
            self.runPostProcess(target, cType, cid)
        else :
            self.log.writeToLog('COMP-060', [target])


    def runPostProcess (self, target, cType, cid) :
        '''Run a post process on a file, in place.'''

        script = os.path.join(self.local.projProcessFolder, cType + '-post_process.py')
        if os.path.isfile(script) :
            err = subprocess.call([script, target])
            if err == 0 :
                self.log.writeToLog('COMP-065', [fName(target)])
            else :
                self.log.writeToLog('COMP-066', [fName(target), str(err)])
        else :
            self.log.writeToLog('COMP-067', [fName(script), cid])


    def postProcessType (self, cType) :
        '''Run the post process on every component of a specified type.'''

        good = 0
        valid = 0
        target = ''
        def runIt (target, cType, c) :
            if os.path.isfile(target) :
                self.runPostProcess(target, cType, c)
                return True
            else :
                self.log.writeToLog('COMP-060', [target])

        for c in self.projConfig['Components'].keys() :
            # We only want a specific type of component and we want to weed 
            # out any meta components
            if self.projConfig['Components'][c]['type'] == cType :
                target = os.path.join(self.local.projProcessFolder, c, c + '.' + cType)
                try :
                    # If the component has a list, then it is a meta component
                    # we will want to skip those
                    l = self.projConfig['Components'][c]['list']
                    pass
                except :
                    # An exception is good in this case
                    valid +=1
                    if runIt(target, cType, c) :
                        good +=1

        # Simple test to see if all the componets were processed
        if good == valid :
            return True
        else :
            return False


    def installPostProcess (self, pid, cType = None) :
        '''Install the post_process.py script into the project processing
        folder for a specified component type. This script will be run on 
        every file of that type that is imported into the project. Some
        projects will have their own specially developed post process
        script. We will look in the parent folder first to see if any
        exsists and grab those first. If one does not exsist we can copy
        a default script.'''

        # In case this is a new project we may need to make a process (components) folder
        if not os.path.isdir(self.local.projProcessFolder) :
            os.mkdir(self.local.projProcessFolder)

        # Set the default paths/names
        editor = ''
        source = ''
        target = ''
        # If there is no cType or no CompTypes yet then we'll do the best we can
        # to set the default paths
        if cType :
            source = os.path.join(self.local.rpmCompTypeFolder, cType, cType + '-post_process.py')
            target = os.path.join(self.local.projProcessFolder, cType + '-post_process.py')
        else :
            # This is somewhat of a guess, we'll get the first one we find
            # but this might need to be changed at some point.
            compTypes = self.userConfig['System']['recognizedComponentTypes']
            for ct in compTypes :
                fn = ct + '-post_process.py'
                source = os.path.join(self.local.rpmCompTypeFolder, ct, fn)
                target = os.path.join(self.local.projProcessFolder, ct + '-post_process.py')

        # Look a little harder to see if there is a source closer by
        home = self.userConfig['Projects'][pid]['projectPath']
        parent = os.path.dirname(home)
        gather = os.path.join(parent, 'gather')
        if os.path.isdir(gather) :
            parent = gather

        if os.path.isfile(os.path.join(parent, self.projectIDCode + '.py')) :
            source = os.path.join(parent, self.projectIDCode + '.py')

        # If nothing else is there, copy in the new script
        if not os.path.isfile(target) :
            # No return from shutil.copy() is good
            if not shutil.copy(source, target) :
                self.log.writeToLog('COMP-070', [fName(target), fName(source)])
            return True
        else :
            self.log.writeToLog('COMP-072', [fName(target)])
            return False


###############################################################################
################################ Font Functions ###############################
###############################################################################

    def addComponentFont (self, font, cType) :
        '''Add a font to a component.'''

        self.addComponentType(cType)
        # Call on the font manager to install the font we want for this component
        self.createManager(cType, 'font')
        self.managers[cType + '_Font'].recordFont(font, cType.capitalize())
        self.managers[cType + '_Font'].installFont(cType.capitalize())


    def setPrimaryFont (self, font, cType) :
        '''Set the primary font for a component.'''

        module = __import__(cType)
        # FIXME: In this next call we use a blank dict to load the
        # comp config section. As long as we call a manager that
        # doesn't need it, we are okay. Otherwise, this needs fixing.
        compobj = getattr(module, cType.capitalize())(self, {})
        self.managers[cType + '_Font'].setPrimaryFont(font, cType.capitalize())


    def removeComponentFont (self, font, cType) :
        '''Remove a font from a component. Remove from the system if
        it is not used in any other component.'''

        terminal('Forget it dude, this is not implemented yet.')


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



