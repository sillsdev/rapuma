#!/bin/sh

# For this to work the following path is needed: ~/Publishing/testArea

# Copy into the testArea folder and extract the files
cp ~/Projects/rapuma/resources/examples/KYUM.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/KYUM.zip -d ~/Publishing/testArea

# Remove any exsiting project of the same ID
rpm project KYU-MYMR-MRKA --manage remove-project

# Create the project
rpm project KYU-MYMR-MRKA --manage add-project --target_path ~/Publishing/testArea --media_type book --name 'Kayah Book of Mark example in the Burmese script'

# Install groups to render
rpm group KYU-MYMR-MRKA Mark --manage add-group --component_type usfm --cid_list mrk --source_id MYMR --source_path ~/Publishing/testArea/KYUM/pt_environ
rpm group KYU-MYMR-MRKA Intro --manage add-group --component_type usfm --cid_list int --source_id MYMR --source_path ~/Publishing/testArea/KYUM/pt_environ

## Set the font to the right one
#rpm font KYU-MYMR-MRKA Mark usfm Padauk --manage primary --force

## Turn on preprocessing for Mark group
#rpm group KYU-MYMR-MRKA Mark --preprocess add-preprocess

## Turn on font features in Padauk & adjust default settings
#rpm settings KYU-MYMR-MRKA project Managers/usfm_Font useRenderingSystem GR
#rpm settings KYU-MYMR-MRKA project Managers/usfm_Font useLanguage kyu
#rpm settings KYU-MYMR-MRKA project Managers/usfm_Font useMapping kye_renumber
#rpm settings KYU-MYMR-MRKA book_layout Fonts fontSizeUnit 0.82pt
#rpm settings KYU-MYMR-MRKA book_layout Fonts lineSpacingFactor 1.3

## Adjust the publication format
#rpm settings KYU-MYMR-MRKA book_layout Columns bodyColumns 2
#rpm settings KYU-MYMR-MRKA book_layout TeXBehavior vFuzz 4.8pt
#rpm settings KYU-MYMR-MRKA book_layout Illustrations useFigurePlaceHolders False
#rpm settings KYU-MYMR-MRKA project Groups/Mark usePreprocessScript True
#rpm settings KYU-MYMR-MRKA project Groups/Mark useIllustrations True

## Copy (system) some preset setting files into the project
#echo copying: extention.tex
#cp ~/Publishing/testArea/KYUM/resources/extentions.tex ~/Publishing/testArea/KYU-MYMR-MRKA/Macros/extentions.tex
#echo copying: Mark_groupPreprocess.py
#cp ~/Publishing/testArea/KYUM/resources/Mark_groupPreprocess.py ~/Publishing/testArea/KYU-MYMR-MRKA/Components/Mark/Mark_groupPreprocess.py
#echo copying: usfm-ext.sty
#cp ~/Publishing/testArea/KYUM/resources/usfm-ext.sty ~/Publishing/testArea/KYU-MYMR-MRKA/Styles/usfm-ext.sty

## Now update the text so the prprocess is used
#rpm group KYU-MYMR-MRKA Mark --manage update-group --force

## Install and switch font (Padauk 2.95 has a bug)
#rpm font KYU-MYMR-MRKA Mark usfm --manage add Padauk_2.701
#rpm font KYU-MYMR-MRKA Mark usfm --manage primary --force Padauk_2.701

## Render the component
#rpm group KYU-MYMR-MRKA Intro --manage render-draft
#rpm group KYU-MYMR-MRKA Mark --manage render-proof
##rpm group KYU-MYMR-MRKA BOOK --manage bind-final

## Backup the project
#rpm project KYU-MYMR-MRKA --manage save-backup



