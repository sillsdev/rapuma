#!/bin/sh

##### Rapuma ScriptureForge Test/Example Script (Part 2) #####

# This is the second in a series of example scripts that help test
# and demonstrate Rapuma running in the ScriptureForge environment.

# NOTE: This script is desined to work with Rapuma version v0.7.202 or
# higher and on the Linux operating system, Ubuntu 14.04 or higher.


## PROJECT SETUP
# This part of this series of example scripts shows how to setup a
# basic project, add groups and components. It assumes that the
# instructions have been followed from the previous script, sf-example_1.sh.
# That being the case, run these commands:

# Create a project
rapuma project SFTEST project add

# Add a group named FOURTEES and add four usfm type components to it
rapuma group SFTEST FOURTEES group add --cid_list "1th 2th 1ti 2ti" --source_path ~/Publishing/my_source/KYUM

# Add a second group named GOSPEL and add four usfm type components
rapuma group SFTEST GOSPEL group add --cid_list "mat mrk luk jhn" --source_path ~/Publishing/my_source/KYUM

# In the next script we will work with project assets
