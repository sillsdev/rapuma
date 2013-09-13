#!/bin/sh

# NOTE: This script is desined to work on the Linux operating system (Ubuntu 12.04).

##### Book of James Template Project Example #####
# In this example, A simple Rapuma project, three versions of the book of James. The project
# will be created from a template of the project created on another system. The purpose is
# to show how templates work. It should be noted that this template was created with this
# command:

# rapuma project ENG-LATN-JAS template save --target_path ~/Publishing/testArea

# (No need to run the above command)

# Start the script by putting in place the backup of this project. These are not Rapuma
# commands, just basic terminal commands used to setup the environment we will be working
# with. Be sure that your system is setup to work with these commands or edit the following
# lines to reflect your system's folder configuration. Otherwise, this script will not work.
mkdir ~/Publishing/testArea
cp resource/example/MBJAS.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/MBJAS.zip -d ~/Publishing/testArea
rm -rf ~/Publishing/testArea/ENG-LATN-JAS

# This first Rapuma command is for deleting any previous copies of this example project
# on your system. It will first backup project data, then remove the current working copy.
echo    rapuma project ENG-LATN-JAS project remove
        rapuma project ENG-LATN-JAS project remove

# Create a new project based on the selected template
echo    rapuma project ENG-LATN-JAS template restore --source_path ~/Publishing/testArea/MBJAS/eng-latn-tmpl.zip --target_path ~/Publishing/testArea
        rapuma project ENG-LATN-JAS template restore --source_path ~/Publishing/testArea/MBJAS/eng-latn-tmpl.zip --target_path ~/Publishing/testArea

# Add groups to the project, each one with one or more components. The components can have
# the same name as used in other groups but need to come from separate sources which they
# are linked to.

# Add MB group with source text
echo    rapuma group ENG-LATN-JAS mb group add --component_type usfm --cid_list jas --source_id mb --source_path ~/Publishing/testArea/MBJAS/sources/mb
        rapuma group ENG-LATN-JAS mb group add --component_type usfm --cid_list jas --source_id mb --source_path ~/Publishing/testArea/MBJAS/sources/mb
# Add KJV group with source text
echo    rapuma group ENG-LATN-JAS kjv group add --component_type usfm --cid_list jas --source_id kjv --source_path ~/Publishing/testArea/MBJAS/sources/kjv
        rapuma group ENG-LATN-JAS kjv group add --component_type usfm --cid_list jas --source_id kjv --source_path ~/Publishing/testArea/MBJAS/sources/kjv
# Add KYU group with source text
echo    rapuma group ENG-LATN-JAS kyu group add --component_type usfm --cid_list jas --source_id kyu --source_path ~/Publishing/testArea/MBJAS/sources/kyu
        rapuma group ENG-LATN-JAS kyu group add --component_type usfm --cid_list jas --source_id kyu --source_path ~/Publishing/testArea/MBJAS/sources/kyu

# With the new project created, and groups added, you can now run the "proof" command
# and render each of the group.

# Render MB group
echo    rapuma group ENG-LATN-JAS mb group proof
        rapuma group ENG-LATN-JAS mb group proof
# Render KJV group
echo    rapuma group ENG-LATN-JAS kjv group proof
        rapuma group ENG-LATN-JAS kjv group proof
# Render KYU group
echo    rapuma group ENG-LATN-JAS kyu group proof
        rapuma group ENG-LATN-JAS kyu group proof

