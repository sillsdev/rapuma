#!/bin/sh

# NOTE: This script is desined to work on the Linux operating system (Ubuntu 12.04).

##### Book of James Basic Project Example #####
# This example Rapuma project is the most basic set of commands needed to create output
# with the Rapuma publishing system. Using the commands in this script, this will create
# an example project on your system and create a rough draft of the Book of James. A basic
# explanation of how it works is explained in the comments that precede each command.

# Fetch and unpack the raw data for this project
# These are not Rapuma commands, just basic terminal commands. Be sure that your system
# is setup to work with these commands or edit the following lines to reflect your system's
# folder configuration. Otherwise, this script will not work.
mkdir ~/Publishing/testArea
cp resource/example/MBJAS.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/MBJAS.zip -d ~/Publishing/testArea
rm -rf ~/Publishing/testArea/ENG-LATN-JAS

# This first Rapuma command is for deleting any previous copies of this example project
# on your system. It will first backup project data, then remove the current working copy.
echo    rapuma project ENG-LATN-JAS project remove --force
        rapuma project ENG-LATN-JAS project remove --force

# This command creates a new project. It defines the type, name and location of the project.
# Currently Rapuma only supports the "book" media type but the architecture, in theory, could
# support a wide variety of outputs like phone, web, tablet, etc.
echo    rapuma project ENG-LATN-JAS project add --media_type book --target_path ~/Publishing/testArea
        rapuma project ENG-LATN-JAS project add --media_type book --target_path ~/Publishing/testArea

# This is where actual content is added to the project in the form of a group that contains components.
# The "james" group is a "usfm" type and contains one component, "jas" (the book of James marked up
# in USFM) The source ID helps Rapuma know what to call its unique source and the source path tells
# Rapuma where to find it.
echo    rapuma group ENG-LATN-JAS mb group add --component_type usfm --cid_list jas --source_id mb --source_path ~/Publishing/testArea/MBJAS/sources/mb
        rapuma group ENG-LATN-JAS mb group add --component_type usfm --cid_list jas --source_id mb --source_path ~/Publishing/testArea/MBJAS/sources/mb

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


