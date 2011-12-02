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

import codecs, os, sys, fileinput, shutil, imp
#from configobj import ConfigObj, Section


# Load the local classes
from tools import *
import component
import auxiliary


###############################################################################
################################## Begin Class ################################
###############################################################################

class Project (object) :

    def __init__(self, projConfig, userConfig, projHome, userHome, rpmHome) :

        self.projHome           = projHome
        self.userHome           = userHome
        self.rpmHome            = rpmHome

        # Load project config files and grouped config information
        self._projConfig        = projConfig
        self._userConfig        = userConfig
        self._components        = {}
        self._auxiliaries       = {}

        # Set all the initial paths and locations
        # System level paths
        self.rpmHome            = rpmHome
        self.userHome           = userHome
        self.projHome           = projHome
        self.rpmAuxTypes        = os.path.join(rpmHome, 'resources', 'lib_auxiliaryTypes')
        self.rpmCompTypes       = os.path.join(rpmHome, 'resources', 'lib_compTypes')
        self.rpmProjTypes       = os.path.join(rpmHome, 'resources', 'lib_projTypes')
        self.rpmShare           = os.path.join(rpmHome, 'resources', 'lib_share')
        self.rpmFonts           = os.path.join(rpmHome, 'resources', 'lib_share', 'Fonts')
        # User/Global level paths
        self.userScripts        = os.path.join(userHome, 'resources', 'lib_scripts')
        self.userFonts          = os.path.join(userHome, 'resources', 'lib_share', 'Fonts')
        self.userIllustrations  = os.path.join(userHome, 'resources', 'lib_illustratons')
        self.userAdmin          = os.path.join(userHome, 'resources', 'lib_admin')
        self.userCompTypes      = os.path.join(userHome, 'resources', 'lib_compTypes')
        self.userProjTypes      = os.path.join(userHome, 'resources', 'lib_projTypes')

        # Set all the system settings
        if self._userConfig :
            self.projConfFile       = os.path.join(self.projHome, '.project.conf')
            self.userConfFile       = os.path.join(self.userHome, 'rpm.conf')
            for k in (  'userName',                 'debugging',
                        'langID',                   'projLogLineLimit',
                        'initDate') :

                setattr(self, k, self._userConfig['System'][k] if self._userConfig else None)

            for k in (  'componentList',            'defaultAuxiliaries',
                        'projectType',              'optionalAuxiliaries',
                        'projectName',              'projectIDCode',
                        'validCompTypes',           'auxiliaryList',
                        'projectCreateDate',        'projAuxiliaries',
                        'projectComponentBindingOrder') :

                 setattr(self, k, self._projConfig['ProjectInfo'][k] if self._projConfig else None)

# FIXME: Start here, make getProjInitSettings() in tools

#            # Get project level config information
#            self._initConfig = getProjInitSettings(self.userHome, self.rpmHome, self.projectType)
#            # Set values for this method
#            setattr(self, 'processFolderName', self._initConfig['Folders']['Process']['name'])

            # Log file names
            for k in (  'projLogFile',                  'projErrorLogFile') :
                setattr(self, k, self._userConfig['Files'][k]['name'] if self._projConfig else None)

            # Now do any necessary initializing for this project


            self.isProjectInitalized    = True


        # Set some flags
        self.writeOutProjConfFile   = False
        self.writeOutUserConfFile   = False
        self.isProjectInitalized    = False

        # If this project is still new these may not exist yet
#        try :

#            # Walk the ComponentTypes section and try to load commands if there are any
#            if isConfSection(self._projConfig, 'ComponentTypes') :
#                for ctype in self._projConfig['ComponentTypes'].keys() :
#                    sys.path.insert(0, os.path.join(self.rpmCompTypes, ctype, 'lib_python'))
#                    __import__(ctype)
#                    __import__(ctype + '_command')
#             
#            # Walk the AuxiliaryTypes section and try to load commands if there are any
#            if isConfSection(self._projConfig, 'AuxiliaryTypes') :
#                for atype in self._projConfig['AuxiliaryTypes'].keys() :
#                    sys.path.insert(0, os.path.join(self.rpmAuxTypes, atype, 'lib_python'))
#                    __import__(atype)
#                    __import__(atype + '_command')

