#!/bin/sh

##### Rapuma ScriptureForge Test/Example Script (Part 1) #####

# This is the first in a series of example scripts that help test
# and demonstrate Rapuma running in the ScriptureForge environment.

# NOTE: This script is desined to work with Rapuma version v0.7.202 or
# higher and on the Linux operating system, Ubuntu 14.04 or higher.


## ENVIRONMENT SETUP
# The main purpose of this script is to setup the environment in which
# the example will be run. This example uses resources from the KYUM
# example found in the Rapuma project resource/example folder. If that
# has not been done the following directions will need to be followed:
#
# First, setup the test environment. Rapuma publishing systems have
# a specified project folder. Create a folder there that will contain
# the source files we will be drawing from. We will call it "my_source"
# for the purpose of this exercise and it will be located here:
#
#   ~/Publishing/my_source/KYUM
#
# You may wish to locate it in a different place on your system. Be sure
# that is reflected in the commands of the rest of the exercises for
# this example. Now find the resource/example/KYUM folder in the Rapuma
# project folder and copy all the contents to your newly created sources
# folder, then extract the compressed files so they are ready to be
# accessed.
#
# Next we need to copy our illustration files into the my_source folder.
# A zip file called KYUM-Illustrations.zip can be found in the Rapuma
# resource/example folder. Copy and extract that file in the 
# my_source/KYUM_Illustrations. Now we are about ready to start.

# But before we start, in case we need to clean out an old test, use
# this Rapuma command:
rapuma project SFTEST project remove

# Next run the sf-example_2.sh script
