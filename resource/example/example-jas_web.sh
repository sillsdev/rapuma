#!/bin/sh

# NOTE: This script is desined to work on the Linux operating system (Ubuntu 12.04).
# Additionally, it is designed to work within the Rapuma Web environment cause output
# to go in its default location under /var/lib/rapuma/work

##### Book of James Basic Project Example #####
# This example Rapuma project is the most basic set of commands needed to create output
# with the Rapuma publishing system. Using the commands in this script, this will create
# an example project on your system and create a rough draft of the Book of James. A basic
# explanation of how it works is explained in the comments that precede each command.

# Fetch and unpack the raw data for this project
# There needs to be several things in place for this script to work. To follow are basic
# terminal commands to copy necessary data for the script to work:
#   cp ~/Projects/rapuma/resource/example/MBJAS.zip /var/lib/rapuma/work
#   unzip -o /var/lib/rapuma/work/MBJAS.zip -d /var/lib/rapuma/work

# This first Rapuma command is for deleting any previous copies of this example project
# on your system. It will first backup project data, then remove the current working copy.
echo    rapuma project ENG-LATN-JAS project remove
        rapuma project ENG-LATN-JAS project remove

# This command creates a new project. It defines the type, name and location of the project.
# Currently Rapuma only supports the "book" media type but the architecture, in theory, could
# support a wide variety of outputs like phone, web, tablet, etc.
echo    rapuma project ENG-LATN-JAS project add --media_type book --name "The Book of James in English" --target_path /var/lib/rapuma/work
        rapuma project ENG-LATN-JAS project add --media_type book --name "The Book of James in English" --target_path /var/lib/rapuma/work

# This is where actual content is added to the project in the form of a group that contains components.
# The "james" group is a "usfm" type and contains one component, "jas" (the book of James marked up
# in USFM) The source ID helps Rapuma know what to call its unique source and the source path tells
# Rapuma where to find it.
echo    rapuma group ENG-LATN-JAS mb group add --component_type usfm --cid_list jas --source_id mb --source_path /var/lib/rapuma/work/MBJAS/sources/mb
        rapuma group ENG-LATN-JAS mb group add --component_type usfm --cid_list jas --source_id mb --source_path /var/lib/rapuma/work/MBJAS/sources/mb

# With simple projects such as this, we can now render the text. The "draft" command will set in
# motion a process that will perform a number of tasks in this project such as import the default
# font and macro package as well as create some default settings files.
echo    rapuma group ENG-LATN-JAS mb group draft -o /var/lib/rapuma/work
        rapuma group ENG-LATN-JAS mb group draft -o /var/lib/rapuma/work