#            # Clean up the path, we don't need this stuck there
#            del sys.path[0]

#        except StandardError as e:
#            self.writeToLog('ERR', 'Failed to load component! due to error: {0}\n'.format(e))


###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def makeProject (self, ptype, pname, pid, pdir='') :
        '''Create a new publishing project.'''

        # Run some basic tests to see if this project can be created
        # Grab the cwd if pdir is empty for the default
        if not pdir or pdir == '.' :
            pdir = os.getcwd()

        # So now that we have a pdir it needs testing
        pdir = os.path.abspath(pdir)
        # Test for parent project.
        if os.path.isfile(os.path.join(pdir, '.project.conf')) :
            self.writeToLog('ERR', 'Halt! Live project already defined in this location')
            return False
        elif os.path.isfile(os.path.join(pdir, '.project.conf' + self.lockExt)) :
            self.writeToLog('ERR', 'Halt! Locked project already defined in target folder')
            return False
        elif os.path.isfile(os.path.join(os.path.dirname(pdir), '.project.conf')) :
            self.writeToLog('ERR', 'Halt! Live project already defined in parent folder')
            return False
        elif os.path.isfile(os.path.join(os.path.dirname(pdir), '.project.conf' + self.lockExt)) :
            self.writeToLog('ERR', 'Halt! Locked project already defined in parent folder')
            return False
        elif not os.path.isdir(os.path.dirname(pdir)) :
            self.writeToLog('ERR', 'Halt! Not a valid (parent) path: ' + pdir)
            return False

        # Test if this project already exists in the user's config file.
        if isRecordedProject(self.userConfFile, pid) :
            self.writeToLog('ERR', 'Halt! ID [' + pid + '] already defined for another project')
            return False

        # If we made it to this point we need to check to see if the project
        # folder exists, if it doesn't make.  We can create only one level deep
        # though.'
        if not os.path.isdir(pdir) :
            os.mkdir(pdir)

        # Create a new version of the project config file
        newProjConfig = getProjSettings(self.userHome, self.rpmHome, ptype)
        self.writeOutProjConfFile = True
        self._projConfig = newProjConfig
        # We will do the project init when the first component is processed

        # Create intitial project settings
        date = tStamp()
        self._projConfig['ProjectInfo']['projectType']            = ptype
        self._projConfig['ProjectInfo']['projectName']            = pname
        self._projConfig['ProjectInfo']['projectCreateDate']      = date
        self._projConfig['ProjectInfo']['projectIDCode']          = pid
        recordProject(self.userConfFile, self._projConfig, pdir)

        # Set some vars that will be needed
        self.projLogFile        = self._userConfig['Files']['projLogFile']['name']
        self.projErrorLogFile   = self._userConfig['Files']['projErrorLogFile']['name']

        # Finally write out the project config file
        if not writeConfFile(self._projConfig, '.project.conf', pdir) :
            terminal('\nERROR: Could not write to: project config file')
#        writeProjConfFile(self._projConfig, pdir)
        self.writeOutProjConfFile = False
        self.writeToLog('MSG', 'Created [' + pid + '] project at: ' + date, 'project.makeProject()')

        return True


    def removeProject (self, pid='') :
        '''Remove the project from the RPM system.  This will not remove the
        project data but will 'disable' the project.'''

        # If no pid was given we'll try to get the current on if there is one
        if pid == '' :
            if self.projectIDCode :
                pid = self.projectIDCode
            else :
                terminal('Project ID code not given or found. Remove project failed.')
                return False

        # If we made it this far we should be able to remove it
        try :
            # Check to see if the project does exist in the user config
            if self._userConfig['Projects'][pid] :
                projPath = self._userConfig['Projects'][pid]['projectPath']
                projConfFile = os.path.join(projPath, '.project.conf')
                # Disable the project
                if os.path.isfile(projConfFile) :
                    os.rename(projConfFile, projConfFile + self.lockExt)

                # Remove references from user rpm.conf write out immediately
                del self._userConfig['Projects'][pid]
                if not writeConfFile(self._userConfig, 'rpm.conf', self.userHome) :
                    terminal('\nERROR: Could not write to: user config file')

                # Report the process is done
                self.writeToLog('MSG', 'Project [' + pid + '] removed from system configuration.')
                return True

        except :
            terminal('Project ID [' + pid + '] not found in system configuration.')
            return False


    def restoreProject (self, pdir='') :
        '''Restore a project in the current folder'''

        # Normalize the path to the project we want to restore
        if pdir == '' or pdir == '.' :
            pdir = os.getcwd()
        else :
            pdir = os.path.abspath(pdir)

        # Restore the project
        projConfFile = os.path.join(pdir, '.project.conf')
        if os.path.isfile(projConfFile + self.lockExt) :
            os.rename(projConfFile + self.lockExt, projConfFile)
            
            # We could put a lot of code here to get this project recorded and
            # check the integrity, or, we could just let that happen the next
            # time RPM is run on the project.  For now we'll do that.
            terminal('Restored project at: ' + pdir)
            return True

        else :
            terminal('Could not find project at: ' + pdir)
            return False


