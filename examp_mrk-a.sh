#!/bin/sh

# For this to work the following path is needed: ~/Publishing/testArea

cp ~/Projects/rapuma/resources/examples/KYUM.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/KYUM.zip -d ~/Publishing/testArea
# Remove any exsiting project of the same ID
rapuma project KYU-MYMR-MRKA -r
# Create the project
rapuma project KYU-MYMR-MRKA -g ~/Publishing/testArea -m book -n 'Kayah Book of Mark example in the Burmese script'
# Install a component to render
rapuma component KYU-MYMR-MRKA usfm mark -a -i mrk -s ~/Publishing/testArea/KYUM/pt_environ
# Set the font to the right one
rapuma font KYU-MYMR-MRKA usfm Padauk -m -f
# Install additional files
rapuma style KYU-MYMR-MRKA usfm custom -a -p ~/Publishing/testArea/KYUM/resources/custom.sty 
# Turn on hyphenation
rapuma hyphen KYU-MYMR-MRKA usfm -a
# Adjust the publication format
rapuma settings KYU-MYMR-MRKA book_layout Columns bodyColumns 2
# Install and switch font
rapuma font KYU-MYMR-MRKA usfm -a Padauk_2.701
rapuma font KYU-MYMR-MRKA usfm -m -f Padauk_2.701
# Render the component
rapuma component KYU-MYMR-MRKA usfm mark -e



