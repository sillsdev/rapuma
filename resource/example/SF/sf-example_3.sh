#!/bin/sh

##### Rapuma ScriptureForge Test/Example Script (Part 3) #####

# This is the third in a series of example scripts that help test
# and demonstrate Rapuma running in the ScriptureForge environment.

# NOTE: This script is desined to work with Rapuma version v0.7.202 or
# higher and on the Linux operating system, Ubuntu 14.04 or higher.


## ASSETS MANAGEMENT
# This part of this series of example scripts shows how to manage
# assets for this test project.

# Rapuma has gathered metadata for illustrations used in the publication.
# The ScriptureForge publishing web interface will handle putting
# the actual illustration asset files in place. However, for this 
# example, we will just use a Bash command to copy them to the right
# location in the project
cp ~/Publishing/my_source/KYUM/kyum-illustrations/* ~/Publishing/SFTEST/Illustration

# These Rapuma commands will deal with font assets needed in the project
rapuma package SFTEST GOSPEL Padauk_2.701 font add
rapuma package SFTEST GOSPEL Padauk_2.701 font primary --force

# At this point the project is setup and the necessary assets have been
# added to the project. In the next example we will make changes to
# configuration files that will enable resonable rendering of the
# project components.