###############################################################################
########################## Component Level Functions ##########################
###############################################################################


    def addNewComponent (self, cid, ctype) :
        '''Add component to the current project by adding them to the component
        binding list and inserting component info into the project conf file.

        All supplied arguments need to be valid.  This function will fail if the
        type, source or ID are not valid or if the component already exsists in
        the binding order list.'''

        # Test for this component and bail if it is there
        try :
            at = self._projConfig['Components'][cid]['compType']
            self.writeToLog('ERR', 'ID: [' + cid + '] cannot be added again.', 'project.addNewComponent()')
            return False

        except :
            # Add main Auxiliary sections if necessary
            buildConfSection(self._projConfig, 'ComponentTypes')
            buildConfSection(self._projConfig, 'Components')

            # First we add the type if it is not already in the project
            if ctype in self.validCompTypes :
                if not ctype in self._projConfig['ComponentTypes'] :
                    self.addNewComponentType(ctype)
            else :
                self.writeToLog('ERR', 'ID: [' + ctype + '] not valid component ID to use in [' + self.projectType + '] project type', 'project.addNewAuxiliary()')

            if not cid in self._projConfig['ComponentTypes'][ctype]['validIdCodes'] :
                self.writeToLog('ERR', 'ID: [' + cid + '] not valid ID for [' + ctype + '] component type', 'project.addNewComponents()')
                return False

            # Add to the installed components list for this type
            compList = []
            compList = self._projConfig['ComponentTypes'][ctype]['installedComponents']
            compList.append(cid)
            self._projConfig['ComponentTypes'][ctype]['installedComponents'] = compList

            # Read in the main settings file for this comp
            compSettings = getCompSettings(self.userHome, self.rpmHome, ctype)

            # Build a section for this aux and merge in the default settings
            buildConfSection(self._projConfig['Components'], cid)
            self._projConfig['Components'][cid].merge(compSettings['ComponentTypes']['ComponentInformation'])

            # Add component code to components list
            listOrder = []
            listOrder = self._projConfig['ProjectInfo']['componentList']
            listOrder.append(cid)
            self._projConfig['ProjectInfo']['componentList'] = listOrder

            # Add component code to binding order list
            if self._projConfig['ComponentTypes'][ctype]['inBindingList'] == 'True' :
                listOrder = []
                listOrder = self._projConfig['ProjectInfo']['projectComponentBindingOrder']
                listOrder.append(cid)
                self._projConfig['ProjectInfo']['projectComponentBindingOrder'] = listOrder

            self.writeOutProjConfFile = True
            self.writeToLog('MSG', 'Component added: ' + str(cid), 'project.addNewComponents()')

            return True


    def removeComponent (self, comp) :
        '''Remove a component from the current project by removing them from the

        component binding list and from their type information section.'''

        # Find out what kind of component type this is
        ctype = self._projConfig['Components'][comp]['compType']

        # Remove from components list first
        orderList = []
        orderList = self._projConfig['ProjectInfo']['componentList']
        if comp in orderList :
            orderList.remove(comp)
            self._projConfig['ProjectInfo']['componentList'] = orderList
            self.writeOutProjConfFile = True
        else :
            self.writeToLog('WRN', 'Component [' + comp + '] not found in component list', 'project.removeComponents()')

        # Remove from Binding order list
        orderList = []
        orderList = self._projConfig['ProjectInfo']['projectComponentBindingOrder']
        if comp in orderList :
            orderList.remove(comp)
            self._projConfig['ProjectInfo']['projectComponentBindingOrder'] = orderList
            self.writeOutProjConfFile = True
        else :
            self.writeToLog('WRN', 'Component [' + comp + '] not found in binding order list', 'project.removeComponents()')
        
        # Remove from the components installed list
        compList = self._projConfig['ComponentTypes'][ctype]['installedComponents']
        if comp in compList :
            compList.remove(comp)
            self._projConfig['ComponentTypes'][ctype]['installedComponents'] = compList
            self.writeOutProjConfFile = True
        
        # Remove the component's section from components
        if comp in self._projConfig['Components'] :
            del self._projConfig['Components'][comp]
            self.writeOutProjConfFile = True
            
        # Remove references in the ComponentTypes section if this is the last
        # component of its kind to be removed. 
        if len(self._projConfig['ComponentTypes'][ctype]['installedComponents']) == 0 :
            self.removeComponentType(ctype)

        # I guess if at least one of the above succeded we removed it
        if self.writeOutProjConfFile :
            self.writeToLog('MSG', 'Removed component: [' + comp + '] from project.', 'project.removeComponents()')


