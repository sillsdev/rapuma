#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20120403
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This manager class will handle component rendering with XeTeX. It tries to
# be somewhat generic so it will work with various macro packages.

# History:
# 20120403 - djd - Started with intial file copied in from ptxplus


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, sys


def prepCommand (task, typeID, inputFile, outputFile, optionalPassedVariable) :
    '''This is the main routine for the class. It will control
        the running of the process classes we want to run.'''

    # Set some global (might be better done in an init section)
    self._task = task
    self._typeID = typeID
    self._inputFile = inputFile
    self._outputFile = outputFile
    self._optionalPassedVariable = optionalPassedVariable
    
    
    # We need to sort out the task that we are running
    # Sometimes parent meta-tasks are being called which
    # need to link to the individual tasks. This sorts that
    # out and runs everthing that is called to run.

    # Make a list that contains all the metaProcesses
    metaTaskList = []
    taskList = []
    metaTaskList = log_manager._settings['System']['Processes']['textMetaProcesses']
    # if this is a meta task then we need to process it as
    # if there are multiple sub-tasks within even though
    # there may only be one
    if self._task in metaTaskList :
        metaTask = self._task
        taskList = log_manager._settings['System']['Processes'][metaTask]
        for thisTask in taskList :
            # It would be good if we gave a little feedback to the user
            # as to what exactly which processes are going to be run and
            # on what.
            head, tail = os.path.split(self._inputFile)
            tools.userMessage('INFO: Now running: ' + thisTask + ' (' + tail + ')')
            # The standard sys.argv[1] setting contains the name of the metaTask
            # However, that is not the name of the actual module we want to send
            # off to process. We need to replace sys.argv[1] with the right task
            # name and any parameters that go with it.
            sys.argv[1] = thisTask
            self.runIt(thisTask)

    # If it is not a meta task then it must be a single one
    # so we will just run it as it comes in
    else :
        self.runIt(self._task)


def runIt (taskCommand) :
    '''This will dynamically run a module when given a
        valid name. The module must have the doIt() function
        defined in the "root" of the module.'''

    # For flexibility, some tasks may have parameters added
    # to them. To initiate the task we need to pull out the
    # the module name to be able to initialize it. Once the
    # module has been initialized, it will get the parmeters
    # from sys.argv[1] and take it from there.
    thisTask = taskCommand.split()[0]

    # Initialize the log manager to do its thing
    log_manager.initializeLog(thisTask, self._typeID, self._inputFile, self._outputFile, self._optionalPassedVariable)

    # For running each process we use one centralized task runner in tools.
    tools.taskRunner(log_manager, thisTask)

    # Close out the process by reporting to the log file
    log_manager.closeOutSessionLog()


