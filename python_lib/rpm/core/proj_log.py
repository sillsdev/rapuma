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

    def __init__(self, local, userConf) :
        '''Do the primary initialization for this manager.'''

        # Set values for this manager
        self.local              = local
        self.userConfig          = userConf.userConfig

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
            'PROJ-011' : ['ERR', 'Failed to write out project configuration file.'],
            'PROJ-015' : ['MSG', 'Added the [<<1>>] meta component to the project.'],
            'PROJ-020' : ['MSG', 'Added the [<<1>>] component to the project.'],
            'PROJ-025' : ['MSG', 'The [<<1>>] component already exists in this project.'],
            'PROJ-030' : ['MSG', 'Changed  [<<1>>][<<2>>][<<3>>] setting from \"<<4>>\" to \"<<5>>\".'],
            'PROJ-035' : ['MSG', 'PROJ-035 - Unassigned error message ID.'],
            'PROJ-040' : ['MSG', 'PROJ-040 - Unassigned error message ID.'],
            'PROJ-050' : ['MSG', 'NOT WORKING YET! - Installed post_process.py script for the [<<1>>] component type.'],

            'COMP-000' : ['MSG', 'Component module messages'],
            'COMP-010' : ['ERR', 'The component ID: [<<1>>] is not a valid for this component type. It cannot be processed by the system.'],
            'COMP-011' : ['ERR', 'There seems to be a problem with component ID: [<<1>>] it may not be a valid ID.'],
            'COMP-012' : ['ERR', 'There seems to be a problem with component ID: [<<1>>] found in the meta component list: [<<2>>], it may not be a valid ID.'],
            'COMP-020' : ['MSG', 'The [<<1>>] component has been locked. The working text for this componet can no longer be updated.'],
            'COMP-021' : ['MSG', 'The [<<1>>] component type has been locked. The working text for any component of this type can no longer be updated.'],
            'COMP-025' : ['MSG', 'The [<<1>>] component has been unlocked. The working text for this componet can now be updated.'],
            'COMP-026' : ['MSG', 'The [<<1>>] component type has been unlocked. The working text for any components of type can now be updated.'],
            'COMP-027' : ['WRN', 'No lock file was found for the [<<1>>] component. You should be able to update the working text for this component.'],
            'COMP-028' : ['WRN', 'No lock file was found for the [<<1>>] component type. You should be able to update working text for any component of this type.'],
            'COMP-030' : ['LOG', 'The [<<1>>] component section has been deleted from the project configuration file.'],
            'COMP-031' : ['LOG', 'The [<<1>>] component folder has been deleted from your hard drive.'],
            'COMP-032' : ['LOG', 'There is no folder found for the [<<1>>] component. No files have been deleted by this operation.'],
            'COMP-033' : ['MSG', 'The [<<1>>] component has been completly deleted from your system. This includes configuration as well as files.'],
            'COMP-035' : ['ERR', 'There was no entry in the project configuration file for the [<<1>>] component. The delete component command cannot be completed.'],
            'COMP-040' : ['ERR', 'There is no listing in the configuration file for [<<1>>]. Please add this component to render it.'],
            'COMP-050' : ['LOG', 'Doing the preprocessing on the [<<1>>] component.'],
            'COMP-060' : ['ERR', 'Could not post process, file not found: [<<1>>].'],
            'COMP-065' : ['LOG', 'Post processes completed successfully on: [<<1>>].'],
            'COMP-067' : ['ERR', 'Post processes script: [<<1>>] was called on the component: [<<2>>] but the script was not found in the project.'],
            'COMP-068' : ['TDO', 'Use the command: [rpm project <project ID> -p <component type>] to install the post process shell script. Modify this script as necessary to complete any post process that need to be done to your components.'],

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
            'XTEX-085' : ['MSG', 'The file: <<1>> was not found, XeTeX will now try to render it.'],
            'XTEX-090' : ['LOG', 'No changes to dependent files found, [<<1>>] does not need to be rerendered at this time.'],
            'XTEX-095' : ['MSG', 'Routing <<1>> to PDF viewer.'],
            'XTEX-100' : ['MSG', '<<1>> cannot be viewed, PDF viewer turned off.'],
            'XTEX-105' : ['ERR', 'PDF viewer failed with error code number: <<1>>'],
            'XTEX-110' : ['MSG', 'The file <<1>> was removed so it could be rerendered.'],
            'XTEX-115' : ['MSG', 'XTEX-115 - Unassigned error message ID.'],
            'XTEX-120' : ['MSG', 'XTEX-120 - Unassigned error message ID.'],

            'TEXT-000' : ['MSG', 'Text module messages'],
            'TEXT-005' : ['MSG', 'TEXT-005 - Unassigned error message ID.'],
            'TEXT-010' : ['MSG', 'Source file editor [<<1>>] is not recognized by this system. Please double check the name used for the source text editor setting.'],
            'TEXT-015' : ['MSG', 'TEXT-015 - Unassigned error message ID.'],
            'TEXT-020' : ['ERR', 'Source file name could not be built because the Name Form ID is missing. Double check to see which editor created the source text.'],
            'TEXT-025' : ['ERR', 'Source file name could not be built because the Name Form ID [<<1>>] is not recognized by this system. Please contact the system developer about this problem.'],
            'TEXT-030' : ['LOG', 'Copied [<<1>>] to [<<2>>] in project.'],
            'TEXT-035' : ['ERR', 'Source file: [<<1>>] not found! Cannot copy to project. Process halting now.'],
            'TEXT-040' : ['WRN', 'The [<<1>>] component type is locked and cannot have any text modifications done to any files of this type at this time.'],
            'TEXT-045' : ['WRN', 'The [<<1>>] component is locked and cannot have any text modifications done to it at this time.'],
            'TEXT-050' : ['LOG', 'Working text file for [<<1>>] has been completed.'],
            'TEXT-055' : ['ERR', 'TEXT-055 - Unassigned error message ID.'],
            'TEXT-060' : ['LOG', 'Completed post processing on component working text.'],

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
            'FONT-047' : ['ERR', 'No record found for the [<<1>>].'],
            'FONT-050' : ['ERR', 'Halt! [<<1>>] not found. - font.copyInFont()'],
            'FONT-060' : ['MSG', 'There were <<1>> new font files copied into the [<<2>>] project font folder. - font.installFont()'],
            'FONT-062' : ['LOG', 'No update to fonts folder needed. - font.installFont()'],
            'FONT-070' : ['LOG', 'Copied the [<<1>>] font file into the project. - font.copyInFont()'],

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

# These have to do with keeping a running project log file.  Everything done is
# recorded in the log file and that file is trimmed to a length that is
# specified in the system settings.  Everything is channeled to the log file but
# depending on what has happened, they are classed in three levels:
#   1) [MSG] - Common event going to log and terminal
#   2) [WRN] - Warning event going to log and terminal if debugging is turned on
#   3) [ERR] - Error event going to the log and terminal
#   4) [LOG] - Messages that go only to the log file to help with debugging
# FIXME: Following not implemented yet
#   5) [TOD] - To do list. Output to a file that helps guide the user.


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
            eventLine = '\"' + tStamp() + '\", \"' + code + '\", \"' + msg + '\"'
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
                if code == 'WRN' and self.userConfig['System']['debugging'] == 'True':
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



