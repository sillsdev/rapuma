#!/bin/sh

##### Rapuma KYUM Test/Example Script #####

# This script will both test the Rapuma publishing system and give a
# user an example of how the Rapuma CLI works for some basic commands.
# It can be run from the command line for testing but for learning
# the CLI, it is best to use this script as a tutorial and take it one
# line at a time, evaluating the results as each command is run.
#
# Before using this script, be sure you have a properly set up system
# according to the "installme" instructions found in the Rapuma doc
# folder.

# NOTE: This script is desined to work with Rapuma version v0.7.202 or
# higher and on the Linux operating system, Ubuntu 14.04 or higher.


## ENVIRONMENT SETUP
# First, setup the test environment. Rapuma publishing systems have
# a specified project folder. For this example we will assume the name
# of that folder is "Publishing". Create a folder in the Publishing
# folder that will contain the source files we will be drawing from.
# We will call it "my_source" for the purpose of this exercise. If you
# want, you can use this command to create it:

#   mkdir -p ~/Publishing/my_source/KYUM

# If you may wish to locate it in a different place on your system. Be
# sure that is reflected in the commands of the rest of the exercises for
# this example. Now find the resource/example/KYUM folder in the Rapuma
# project folder and copy all the contents to your newly created sources
# folder, then extract the compressed files so they are ready to be
# accessed.



# Set up assets folder instructions




#
# Once this is done you should be ready to work through the rest
# of this example script.


## CREATING A PROJECT
# This next command creates a new project in the Rapuma project folder. 
# After this command is run there will be a new project folder created
# named "KYU-MYMR-KYUMTEST" in the main project folder.

rapuma publication KYU-MYMR-KYUMTEST project create


## PROJECT REMOVAL
# This Rapuma command is for deleting any previous copies of this 
# example project on your system. Be careful when using this command
# as this action cannot be undone. This command permanently removes the
# project and its contents. Any work done will be lost when it is run.
#
#   rapuma publication KYU-MYMR-KYUMTEST project remove
#
# Note that this would be the same as selecting the project folder in
# your file browser and deleting it.


## ADDING GROUPS AND COMPONENTS
# A group is the container used to hold components that are rendered
# to become part of the content of the publication. All the components
# in a group must be of the same type. Component types cannot be mixed
# in a group. To create our first group, use this command:

rapuma content KYU-MYMR-KYUMTEST GOSPEL group add --comp_type usfm

# That command created an empty group called GOSPEL which will contain
# USFM file components after we run this command:

rapuma content KYU-MYMR-KYUMTEST GOSPEL component add --cid_list "mat luk jhn" --path ~/Publishing/my_source/KYUM

# The first four books of the NT have now been imported into the project
# and you can find them in the Component folder. Often it becomes necessary
# to update files as changes might have to be made to the source. For
# example, if an illustration had to be added to the source of the Book
# of John, it would be necessary to update it with this command:

rapuma content KYU-MYMR-KYUMTEST GOSPEL component update --cid_list jhn --path ~/Publishing/my_source/KYUM

# Components can be added to a group after the initial import process.
# You would use the same "add" command as above, only adjust the
# --cid_list parameter to add the component you need. To remove a
# component, you would use the "remove" command. Next in our example,
# we will add the Book of Acts and Mark to the GOSPEL group, then remove
# Acts as it was a pretend mistake.

rapuma content KYU-MYMR-KYUMTEST GOSPEL component add --cid_list "act mrk" --path ~/Publishing/my_source/KYUM
rapuma content KYU-MYMR-KYUMTEST GOSPEL component remove --cid_list act


## ASSET MANAGEMENT
# Assets are parts of a project but are not treated like the source.
# For this example, we will work with Font and Illustration assets. First
# we will bring in the font we need for this project with these commands:

rapuma asset KYU-MYMR-KYUMTEST GOSPEL font add --file_name Padauk_2.701.zip --path ~/Publishing/my_source/assets --primary
rapuma asset KYU-MYMR-KYUMTEST GOSPEL font remove --file_name "Charis SIL_4.106.zip"

