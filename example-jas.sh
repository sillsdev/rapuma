#!/bin/sh

##### Book of James Project Example #####
# This example Rapuma project is the most basic set of commands needed to create output
# with the Rapuma publishing system. This will create an example project on your system
# and create a rough draft of the Book of James. A basic explanation of how it works is
# explained in the following steps

# Fetch and unpack the raw data for this project
# These are not Rapuma commands, just basic terminal commands. Be sure that your system
# is setup to work with these commands or edit the following lines to reflect your system's
# folder configuration. Otherwise, this script will not work.
cp ~/Projects/rapuma/resource/example/MBJAS.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/MBJAS.zip -d ~/Publishing/testArea

# This first Rapuma command is for deleting any previous copies of this example project
# on your system. It will first backup project data, then remove the current working copy.
rapuma project ENG-LATN-JAS project remove

# This command creates a new project. It defines the type, name and location of the project.
# Currently Rapuma only supports the "book" media type but the architecture, in theory, could
# support a wide variety of outputs like phone, web, tablet, etc.
rapuma project ENG-LATN-JAS project add --media_type book --name "The Book of James in English" --target_path ~/Publishing/testArea

# This is where actual content is added to the project in the form of a group that contains components.
# The "james" group is a "usfm" type and contains one component, "jas" (the book of James marked up
# in USFM) The source ID helps Rapuma know what to call its unique source and the source path tells
# Rapuma where to find it.
rapuma group ENG-LATN-JAS james group add --component_type usfm --cid_list jas --source_id mb --source_path ~/Publishing/testArea/MBJAS

# With simple projects such as this, we can now render the text. The "draft" command will set in
# motion a process that will perform a number of tasks in this project such as import the default
# font and macro package as well as create some default settings files.
rapuma group ENG-LATN-JAS james group draft

