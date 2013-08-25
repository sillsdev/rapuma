#!/bin/sh

# NOTE: This script is desined to work on the Linux operating system (Ubuntu 12.04).

##### Book of James Basic Project Example #####
# In this example, A simple Rapuma project (the basic book of James) will be restored from
# a backup of the project from another system. The purpose is to show how backups are normally
# restored. It should be noted that this backup was created with this command:

# rapuma project ENG-LATN-JAS backup save --target_path ~/Publishing/testArea

# (Do not run the above command)

# Fetch and put in place the backup of this project. These are not Rapuma commands,
# just basic terminal commands. Be sure that your system is setup to work with these
# commands or edit the following lines to reflect your system's folder configuration.
# Otherwise, this script will not work.
mkdir ~/Publishing/testArea
cp resource/example/MBJAS.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/MBJAS.zip -d ~/Publishing/testArea
rm -rf ~/Publishing/testArea/ENG-LATN-JAS

# This first Rapuma command is for deleting any previous copies of this example project
# on your system. It will first backup project data, then remove the current working copy.
echo rapuma project ENG-LATN-JAS project remove
rapuma project ENG-LATN-JAS project remove

# Create a new project based on the selected template
echo rpm project ENG-LATN-JAS template restore --source_path ~/Publishing/testArea/MBJAS --target_path ~/Publishing/testArea
rpm project ENG-LATN-JAS template restore --source_path ~/Publishing/testArea/MBJAS/eng-latn-tmpl.zip --target_path ~/Publishing/testArea

# Add a group with a component to the project.
echo rpm group ENG-LATN-JAS james group add --component_type usfm --cid_list jas --source_id mb --source_path ~/Publishing/testArea/MBJAS
rpm group ENG-LATN-JAS james group add --component_type usfm --cid_list jas --source_id mb --source_path ~/Publishing/testArea/MBJAS

# With the new project created, you can now run the "proof" command and render the group.
echo rapuma group ENG-LATN-JAS james group proof
rapuma group ENG-LATN-JAS james group proof

