#!/bin/sh

# For this to work the following path is needed: ~/Publishing/testArea

# Copy into the testArea folder and extract the files
cp ~/Projects/rapuma/resources/examples/KYUM.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/KYUM.zip -d ~/Publishing/testArea

# Remove any exsiting project of the same ID
rpm project KYU-MYMR-MRKA project remove

# Create the project
rpm project KYU-MYMR-MRKA project add --target_path ~/Publishing/testArea --media_type book --name 'Kayah Book of Mark example in the Burmese script'

# Install groups to render
rpm group KYU-MYMR-MRKA Mark group add --component_type usfm --cid_list mrk --source_id MYMR --source_path ~/Publishing/testArea/KYUM/pt_environ
rpm group KYU-MYMR-MRKA Intro group add --component_type usfm --cid_list int --source_id MYMR --source_path ~/Publishing/testArea/KYUM/pt_environ

# Turn on preprocessing for Mark group
rpm group KYU-MYMR-MRKA Mark preprocess add

# Turn on hyphenation for Mark group
rpm group KYU-MYMR-MRKA Mark hyphenation add

# Turn on font features in Padauk & adjust default settings
rpm settings KYU-MYMR-MRKA usfmTex Fonts useRenderingSystem GR
rpm settings KYU-MYMR-MRKA usfmTex Fonts useLanguage kyu
rpm settings KYU-MYMR-MRKA usfmTex Fonts useMapping kye_renumber
rpm settings KYU-MYMR-MRKA usfmTex Fonts fontSizeUnit 0.82pt
rpm settings KYU-MYMR-MRKA usfmTex Fonts lineSpacingFactor 1.3

# Adjust the publication format
rpm settings KYU-MYMR-MRKA layout PageLayout bodyColumns 2
rpm settings KYU-MYMR-MRKA usfmTex TeXBehavior vFuzz 4.8pt
rpm settings KYU-MYMR-MRKA usfmTex Illustrations useFigurePlaceHolders False
rpm settings KYU-MYMR-MRKA project Groups/Mark usePreprocessScript True
rpm settings KYU-MYMR-MRKA project Groups/Mark useIllustrations True
rpm settings KYU-MYMR-MRKA project Groups/Mark bindingOrder 2
rpm settings KYU-MYMR-MRKA project Groups/Intro bindingOrder 1

# Copy (system) some preset setting files into the project
echo copying: usfmTex-ext.tex
cp ~/Publishing/testArea/KYUM/resources/usfmTex-ext.tex ~/Publishing/testArea/KYU-MYMR-MRKA/Macros/usfmTex/usfmTex-ext.tex
echo copying: MYMR_textPreprocess.py
cp ~/Publishing/testArea/KYUM/resources/MYMR_textPreprocess.py ~/Publishing/testArea/KYU-MYMR-MRKA/Scripts/MYMR_textPreprocess.py
echo copying: usfmTex-ext.sty
cp ~/Publishing/testArea/KYUM/resources/usfmTex-ext.sty ~/Publishing/testArea/KYU-MYMR-MRKA/Macros/usfmTex/usfmTex-ext.sty

# Now update the text so the customized (edited) prprocess is used
rpm group KYU-MYMR-MRKA Mark group update --force

# Install and switch font (Padauk 2.95 has a bug)
rpm package KYU-MYMR-MRKA Mark Padauk_2.701 font add
rpm package KYU-MYMR-MRKA Mark Padauk_2.701 font primary --force

# Render the component
rpm group KYU-MYMR-MRKA Intro group draft
rpm group KYU-MYMR-MRKA Mark group proof
rpm project KYU-MYMR-MRKA project bind

# Backup the project
rpm project KYU-MYMR-MRKA backup save



