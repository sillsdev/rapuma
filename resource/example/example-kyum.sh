#!/bin/sh

##### Rapuma KYUM Test/Example Script #####

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
#   ~/Publishing/my_source/KYUM
#
# You may wish to locate it in a different place on your system. Be sure
# that is reflected in the commands of the rest of the exercises for
# this example. Now find the resource/example/KYUM.zip file in the Rapuma
# program folder and copy it to your newly created sources folder.
# Extract the contents which is in the KYUM folder into the my_source
# folder. Once this is done you should be ready to work through the rest
# of this example script.


## ADDING A PROJECT
# This next command creates a new project in the Rapuma project folder. 
# After this command is run there will be a new project folder created
# named "KYU-MYMR-KYUMTEST" in the main project folder.

rapuma project KYU-MYMR-KYUMTEST project add


## PROJECT REMOVAL
# This Rapuma command is for deleting any previous copies of this 
# example project on your system. Be careful when using this command
# as this action cannot be undone. This command permanently removes the
# project and its contents. Any work done on it will be lost when a
# command like this is run:
#
#   rapuma project KYU-MYMR-KYUMTEST project remove
#
# Note that this would be the same as selecting the project folder in
# your file browser and deleting it.


## ADDING STANDARD GROUPS
# A group is the container used to hold components that are rendered
# into the publication. A standard group is one of three pre-defined
# component containers. They are, OT, NT and BIBLE. Using one of these
# three group designators will allow Rapuma to auto-create a group
# which will contain all the components necessary for that group
# Note that for this test project we will only be using the NT group.
# Sadly, the OT texts do not exist yet for the KYU language.
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
#   rapuma group KYU-MYMR-KYUMTEST NT group add --source_path ~/Publishing/my_source/KYUM
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
#   rapuma group KYU-MYMR-KYUMTEST GOSPEL group add --cid_list "mat mrk luk jhn" --source_path ~/Publishing/my_source/KYUM
#
# This group (GOSPEL) will contain the component books, Matthew, Mark,
# Luke and John and nothing else.
#
# For this example we'll create a NT by adding this group to the project
# with this command:

rapuma group KYU-MYMR-KYUMTEST NT group add --source_path ~/Publishing/my_source/KYUM


## ADDING DOCUMENT FEATURES
# There are a number of features that can be added to a document to help
# in the typesetting process. These are controled by settings found in
# the configuration files found in the project Config folder. Project
# settings can be changed manualy with a text editor. Or, with "settings"
# a special Rapuma command included for this purpose. The settings command
# has four parameters, they are configuration, section, key, and value.
# The command would be constructed like this:
#
#   rapuma settings KYU-MYMR-KYUMTEST <configuration> <section> <key> <value>
#

# A helpful parameter setting for this project would be this:

rapuma settings KYU-MYMR-KYUMTEST usfmTex TeXBehavior vFuzz 4.8pt

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
#   rapuma group KYU-MYMR-KYUMTEST NT group render
#
# Rapuma, by default uses an internal version of XeTeX to render. If that
# isn't working for whatever reason, there is a way to fall back to a
# system-installed version of XeTeX. To switch to the external version
# could use this command:

rapuma settings KYU-MYMR-KYUMTEST project Managers/usfm_Xetex runExternalXetex True 

# For this part of example, we are going to just render one component
# from the NT group, the Book of James with this command:

rapuma group KYU-MYMR-KYUMTEST NT group render --cid_list jas

# You will note that the rendering came out very bad as the output is
# pretty much all little square boxes. This brings us to working with
# fonts.


## SETTING UP FONTS
# Currently, setting up fonts in Rapuma is a little tedious and unstable.
# For this example, without going into detail, we will use the existing
# mechanism to import the appropreat font into the project.

# First import the font with this command:
rapuma package KYU-MYMR-KYUMTEST NT Padauk_2.701 font add
# Be sure the font is set to be the primary project font
rapuma package KYU-MYMR-KYUMTEST NT Padauk_2.701 font primary --force

