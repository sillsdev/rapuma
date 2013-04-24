#!/bin/sh

# For this to work the following path is needed: ~/Publishing/testArea

cp ~/Projects/rapuma/resources/examples/KYUM.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/KYUM.zip -d ~/Publishing/testArea
# Remove any exsiting project of the same ID
rpm project KYU-MYMR-MRKA -d
# Create the project
rpm project KYU-MYMR-MRKA -t ~/Publishing/testArea -m book -n 'Kayah Book of Mark example in the Burmese script'
# Install groups to render
rpm group KYU-MYMR-MRKA Mark -c usfm -m add -i mrk -d MYMR -s ~/Publishing/testArea/KYUM/pt_environ
rpm group KYU-MYMR-MRKA Intro -c usfm -m add -i int -d MYMR -s ~/Publishing/testArea/KYUM/pt_environ
# Create a binding group
rpm group KYU-MYMR-MRKA BOOK -c bind -m add -i "Intro Mark"
# Set the font to the right one
rpm font KYU-MYMR-MRKA Mark usfm Padauk -m -f
# Turn on font features in Padauk & adjust default settings
rpm settings KYU-MYMR-MRKA project Managers/usfm_Font useRenderingSystem GR
rpm settings KYU-MYMR-MRKA project Managers/usfm_Font useLanguage kyu
rpm settings KYU-MYMR-MRKA project Managers/usfm_Font useMapping kye_renumber
rpm settings KYU-MYMR-MRKA book_layout Fonts fontSizeUnit 0.82pt
rpm settings KYU-MYMR-MRKA book_layout Fonts lineSpacingFactor 1.3
# Adjust the publication format
rpm settings KYU-MYMR-MRKA book_layout Columns bodyColumns 2
rpm settings KYU-MYMR-MRKA book_layout TeXBehavior vFuzz 4.8pt
rpm settings KYU-MYMR-MRKA book_layout Illustrations useFigurePlaceHolders False
rpm settings KYU-MYMR-MRKA project Groups/Mark usePreprocessScript True
rpm settings KYU-MYMR-MRKA project Groups/Mark useIllustrations True
# Copy (system) some preset setting files into the project
echo copying: extention.tex
cp ~/Publishing/testArea/KYUM/resources/extentions.tex ~/Publishing/testArea/KYU-MYMR-MRKA/Macros/extentions.tex
echo copying: Mark_groupPreprocess.py
cp ~/Publishing/testArea/KYUM/resources/Mark_groupPreprocess.py ~/Publishing/testArea/KYU-MYMR-MRKA/Components/Mark/Mark_groupPreprocess.py
echo copying: usfm-ext.sty
cp ~/Publishing/testArea/KYUM/resources/usfm-ext.sty ~/Publishing/testArea/KYU-MYMR-MRKA/Styles/usfm-ext.sty
# Now update the text so the prprocess is used
rpm group KYU-MYMR-MRKA Mark -m update -f
# Install and switch font (Padauk 2.95 has a bug)
rpm font KYU-MYMR-MRKA Mark usfm -a Padauk_2.701
rpm font KYU-MYMR-MRKA Mark usfm -m -f Padauk_2.701
# Render the component
rpm group KYU-MYMR-MRKA Intro -m execute
rpm group KYU-MYMR-MRKA Mark -m execute
rpm group KYU-MYMR-MRKA BOOK -m execute
# Backup the project
rpm project KYU-MYMR-MRKA -p backup



