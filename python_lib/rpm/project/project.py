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
import manager as mngr
import component as cmpt
import command as projCmd
import user_config as userConfig

###############################################################################
################################## Begin Class ################################
###############################################################################

class Project (object) :

    def __init__(self, userConfig, projHome, userHome, rpmHome) :
        '''Instantiate this class.'''

        self._userConfig            = userConfig
        self._projConfig            = ConfigObj()
        self._layoutConfig          = ConfigObj()
        self.confFileList           = ['userConfig', 'projConfig', 'layoutConfig']
#        self.confFileList           = ['userConfig', 'projConfig']
        self.commands               = {}
        self.components             = {}
        self.componentType          = {}
#        self.projHome               = projHome
#        self.userHome               = userHome
#        self.rpmHome                = rpmHome
#        self.userConfFileName       = 'rpm.conf'
#        self.rpmConfigFolder        = os.path.join(self.rpmHome, 'config')
#        self.rpmResourceFolder      = os.path.join(self.rpmHome, 'resources')
#        self.rpmLibShareFolder      = os.path.join(self.rpmResourceFolder, 'lib_share')
#        self.rpmFontsFolder         = os.path.join(self.rpmLibShareFolder, 'fonts')
#        self.rpmMacrosFolder        = os.path.join(self.rpmLibShareFolder, 'macros')
#        self.rpmIllustrationsFolder = os.path.join(self.rpmLibShareFolder, 'illustrations')
#        self.rpmXmlConfigFile       = os.path.join(self.rpmConfigFolder, 'rpm.xml')
#        self.rpmLayoutDefaultFile   = os.path.join(self.rpmConfigFolder, 'layout_default.xml')
        self.projectType            = None
        self.projectIDCode          = None
        self.projConfFileName       = 'project.conf'
        self.configFolderName       = 'Config'
#        self.projConfFolder         = os.path.join(self.projHome, self.configFolderName)
#        self.processFolder          = os.path.join(self.projHome, 'Process')
#        self.macrosFolder           = os.path.join(self.processFolder, 'Macros')
#        self.fontsFolder            = os.path.join(self.projHome, 'Fonts')
#        self.textFolder             = os.path.join(self.projHome, 'WorkingText')
#        self.hyphenationFolder      = os.path.join(self.projHome, 'Hyphenation')
        self.userConfFile           = os.path.join(self.userHome, self.userConfFileName)
        self.layoutConfFile         = os.path.join(self.projConfFolder, 'layout.conf')
        self.projConfFile           = os.path.join(self.projConfFolder, self.projConfFileName)
        self.projLogFile            = os.path.join(self.projHome, 'rpm.log')
        self.projErrorLogFile       = os.path.join(self.projHome, 'error.log')
        self.writeOutProjConfFile   = False

        # Add file names to each of our conf objects
        self._userConfig.filename   = self.userConfFile
        self._projConfig.filename   = self.projConfFile
        self._layoutConfig.filename = self.layoutConfFile
        # If there is no projConfFile then we do not want these
        if os.path.isfile(self.projConfFile) :
            self._layoutConfig.filename = self.layoutConfFile
        else :
            self._layoutConfig.filename = 'nothing'
#        print 'xxxxxx', self._layoutConfig.filename
        # All available commands in context


###############################################################################
############################ Project Level Functions ##########################
###############################################################################

    def initProject (self) :
        '''Initialize the project object and load the project type class.'''

        # Initialize the managers dictionary here
        self.managers = {}

        # Create a fresh merged version of the projConfig
        self._projConfig  = ConfigObj(self.projConfFile)
        self.projectType = self._projConfig['ProjectInfo']['projectType']
        buildConfSection(self._userConfig, 'Projects')
        userConfig.registerProject(self._userConfig, self._projConfig, self.projHome)

        # Do some cleanup like getting rid of the last sessions error log file.
        try :
            if os.path.isfile(projErrorLogFile) :
                os.remove(projErrorLogFile)
        except :
            pass

        # Initialize the project type
        m = __import__(self.projectType)
        self.__class__ = getattr(m, self.projectType[0].upper() + self.projectType[1:])

        # Update the existing config file with the project type XML file
        # if needed
        newXmlDefaults = os.path.join(self.rpmConfigFolder, self.projectType + '.xml')
        xmlConfig = getXMLSettings(newXmlDefaults)
        newConf = ConfigObj(xmlConfig.dict()).override(self._projConfig)
        for s,v in self._projConfig.items() :
            if s not in newConf :
                newConf[s] = v

        if self._projConfig != newConf :
            self._projConfig = newConf

        # Bring in default layout config information
        if not os.path.isfile(self.layoutConfFile) :
            self._layoutConfig  = ConfigObj(getXMLSettings(self.rpmLayoutDefaultFile))