# 
# During import, if it is present in the source text, Rapuma has gathered
# metadata for illustrations used in the publication. For this example,
# we will just use some Bash to copy them to the right location in the
# project.

mkdir -p ~/Publishing/KYU-MYMR-KYUMTEST/Illustration
cp ~/Publishing/my_source/KYUM/kyum-illustrations/* ~/Publishing/KYU-MYMR-KYUMTEST/Illustration


###########################################################################

# Stopping here for now

# REM: rapuma setting KYU-MYMR-KYUMTEST usfmTex --section TeXBehavior --key vFuzz --value 4.6pt


#REM: rapuma process KYU-MYMR-KYUMTEST component render GOSPEL --cid_list mat



#A standard group is one of three pre-defined
## component containers. They are, OT, NT and BIBLE. Using one of these
## three group designators will allow Rapuma to auto-create a group
## which will contain all the components necessary for that group
## Note that for this test project we will only be using the NT group.
## Sadly, the OT texts do not exist yet for the KYU language.
## 
## At this point the project is started but there are no groups in it 
## and no components to render. This next command is where actual
## content is added to the project in the form of groups which contain


## This needs to be rewritten. Components are not added when groups are made!



## components. The group components have to have valid IDs recognized
## by Paratext. Custom component IDs are not recognized. The actuall
## group ID, however, can be anything. These three IDs have speical
## meaning to the system, they are OT, NT, and BIBLE. These IDs enable
## Rapuma to auto-create these groups without having to specify the
## components. OT is for the Old Testament (GEN-MAL). NT is for New
## Testament (MAT-REV). BIBLE is the normal connoical collection of
## books (GEN-REV). To create one of these groups a command formed like
## the following can be used:
## 
##   rapuma content KYU-MYMR-KYUMTEST NT group add --comp_type
##
## With this command Rapuma will search the files in "my_source" and
## look for SFM or USFM extention files and check to see if any have the
## ID of a component needed for the NT group (MAT-REV). When it finds a
## file with an ID that is defined for the NT group, Rapuma imports the
## text into the project. If an ID is not found during the process, that
## component will be skipped. If two IDs around found for the same
## component, the first one it finds will be used. (If you have two
## valid files with the same ID Rapuma can't help you sort that out.)
##
## If you want to create a custom sub-group...
##
##   rapuma group KYU-MYMR-KYUMTEST GOSPEL group add --cid_list "mat mrk luk jhn" --source_path ~/Publishing/my_source/KYUM
##
## This group (GOSPEL) will contain the component books, Matthew, Mark,
## Luke and John and nothing else.
##
## For this example we'll create a NT by adding this group to the project
## with this command:

#rapuma group KYU-MYMR-KYUMTEST NT group add --source_path ~/Publishing/my_source/KYUM

## If changes are made to a component, that component will need to be 
## re-updated or re-imported into the project. This is an example of a
## command that will do that:

##   rapuma group KYU-MYMR-KYUMTEST NT group update --cid_list jhn --source_path ~/Publishing/my_source/KYUM

## If the entire group needs to be updated, then just leave out the
## --cid_list parameter. Then all the group components will be updated.


### ADDING DOCUMENT FEATURES
## There are a number of features that can be added to a document to help
## in the typesetting process. These are controled by settings found in
## the configuration files found in the project Config folder. Project
## settings can be changed manualy with a text editor. Or, with "settings"
## a special Rapuma command included for this purpose. The settings command
## has four parameters, they are configuration, section, key, and value.
## The command would be constructed like this:
##
##   rapuma settings KYU-MYMR-KYUMTEST <configuration> <section> <key> <value>
##

## A helpful parameter setting for this project would be this:

#rapuma settings KYU-MYMR-KYUMTEST usfmTex TeXBehavior vFuzz 4.8pt

## Note that any Rapuma setting, project or system, can be changed with
## the settings command as long as the four parameters are valid. One
## drawback is you have to know exactly what the parameters are, and what
## they do. In the CLI interface does not provide a good explanation for
## configuration paramters at this time. (Though that would be a good
## thing to add!) Because of this it is often necessary to open a
## configuration file in an editor to discover what you need to know.
## If that is the case, you can just make the changes directly.


### RENDERING PROJECT COMPONENTS
## With more complex projects there would be more setup to do. With this
## simple one we can move on to rendering. To render the entire NT group
## we created above, we would use a command like this:
##
##   rapuma group KYU-MYMR-KYUMTEST NT group render
##
## Rapuma, by default uses an internal version of XeTeX to render. If that
## isn't working for whatever reason, there is a way to fall back to a
## system-installed version of XeTeX. To switch to the external version
## could use this command:

#rapuma settings KYU-MYMR-KYUMTEST project Managers/usfm_Xetex runExternalXetex True 

## For this part of example, we are going to just render one component
## from the NT group, the Book of James with this command:

#rapuma group KYU-MYMR-KYUMTEST NT group render --cid_list jas

## You will note that the rendering came out very bad as the output is
## pretty much all little square boxes. This brings us to working with
## fonts.


### SETTING UP FONTS
## Currently, setting up fonts in Rapuma is a little tedious and unstable.
## For this example, without going into detail, we will use the existing
## mechanism to import the appropreat font into this project.

## First import the font with this command:
#rapuma package KYU-MYMR-KYUMTEST NT Padauk_2.701 font add
## Be sure the font is set to be the primary project font
#rapuma package KYU-MYMR-KYUMTEST NT Padauk_2.701 font primary --force

## Now for some magic commands to make things look nicer
## First, turn on Graphite rendering
#rapuma settings KYU-MYMR-KYUMTEST usfmTex FontSettings useRenderingSystem GR
## Set the language the font will be using to Kayah
#rapuma settings KYU-MYMR-KYUMTEST usfmTex FontSettings useLanguage kyu
## Map numbers found in the text to the Burmese form
#rapuma settings KYU-MYMR-KYUMTEST usfmTex FontSettings useMapping kye_renumber
## Set the font scale size
#rapuma settings KYU-MYMR-KYUMTEST usfmTex FontSettings fontSizeUnit 0.82
## Increase the line space factor (leading)
#rapuma settings KYU-MYMR-KYUMTEST usfmTex FontSettings lineSpacingFactor 1.3


### ADVANCED FORMAT COMMANDS
## Here we can add some commands for adding illustrations and other
## format issue solutions


### ADVANCED RENDERING COMMANDS

## To save the Book of James file you would add the --save switch to
## the command:

#rapuma group KYU-MYMR-KYUMTEST NT group render --cid_list jas --save

## Now you will note that a folder has been created called Deliverable
## and in is a file named: KYU-MYMR-KYUMTEST_NT_060-jas_20140812.pdf
## Actually, the last number will be different as it is tied to the 
## current date but it will be something like the above name.
##
## The name given to the rendered file is created by the Rapuma system
## and follows a default format. In some situations it maybe necessary
## to give the newly rendered file a specific name. This can be done by
## using the --override command during rendering. The --override command
## would be followed by the path and file name indicating to Rapuma
## where the file should be delivered and what it should be named.
## For example, this command, like above, would render James, name the
## file James.pdf and put it in the root of the project and view it:

#rapuma group KYU-MYMR-KYUMTEST NT group render --cid_list jas --save --override ~/Publishing/KYU-MYMR-KYUMTEST/James.pdf

## [Note that the path needs to reflect your specific system.]
## One other render feature that is worth noting is Rapuma ability to
## just produce a document with specific pages. For this we would add the
## --pages command like this:

#rapuma group KYU-MYMR-KYUMTEST NT group render --cid_list jhn --save --override ~/Publishing/KYU-MYMR-KYUMTEST/John-test.pdf --pages 15-20

## If you run that command you will see pages 15 through 20 from the
## Gospel of John found in the root of your example project.


### SETTING UP BACKGROUND OUTPUT
## Rapuma supports 3 different types of backgrounds: cropmarks, watermark
## and pagebox. The cropmarks show the trim size of the paper. The lines
## background will show where the text aligns to help with design and
## the paging process. The watermark will put a message in gray in the
## background of the page to prevent premature use of the document for
## publication. Finally, the pagebox background will place a box around
## the edge of the page to mark the trim size of the page.
##
## Two of the three backgrounds listed here can be added to the rendered
## with this command:

#rapuma settings KYU-MYMR-KYUMTEST layout DocumentFeatures backgroundComponents watermark,cropmarks

## Note that the background list has no spaces in it. This is necessary
## because we are using the CLI for transmitting the command.

## The watermark text default is DRAFT. It can be changed with this
## command:

#rapuma settings KYU-MYMR-KYUMTEST layout DocumentFeatures watermarkText PROOF

## If any changes are made to the background settings, the background file
## needs to be remade so the next time Rapuma is run the results will be
## as expected. To recreate the background file use this command:

#rapuma project KYU-MYMR-KYUMTEST project update --update_type background

## To output the background when you render, add --background (or -b) to
## the render command like this:

#rapuma group KYU-MYMR-KYUMTEST NT group render --cid_list 1ti --background

## When using backgrounds you can add information to the header and footer
## of the background. To use this feature add the --doc_info command to
## your command like this:

#rapuma group KYU-MYMR-KYUMTEST NT group render --cid_list 2ti --background --doc_info

## By default no text is assigned. To add some information text a command
## like this could be used:

#rapuma settings KYU-MYMR-KYUMTEST layout DocumentFeatures docInfoText "Doc info text"

## Rapuma has some aids to help with formating new publications. They are
## called diagnostics. Currently, there is only one but more can be added.
## To check the leading of the body text the "leading" diagnostic aid can
## be added by using this command:

#rapuma group KYU-MYMR-KYUMTEST NT group render --cid_list heb --diagnostic

## Note that you cannot use --background (and/or --doc_info) with
## --diagnostic at the same time. That will cause an error


### USING THE BIND COMMAND
## As there is currently only one group in this particular example, this
## this will not be covered at this time. For more information on binding
## please refer to the KJV example.


### WORKING WITH ILLUSTRATIONS
## Scripture publications often need illustrations. Rapuma can work with
## basic illustration placement in the running text. A number of things
## need to happen for successful illustration useage. First, \fig markers
## need to be found in the source text. If they are not in the original,
## there is no foundational information to work with for placing the
## illustrations. With valid \fig markers in the source text, Rapuma will
## create/populate the illustration.conf file when the source text is
## imported into the project. Once the import is completed you will see
## that the illustration.conf file now contains entries for six
## illustrations that are used in the Book of John. (For this example we
## limit illustrations to just that book.)
##
## Next we need to bring our illustration files into the project. One way
## way is to just copy them into the project Illustration folder. They
## can be found in my_source/KYUM_Illustrations. Copy the six png files
## there to KYU-MYMR-KYUMTEST/Illustration folder.
## 
## With the illustration files in place, at this point we need to
## "turn on" illustrations with this command:
##
##   rapuma settings KYU-MYMR-KYUMTEST project Groups/NT useIllustrations True
##
## When you render now, The illustrations will be placed but you will only
## see a box representing where the image is supposed to go. These boxes
## are called figure place holders. This is set this way by default to
## allow for faster rendering during composition. To be able to view
## illustrations in the rendered output use this command:
##
##   rapuma settings KYU-MYMR-KYUMTEST layout DocumentFeatures useFigurePlaceHolders False
##
## More than likely the illustrations will not be in the correct place
## and adjustments will be needed. The placement settings are found in
## the illustration.conf file. There are a number of settings that can
## help adjust the placement and size of the illustrations. For example,
## in the book of John, which was just rendered, on page 5, the illustration
## which is to go with chapter 2, verse 6 is in the upper left corner
## and it should be in the lower right. This command will change it:
##
##   rapuma settings KYU-MYMR-KYUMTEST illustration NT/lb00135 position br
##
## This is just one of the many adjustments that can be made to an
## illustration.

