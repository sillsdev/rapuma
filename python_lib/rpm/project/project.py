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


###############################################################################
################################## Begin Class ################################
###############################################################################

class Project (object) :

    def __init__(self, userConfig, projHome, userHome, rpmHome) :
        '''Instantiate this class.'''

        self._userConfig            = userConfig
        self._projConfig            = {}
        self.projHome               = projHome
        self.userHome               = userHome
        self.rpmHome                = rpmHome
        self.rpmConfigFolder        = os.path.join(rpmHome, 'config')
        self.projectType            = None
        self.projectIDCode          = None
        self.lockExt                = '.lock'
        self.projConfFileName       = 'project.conf'
        self.configFolderName       = 'config'
        self.projConfFolder         = os.path.join(projHome, self.configFolderName)
        self.projConfFile           = os.path.join(self.projConfFolder, self.projConfFileName)
        self.projLogFile            = os.path.join(projHome, 'rpm.log')
        self.projErrorLogFile       = os.path.join(projHome, 'error.log')
        self.userConfFileName       = 'rpm.conf'
        self.userConfFile           = os.path.join(userHome, self.userConfFileName)
        self.writeOutProjConfFile   = False


###############################################################################
############################ Project Level Functions ##########################
###############################################################################

    def initProject(self) :
        '''This is a place holder method for the real one that gets loaded
        with the project type class.'''
        pass


    def initManager(self) :
        '''This is a place holder method for the real one that gets loaded
        with the project type class.'''
        pass

# FIXME: Start here
    def runBasicManagerInit (self, initInfo) :
        '''Do a basic initialisation according to the settings in an init file.'''

        files = initInfo['Files'].keys()
        for f in files :
            fileName = initInfo['Files'][f]['name']
            path = fileName.split('/')[:-1]

            # Check for path defaults in the projConfFile If they are not there,
            # we will create a path override section and add the default that we
            # get from the init file.  If an override is found then we will use
            # that value.
            folderName = ''
            buildConfSection(self._projConfig, 'FolderNameOverride')
            for f in path :
                if f[0] == '%' :
                    f = f.strip('%')
                    try :
                        fo = self._projConfig['FolderNameOverride'][f]
                        folderName = fo
                    except :
                        self._projConfig['FolderNameOverride'][f] = f
                        writeConfFile(self._projConfig, self.projConfFile)
            
            
            
            print folderName
                    
            # %Fonts%/fonts.xml
            
            # After all the path names are settled we will create the path so that
            # when the file needs to be made it has a place to go.
                    
            thisFolder = self.getAuxFileFolderPath(folder, initInfo)
            thisFile = os.path.join(thisFolder, fileName)

            # Create source file name
            sourceFile = os.path.join(self.project.rpmHome, 'resources', 'lib_auxiliaryTypes', atype, 'lib_files', fileName)
            # Make the file if it is not already there
            if not os.path.isfile(thisFile) :
                if os.path.isfile(sourceFile) :
                    shutil.copy(sourceFile, thisFile)
                else :
                    open(thisFile, 'w').close()
                    if self.project.debugging == 'True' :
                        terminal('Created file: ' + thisFile)


    def startProjInit (self, projConfig) :
        '''Initialize a project.'''

        # Create a fresh merged version of the projConfig
        self._projConfig  = ConfigObj(self.projConfFile)
        self.projectType = self._projConfig['ProjectInfo']['projectType']
        buildConfSection(self._userConfig, 'Projects')
        recordProject(self._userConfig, self._projConfig, self.projHome)

        # Do some cleanup like getting rid of the last sessions error log file.
        try :
            if os.path.isfile(projErrorLogFile) :
                os.remove(projErrorLogFile)
        except :
            pass

        # Initialize the project type
        m = __import__(self.projectType)
        self.__class__ = getattr(m, self.projectType[0].upper() + self.projectType[1:])
        self.initProject()


    def makeProject (self, ptype, pname, pid, pdir='') :
        '''Create a new publishing project.'''

        # Run some basic tests to see if this project can be created
        # Grab the cwd if pdir is empty for the default
        if not pdir or pdir == '.' :
            pdir = os.getcwd()

        # So now that we have a pdir it needs testing
        pdir = os.path.abspath(pdir)
        # Test for parent project.
        if os.path.isfile(self.projConfFile) :
            self.writeToLog('ERR', 'Halt! Live project already defined in this location')
            return False
        elif os.path.isfile(self.projConfFile + self.lockExt) :
            self.writeToLog('ERR', 'Halt! Locked project already defined in target folder')
            return False
        elif os.path.isfile(os.path.join(os.path.dirname(pdir), self.projConfFileName)) :
            self.writeToLog('ERR', 'Halt! Live project already defined in parent folder')
            return False
        elif os.path.isfile(os.path.join(os.path.dirname(pdir), self.projConfFileName + self.lockExt)) :
            self.writeToLog('ERR', 'Halt! Locked project already defined in parent folder')
            return False
        elif not os.path.isdir(os.path.dirname(pdir)) :
            self.writeToLog('ERR', 'Halt! Not a valid (parent) path: ' + pdir)
            return False

        # Test if this project already exists in the user's config file.
        if isRecordedProject(self._userConfig, pid) :
            self.writeToLog('ERR', 'Halt! ID [' + pid + '] already defined for another project')
            return False

        # If we made it to this point we need to check to see if the project
        # folder exists, if it doesn't make it.
        if not os.path.exists(pdir) :
            os.mkdirs(pdir)

        # Create a new version of the project config file
        self.writeOutProjConfFile = True
        self._projConfig = getXMLSettings(os.path.join(self.rpmConfigFolder, ptype + '.xml'))

        # Create intitial project settings
        date = tStamp()
        self._projConfig['ProjectInfo']['projectType']            = ptype
        self._projConfig['ProjectInfo']['projectName']            = pname
        self._projConfig['ProjectInfo']['projectCreateDate']      = date
        self._projConfig['ProjectInfo']['projectIDCode']          = pid
        recordProject(self._userConfig, self._projConfig, pdir)

        # Finally write out the project config file
        if not writeConfFile(self._projConfig, self.projConfFile) :
            terminal('\nERROR: Could not write to: project config file')
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
                # Disable the project
                if os.path.isfile(self.projConfFile) :
                    os.rename(self.projConfFile, self.projConfFile + self.lockExt)

                # Remove references from user rpm.conf write out immediately
                del self._userConfig['Projects'][pid]
                if not writeConfFile(self._userConfig, self.userConfFile) :
                    terminal('\nERROR: Could not write to: user config file')

                # Report the process is done
                self.writeToLog('MSG', 'Project [' + pid + '] removed from system configuration.')
                return True

        except :
            terminal('Project ID [' + pid + '] not found in system configuration.')
            return False


    def restoreProject (self, pdir='') :
        '''Restore a project in the current folder'''

        pass


###############################################################################
########################## Component Level Functions ##########################
###############################################################################


    def addNewComponent (self, cid, ctype) :
        '''Add component to the current project by adding them to the component
        binding list and inserting component info into the project conf file.'''

        pass


    def removeComponent (self, comp) :
        '''Remove a component from the current project by removing them from the
        component binding list and from their type information section.'''

        pass


###############################################################################
############################ System Level Functions ###########################
###############################################################################


    def changeSystemSetting (self, key, value) :
        '''Change global default setting (key, value) in the System section of
        the RPM user settings file.  This will write out changes
        immediately.'''

        pass


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