#            self._layoutConfig.filename = self.layoutConfFile
        else :
            self._layoutConfig = ConfigObj(self.layoutConfFile)

        # Create some common folders used in every project (if needed)
        if not os.path.isdir(self.processFolder) :
            os.mkdir(self.processFolder)
        if not os.path.isdir(self.textFolder) :
            os.mkdir(self.textFolder)
        if not os.path.isdir(self.fontsFolder) :
            os.mkdir(self.fontsFolder)


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

        self.writeToLog('LOG', 'Created the [' + fullName + '] manager object.')
        return self.managers[fullName]


    def loadManager (self, cType, mType) :
        '''Do basic load on a manager.'''

        fullName = cType + '_' + mType.capitalize()
        cfg = self._projConfig['Managers'][fullName]
        module = __import__(mType)
        manobj = getattr(module, mType.capitalize())(self, cfg, cType)
        self.managers[fullName] = manobj


    def addManager (self, cType, mType) :
        '''Create a manager reference in the project config that components will point to.'''

        fullName = cType + '_' + mType.capitalize()
        # Insert the Manager section if it is not already there
        buildConfSection(self._projConfig, 'Managers')
        if not testForSetting(self._projConfig['Managers'], fullName) :
            buildConfSection(self._projConfig['Managers'], fullName)
            managerDefaults = getXMLSettings(os.path.join(self.rpmConfigFolder, mType + '.xml'))
            for k, v, in managerDefaults.iteritems() :
                # Do not overwrite if a value is already there
                if not testForSetting(self._projConfig['Managers'][fullName], k) :
                    self._projConfig['Managers'][fullName][k] = v
                    self.writeOutProjConfFile = True


###############################################################################
########################## Component Level Functions ##########################
###############################################################################

    def renderComponent (self, cid) :
        '''Render a single component. This will ensure there is a component
        object, then render it.'''

        self.createComponent(cid).render()


    def createComponent (self, cid) :
        '''Create a component object that can be acted on.'''

        # If the object already exists just return it
        if cid in self.components : return self.components[cid]
        
        # Otherwise, create a new one and return it
        cfg = self._projConfig['Components'][cid]
        cType = cfg['type']
        module = __import__(cType)
        compobj = getattr(module, cType.capitalize())(self, cfg)
        self.components[cid] = compobj

        return compobj


    def addComponent (self, cid, cType) :
        '''This will add a component to the object we created 
        above in createComponent().'''

        try :
            x = self._projConfig['Components'][cid]
            self.writeToLog('MSG', 'The [' + cid + '] component already exists in this project.')
        except :
            buildConfSection(self._projConfig, 'Components')
            buildConfSection(self._projConfig['Components'], cid)
            self._projConfig['Components'][cid]['name'] = cid
            self._projConfig['Components'][cid]['type'] = cType
            self.writeOutProjConfFile = True
            self.writeToLog('MSG', 'Added the [' + cid + '] component to the project')


###############################################################################
############################ System Level Functions ###########################
###############################################################################


#    def addCommand(self, name, cls) :
#        '''Add a command to the command list.'''

#        self.commands[name] = cls


    def run(self, command, opts, userConfig) :
        '''Run a command'''

        if command in self.commands :
            self.commands[command].run(opts, self, userConfig)
        else :
            terminalError('The command: [' + command + '] failed to run with these options: ' + str(opts))


#    def help(self, command, opts, userConfig) :
#        '''Give the user the documented help'''
#        # FIXME: This is not giving us help for the specific commands
#        if len(opts) and opts[0] in self.commands :
#            self.commands[opts[0]].help()
#        else :
#            for k in sorted(self.commands.keys()) :
#                terminal(k)


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