#    def addNewComponentType (self, ctype) :
#        '''This will add all the component type information to a project.'''

#        # Test to see if the section is there, do not add if it is
#        buildConfSection(self._projConfig['ComponentTypes'], ctype)
#        thisCompType = getCompSettings(self.userHome, self.rpmHome, ctype)
#        self._projConfig['ComponentTypes'][ctype].merge(thisCompType['ComponentTypes']['ComponentTypeInformation'])
#        self.writeOutProjConfFile = True
#        self.writeToLog('MSG', 'Component type: [' + ctype + '] added to project.', 'project.addNewComponentType()')
#        return True


#    def removeComponentType (self, ctype) :
#        '''Remove a component type to the current project.  Before doing so, it
#        must varify that the requested component type is valid.'''

#        if len(self._projConfig['ComponentTypes'][ctype]['installedComponents']) == 0 :
#            # Remove references in the ComponentType section
#            del self._projConfig['ComponentTypes'][ctype]
#            self.writeOutProjConfFile = True
#            # FIXME: More should be done at this point to remove files, etc of the comp type.
#            self.writeToLog('MSG', 'Component type: [' + ctype + '] removed from project.', 'project.removeComponentType()')
#        else :
#            self.writeToLog('WRN', 'Component type: [' + ctype + '] does not exsits.', 'project.removeComponentType()')


#    def getUninitializedComponent (self, cid) :
#        '''Create an object for a specified component.'''

#        if cid and cid not in self._projConfig['Components'] :
#            self.writeToLog('ERR', 'Component: [' + cid + '] not found.', 'project.getComponent()')            
#            return None
#        
#        if not cid in self._components :
#            config = self._projConfig['Components'][cid]
#            ctype = config['compType']
#            if not ctype in component.componentTypes :
#                self._components[cid] = component.component(self, config, None, cid)
#            else :
#                self._components[cid] = component.componentTypes[ctype](self, config, self._projConfig['ComponentTypes'][ctype], cid)
#        return self._components[cid]


#    def getComponent (self, cid) :
#        '''A function for initializing (making directories, etc.) a component which is called by the
#        component or project when a process is run.'''

#        comp = self.getUninitializedComponent(cid)
#        # Init all aux comps before the comp init
#        self.initCompAuxiliaries(comp)
#        # Now init the comp
#        comp.initComponent()
#        return comp




###############################################################################
############################ System Level Functions ###########################
###############################################################################


    def changeSystemSetting (self, key, value) :
        '''Change global default setting (key, value) in the System section of
        the RPM user settings file.  This will write out changes
        immediately.'''

        if not self._userConfig['System'][key] == value :
            self._userConfig['System'][key] = value
            reportSysConfUpdate(self)
            terminal('Changed ' + key + ' to: ' + value)
            setattr(self, key, self._userConfig['System'][key] if self._userConfig else None)
        else :
            terminal(key + ' already set to ' + value)


