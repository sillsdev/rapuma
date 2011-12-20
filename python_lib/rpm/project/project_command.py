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
        if self.options.ptype and self.options.pname and self.options.pid :
            aProject.makeProject(self.options.ptype, self.options.pname, self.options.pid, self.options.pdir)
        else :
            raise SyntaxError, "Error: Missing required options!"

    def setupOptions(self, parser) :
        self.parser.add_option("-t", "--ptype", action="store", help="Set the type of project this will be. (Required)")
        self.parser.add_option("-n", "--pname", action="store", help="Set the name of project this will be. (Required)")
        self.parser.add_option("-i", "--pid", action="store", help="Set the type of project this will be. (Required)")
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


class RenderProject (Command) :
    '''Renders the current project. With no group or component specified,
    the entire project is rendered.'''

    type = 'project_render'

    def run(self, args, aProject, userConfig) :
        super(RenderProject, self).run(args, aProject, userConfig)

        aProject.renderProject(self.options.comp)

    def setupOptions(self, parser) :
        self.parser.add_option("-c", "--comp", type="string", action="store", default='', help="Render the specified component.")


class AddComponent (Command) :
    '''Add a component to a project.'''

    type = "component_add"

    def run (self, args, aProject, userConfig) :
        super(AddComponent, self).run(args, aProject, userConfig)

        if self.options :
            aProject.addComponent(self.options.name, self.options.type)
        else :
            raise SyntaxError, "Error: Missing required arguments!"

    def setupOptions (self, parser) :
        self.parser.add_option("-n", "--name", type="string", action="store", default="contents", help="Give a name to this component group. (Required)")
        self.parser.add_option("-t", "--type", type="string", action="store", default="usfm", help="Assign the component markup type. Default is USFM.")


class RemoveComponent (Command) :
    '''Remove a component from a project.'''

    type = "component_remove"

    def run (self, args, aProject, userConfig) :
        super(RemoveComponent, self).run(args, aProject, userConfig)

        if self.options.component :
            aProject.removeComponent(self.options.component)
        else :
            raise SyntaxError, "Error: Missing required arguments!"

    def setupOptions (self, parser) :
        self.parser.add_option("-c", "--component", type="string", action="store", help="Remove a component from the project. (Required)")


class AddComponentManager (Command) :
    '''Add a manager to a component.'''

    type = "component_add-manager"

    def run (self, args, aProject, userConfig) :
        super(AddComponentManager, self).run(args, aProject, userConfig)

        if self.options :
            aProject.addComponentManager(self.options.comp, self.options.manager, self.options.mtype)
        else :
            raise SyntaxError, "Error: Missing required arguments!"

    def setupOptions (self, parser) :
        self.parser.add_option("-c", "--comp", type="string", action="store", help="List the component ID for this component. (Required)")
        self.parser.add_option("-m", "--manager", type="string", action="store", help="List the ID for the manager to be bound to this component.")
        self.parser.add_option("-t", "--mtype", type="string", action="store", help="List the type of this manager.")


class RenderComponent (Command) :
    '''Render a single component.'''

    type = "render_component"

    def run (self, args, aProject, userConfig) :
        super(RenderComponent, self).run(args, aProject, userConfig)
        if self.options :
            aProject.renderComponent(self.options.comp)
        else :
            raise SyntaxError, "Error: Missing required arguments!"

    def setupOptions (self, parser) :
        self.parser.add_option("-c", "--comp", type="string", action="store", help="Render this specific component. (Required)")



