#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111209
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project commands.  This relys a lot on the
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

class Command (object) :
    '''The main command object class.'''

#    __metaclass__ = MetaCommand
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


class CreateProject (Command) :
    '''Create a new project based on a predefined project type.'''

    type = "project_create"

    def help(self) :
        self.parser.print_help()

    def run(self, args, aProject, userConfig) :
        super(CreateProject, self).run(args, aProject, userConfig)
        
        # Check for "required" options
        if  self.options.pid and self.options.ptype :
            aProject.makeProject(self.options.pid, self.options.ptype, self.options.pdir, self.options.pname)
        else :
            raise SyntaxError, "Error: Missing required options!"

    def setupOptions(self, parser) :
        self.parser.add_option("-i", "--pid", type="string", action="store", help="Give the ID for this project. (Required)")
        self.parser.add_option("-t", "--ptype", type="string", action="store", help="Set the type of project this will be. (Required)")
        self.parser.add_option("-d", "--pdir", type="string", action="store", help="Directory to create this project in, the default is current directory.")
        self.parser.add_option("-n", "--pname", type="string", action="store", help="Set the name of project this will be.")


class RemoveProject (Command) :
    '''Remove an active project from the system and lock the working conf files.
    If no project ID is given the default is the project in the cwd.  If there
    is no project in the cwd it will fail.'''

    type = "project_remove"

    def run(self, args, aProject, userConfig) :
        super(RemoveProject, self).run(args, aProject, userConfig)

        if  self.options.pid :
            aProject.removeProject(self.options.pid)
        else :
            raise SyntaxError, "Error: Missing required arguments: -i (Project ID)"

    def setupOptions(self, parser) :
        self.parser.add_option("-i", "--pid", type="string", action="store", help="Give the ID for this project. (Required)")


class RestoreProject (Command) :
    '''Restores a project in the dir given. The default dir is cwd.'''

    type = 'project_restore'

    def run(self, args, aProject, userConfig) :
        super(RestoreProject, self).run(args, aProject, userConfig)

        if  self.options.pid and self.options.pdir :
            aProject.restoreProject(self.options.pid, self.options.pdir)
        else :
            raise SyntaxError, "Error: Missing required arguments: -i (Project ID)"

    def setupOptions(self, parser) :
        self.parser.add_option("-i", "--pid", type="string", action="store", help="Give the ID for this project. (Required)")
        self.parser.add_option("-d", "--pdir", type="string", action="store", help="Directory to restort this project in, the default is current directory.")


class RenderProject (Command) :
    '''Renders the current project. With no group or component specified,
    the entire project is rendered.'''

    type = 'project_render'

    def run(self, args, aProject, userConfig) :
        super(RenderProject, self).run(args, aProject, userConfig)

        if  self.options.pid :
            aProject.renderProject(self.options.pid)
        else :
            raise SyntaxError, "Error: Missing required arguments: -i (Project ID) & -c (Component)"

    def setupOptions(self, parser) :
        self.parser.add_option("-i", "--pid", type="string", action="store", help="Give the ID for this project. (Required)")


class AddComponent (Command) :
    '''Add a component to a project.'''

    type = "component_add"

    def run (self, args, aProject, userConfig) :
        super(AddComponent, self).run(args, aProject, userConfig)

        if self.options.pid and self.options.cid and self.options.type :
            aProject.addComponent(self.options.cid, self.options.type)
        else :
            raise SyntaxError, "Error: Missing required arguments!"

    def setupOptions (self, parser) :
        self.parser.add_option("-i", "--pid", type="string", action="store", help="Give the ID for this project. (Required)")
        self.parser.add_option("-c", "--cid", type="string", action="store", default="contents", help="Give a name to this component group. (Required)")
        self.parser.add_option("-t", "--type", type="string", action="store", default="usfm", help="Assign the component markup type. Default is USFM.")


class RemoveComponent (Command) :
    '''Remove a component from a project.'''

    type = "component_remove"

    def run (self, args, aProject, userConfig) :
        super(RemoveComponent, self).run(args, aProject, userConfig)

        if self.options.pid and self.options.cid :
            aProject.removeComponent(self.options.cid)
        else :
            raise SyntaxError, "Error: Missing required arguments!"

    def setupOptions (self, parser) :
        self.parser.add_option("-i", "--pid", type="string", action="store", help="Give the ID for this project. (Required)")
        self.parser.add_option("-c", "--cid", type="string", action="store", help="Remove a component from the project. (Required)")


class RenderComponent (Command) :
    '''Render a single component.'''

    type = "render_component"

    def run (self, args, aProject, userConfig) :
        super(RenderComponent, self).run(args, aProject, userConfig)
        if self.options.pid and self.options.cid :
            aProject.renderComponent(self.options.cid)
        else :
            raise SyntaxError, "Error: Missing required arguments!"

    def setupOptions (self, parser) :
        self.parser.add_option("-i", "--pid", type="string", action="store", help="Give the ID for this project. (Required)")
        self.parser.add_option("-c", "--cid", type="string", action="store", help="Render this specific component. (Required)")



