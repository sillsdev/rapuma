#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20120522
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handel all project logging operations

# History:
# 20120522 - djd - Start with original code copied in from tools.py


###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os

# Load the local classes
from tools import *


class ProjLog (object) :

    def __init__(self, local, usrConf) :
        '''Do the primary initialization for this manager.'''

        # Set values for this manager
        self.local              = local
        self.usrConf            = usrConf

        # Error Codes
        # Each 4 letter ID type corresponds to a section in the options parser
        # The ID type code is followed by a 3 digit number. We can have up to
        # 999 error messages for each ID type. Messages come in 4 types they are:
        #    MSG = General messages go to both the terminal and log file
        #    LOG = Messages that go only to the log file
        #    WRN = Warnings that go to the terminal and log file
        #    ERR = Errors that go to both the terminal and log file
        #    TOD = Messages that will go to a special todo file to guide the user
        self.errorCodes     = {

            'PROJ-000' : ['MSG', 'Messages that deal with issues on the project level, file one: <<1>>, file two: <<2>>'],
            'PROJ-005' : ['LOG', 'Created the [<<1>>] manager object.'],
            'PROJ-010' : ['LOG', 'Wrote out project configuration file.'],
            'PROJ-015' : ['MSG', 'Added the [<<1>>] meta component to the project.'],
            'PROJ-020' : ['MSG', 'Added the [<<1>>] component to the project.'],
            'PROJ-025' : ['MSG', 'The [<<1>>] component already exists in this project.'],
            'PROJ-030' : ['MSG', 'Changed  [<<1>>][<<2>>][<<3>>] setting from \"<<4>>\" to \"<<5>>\".'],
            'PROJ-035' : ['MSG', 'PROJ-035 - Unassigned error message ID.'],
            'PROJ-040' : ['MSG', 'PROJ-040 - Unassigned error message ID.'],

            'COMP-000' : ['MSG', 'Component level messages'],
            'COMP-005' : ['TOD', 'The ParaTExt SSF file could not be found. Check the project folder to see if it exsits.'],
            'COMP-010' : ['LOG', 'Version number: [<<1>>], was found. Assumed persistent values have been merged.'],
            'COMP-015' : ['LOG', 'Version number present, not running persistant values.'],
            'COMP-020' : ['LOG', 'Wrote out new layout configuration file.'],
            'COMP-025' : ['MSG', 'Rendering of [<<1>>] successful.'],
            'COMP-030' : ['ERR', 'Rendering [<<1>>] was unsuccessful. <<2>> (<<3>>)'],
            'COMP-035' : ['ERR', 'XeTeX error code [<<1>>] not understood by RPM.'],
            'COMP-040' : ['LOG', 'Created: <<1>>'],
            'COMP-045' : ['TOD', 'File <<1>> is missing. Check the error log for an import error for this required file. The system cannot render without it.'],
            'COMP-050' : ['TOD', 'USFM working text not found: <<1>>. This is required in order to render.'],
            'COMP-055' : ['TOD', 'make<<1>>() failed to create: <<2>>. This is a required file in order to render.'],
            'COMP-060' : ['LOG', 'Settings changed, <<1>> recreated.'],
            'COMP-065' : ['LOG', 'File: <<1>> missing, created a new one.'],
            'COMP-070' : ['LOG', 'Copied macro: <<1>>'],
            'COMP-075' : ['ERR', 'No macro package for : <<1>>'],
            'COMP-080' : ['LOG', 'There has been a change in [<<1>>], [<<2>>] needs to be rerendered.'],
            'COMP-085' : ['LOG', '<<1>> not found, it will be rendered.'],
            'COMP-090' : ['LOG', 'No changes to dependent files found, [<<1>>] does not need to be rerendered at this time.'],
            'COMP-095' : ['MSG', 'Routing <<1>> to PDF viewer.'],
            'COMP-100' : ['MSG', '<<1>> cannot be viewed, PDF viewer turned off.'],
            'COMP-105' : ['MSG', 'COMP-105 - Unassigned error message ID.'],
            'COMP-110' : ['MSG', 'COMP-110 - Unassigned error message ID.'],
            'COMP-115' : ['MSG', 'COMP-115 - Unassigned error message ID.'],
            'COMP-120' : ['MSG', 'COMP-120 - Unassigned error message ID.'],

            'FONT-000' : ['MSG', 'Font issue messages'],
            'FONT-005' : ['MSG', 'FONT-005 - Unassigned error message ID.'],
            'FONT-010' : ['MSG', 'FONT-010 - Unassigned error message ID.'],
            'FONT-015' : ['MSG', 'FONT-015 - Unassigned error message ID.'],
            'FONT-020' : ['MSG', 'FONT-020 - Unassigned error message ID.'],
            'FONT-025' : ['MSG', 'FONT-025 - Unassigned error message ID.'],
            'FONT-030' : ['MSG', 'FONT-030 - Unassigned error message ID.'],
            'FONT-035' : ['MSG', 'FONT-035 - Unassigned error message ID.'],
            'FONT-040' : ['MSG', 'FONT-040 - Unassigned error message ID.'],

            'STYL-000' : ['MSG', 'Messages for style level issues'],
            'STYL-005' : ['MSG', 'STYL-005 - Unassigned error message ID.'],
            'STYL-010' : ['MSG', 'STYL-010 - Unassigned error message ID.'],
            'STYL-015' : ['MSG', 'STYL-015 - Unassigned error message ID.'],
            'STYL-020' : ['MSG', 'STYL-020 - Unassigned error message ID.'],
            'STYL-025' : ['MSG', 'STYL-025 - Unassigned error message ID.'],
            'STYL-030' : ['MSG', 'STYL-030 - Unassigned error message ID.'],
            'STYL-035' : ['MSG', 'STYL-035 - Unassigned error message ID.'],
            'STYL-040' : ['MSG', 'STYL-040 - Unassigned error message ID.'],

            'SETG-000' : ['MSG', 'Messages for setting issues'],
            'SETG-005' : ['MSG', 'SETG-005 - Unassigned error message ID.'],
            'SETG-010' : ['MSG', 'SETG-010 - Unassigned error message ID.'],
            'SETG-015' : ['MSG', 'SETG-015 - Unassigned error message ID.'],
            'SETG-020' : ['MSG', 'SETG-020 - Unassigned error message ID.'],
            'SETG-025' : ['MSG', 'SETG-025 - Unassigned error message ID.'],
            'SETG-030' : ['MSG', 'SETG-030 - Unassigned error message ID.'],
            'SETG-035' : ['MSG', 'SETG-035 - Unassigned error message ID.'],
            'SETG-040' : ['MSG', 'SETG-040 - Unassigned error message ID.'],

            'TEST-000' : ['MSG', 'Test level messages'],
            'TEST-005' : ['MSG', 'TEST-005 - Unassigned error message ID.'],
            'TEST-010' : ['MSG', 'TEST-010 - Unassigned error message ID.'],
            'TEST-015' : ['MSG', 'TEST-015 - Unassigned error message ID.'],
            'TEST-020' : ['MSG', 'TEST-020 - Unassigned error message ID.'],
            'TEST-025' : ['MSG', 'TEST-025 - Unassigned error message ID.'],
            'TEST-030' : ['MSG', 'TEST-030 - Unassigned error message ID.'],
            'TEST-035' : ['MSG', 'TEST-035 - Unassigned error message ID.'],
            'TEST-040' : ['MSG', 'TEST-040 - Unassigned error message ID.']

                              }


