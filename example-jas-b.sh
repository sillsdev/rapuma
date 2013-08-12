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
cp ~/Projects/rapuma/resource/example/MBJAS.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/MBJAS.zip -d ~/Publishing/testArea
rm -rf ~/Publishing/testArea/ENG-LATN-JAS

# This first Rapuma command is for deleting any previous copies of this example project
# on your system. It will first backup project data, then remove the current working copy.
rapuma project ENG-LATN-JAS project remove

# Restore the backup with the following command. Rapuma will expect to find a backup file
# named ENG-LATN-JAS.zip in the source path specified.
rapuma project ENG-LATN-JAS backup restore --source_path ~/Publishing/testArea/MBJAS --target_path ~/Publishing/testArea

# Link up the project with its source. This change is made directly to the Rapuma system
# configuration file and will prevent warnings from being given on other operations.
rapuma settings ENG-LATN-JAS rapuma Projects/ENG-LATN-JAS mb_sourcePath ~/Publishing/testArea/MBJAS

# With the project restored, you can now run the "final" command. This will create a PDF
# that should be identical to the one found in the Deliverable folder which was made on
# another system.
rapuma group ENG-LATN-JAS james group final

