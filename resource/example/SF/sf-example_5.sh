#!/bin/sh

##### Rapuma ScriptureForge Test/Example Script (Part 5) #####

# This is the fifth in a series of example scripts that help test
# and demonstrate Rapuma running in the ScriptureForge environment.

# NOTE: This script is desined to work with Rapuma version v0.7.202 or
# higher and on the Linux operating system, Ubuntu 14.04 or higher.


## RENDERING AND BINDING THE PROJECT PUBLICATION
# This example builds off of the previous four and the goal is to render
# and bind the components in this project into what we will concider
# the final form, at least for this example.

# Render the two groups
rapuma group SFTEST GOSPEL group render
rapuma group SFTEST FOURTEES group render

# Bind the two groups into presentation form
rapuma project SFTEST project bind --background --doc_info --save
