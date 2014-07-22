#!/bin/sh

# Rapuma KJV Test/Example Script

# This script will both test the Rapuma publishing system and give a
# user an example of how the Rapuma CLI works for some basic commands.
# Before using this script, be sure you have a properly set up system
# according to the "installme" instructions found in the Rapuma doc
# folder.

# NOTE: This script is desined to work with Rapuma version v0.7.011 or
# higher and on the Linux operating system, Ubuntu 12.04 or higher.

## SETUP
# First, setup the test environment. Rapuma publishing systems have
# a specified project folder. Create a folder there that will contain
# the source files we will be drawing from. We will call it "sources"
# for the purpose of this exercise. Find the testing/sources/KJV.zip file
# in the Rapuma program folder and copy it to your newly created sources
# folder. Extract the contents there. Once this is done you should be
# ready to work through the rest of this example script.

## PROJECT REMOVAL
# This first Rapuma command is for deleting any previous copies of 
# this example project on your system. It does not have to be run the 
# first time. Be careful as this step cannot be undone. This command 
# permanently removes the project and its contents. Any work done on
# the project will be lost when this command is run. 
echo    rapuma project ENG-LATN-KJVTEST project remove
        rapuma project ENG-LATN-KJVTEST project remove

## ADDING A PROJECT
# This next command creates a new project in the Rapuma project folder. 
# After this command is run there will be a new project folder created
# named "ENG-LATN-KJVTEST" in the main project folder.
echo    rapuma project ENG-LATN-KJVTEST project add
        rapuma project ENG-LATN-KJVTEST project add

## ADDING COMPONENTS
# At this point the project is started but there are no components 
# in it. This next command is where actual content is added to the 
# project in the form of components. The group components have to 
# have valid IDs recognized by Paratext. Custom component IDs are 
# not recognized. The actuall group ID, however, can be anything. 
# Three IDs have some speical meaning to the system, however. They 
# are OT, NT, and BIBLE. These IDs enable Rapuma to auto-create 
# these groups without having to specify the components. OT is for 
# the Old Testament (GEN-MAL). NT is for New Testament (MAT-REV). 
# BIBLE is the normal connoical collection of books (GEN-REV). To 
# create one of these groups a command formed like the following can 
# be used:
# 
#   rapuma group ENG-LATN-KJV NT group add --source_path ~/my_source
#
# With this command Rapuma will search the files in "my_source" and
# look for SFM or USFM extention files and check to see if any have the
# ID of a component needed for the NT group (MAT-REV). When it finds a
# file with an ID that is defined for the NT group, Rapuma imports the
# text into the project. If an ID is not found during the process, that
# component will be skipped. If two IDs around found for the same
# component, the first one it finds will be used. (If you have two
# valid files with the same ID Rapuma can't help you sort that out.)
#
# If you want to create a custom group...
#
#   rapuma group ENG-LATN-KJV GOSPEL group add --cid_list "mat mrk luk jhn" --source_path ~/my_source
#
# This group (GOSPEL) will contain the component books, Matthew, Mark,
# Luke and John and nothing else.
# For this example we'll create the full NT group with this command:

echo    rapuma group ENG-LATN-KJV NT group add --source_path ~/my_source
        rapuma group ENG-LATN-KJV NT group add --source_path ~/my_source






## RENDERING PROJECT COMPONENTS
# ...
# With simple projects such as this, we can now render the text. The "render" command will set in
# motion a process that will perform a number of tasks in this project such as import the default
# font and macro package as well as create some default settings files.
echo    rapuma group ENG-LATN-JAS mb group render
        rapuma group ENG-LATN-JAS mb group render

# The above command is for "view only". To save the file add the --force command. This
# will save the newly produced PDF file in the Deliverables folder.
echo    rapuma group ENG-LATN-JAS mb group render --force
        rapuma group ENG-LATN-JAS mb group render --force

# Another variation of the above command uses the --override command to save the output
# to a custom file name and location.
echo    rapuma group ENG-LATN-JAS mb group render --override ~/Publishing/testArea/ENG-LATN-JAS/mysillyname.pdf
        rapuma group ENG-LATN-JAS mb group render --override ~/Publishing/testArea/ENG-LATN-JAS/mysillyname.pdf