# Now for some magic commands to make things look nicer
# First, turn on Graphite rendering
rapuma settings KYU-MYMR-KYUMTEST usfmTex FontSettings useRenderingSystem GR
# Set the language the font will be using to Kayah
rapuma settings KYU-MYMR-KYUMTEST usfmTex FontSettings useLanguage kyu
# Map numbers found in the text to the Burmese form
rapuma settings KYU-MYMR-KYUMTEST usfmTex FontSettings useMapping kye_renumber
# Set the font scale size
rapuma settings KYU-MYMR-KYUMTEST usfmTex FontSettings fontSizeUnit 0.82
# Increase the line space factor (leading)
rapuma settings KYU-MYMR-KYUMTEST usfmTex FontSettings lineSpacingFactor 1.3


## ADVANCED FORMAT COMMANDS
# Here we can add some commands for adding illustrations and other
# format issue solutions


## ADVANCED RENDERING COMMANDS

# To save the Book of James file you would add the --save switch to
# the command:

rapuma group KYU-MYMR-KYUMTEST NT group render --cid_list jas --save

# Now you will note that a folder has been created called Deliverable
# and in is a file named: KYU-MYMR-KYUMTEST_NT_060-jas_20140812.pdf
# Actually, the last number will be different as it is tied to the 
# current date but it will be something like the above name.
#
# The name given to the rendered file is created by the Rapuma system
# and follows a default format. In some situations it maybe necessary
# to give the newly rendered file a specific name. This can be done by
# using the --override command during rendering. The --override command
# would be followed by the path and file name indicating to Rapuma
# where the file should be delivered and what it should be named.
# For example, this command, like above, would render James, name the
# file James.pdf and put it in the root of the project and view it:

rapuma group KYU-MYMR-KYUMTEST NT group render --cid_list jas --save --override ~/Publishing/KYU-MYMR-KYUMTEST/James.pdf

# [Note that the path needs to reflect your specific system.]
# One other render feature that is worth noting is Rapuma ability to
# just produce a document with specific pages. For this we would add the
# --pages command like this:

rapuma group KYU-MYMR-KYUMTEST NT group render --cid_list jhn --save --override ~/Publishing/KYU-MYMR-KYUMTEST/John-test.pdf --pages 15-20

# If you run that command you will see pages 15 through 20 from the
# Gospel of John found in the root of your example project.


## SETTING UP BACKGROUND OUTPUT
# Rapuma supports 3 different types of backgrounds: cropmarks, watermark
# and pagebox. The cropmarks show the trim size of the paper. The lines
# background will show where the text aligns to help with design and
# the paging process. The watermark will put a message in gray in the
# background of the page to prevent premature use of the document for
# publication. Finally, the pagebox background will place a box around
# the edge of the page to mark the trim size of the page.
#
# Two of the three backgrounds listed here can be added to the rendered
# with this command:

rapuma settings KYU-MYMR-KYUMTEST layout DocumentFeatures backgroundComponents watermark,cropmarks

# Note that the background list has no spaces in it. This is necessary
# because we are using the CLI for transmitting the command.

# The watermark text default is DRAFT. It can be changed with this
# command:

rapuma settings KYU-MYMR-KYUMTEST layout DocumentFeatures watermarkText PROOF

# If any changes are made to the background settings, the background file
# needs to be remade so the next time Rapuma is run the results will be
# as expected. To recreate the background file use this command:

rapuma project KYU-MYMR-KYUMTEST project update --update_type background

# To output the background when you render, add --background (or -b) to
# the render command like this:

rapuma group KYU-MYMR-KYUMTEST NT group render --cid_list 1ti --background

# When using backgrounds you can add information to the header and footer
# of the background. To use this feature add the --doc_info command to
# your command like this:

rapuma group KYU-MYMR-KYUMTEST NT group render --cid_list 2ti --background --doc_info

# By default no text is assigned. To add some information text a command
# like this could be used:

rapuma settings KYU-MYMR-KYUMTEST layout DocumentFeatures docInfoText "Doc info text"

# Rapuma has some aids to help with formating new publications. They are
# called diagnostics. Currently, there is only one but more can be added.
# To check the leading of the body text the "leading" diagnostic aid can
# be added by using this command:

rapuma group KYU-MYMR-KYUMTEST NT group render --cid_list heb --diagnostic

# Note that you cannot use --background (and/or --doc_info) with
# --diagnostic at the same time. That will cause an error


## USING THE BIND COMMAND
# As there is currently only one group in this particular example, this
# this will not be covered at this time. For more information on binding
# please refer to the KJV example.
