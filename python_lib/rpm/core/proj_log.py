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
            'PROJ000' : ['MSG', 'Messages that deal with issues on the project level, file one: <<1>>, file two: <<2>>'],
            'COMP000' : ['MSG', 'Component level messages'],
            'FONT000' : ['MSG', 'Font issue messages'],
            'STYL000' : ['MSG', 'Messages for style level issues'],
            'SETG000' : ['MSG', 'Messages for setting issues'],
            'TEST000' : ['MSG', 'Test level messages']
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
            terminal('\nThe code: [' + code + '] is not recognized by the RPM system.')
            dieNow()

        # Now s/r any args that need to be added to msg.
        # Look for a <<#>> pattern replace it with
        # the corresponding position in the args list.
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

                # FIXME: Add the TOD list output here

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



