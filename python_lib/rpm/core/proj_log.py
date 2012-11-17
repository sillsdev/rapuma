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
            'PROJ-010' : ['LOG', 'Wrote out [<<1>>] settings to the project configuration file.'],
            'PROJ-011' : ['ERR', 'Failed to write out project [<<1>>] settings to the project configuration file.'],
            'PROJ-030' : ['MSG', 'Changed  [<<1>>][<<2>>][<<3>>] setting from \"<<4>>\" to \"<<5>>\".'],
            'PROJ-040' : ['ERR', 'Problem making setting change. Section [<<1>>] missing from configuration file.'],
            'PROJ-050' : ['ERR', 'Component [<<1>>] working text file was not found in the project configuration.'],
            'PROJ-060' : ['ERR', 'Component [<<1>>] was not found in the project configuration.'],
            'PROJ-070' : ['ERR', 'Source file not found: [<<1>>].'],
            'PROJ-080' : ['MSG', 'Successful copy of [<<1>>] to [<<2>>].'],
            'PROJ-090' : ['ERR', 'Target file [<<1>>] already exists. Use force (-f) to overwrite.'],
            'PROJ-100' : ['ERR', 'Failed to set source path. Error given was: [<<1>>]'],

            'COMP-000' : ['MSG', 'Component processing messages'],
            'COMP-005' : ['ERR', 'Component type [<<1>>] is not supported by the system.'],
            'COMP-010' : ['ERR', 'The component ID: [<<1>>] is not a valid for this component type. It cannot be processed by the system.'],
            'COMP-011' : ['ERR', 'There seems to be a problem with component ID: [<<1>>] it may not be a valid ID.'],
            'COMP-012' : ['ERR', 'There seems to be a problem with component ID: [<<1>>] found in the meta component list: [<<2>>], it may not be a valid ID.'],
            'COMP-020' : ['MSG', 'Added the [<<1>>] component to the project.'],
            'COMP-022' : ['LOG', 'Force switch was set (-f). Added the [<<1>>] component to the project.'],
            'COMP-025' : ['WRN', 'The [<<1>>] component is already listed in the RPM project configuration and is locked. Please unlock or use the force switch (-f) to cause the sytem to install new working text or overwrite the existing working text.'],
            'COMP-030' : ['LOG', 'The [<<1>>] component section has been deleted from the project configuration file.'],
            'COMP-031' : ['LOG', 'The [<<1>>] component folder has been deleted from your hard drive.'],
            'COMP-032' : ['LOG', 'There is no folder found for the [<<1>>] component. No files have been deleted by this operation.'],
            'COMP-033' : ['LOG', 'The [<<1>>] component has been completly deleted from your system. This includes configuration as well as files.'],
            'COMP-035' : ['LOG', 'There was no entry in the project configuration file for the [<<1>>] component. The delete component command cannot be completed.'],
            'COMP-040' : ['ERR', 'There is no listing in the configuration file for [<<1>>]. Please add this component to render it.'],
            'COMP-050' : ['LOG', 'Doing the preprocessing on the [<<1>>] component.'],
            'COMP-060' : ['MSG', 'The [<<1>>] component type has been added to the project.'],
            'COMP-065' : ['ERR', 'Adding the [<<1>>] component type to the project failed.'],
            'COMP-070' : ['ERR', 'Failed to render the [<<1>>] component. - project.renderComponent()'],
            'COMP-080' : ['ERR', 'Validate component is not implemented yet!'],
            'COMP-090' : ['ERR', 'Component type [<<1>>] source path is [<<2>>] cannot use [<<3>>] as a replacement. Use (-f) force to override the current setting.'],

            'GRUP-000' : ['MSG', 'Group processing messages'],
            'GRUP-010' : ['MSG', ''],
            'GRUP-015' : ['MSG', 'Added the [<<1>>] component group to the project.'],
            'GRUP-070' : ['ERR', 'The component group [<<1>>] is locked. Process halted! Please unlock it before continuing. - project.removeGroupComponent()'],
            'GRUP-071' : ['ERR', 'The configuration setting for the [<<1>>] group does not appear valid. Process halted! - project.removeGroupComponent()'],
            'GRUP-073' : ['MSG', 'Force switch was set (-f). The component group [<<1>>] was removed along with all related components. To bad if you did not meant to do that. :-( - project.removeGroupComponent()'],
            'GRUP-075' : ['MSG', 'The configuration listing for the component group [<<1>>] has been removed from the project. - project.removeGroupComponent()'],
            'GRUP-077' : ['LOG', 'Config settings successfully written out for the deletion of the component group [<<1>>] - project.removeGroupComponent()'],

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
            'XTEX-050' : ['ERR', 'USFM working text not found: <<1>>. This is required in order to render.'],
            'XTEX-055' : ['ERR', 'make<<1>>() failed to properly create: <<2>>. This is a required file in order to render.'],
            'XTEX-060' : ['LOG', 'Settings changed in [<<1>>], [<<2>>] needed to be recreated.'],
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
            'TEXT-005' : ['ERR', 'Component type [<<1>>] is not supported by the text manager.'],
            'TEXT-010' : ['MSG', 'Source file editor [<<1>>] is not recognized by this system. Please double check the name used for the source text editor setting.'],
            'TEXT-015' : ['MSG', 'TEXT-015 - Unassigned error message ID.'],
            'TEXT-020' : ['ERR', 'Source file name could not be built because the Name Form ID is missing or incorrect. Double check to see which editor created the source text.'],
            'TEXT-030' : ['LOG', 'Copied [<<1>>] to [<<2>>] in project.'],
            'TEXT-035' : ['ERR', 'Source file: [<<1>>] not found! Cannot copy to project. Process halting now.'],
            'TEXT-040' : ['WRN', 'The [<<1>>] component type is locked and cannot have any text modifications done to any files of this type at this time.'],
            'TEXT-045' : ['WRN', 'The [<<1>>] component is locked and cannot have any text modifications done to it at this time.'],
            'TEXT-050' : ['LOG', 'Working text file for [<<1>>] has been completed.'],
            'TEXT-055' : ['ERR', 'TEXT-055 - Unassigned error message ID.'],
            'TEXT-060' : ['MSG', 'Completed installation on [<<1>>] component working text.'],
            'TEXT-070' : ['ERR', 'Unable to copy [<<1>>] to [<<2>>] - error in text.'],
            'TEXT-080' : ['LOG', 'Validating text using the [<<1>>] style file.'],
            'TEXT-090' : ['ERR', 'Text validation failed on USFM file: [<<1>>] It reported this error: [<<2>>]'],
            'TEXT-100' : ['LOG', 'Normalizing Unicode text to the [<<1>>] form..'],
            'TEXT-150' : ['MSG', 'USFM file: [<<1>>] is valid.'],
            'TEXT-155' : ['ERR', 'USFM file: [<<1>>] did NOT pass the validation test.'],
            'TEXT-160' : ['ERR', 'Unable to complete working text installation for [<<1>>]. May require \"force\" (-f).'],

            'FONT-000' : ['MSG', 'Font module messages'],
            'FONT-005' : ['MSG', 'FONT-005 - Unassigned error message ID.'],
            'FONT-010' : ['LOG', 'Wrote out new font configuration (font.__init__())'],
            'FONT-015' : ['MSG', 'FONT-015 - Unassigned error message ID.'],
            'FONT-020' : ['ERR', 'Failed to find font setting in ParaTExt project (.ssf file). A primary font must be set before this component can be successfully rendered.'],
            'FONT-025' : ['ERR', 'No source editor was found for this project. Please enter this setting before continuing.'],
            'FONT-030' : ['ERR', 'Font [<<1>>] is already the primary font for the [<<2>>] component type.'],
            'FONT-032' : ['MSG', 'Force switch was set (-f). Forced font [<<1>>] to be the primary font for the [<<2>>] component type.'],
            'FONT-035' : ['MSG', 'The primary font for component type [<<1>>] has been set to [<<2>>]'],
            'FONT-037' : ['MSG', 'The font [<<1>>] is already set for component type [<<2>>]. Use -f to force change it to another font.'],
            'FONT-040' : ['ERR', 'Font bundle file [<<1>>] not found. Process halted. (font.checkForSubFont() or recordFont)'],
            'FONT-041' : ['ERR', 'Font bundle [<<1>>] not found. Process halted. (font.checkForSubFont())'],
            'FONT-042' : ['MSG', 'Force switch was set (-f). [<<1>>] font setup information was force added to project config'],
            'FONT-045' : ['LOG', '<<1>> font setup information added to project config'],
            'FONT-047' : ['LOG', 'The [<<1>>] font already has a listing in the configuration.'],
            'FONT-050' : ['ERR', 'Halt! [<<1>>] not found. - font.copyInFont()'],
            'FONT-060' : ['MSG', 'Force switch was set (-f). The <<1>> font bundle has been force copied into the project font folder. - font.installFont()'],
            'FONT-062' : ['LOG', 'The <<1>> font bundle already exsits in the font folder. - font.installFont()'],
            'FONT-065' : ['ERR', 'Failed to extract the [<<1>>] font bundle into the project. Font install process failed. - font.installFont()'],
            'FONT-067' : ['MSG', 'The <<1>> font bundle has been copied into the project font folder. - font.installFont()'],
            'FONT-070' : ['LOG', 'Copied the [<<1>>] font file into the project. - font.copyInFont()'],
            'FONT-080' : ['MSG', 'Removed the [<<1>>] font from the [<<2>>] component type settings. - font.removeFont()'],
            'FONT-082' : ['MSG', 'Force switch was set (-f). This process has completely removed the [<<1>>] font and settings from the project. - font.removeFont()'],
            'FONT-085' : ['ERR', 'Could not remove! The [<<1>>] font was not listed in the [<<2>>] component type settings. - font.removeFont()'],
            'FONT-090' : ['WRN', 'No replacement for primary font found.  - font.removeFont()'],
            'FONT-100' : ['ERR', 'This function has not been implemented yet!.  - font.setGlyphMap()'],
            'FONT-110' : ['ERR', 'This editor: [<<1>>] is not recognized by the system. System halted.  - font.varifyFont()'],
            'FONT-120' : ['ERR', 'Font bundle file [<<1>>] not found. Process halted. (font.copyInFont())'],
            'FONT-130' : ['MSG', 'Font [<<1>>] has been (or was already) installed into the project.'],

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
            'STYL-005' : ['ERR', 'Component type [<<1>>] is not supported by the style manager.'],
            'STYL-007' : ['ERR', 'The [<<1>>] component type source text editor [<<2>>] is not supported by the style manager.'],
            'STYL-010' : ['MSG', 'The style file [<<1>>] was set as the [<<2>>] style file for the [<<3>>] component type.'],
            'STYL-020' : ['ERR', 'Style file: [<<1>>] was not found. Operation failed.'],
            'STYL-030' : ['WRN', 'Style file: [<<1>>] already exsits. Use (-f) force to replace it.'],
            'STYL-060' : ['LOG', 'The file [<<1>>] was validated and copied to the project styles folder.'],
            'STYL-065' : ['LOG', 'The file [<<1>>] was copied to the project styles folder.'],
            'STYL-070' : ['ERR', 'Style file: [<<1>>] is not valid. Copy operation failed!'],
            'STYL-075' : ['LOG', 'Style file: [<<1>>] is not valid. Will attempt to find a valid one from another source.'],
            'STYL-090' : ['LOG', 'Style file: [<<1>>] was not found.'],
            'STYL-100' : ['LOG', 'No style file setting was found for the [<<1>>] component type. Nothing has been done.'],
            'STYL-110' : ['MSG', 'Force switch was set (-f). Style file: [<<1>>] was removed from the project and references removed from the [<<2>>] settings.'],
            'STYL-120' : ['MSG', 'Style file: [<<1>>] was removed from the [<<2>>] settings.'],
            'STYL-150' : ['MSG', 'Style file: [<<1>>] is valid.'],
            'STYL-155' : ['ERR', 'Style file: [<<1>>] did NOT pass the validation test.'],

            'PREP-000' : ['MSG', 'Messages for preprocessing issues (mainly found in project.py)'],
            'PREP-010' : ['ERR', 'The component type specified [<<1>>] is not found. Process halting! - project.runPreprocess()'],
            'PREP-020' : ['ERR', 'Could not run preprocess, file not found: [<<1>>].'],
            'PREP-030' : ['ERR', 'The component type [<<1>>] is locked and cannot be processed.'],
            'PREP-040' : ['ERR', 'The component [<<1>>] is locked and cannot be processed.'],
            'PREP-050' : ['MSG', 'Preprocesses completed successfully on: [<<1>>].'],
            'PREP-055' : ['LOG', 'No preprocesses registered for this component type [<<1>>].'],
            'PREP-060' : ['ERR', 'Preprocesses did not completed successfully on: [<<1>>], This is the error reported: [<<2>>]. If there is a log for this process script, check it for details.'],
            'PREP-070' : ['ERR', 'Preprocesses script: [<<1>>] was called on the component: [<<2>>] but the script was not found in the project.'],
            'PREP-075' : ['TDO', 'Use the command: [rpm process <project ID> <component type> -a ] to install a default starter scritp. Use the -s <script name> option to import a custom preprocessing script.'],
            'PREP-080' : ['ERR', 'A file named [<<1>>] is already registered as the preprocess script for this component type. Please use -f (force) to remove it if you want to install a fresh or different script.'],
            'PREP-081' : ['ERR', 'This script is already registered as the preprocess script for this component type. Please use -f (force) to reinstall a fresh or different script.'],
            'PREP-082' : ['ERR', 'The script file: [<<1>>] already exsists in the Scripts folder. Cannot copy over old file. Please use -f (force) to remove it if you want to install a fresh or different file.'],
            'PREP-085' : ['ERR', 'Source script not found: [<<1>>]'],
            'PREP-090' : ['LOG', 'Copied in custom preprocess file: [<<1>>] into Scripts folder.'],
            'PREP-100' : ['LOG', 'The contents of the file [<<1>>] have been extracted into the Scripts folder.'],
            'PREP-105' : ['ERR', 'The contents of the file [<<1>>] failed to be extracted into the Scripts folder. Install custom preprocessing script failed.'],
            'PREP-110' : ['MSG', 'Preprocessing script: [<<1>>] has been installed into the Scripts folder and should be ready for use.'],
            'PREP-115' : ['MSG', 'Force switch was set (-f). Preprocessing script: [<<1>>] has been installed into the Scripts folder and should be ready for use.'],
            'PREP-120' : ['MSG', 'Copied in default preprocess file: [<<1>>] into Scripts folder from source: [<<2>>].'],
            'PREP-130' : ['MSG', 'Removed [<<1>>] script reference from the [<<2>>] component type.'],
            'PREP-135' : ['MSG', 'There was no preprocess script for comonent type [<<1>>] found in the project configuration.'],

            'POST-000' : ['MSG', 'Messages for post processing issues (mainly found in project.py)'],
            'POST-010' : ['ERR', 'The component type specified [<<1>>] is not found. Process halting! - project.runPreprocess()'],
            'POST-050' : ['MSG', 'Post processes completed successfully.'],
            'POST-055' : ['MSG', 'No post processes registered for this component type [<<1>>].'],
            'POST-060' : ['ERR', 'Post processes did not completed successfully. This is the error reported: [<<1>>]. If there is a log for this process script, please check it for details.'],
            'POST-070' : ['ERR', 'Post processes script: [<<1>>] was called but the script was not found in the project.'],
            'POST-075' : ['TDO', 'Use the command: [rpm process <project ID> <component type> -a ] to install a default starter scritp. Use the -s <script name> option to import a custom post processing script.'],
            'POST-080' : ['ERR', 'A file named [<<1>>] is already registered as the post process script for this component type. Please use -f (force) to install a fresh copy.'],
            'POST-082' : ['ERR', 'The script file: [<<1>>] already exsists in the Scripts folder. Cannot copy over old file. Please use -f (force) to remove it if you want to install a fresh copy.'],
            'POST-085' : ['ERR', 'Source script not found: [<<1>>]'],
            'POST-090' : ['LOG', 'Copied in custom post process file: [<<1>>] into Scripts folder.'],
            'POST-110' : ['MSG', 'Post processing script: [<<1>>] has been installed into the Scripts folder and should be ready for use.'],
            'POST-115' : ['MSG', 'Force switch was set (-f). Post processing script: [<<1>>] has been installed into the Scripts folder and should be ready for use.'],
            'POST-120' : ['LOG', 'Copied in default post process file: [<<1>>] into Scripts folder from source: [<<2>>].'],
            'POST-130' : ['MSG', 'Removed [<<1>>] script reference from the [<<2>>] component type.'],
            'POST-135' : ['MSG', 'There was no post process script for comonent type [<<1>>] found in the project configuration.'],

            'LOCK-000' : ['MSG', 'Messages for project and component locking.'],
            'LOCK-010' : ['LOG', 'The [<<1>>] component is not found in this project.'],
            'LOCK-020' : ['LOG', 'The lock setting on the [<<1>>] component group has been set to [<<2>>]. Each of the individual components in the group are set to [<<2>>] as well.'],
            'LOCK-030' : ['LOG', 'The lock setting on the [<<1>>] component has been set to [<<2>>].'],

            'LOCK-058' : ['MSG', 'The [<<1>>] component has been locked. No further text processes can be run on it unless it is unlocked (-u).'],
            'LOCK-068' : ['MSG', 'The [<<1>>] component has been unlocked. This component can be processed.'],

            'SETG-000' : ['MSG', 'Messages for setting issues (probably only in project.py)'],
            'SETG-005' : ['MSG', 'SETG-005 - Unassigned error message ID.'],
            'SETG-010' : ['MSG', 'SETG-010 - Unassigned error message ID.'],
            'SETG-015' : ['MSG', 'SETG-015 - Unassigned error message ID.'],
            'SETG-020' : ['MSG', 'SETG-020 - Unassigned error message ID.'],
            'SETG-025' : ['MSG', 'SETG-025 - Unassigned error message ID.'],
            'SETG-030' : ['MSG', 'SETG-030 - Unassigned error message ID.'],
            'SETG-035' : ['MSG', 'SETG-035 - Unassigned error message ID.'],
            'SETG-040' : ['MSG', 'SETG-040 - Unassigned error message ID.'],

            'XPRT-000' : ['MSG', 'Messages for export issues (probably only in project.py)'],
            'XPRT-005' : ['MSG', 'Unassigned error message ID.'],
            'XPRT-010' : ['ERR', 'Export file name could not be formed with available configuration information.'],
            'XPRT-020' : ['ERR', 'Unable to export: [<<1>>].'],
            'XPRT-030' : ['MSG', 'Files exported to [<<1>>].'],
            'XPRT-040' : ['MSG', 'Begining export, please wait...'],
            'XPRT-050' : ['MSG', 'Unassigned error message ID.'],

            'EXMP-000' : ['MSG', 'Messages for running example projects.'],
            'EXMP-005' : ['MSG', 'Unassigned error message ID.'],
            'EXMP-010' : ['MSG', 'Finished running basic project example.'],
            'EXMP-030' : ['MSG', 'Finished running custom project example.'],
            'EXMP-020' : ['MSG', 'Unassigned error message ID.'],

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



