#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110823
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle system process commands.  This relys a lot on the
# optparse lib.  Documentation can be found here:
# http://docs.python.org/library/optparse.html

# History:
# 20110823 - djd - Started with intial file from RPM project


###############################################################################
################################# Command Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os
from optparse import OptionParser

# Load the local classes
from tools import *

commands = {}

class MetaCommand(type) :

    def __init__(cmd, namestring, t, d) :
        global commands
        super(MetaCommand, cmd).__init__(namestring, t, d)
        if cmd.type :
            commands[cmd.type] = cmd.__call__()


class Command (object) :
    '''The main command object class.'''

    __metaclass__ = MetaCommand
    type = None

    # Intitate the whole class
    def __init__(self) :
        self.parser = OptionParser(self.__doc__)
        self.setupOptions(self.parser)

    def run(self, args, aProject, userConfig) :
        if not aProject :
            pass
            # die with error
        (self.options, self.args) = self.parser.parse_args(args = args)
        
    def setupOptions(self, parser) :
        pass
        
    def help(self) :
        self.parser.print_help()


###############################################################################
########################### Command Classes Go Here ###########################
###############################################################################
# Insert the commands you want visable to the system here in the order you want
# them to appear when listed.


class About (Command) :
    '''Display the system's About text'''

    type = "system_about"

    def run(self, args) :
        super(About, self).run(args)
#        terminal(aProject._userConfig['System']['aboutText'])


class ChangeSettings (Command) :
    '''Change a system setting.'''

    type = "system_settings_change"

    def run(self, args, aProject, userConfig) :
        (self.options, self.args) = self.parser.parse_args(args = args)
        new = args[1]
        old = userConfig['System'][args[0][2:]]

        if new != old :
            userConfig['System'][args[0][2:]] = new
            terminal('Changed ' + args[0][2:] + ' from [' + old + '] to ' + new)
            userConfig['System']['writeOutUserConfFile'] = 'True'
        else :
            terminal('New setting is the same, no need to change.')

        return userConfig

    def setupOptions(self, parser) :
        self.parser.add_option("--userName", action="store", help="Change the system user name.")
        self.parser.add_option("--language", action="store", help="Change the interface language.")
        self.parser.add_option("--loglimit", action="store", help="Set the number of lines the log file is allowed to have.")


class Debugging (Command) :
    '''Turn on debugging (verbose output) in the logging.'''

    type = "system_debug"

    def run(self, args, aProject, userConfig) :
        super(Debugging, self).run(args, aProject, userConfig)
        if args[0][2:] == 'on' :
            aProject.changeSystemSetting("debugging", "True")

        if args[0][2:] == 'off' :
            aProject.changeSystemSetting("debugging", "False")

    def setupOptions(self, parser) :
        self.parser.add_option("--on", action="store_true", help="Turn on debugging for the log file output.")
        self.parser.add_option("--off", action="store_false", help="Turn off debugging for the log file output.")


class Help (Command) :
    '''Provide user with information on a specific command.'''

    type = "help"

    def run(self, args, aProject, userConfig) :
        global commands
        if len(args) :
            cmd = commands[args[0]]
            cmd.help()
        else :
            for c in commands.keys() :
                terminal(c)

            if len(commands) <= 2 :
                terminal("\nType [help command] for more general command information.")


class GUIManager (Command) :
    '''Start a RPM GUI manager program'''

    type = "manager"

    def run(self, args) :
        super(GUIManager, self).run(args)
        if args[1].lower() == 'standard' :
            terminal("Sorry, this GUI Manager has not been implemented yet.")
        elif args[1].lower() == 'web' :
            terminal("Sorry, the web client has not been implemented yet.")
        else :
            terminal("Not a recognized GUI Manager.")

    def setupOptions(self, parser) :
        self.parser.add_option("-c", "--client", action="store", type="string", help="Start up the RPM client.")


class CreateProject (Command) :
    '''Create a new project based on a predefined project type.'''

    type = "project_create"

    def help(self) :
        self.parser.print_help()

    def run(self, args, aProject, userConfig) :
        super(CreateProject, self).run(args, aProject, userConfig)
        
        # Check for "required" options
        if self.options.ptype and self.options.pname and self.options.pid :
            aProject.makeProject(self.options.ptype, self.options.pname, self.options.pid, self.options.pdir)
        else :
            terminal('Error: A command option is missing!')
            self.help()

    def setupOptions(self, parser) :
        self.parser.add_option("-t", "--ptype", action="store", help="Set the type of project this will be, this is required.")
        self.parser.add_option("-n", "--pname", action="store", help="Set the name of project this will be, this is required.")
        self.parser.add_option("-i", "--pid", action="store", help="Set the type of project this will be, this is required.")
        self.parser.add_option("-d", "--pdir", action="store", help="Directory to create this project in, the default is current directory.")


class RemoveProject (Command) :
    '''Remove an active project from the system and lock the working conf files.
    If no project ID is given the default is the project in the cwd.  If there
    is no project in the cwd it will fail.'''

    type = "project_remove"

    def run(self, args, aProject, userConfig) :
        super(RemoveProject, self).run(args, aProject, userConfig)
        if len(args) :
            aProject.removeProject(args[1])

    def setupOptions(self, parser) :
        self.parser.add_option("-i", "--pid", type="string", action="store", help="The ID code of the project to be removed. The default is the current working directory.")


class RestoreProject (Command) :
    '''Restores a project in the dir given. The default dir is cwd.'''

    type = 'project_restore'

    def run(self, args, aProject, userConfig) :
        super(RestoreProject, self).run(args, aProject, userConfig)

        aProject.restoreProject(args[1])

    def setupOptions(self, parser) :
        self.parser.add_option("-d", "--dir", type="string", action="store", help="Restore a project in this directory")



