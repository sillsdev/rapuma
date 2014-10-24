#!/bin/sh

##### Rapuma KJV Test/Example Script #####

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
# the source files we will be drawing from. We will call it "my_source"
# for the purpose of this exercise and it will be located here:
#
#   ~/Publishing/my_source/KJV
#
# You may wish to locate it in a different place on your system. Be sure
# that is reflected in the commands of the rest of the exercises for
# this example. Now find the testing/sources/KJV.zip file in the Rapuma
# program folder and copy it to your newly created sources folder.
# Extract the contents which is in the KJV folder into the my_source
# folder. Once this is done you should be ready to work through the rest
# of this example script.

## ADDING A PROJECT
# This next command creates a new project in the Rapuma project folder. 
# After this command is run there will be a new project folder created
# named "ENG-LATN-KJVTEST" in the main project folder.

rapuma project ENG-LATN-KJVTEST project add


## PROJECT REMOVAL
# This Rapuma command is for deleting any previous copies of this 
# example project on your system. Be careful when using this command
# as this action cannot be undone. This command permanently removes the
# project and its contents. Any work done on it will be lost when a
# command like this is run:
#
#   rapuma project ENG-LATN-KJVTEST project remove
#
# Note that this would be the same as selecting the project folder in
# your file browser and deleting it.


## ADDING STANDARD GROUPS
# A group is the container used to hold components that are rendered
# into the publication. A standard group is one of three pre-defined
# component containers. They are, OT, NT and BIBLE. Using one of these
# three group designators will allow Rapuma to auto-create a group
# which will contain all the components necessary for that group.
# 
# At this point the project is started but there are no groups in it 
# and no components to render. This next command is where actual
# content is added to the project in the form of groups which contain
# components. The group components have to have valid IDs recognized
# by Paratext. Custom component IDs are not recognized. The actuall
# group ID, however, can be anything. These three IDs have speical
# meaning to the system, they are OT, NT, and BIBLE. These IDs enable
# Rapuma to auto-create these groups without having to specify the
# components. OT is for the Old Testament (GEN-MAL). NT is for New
# Testament (MAT-REV). BIBLE is the normal connoical collection of
# books (GEN-REV). To create one of these groups a command formed like
# the following can be used:
# 
#   rapuma group ENG-LATN-KJVTEST NT group add --source_path ~/Publishing/my_source/KJV
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
# If you want to create a custom sub-group...
#
#   rapuma group ENG-LATN-KJVTEST GOSPEL group add --cid_list "mat mrk luk jhn" --source_path ~/Publishing/my_source/KJV
#
# This group (GOSPEL) will contain the component books, Matthew, Mark,
# Luke and John and nothing else.
#
# For this example we'll create the full NT group with this command:

rapuma group ENG-LATN-KJVTEST NT group add --source_path ~/Publishing/my_source/KJV


## ADDING CUSTOM GROUPS AND COMPONENTS
# As noted above, you can create a custom group to handle portions of
# content which are not in a standard order or contain components that
# are not Scripture, like front and back mater.
#
# In the case of front mater, the USFM standard allows the "frt" ID
# to be used to indicate components that are used in the front of the
# publication. There are several other official IDs used for these
# types of peripheral components. Consult the USFM manual for more
# information.
#
# Just like with standard groups, you would use a command such as this
# to create a custom group which contains all the front mater:

rapuma group MLF-THAI-NTREV FRONT group add -s ~/ParatextProjects/MLF -i "xxa xxb xxc"

# This adds a group to our publication that will contain all the front
# mater. The xxa, xxb and xxc are valid USFM IDs for components that
# can contain anything. In this case xxa is our title page, xxb is the
# verso page and xxc is the table of contents. Note, you could not use
# an ID like "toc" for the table of contents because "toc" is not a
# valid USFM component ID.

##### NOTE: Need more explanation added here #####

## ADDING DOCUMENT FEATURES
# There are a number of features that can be added to a document to help
# in the typesetting process. These are controled by settings found in
# the configuration files found in the project Config folder. Project
# settings can be changed manualy with a text editor. Or, with "settings"
# a special Rapuma command included for this purpose. The settings command
# has four parameters, they are configuration, section, key, and value.
# The command would be constructed like this:
#
#   rapuma settings ENG-LATN-KJVTEST <configuration> <section> <key> <value>
#
# For example, the background, by default, is turned on. It could be turned
# off with this command:

