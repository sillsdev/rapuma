#!/bin/sh

# For this to work the following path is needed: ~/Publishing/testArea

# Copy into the testArea folder and extract the files
cp ~/Projects/rapuma/resources/examples/KYUM.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/KYUM.zip -d ~/Publishing/testArea

# Remove any exsiting project of the same ID
rapuma project KYU-MYMR-MRKA --manage remove-project

# Create the project
rapuma project KYU-MYMR-MRKA --manage add-project --target_path ~/Publishing/testArea --media_type book --name 'Kayah Book of Mark example in the Burmese script'

# Install groups to render
rapuma group KYU-MYMR-MRKA Mark --manage add-group --component_type usfm --cid_list mrk --source_id MYMR --source_path ~/Publishing/testArea/KYUM/pt_environ
rapuma group KYU-MYMR-MRKA Intro --manage add-group --component_type usfm --cid_list int --source_id MYMR --source_path ~/Publishing/testArea/KYUM/pt_environ

# Set the font to the right one
rapuma font KYU-MYMR-MRKA Mark usfm Padauk --manage primary --force

# Turn on preprocessing for Mark group
rapuma group KYU-MYMR-MRKA Mark --preprocess add-preprocess

# Turn on font features in Padauk & adjust default settings
rapuma settings KYU-MYMR-MRKA project Managers/usfm_Font useRenderingSystem GR
rapuma settings KYU-MYMR-MRKA project Managers/usfm_Font useLanguage kyu
rapuma settings KYU-MYMR-MRKA project Managers/usfm_Font useMapping kye_renumber
rapuma settings KYU-MYMR-MRKA book_layout Fonts fontSizeUnit 0.82pt
rapuma settings KYU-MYMR-MRKA book_layout Fonts lineSpacingFactor 1.3

# Adjust the publication format
rapuma settings KYU-MYMR-MRKA book_layout Columns bodyColumns 2
rapuma settings KYU-MYMR-MRKA book_layout TeXBehavior vFuzz 4.8pt
rapuma settings KYU-MYMR-MRKA book_layout Illustrations useFigurePlaceHolders False
rapuma settings KYU-MYMR-MRKA project Groups/Mark usePreprocessScript True
rapuma settings KYU-MYMR-MRKA project Groups/Mark useIllustrations True

# Copy (system) some preset setting files into the project
echo copying: extention.tex
cp ~/Publishing/testArea/KYUM/resources/extentions.tex ~/Publishing/testArea/KYU-MYMR-MRKA/Macros/extentions.tex
echo copying: Mark_groupPreprocess.py
cp ~/Publishing/testArea/KYUM/resources/Mark_groupPreprocess.py ~/Publishing/testArea/KYU-MYMR-MRKA/Components/Mark/Mark_groupPreprocess.py
echo copying: usfm-ext.sty
cp ~/Publishing/testArea/KYUM/resources/usfm-ext.sty ~/Publishing/testArea/KYU-MYMR-MRKA/Styles/usfm-ext.sty

# Now update the text so the prprocess is used
rapuma group KYU-MYMR-MRKA Mark --manage update-group --force

# Install and switch font (Padauk 2.95 has a bug)
rapuma font KYU-MYMR-MRKA Mark usfm --manage add Padauk_2.701
rapuma font KYU-MYMR-MRKA Mark usfm --manage primary --force Padauk_2.701

# Render the component
rapuma group KYU-MYMR-MRKA Intro --manage render-draft
rapuma group KYU-MYMR-MRKA Mark --manage render-proof
#rapuma group KYU-MYMR-MRKA BOOK --manage bind-final

# Backup the project
rapuma project KYU-MYMR-MRKA --manage save-backup


