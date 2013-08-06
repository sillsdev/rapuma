#!/usr/bin/python
# -*- coding: utf_8 -*-
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handel all project logging operations


###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, fileinput, sys

# Load the local classes
from rapuma.core.tools          import Tools
from rapuma.core.proj_local     import ProjLocal
from rapuma.core.user_config    import UserConfig


class ProjLog (object) :

    def __init__(self, pid) :
        '''Do the primary initialization for this manager.'''

        self.tools              = Tools()
        self.pid                = pid
        self.rapumaHome         = os.environ.get('RAPUMA_BASE')
        self.userHome           = os.environ.get('RAPUMA_USER')
        self.user               = UserConfig()
        self.userConfig         = self.user.userConfig
        self.local              = ProjLocal(pid)


###############################################################################
############################### Logging Functions #############################
###############################################################################

# These have to do with keeping a running project log file.  Everything done is
# recorded in the log file and that file is trimmed to a length that is
# specified in the system settings.  Everything is channeled to the log file but
# depending on what has happened, they are classed in three levels:
#   1) [MSG] - Common event going to log and terminal
#   2) [WRN] - Warning event going to log and terminal if debugging is turned on
#   3) [ERR] - Error event going to the log and terminal and kills the process
#   4) [LOG] - Messages that go only to the log file to help with debugging
# FIXME: Following not implemented yet
#   5) [TOD] - To do list. Output to a file that helps guide the user.


    def writeToLog (self, errCode, args=None, location=None) :
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

        # Get the message from the errorCode list the module sent
        if type(errCode) == list :
            if location :
                msg = errCode[1] + ' : (' + location + ')'
            else :
                msg = errCode[1]
            code = errCode[0]
        else :
            self.tools.terminal('\nThe code: [' + errCode + '] is not recognized by the Rapuma system.')
            return

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
            self.tools.terminal('\n' + code + ' - ' + msg)

        # Test to see if this is a live project by seeing if the project conf is
        # there.  If it is, we can write out log files.  Otherwise, why bother?
        if os.path.isfile(self.local.projConfFile) :

            # Build the event line
            eventLine = '\"' + self.tools.tStamp() + '\", \"' + code + '\", \"' + msg + '\"'

            # Do we need a log file made?
            try :
                if not os.path.isfile(self.local.projLogFile) or os.path.getsize(self.local.projLogFile) == 0 :
                    writeObject = codecs.open(self.local.projLogFile, "w", encoding='utf_8')
                    writeObject.write('Rapuma event log file created: ' + self.tools.tStamp() + '\n')
                    writeObject.close()

                # Now log the event to the top of the log file using preAppend().
                self.preAppend(eventLine, self.local.projLogFile)

                # FIXME: Add the TOD list output here, also, output any TODs 
                # to the error log as well as these are bad errors.

                # Write errors and warnings to the error log file
                if code == 'WRN' and self.userConfig['System']['debugging'] == 'True':
                    self.writeToErrorLog(self.local.projErrorLogFile, eventLine)

                if code == 'ERR' :
                    self.writeToErrorLog(self.local.projErrorLogFile, eventLine)

            except Exception as e :
                # If we don't succeed, we should probably quite here
                self.tools.terminal("Failed to write message to log file: " + msg)
                self.tools.terminal('Internal error: [' + str(e) + ']')
                self.tools.dieNow()
            
            # Halt the process if this was an 'ERR' level type code
            if code == 'ERR' :
                self.tools.dieNow('Unrecoverable error.')

        return


    def writeToErrorLog (self, errorLog, eventLine) :
        '''In a perfect world there would be no errors, but alas there are and
        we need to put them in a special file that can be accessed after the
        process is run.  The error file from the previous session is deleted at
        the beginning of each new run.'''

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
            self.tools.terminal('Error writing this event to error log: ' + eventLine)

        return


    def preAppend (self, line, file_name) :
        '''Got the following code out of a Python forum.  This will pre-append a
        line to the beginning of a file.'''

#        import pdb; pdb.set_trace()

        fobj = fileinput.FileInput(file_name, inplace=1)
        first_line = fobj.readline()
        sys.stdout.write("%s\n%s" % (line, first_line))
        for line in fobj:
            sys.stdout.write("%s" % line)

        fobj.close()



