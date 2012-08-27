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

            'PROJ-000' : ['MSG', 'Project module messages'],
            'PROJ-005' : ['LOG', 'Created the [<<1>>] manager object.'],
            'PROJ-010' : ['LOG', 'Wrote out project configuration file.'],
            'PROJ-015' : ['MSG', 'Added the [<<1>>] meta component to the project.'],
            'PROJ-020' : ['MSG', 'Added the [<<1>>] component to the project.'],
            'PROJ-025' : ['MSG', 'The [<<1>>] component already exists in this project.'],
            'PROJ-030' : ['MSG', 'Changed  [<<1>>][<<2>>][<<3>>] setting from \"<<4>>\" to \"<<5>>\".'],
            'PROJ-035' : ['MSG', 'PROJ-035 - Unassigned error message ID.'],
            'PROJ-040' : ['MSG', 'PROJ-040 - Unassigned error message ID.'],

            'COMP-000' : ['MSG', 'Component module messages'],
            'COMP-010' : ['MSG', 'The component ID: [<<1>>] is not a valid for this component type. It cannot be processed by the system.'],
            'COMP-020' : ['MSG', 'COMP-020 - Unassigned error message ID.'],
            'COMP-030' : ['ERR', 'The delete component function has not been implemented yet. This component will have to be manually removed. Sorry about that.'],
            'COMP-035' : ['ERR', 'The view component function has not been implemented yet. Sorry about that.'],
            'COMP-040' : ['MSG', 'COMP-040 - Unassigned error message ID.'],
            'COMP-050' : ['MSG', 'COMP-050 - Unassigned error message ID.'],

            'XTEX-000' : ['MSG', 'XeTeX module messages'],
            'XTEX-005' : ['TOD', 'The ParaTExt SSF file could not be found. Check the project folder to see if it exsits.'],
            'XTEX-010' : ['LOG', 'Version number: [<<1>>], was found. Assumed persistent values have been merged.'],
            'XTEX-015' : ['LOG', 'Version number present, not running persistant values.'],
            'XTEX-020' : ['LOG', 'Wrote out new layout configuration file.'],
            'XTEX-025' : ['MSG', 'Rendering of [<<1>>] successful.'],
            'XTEX-030' : ['ERR', 'Rendering [<<1>>] was unsuccessful. <<2>> (<<3>>)'],
            'XTEX-035' : ['ERR', 'XeTeX error code [<<1>>] not understood by RPM.'],
            'XTEX-040' : ['LOG', 'Created: <<1>>'],
            'XTEX-045' : ['TOD', 'File <<1>> is missing. Check the error log for an import error for this required file. The system cannot render without it.'],
            'XTEX-050' : ['TOD', 'USFM working text not found: <<1>>. This is required in order to render.'],
            'XTEX-055' : ['TOD', 'make<<1>>() failed to create: <<2>>. This is a required file in order to render.'],
            'XTEX-060' : ['LOG', 'Settings changed, <<1>> recreated.'],
            'XTEX-065' : ['LOG', 'File: <<1>> missing, created a new one.'],
            'XTEX-070' : ['LOG', 'Copied macro: <<1>>'],
            'XTEX-075' : ['ERR', 'No macro package for : <<1>>'],
            'XTEX-080' : ['LOG', 'There has been a change in [<<1>>], [<<2>>] needs to be rerendered.'],
            'XTEX-085' : ['MSG', '<<1>> not found, it cannot be viewed.'],
            'XTEX-090' : ['LOG', 'No changes to dependent files found, [<<1>>] does not need to be rerendered at this time.'],
            'XTEX-095' : ['MSG', 'Routing <<1>> to PDF viewer.'],
            'XTEX-100' : ['MSG', '<<1>> cannot be viewed, PDF viewer turned off.'],
            'XTEX-105' : ['ERR', 'PDF viewer failed with error code number: <<1>>'],
            'XTEX-110' : ['MSG', 'XTEX-110 - Unassigned error message ID.'],
            'XTEX-115' : ['MSG', 'XTEX-115 - Unassigned error message ID.'],
            'XTEX-120' : ['MSG', 'XTEX-120 - Unassigned error message ID.'],

            'TEXT-000' : ['MSG', 'Text module messages'],
            'TEXT-005' : ['MSG', 'TEXT-005 - Unassigned error message ID.'],
            'TEXT-010' : ['MSG', 'Source file editor [<<1>>] is not recognized by this system. Please double check the name used for the source text editor setting.'],
            'TEXT-015' : ['MSG', 'TEXT-015 - Unassigned error message ID.'],
            'TEXT-020' : ['ERR', 'Source file name could not be built because the Name Form ID is missing. Double check to see which editor created the source text.'],
            'TEXT-025' : ['ERR', 'Source file name could not be built because the Name Form ID [<<1>>] is not recognized by this system. Please contact the system developer about this problem.'],
            'TEXT-030' : ['LOG', 'Copied [<<1>>] to [<<2>>] in project.'],
            'TEXT-035' : ['ERR', 'Source file: [<<1>>] not found! Cannot copy to project.'],
            'TEXT-040' : ['MSG', 'TEXT-040 - Unassigned error message ID.'],

            'FONT-000' : ['MSG', 'Font module messages'],
            'FONT-005' : ['MSG', 'FONT-005 - Unassigned error message ID.'],
            'FONT-010' : ['LOG', 'Wrote out new font configuration (font.__init__())'],
            'FONT-015' : ['MSG', 'FONT-015 - Unassigned error message ID.'],
            'FONT-020' : ['ERR', 'Failed to find font setting in ParaTExt project (.ssf file). A primary font must be set before this component can be successfully rendered.'],
            'FONT-025' : ['ERR', 'No source editor was found for this project. Please enter this setting before continuing.'],
            'FONT-030' : ['ERR', 'The source editor: <<1>>, is not currently supported by the system. Please enter a supported editor into the configuration settings before continuing, or contact the system developer to add support for your editor.'],
            'FONT-035' : ['MSG', 'Set the project primary font to: <<1>>'],
            'FONT-040' : ['ERR', 'Font file [<<1>>.xml] not found. (font.recordFont())'],
            'FONT-045' : ['LOG', '<<1>> font setup information added to project config'],
            'FONT-050' : ['ERR', 'Halt! <<!>> not found. (font.copyInFont()'],

            'LYOT-000' : ['MSG', 'Layout module messages'],
            'LYOT-005' : ['MSG', 'LYOT-005 - Unassigned error message ID.'],
            'LYOT-010' : ['LOG', 'Wrote out new layout configuration file. (layout.__init__())'],
            'LYOT-015' : ['MSG', 'LYOT-015 - Unassigned error message ID.'],
            'LYOT-020' : ['MSG', 'LYOT-020 - Unassigned error message ID.'],
            'LYOT-025' : ['MSG', 'LYOT-025 - Unassigned error message ID.'],

            'ILUS-000' : ['MSG', 'Illustration module messages'],
            'ILUS-005' : ['MSG', 'ILUS-005 - Unassigned error message ID.'],
            'ILUS-010' : ['LOG', 'Wrote out new illustration configuration file. (illustration.__init__())'],
            'ILUS-015' : ['MSG', 'ILUS-015 - Unassigned error message ID.'],
            'ILUS-020' : ['MSG', 'ILUS-020 - Unassigned error message ID.'],
            'ILUS-025' : ['MSG', 'ILUS-025 - Unassigned error message ID.'],

            'STYL-000' : ['MSG', 'Style module messages'],
            'STYL-005' : ['MSG', 'STYL-005 - Unassigned error message ID.'],
            'STYL-010' : ['LOG', 'Main style file copied in from PT project.'],
            'STYL-015' : ['ERR', 'Main style file creation not supported yet. This is a required file.'],
            'STYL-020' : ['LOG', 'Custom style file in PT project not found.'],
            'STYL-025' : ['MSG', 'STYL-025 - Unassigned error message ID.'],
            'STYL-030' : ['ERR', 'Custom style file creation not supported yet.'],
            'STYL-035' : ['MSG', 'STYL-035 - Unassigned error message ID.'],
            'STYL-040' : ['ERR', 'Component style override file creation not supported yet.'],

            'SETG-000' : ['MSG', 'Messages for setting issues (probably only in project.py)'],
            'SETG-005' : ['MSG', 'SETG-005 - Unassigned error message ID.'],
            'SETG-010' : ['MSG', 'SETG-010 - Unassigned error message ID.'],
            'SETG-015' : ['MSG', 'SETG-015 - Unassigned error message ID.'],
            'SETG-020' : ['MSG', 'SETG-020 - Unassigned error message ID.'],
            'SETG-025' : ['MSG', 'SETG-025 - Unassigned error message ID.'],
            'SETG-030' : ['MSG', 'SETG-030 - Unassigned error message ID.'],
            'SETG-035' : ['MSG', 'SETG-035 - Unassigned error message ID.'],
            'SETG-040' : ['MSG', 'SETG-040 - Unassigned error message ID.'],

            'TEST-000' : ['MSG', 'Test level messages (probably only in project.py)'],
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
            eventLine = '\"' + tStamp() + '\", \"' + msg + '\"'
#            if code == 'ERR' :
#                eventLine = '\"' + tStamp() + '\", \"' + code + '\", \"' + mod + msg + '\"'
#            else :
#                eventLine = '\"' + tStamp() + '\", \"' + code + '\", \"' + msg + '\"'

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