###############################################################################
############################### Logging Functions #############################
###############################################################################

    def writeToLog (self, errCode, args=None, mod=None) :
        '''Send an event to one of the log files or the terminal if specified.
        Everything gets written to a log.  Where a message gets written to
        depends on what type code it is.  The type code is in with the error
        code data.  There are five type codes:
            MSG = General messages go to both the terminal and log file
            LOG = Messages that go only to the log file
            WRN = Warnings that go to the terminal and log file
            ERR = Errors that go to both the terminal and log file
            TOD = Messages that will go to a special todo file to guide the user
        The errCode points to a specific message that will be sent to a log
        file. The args parameter can contain extra information like file names
        to help the user better figure out what happened.'''

        # Build the mod line
        if mod :
            mod = mod + ': '
        else :
            mod = ''

        # Get the message from the code
        if errCode in self.errorCodes.keys() :
            msg = self.errorCodes[errCode][1]
            code = self.errorCodes[errCode][0]
        else :
            terminal('\nThe code: [' + errCode + '] is not recognized by the RPM system.')
            dieNow()

        # If args were given, do s/r on them and add 
        # args info that needs to be added to msg.
        # Look for a <<#>> pattern replace it with
        # the corresponding position in the args list.
        if args :
            c = 0
            for a in args :
                c +=1
                msg = msg.replace('<<' + str(c) + '>>', args[c-1])

        # Write out everything but LOG messages to the terminal
        if code != 'LOG' and code != 'TOD' :
            terminal('\n' + code + ' - ' + msg)

        # Test to see if this is a live project by seeing if the project conf is
        # there.  If it is, we can write out log files.  Otherwise, why bother?
        if os.path.isfile(self.local.projConfFile) :

            # Build the event line
            if code == 'ERR' :
                eventLine = '\"' + tStamp() + '\", \"' + code + '\", \"' + mod + msg + '\"'
            else :
                eventLine = '\"' + tStamp() + '\", \"' + code + '\", \"' + msg + '\"'

            # Do we need a log file made?
            try :
                if not os.path.isfile(self.local.projLogFile) or os.path.getsize(self.local.projLogFile) == 0 :
                    writeObject = codecs.open(self.local.projLogFile, "w", encoding='utf_8')
                    writeObject.write('RPM event log file created: ' + tStamp() + '\n')
                    writeObject.close()

                # Now log the event to the top of the log file using preAppend().
                self.preAppend(eventLine, self.local.projLogFile)

                # FIXME: Add the TOD list output here, also, output any TODs 
                # to the error log as well as these are bad errors.

                # Write errors and warnings to the error log file
                if code == 'WRN' and self.usrConf['System']['debugging'] == 'True':
                    self.writeToErrorLog(self.local.projErrorLogFile, eventLine)

                if code == 'ERR' :
                    self.writeToErrorLog(self.local.projErrorLogFile, eventLine)

            except :
                terminal("Failed to write message to log file: " + msg)

        return


    def writeToErrorLog (self, errorLog, eventLine) :
        '''In a perfect world there would be no errors, but alas there are and
        we need to put them in a special file that can be accessed after the
        process is run.  The error file from the previous session is deleted at
        the begining of each new run.'''

        try :
            # Because we want to read errors from top to bottom, we don't pre append
            # them to the error log file.
            if not os.path.isfile(errorLog) :
                writeObject = codecs.open(errorLog, "w", encoding='utf_8')
            else :
                writeObject = codecs.open(errorLog, "a", encoding='utf_8')

            # Write and close
            writeObject.write(eventLine + '\n')
            writeObject.close()
        except :
            terminal('Error writing this event to error log: ' + eventLine)

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



