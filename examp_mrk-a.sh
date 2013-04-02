#!/bin/sh

# For this to work the following path is needed: ~/Publishing/testArea

#cp ~/Projects/rapuma/resources/examples/KYUM.zip ~/Publishing/testArea
#unzip -o ~/Publishing/testArea/KYUM.zip -d ~/Publishing/testArea
# Remove any exsiting project of the same ID
rapuma project KYU-MYMR-MRKA -r
# Create the project
rapuma project KYU-MYMR-MRKA -g ~/Publishing/testArea -m book -n 'Kayah Book of Mark example in the Burmese script'
# Install a group to render
rapuma group KYU-MYMR-MRKA Mark -c usfm -a -i mrk -d MYMR -s ~/Publishing/testArea/KYUM/pt_environ
# Set the font to the right one
#rapuma font KYU-MYMR-MRKA Mark usfm Padauk -m -f
# Turn on font features in Padauk
#rapuma settings KYU-MYMR-MRKA project Managers/usfm_Font useRenderingSystem GR
#rapuma settings KYU-MYMR-MRKA project Managers/usfm_Font useLanguage kyu
#rapuma settings KYU-MYMR-MRKA project Managers/usfm_Font useMapping kye_renumber
# Adjust the publication format
#rapuma settings KYU-MYMR-MRKA book_layout Columns bodyColumns 2
# Install and switch font (Padauk 2.95 has a bug)
#rapuma font KYU-MYMR-MRKA Mark usfm -a Padauk_2.701
#rapuma font KYU-MYMR-MRKA Mark usfm -m -f Padauk_2.701
# Render the component
#rapuma group KYU-MYMR-MRKA Mark -e