###############################################################################
################################# Logging routines ############################
###############################################################################

# These have to do with keeping a running project log file.  Everything done is
# recorded in the log file and that file is trimmed to a length that is
# specified in the system settings.  Everything is channeled to the log file but
# depending on what has happened, they are classed in three levels:
#   1) Common event going to log and terminal
#   2) Warning event going to log and terminal if debugging is turned on
#   3) Error event going to the log and terminal

    def writeToLog (self, code, msg, mod = None) :
        '''Send an event to the log file. and the terminal if specified.
        Everything gets written to the log.  Whether a message gets written to
        the terminal or not depends on what type (code) it is.  There are four
        codes:
            MSG = General messages go to both the terminal and log file
            LOG = Messages that go only to the log file
            WRN = Warnings that go to the terminal and log file
            ERR = Errors that go to both the terminal and log file.'''

        # Build the mod line
        if mod :
            mod = mod + ': '
        else :
            mod = ''

        # Write out everything but LOG messages to the terminal
        if code != 'LOG' :
            terminal('\n' + code + ' - ' + msg)

        # Test to see if this is a live project by seeing if the project conf is
        # there.  If it is, we can write out log files.  Otherwise, why bother?
        if os.path.isfile(self.projConfFile) :

            # When are we doing this?
            ts = tStamp()
            
            # Build the event line
            if code == 'ERR' :
                eventLine = '\"' + ts + '\", \"' + code + '\", \"' + mod + msg + '\"'
            else :
                eventLine = '\"' + ts + '\", \"' + code + '\", \"' + msg + '\"'

            # Do we need a log file made?
            try :
                if not os.path.isfile(self.projLogFile) or os.path.getsize(self.projLogFile) == 0 :
                    writeObject = codecs.open(self.projLogFile, "w", encoding='utf_8')
                    writeObject.write('RPM event log file created: ' + ts + '\n')
                    writeObject.close()

                # Now log the event to the top of the log file using preAppend().
                self.preAppend(eventLine, self.projLogFile)

                # Write errors and warnings to the error log file
                if code == 'WRN' and self.debugging == 'True':
                    self.writeToErrorLog(eventLine)

                if code == 'ERR' :
                    self.writeToErrorLog(eventLine)

            except :
                terminal("Failed to write: " + msg)

        return


    def writeToErrorLog (self, eventLine) :
        '''In a perfect world there would be no errors, but alas there are and
        we need to put them in a special file that can be accessed after the
        process is run.  The error file from the previous session is deleted at
        the begining of each new run.'''

        try :
            # Because we want to read errors from top to bottom, we don't pre append
            # them to the error log file.
            if not os.path.isfile(self.projErrorLogFile) :
                writeObject = codecs.open(self.projErrorLogFile, "w", encoding='utf_8')
            else :
                writeObject = codecs.open(self.projErrorLogFile, "a", encoding='utf_8')

            # Write and close
            writeObject.write(eventLine + '\n')
            writeObject.close()
        except :
            terminal(eventLine)

        return


    def trimLog (self, projLogLineLimit = 1000) :
        '''Trim the system log file.  This will take an existing log file and
        trim it to the amount specified in the system file.'''

        # Of course this isn't needed if there isn't even a log file
        if os.path.isfile(self.projLogFile) :

            # Change this to an int()
            projLogLineLimit = int(projLogLineLimit)
            
            # Read in the existing log file
            readObject = codecs.open(self.projLogFile, "r", encoding='utf_8')
            lines = readObject.readlines()
            readObject.close()

            # Process only if we have enough lines
            if len(lines) > projLogLineLimit :
                writeObject = codecs.open(self.projLogFile, "w", encoding='utf_8')
                lineCount = 0
                for line in lines :
                    if projLogLineLimit > lineCount :
                        writeObject.write(line)
                        lineCount +=1

                writeObject.close()

        return


    def preAppend (self, line, file_name) :
        '''Got the following code out of a Python forum.  This will pre-append a
        line to the begining of a file.'''

        fobj = fileinput.FileInput(file_name, inplace=1)
        first_line = fobj.readline()
        sys.stdout.write("%s\n%s" % (line, first_line))
        for line in fobj:
            sys.stdout.write("%s" % line)

        fobj.close()


