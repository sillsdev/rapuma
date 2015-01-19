#!/bin/sh

##### Rapuma KJV Test/Example Script #####

# This script will both test the Rapuma publishing system and give a
# user an example of how the Rapuma CLI works for some basic commands.
# Before using this script, be sure you have a properly set up system
# according to the "installme" instructions found in the Rapuma doc
# folder.

# NOTE: This script is desined to work with Rapuma version v0.7.202 or
# higher and on the Linux operating system, Ubuntu 14.04 or higher.


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
# this example. Now find the resource/example/KJV folder in the Rapuma
# project folder and copy all the contents to your newly created sources
# folder, then extract the compressed files so they are ready to be
# accessed.


## ADDING A PROJECT
# This next command creates a new project in the Rapuma project folder. 
# After this command is run there will be a new project folder created
# named "ENG-LATN-KJVTEST" in the main project folder.

rapuma publication ENG-LATN-KJVTEST project create


## PROJECT REMOVAL
# This Rapuma command is for deleting any previous copies of this 
# example project on your system. Be careful when using this command
# as this action cannot be undone. This command permanently removes the
# project and its contents. Any work done on it will be lost when a
# command like this is run:
#
#   rapuma publication ENG-LATN-KJVTEST project remove
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
#   rapuma contents ENG-LATN-KJVTEST NT group add --comp_type usfm
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
# For this example we'll create a full Bible by adding these two groups
# to the project with these commands:

rapuma group ENG-LATN-KJVTEST NT group add --source_path ~/Publishing/my_source/KJV
rapuma group ENG-LATN-KJVTEST OT group add --source_path ~/Publishing/my_source/KJV

# If changes are made to a component, that component will need to be 
# re-updated or re-imported into the project. This is an example of a
# command that will do that:

#   rapuma group ENG-LATN-KJVTEST NT group update --cid_list jhn --source_path ~/Publishing/my_source/KJV

# If the entire group needs to be updated, then just leave out the
# --cid_list parameter. Then all the group components will be updated.


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

# A helpful parameter setting for this project would be this:

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
# Rapuma, by default uses an internal version of XeTeX to render. If that
# isn't working for whatever reason, there is a way to fall back to a
# system-installed version of XeTeX. To switch to the external version
# could use this command:

rapuma settings ENG-LATN-KJVTEST project Managers/usfm_Xetex runExternalXetex True 

# For this part of example, we are going to just render one component
# from the NT group, the Book of James with this command:

rapuma group ENG-LATN-KJVTEST NT group render --cid_list jas

# To save the Book of James file you would add the --save switch to
# the command:

rapuma group ENG-LATN-KJVTEST NT group render --cid_list jas --save

# Now you will note that a folder has been created called Deliverable
# and in is a file named: ENG-LATN-KJVTEST_NT_060-jas_20140812.pdf
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

rapuma group ENG-LATN-KJVTEST NT group render --cid_list jas --save --override ~/Publishing/ENG-LATN-KJVTEST/James.pdf

# [Note that the path needs to reflect your specific system.]
# One other render feature that is worth noting is Rapuma ability to
# just produce a document with specific pages. For this we would add the
# --pages command like this:

rapuma group ENG-LATN-KJVTEST NT group render --cid_list jhn --save --override ~/Publishing/ENG-LATN-KJVTEST/John-test.pdf --pages 15-20

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

rapuma settings ENG-LATN-KJVTEST layout DocumentFeatures backgroundComponents watermark,cropmarks

# Note that the background list has no spaces in it. This is necessary
# because we are using the CLI for transmitting the command.

# The watermark text default is DRAFT. It can be changed with this
# command:

rapuma settings ENG-LATN-KJVTEST layout DocumentFeatures watermarkText PROOF

# If any changes are made to the background settings, the background file
# needs to be remade so the next time Rapuma is run the results will be
# as expected. To recreate the background file use this command:

rapuma project ENG-LATN-KJVTEST project update --update_type background

# To output the background when you render, add --background (or -b) to
# the render command like this:

rapuma group ENG-LATN-KJVTEST NT group render --cid_list 1ti --background

# When using backgrounds you can add information to the header and footer
# of the background. To use this feature add the --doc_info command to
# your command like this:

rapuma group ENG-LATN-KJVTEST NT group render --cid_list 2ti --background --doc_info

# By default no text is assigned. To add some information text a command
# like this could be used:

rapuma settings ENG-LATN-KJVTEST layout DocumentFeatures docInfoText "Doc info text"

# Rapuma has some aids to help with formating new publications. They are
# called diagnostics. Currently, there is only one but more can be added.
# To check the leading of the body text the "leading" diagnostic aid can
# be added by using this command:

rapuma group ENG-LATN-KJVTEST NT group render --cid_list heb --diagnostic

# Note that you cannot use --background (and/or --doc_info) with
# --diagnostic at the same time. That will cause an error


## ADDING HYPHENATION TO A PROJECT
# Because XeTeX has hyphenation capabilities, Rapuma projects have a
# place for the necessary files to be which will allow hyphenation in
# XeTeX to work. To be sure hyphenation will work properly, two files
# must be present (copied into) the component group folder that is
# being rendered. For this exersize two files have been prepared for
# use. They can be found in the resources folder. Copy the
# kjv-hyphenation.tex and kjv-lccode.tex files to the project's NT group
# folder which is in the Component folder. Rename them to NT-hyphenation.tex
# and NT-lccode.tex. After this has been done you should be able to run
# this render command and see some results:

rapuma group ENG-LATN-KJVTEST NT group render --cid_list jhn --hyphenation

# Because the hyphenation example we use is very simple, we only render
# the Book of John for this example so results can be easily seen. Please
# refer the notes in the NT-hyphenation.tex file in the project for more
# information on how it all works and how to see the results.


## USING THE BIND COMMAND
# The composition process in Rapuma is a render, adjust repeat cycle.
# Once every component (book) in all the groups has gone through the
# composition process, binding is the next process. Before the bind
# command can be used, the groups should be rendered all together with
# these commands:

rapuma group ENG-LATN-KJVTEST OT group render
rapuma group ENG-LATN-KJVTEST NT group render

# After that is run, if you look at the page number at the begining of
# Matthew in the NT group, you will notice that it starts with number 1.
# As we move into the binding process, page numbers become important.
# After the groups have been rendered the first time, you will need to
# adjust the starting page number on the NT group (as it will follow OT
# group). This command (adjust the pg. no. if necessary) will do it:

rapuma settings ENG-LATN-KJVTEST project Groups/NT startPageNumber 1079

# Now rerun the NT group to adjust the page numbers. There is no need
# to rerun the OT group.

rapuma group ENG-LATN-KJVTEST NT group render

# The bind process merges the rendered group PDF files into one. However,
# Rapuma needs to know what order the files need to be merged together.
# In this case the setting commands would be:

rapuma settings ENG-LATN-KJVTEST project Groups/OT bindingOrder 1
rapuma settings ENG-LATN-KJVTEST project Groups/NT bindingOrder 2

# With these settings made Binding should now be possible. Use a command
# like this to preform a bind operation:

rapuma project ENG-LATN-KJVTEST project bind

# This gives you a temporary view-version of the publication. If you
# want to save it to the Deliverable folder, like the render command,
# add the --save (or -s) switch. At that point you will need to rerun
# the bind command. Note you can also use the --background and 
# --doc_info switches to add these to the output. But you cannot use
# the --diagnostic command in the bind mode.

# Please note that because of the underlying process, binding can take
# a lot of time compared to rendering, 3 to 5 minutes for a whole Bible.
# Do not interupt the process while it is running.
