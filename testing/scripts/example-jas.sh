#!/bin/sh

# NOTE: This script is desined to work on the Linux operating system 
# (Ubuntu 12.04).

##### Book of James Basic Project Example #####
# This example Rapuma project is the most basic set of commands needed
# to create output with the Rapuma publishing system. Using the 
# commands in this script, this will create an example project on your
# system and create a rough draft of the Book of James. A basic 
# explanation of how it works is explained in the comments that 
# precede each command.

# Fetch and unpack the raw data for this project These are not Rapuma 
# commands, just basic terminal commands. Be sure that your system is 
# setup to work with these commands or edit the following lines to 
# reflect your system's folder configuration. Otherwise, this script 
# will not work.
mkdir ~/Publishing/testArea
cp resource/example/MBJAS.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/MBJAS.zip -d ~/Publishing/testArea
rm -rf ~/Publishing/testArea/ENG-LATN-JAS

# This first Rapuma command is for deleting any previous copies of 
# this example project on your system. It does not have to be run the 
# first time. Be careful as this step cannot be undone. This command 
# permanently removes the project.
echo    rapuma project ENG-LATN-JAS project remove
        rapuma project ENG-LATN-JAS project remove

# This command creates a new project in the Rapuma project folder. 
# Currently Rapuma only supports the "book" media type but the 
# architecture, in theory, could support a wide variety of outputs 
# like phone, web, tablet, etc. Rapuma will default to book-type media
# so it is not necessary to use that designator.
echo    rapuma project ENG-LATN-JAS project add
        rapuma project ENG-LATN-JAS project add

# This is where actual content is added to the project in the form of a
# group that contains components. The group designator for this project
# is "mb" and the component type is assumed to be "usfm" but if not, it
# can be specified with --component_type. The --source_list option
# contains a valid path and file name to the book of James, the only
# component for this group. if more books were desired to be in this
# group they would be listed in quotes separated by spaces. Note, it is
# not wise to use spaces in file names. (sorry) The use of --force (-f)
# for this command will cause it to overwrite any existing data for this
# group. Otherwise a warning will be given and the process will stop.

echo    rapuma group ENG-LATN-JAS mb group add --source_list ~/Publishing/testArea/MBJAS/sources/mb/jas.usfm
        rapuma group ENG-LATN-JAS mb group add --source_list "~/Publishing/testArea/MBJAS/sources/mb/jas.usfm ~/Publishing/testArea/MBJAS/sources/mb/41MATBRUvu1.SFM"

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