rapuma settings ENG-LATN-KJVTEST layout DocumentFeatures useBackground False

# An additional helpful parameter setting for this project would be this:

rapuma settings ENG-LATN-KJVTEST usfmTex TeXBehavior vFuzz 2.5pt

# Note that any Rapuma setting, project or system, can be changed with
# the settings command as long as the four parameters are valid. One
# drawback is you have to know exactly what the parameters are, and what
# they do. In the CLI interface does not provide a good explanation for
# configuration paramters at this time. (Though that would be a good
# thing to add!) Because of this it is often necessary to open a
# configuration file in an editor to discover what you need to know.
# If that is the case, you can just make the changes directly.


## RENDERING PROJECT COMPONENTS
# With more complex projects there would be more setup to do. With this
# simple one we can move on to rendering. To render the entire NT group
# we created above, we would use a command like this:
#
#   rapuma group ENG-LATN-KJVTEST NT group render
#
# However, for this example, we are going to just render one component
# out of the entire NT group, the Book of James. To do this, we would
# use this command:

rapuma group ENG-LATN-KJVTEST NT group render --cid_list jas

# You see that it has PROOF watermark background and the page is set on
# an A4 page. This is to make printing for proofing easier. However,
# the above command is for "view-only". To save the file add the --force
# command. This will save the newly produced PDF file in the Deliverable
# folder which will be added when the file is created. The Deliverable
# is where Rapuma stores specified rendered files and should never do
# any "clean-up" in that folder. To save the Book of James file you
# would run this command:

rapuma group ENG-LATN-KJVTEST NT group render --cid_list jas --force

# Now you will note that a folder has been created called Deliverable
# and in is a file named: ENG-LATN-KJVTEST_NT_060-jas_20140812.pdf
#
# The name given to the rendered file is created by the Rapuma system
# and follows a default format. In some situations it maybe necessary
# to give the newly rendered file a specific name. This can be done by
# using the --override command during rendering. The --override command
# would be followed by the path and file name indicating to Rapuma
# where the file should be delivered and what it should be named.
# For example, this command, like above, would render James, name the
# file James.pdf and put it in the root of the project and view it:

rapuma group ENG-LATN-KJVTEST NT group render --cid_list jas --force --override ~/Publishing/ENG-LATN-KJVTEST/James.pdf

# [Note that the path needs to reflect your specific system.]
# One other render feature that is worth noting is Rapuma ability to
# just produce a document with specific pages. For this we would add the
# --pages command like this:

rapuma group ENG-LATN-KJVTEST NT group render --cid_list jas --force --override ~/Publishing/ENG-LATN-KJVTEST/James.pdf --pages 2-3

# If you run that command you will see pages 2 and 3 from the Book of
# James found in the root of your example project.


## SETTING UP BACKGROUND OUTPUT
# There are several backgrounds that can be added to the document output.
# To turn on the background, use this command:

rapuma settings ENG-LATN-KJVTEST layout DocumentFeatures useBackground True

# Rapuma supports 4 different types of backgrounds, cropmarks, lines
# watermark and pagebox. The cropmarks show the trim size of the paper.
# The lines background will show where the text aligns to help with design
# and the paging process. The watermark will put a message in gray in the
# background of the page to prevent premature use of the document for
# publication. Finally, the pagebox background will place a box around
# the edge of the page to mark the trim size of the page.
#
# One of the four backgrounds listed here can be added to the rendered
# with this command:

rapuma settings ENG-LATN-KJVTEST layout DocumentFeatures backgroundComponents "watermark"

Watermark text can be changed with:
rapuma settings ENG-LATN-KJVTEST layout DocumentFeatures watermarkText PROOF


# We have a bug in Rapuma that will not allow us to update a setting
# with a list if items.



you can add doc info with
rapuma settings ENG-LATN-KJVTEST layout DocumentFeatures useDocInfo True
rapuma settings ENG-LATN-KJVTEST layout DocumentFeatures docInfoText "Doc info text"

change by command or edit layout.conf file

delete the background.pdf file in Illustration folder after change is made


*** Add feature to facilitate a checkbox to regenerate background on run "regenerateBackground = True" (default is True)



