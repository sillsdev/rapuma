#!/bin/sh

##### Rapuma ScriptureForge Test/Example Script #####

# This script will both test the Rapuma publishing system and provide
# a model for testing the ScriptureForge UI. The goal is to produce
# a PDF of the Book of John in the Kayah language, Burmese script.
# Note this script is for developer use only and may not be used in
# any public venue.

# NOTE: This script is desined to work with Rapuma version v0.7.011 or
# higher and on the Linux operating system, Ubuntu 12.04 or higher.


## SETUP
# This example uses resources from the KYUM example. If that example
# has been setup to be run on this system, these instructions maybe
# skipped. Otherwise...
#
# First, setup the test environment. Rapuma publishing systems have
# a specified project folder. Create a folder there that will contain
# the source files we will be drawing from. We will call it "my_source"
# for the purpose of this exercise and it will be located here:
#
#   ~/Publishing/my_source/KYUM
#
# You may wish to locate it in a different place on your system. Be sure
# that is reflected in the commands of the rest of the exercises for
# this example. Now find the resource/example/KYUM folder in the Rapuma
# project folder and copy all the contents to your newly created sources
# folder, then extract the compressed files so they are ready to be
# accessed.
#
# Next we need to bring our illustration files into the project. One way
# way is to just copy them into the project Illustration folder. They
# can be found in my_source/KYUM_Illustrations. However, the Illustration
# folder doesn't exist yet so to jumpstart the process we will run these
# commands:

# But before we do that, in case we need to clean out an old test, run this first:
rapuma project SFTEST project remove


# Once this is done you should be ready to work through the rest
# of this example script.

# Now this will all run on auto-pilot
rapuma project SFTEST project add
rapuma group SFTEST GOSPEL group add --cid_list "mat mrk luk jhn" --source_path ~/Publishing/my_source/KYUM

# Take a little break here to copy in the illustrations that were found in the Book of John
mkdir -p ~/Publishing/SFTEST/Illustration
cp ~/Publishing/my_source/KYUM/kyum-illustrations/* ~/Publishing/SFTEST/Illustration

# Resume Rapuma commands
rapuma group SFTEST FOURTEES group add --cid_list "1th 2th 1ti 2ti" --source_path ~/Publishing/my_source/KYUM
rapuma settings SFTEST usfmTex TeXBehavior vFuzz 4.8pt
rapuma settings SFTEST project Groups/GOSPEL useIllustrations True
rapuma settings SFTEST illustration GOSPEL/lb00135 position br
rapuma package SFTEST GOSPEL Padauk_2.701 font add
rapuma package SFTEST GOSPEL Padauk_2.701 font primary --force
rapuma settings SFTEST usfmTex FontSettings useRenderingSystem GR
rapuma settings SFTEST usfmTex FontSettings useLanguage kyu
rapuma settings SFTEST usfmTex FontSettings useMapping kye_renumber
rapuma settings SFTEST usfmTex FontSettings fontSizeUnit 0.82
rapuma settings SFTEST usfmTex FontSettings lineSpacingFactor 1.3
rapuma settings SFTEST layout DocumentFeatures backgroundComponents watermark,cropmarks
rapuma settings SFTEST layout DocumentFeatures watermarkText "SF Test"
rapuma settings SFTEST layout DocumentFeatures useFigurePlaceHolders False
rapuma settings SFTEST layout DocumentFeatures columnGutterRule True
rapuma settings SFTEST usfmTex Columns columnGutterFactor 20
rapuma settings SFTEST usfmTex Columns columnGutterRuleSkip 4
rapuma settings SFTEST usfmTex ChapterVerse useMarginalVerses True
rapuma settings SFTEST project Groups/GOSPEL bindingOrder 1
rapuma settings SFTEST project Groups/FOURTEES bindingOrder 2
rapuma project SFTEST project update --update_type background
rapuma settings SFTEST layout DocumentFeatures docInfoText "ScriptureForge Test Render"
rapuma group SFTEST GOSPEL group render
rapuma group SFTEST FOURTEES group render
rapuma project SFTEST project bind --background --doc_info --override ~/Publishing/SFTEST/FinalRender.pdf
