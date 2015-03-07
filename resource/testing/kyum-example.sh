#!/bin/sh

##### Rapuma KYUM Test/Example Script #####

# This script will both test the Rapuma publishing system. For a more
# detailed explanation of commands used, refer to the totorial document
# (File: KYUM_ExampleAndTotorial.odt). This will give information on how
# to set up the test environment so the commands below will work.
#
# NOTE: This script is desined to work with Rapuma version v0.7.202 or
# higher and on the Linux operating system, Ubuntu 14.04 or higher.

# This allows the command to be echoed
set -v


## PROJECT REMOVAL (For a clean start)
~/Projects/rapuma/scripts/rapuma publication KYU-MYMR-KYUMTEST project remove


## CREATING A PROJECT
~/Projects/rapuma/scripts/rapuma publication KYU-MYMR-KYUMTEST project create


## ADDING/REMOVING GROUPS
~/Projects/rapuma/scripts/rapuma content KYU-MYMR-KYUMTEST group add --group GOSPEL --comp_type usfm
~/Projects/rapuma/scripts/rapuma content KYU-MYMR-KYUMTEST group remove --group GOSPEL
~/Projects/rapuma/scripts/rapuma content KYU-MYMR-KYUMTEST group add --group FOURTEES --comp_type usfm
~/Projects/rapuma/scripts/rapuma content KYU-MYMR-KYUMTEST group add --group GOSPEL --comp_type usfm
~/Projects/rapuma/scripts/rapuma content KYU-MYMR-KYUMTEST group add --group FRONT --comp_type pdf


## ASSET MANAGEMENT: Macros, Fonts, and Preprocess scripts
# Macros
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST macro add --path ~/Publishing/my_source/KYUM/updates/usfmTex_20150228.zip --component_type usfm
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST macro remove --component_type usfm
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST macro add --path ~/Publishing/my_source/assets/macros/usfmTex_20150225.zip --component_type usfm
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST macro update --path ~/Publishing/my_source/KYUM/updates/usfmTex_20150228.zip --component_type usfm
# Fonts
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST font add --path ~/Publishing/my_source/assets/fonts/Charis\ SIL_4.106.zip --component_type usfm
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST font add --path ~/Publishing/my_source/assets/fonts/Padauk_2.701.zip --component_type usfm
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST font remove --package_id "Charis SIL_4.106"
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST font update --path ~/Publishing/my_source/assets/fonts/Padauk_2.701.zip
# Scripts
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST script add --group GOSPEL --path ~/Publishing/my_source/KYUM/process/kyum_textPreprocess.py --preprocess
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST script update --group GOSPEL --path ~/Publishing/my_source/KYUM/updates/kyum_textPreprocess-v2.py --preprocess
# Turn on preprocessing
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST project --section Groups/GOSPEL --key usePreprocessScript --value True


## ADDING/REMOVING/UPDATING COMPONENTS IN GROUPS
~/Projects/rapuma/scripts/rapuma content KYU-MYMR-KYUMTEST component add --group GOSPEL --cid_list "mat luk jhn" --path ~/Publishing/my_source/KYUM/PT-source
~/Projects/rapuma/scripts/rapuma content KYU-MYMR-KYUMTEST component add --group GOSPEL --cid_list "act mrk" --path ~/Publishing/my_source/KYUM/PT-source
~/Projects/rapuma/scripts/rapuma content KYU-MYMR-KYUMTEST component remove --group GOSPEL --cid_list act
~/Projects/rapuma/scripts/rapuma content KYU-MYMR-KYUMTEST component add --group FOURTEES --cid_list "1th 2th 1ti 2ti" --path ~/Publishing/my_source/KYUM/PT-source
~/Projects/rapuma/scripts/rapuma content KYU-MYMR-KYUMTEST component update --group GOSPEL --cid_list jhn --path ~/Publishing/my_source/KYUM/updates
~/Projects/rapuma/scripts/rapuma content KYU-MYMR-KYUMTEST component add --group FRONT --cid_list "cover title copyright toc introduction" --path ~/Publishing/my_source/KYUM/FRONT-source
~/Projects/rapuma/scripts/rapuma content KYU-MYMR-KYUMTEST component remove --group FRONT --cid_list "cover"
~/Projects/rapuma/scripts/rapuma content KYU-MYMR-KYUMTEST component update --group FRONT --cid_list "title" --path ~/Publishing/my_source/KYUM/updates


## ASSET MANAGEMENT: Macros and Fonts
# Illustrations
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST illustration add --group GOSPEL --path ~/Publishing/my_source/assets/illustrations
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST illustration remove --group GOSPEL  
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST illustration add --group GOSPEL --path ~/Publishing/my_source/assets/illustrations
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST illustration update --group GOSPEL --path ~/Publishing/my_source/KYUM/updates


## SETTINGS
# Bind order
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST project --section Groups/FRONT --key bindingOrder --value 1
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST project --section Groups/GOSPEL --key bindingOrder --value 2
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST project --section Groups/FOURTEES --key bindingOrder --value 3
# General
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST macro --section Macros/usfmTex_20150228/TeXBehavior --key vFuzz --value 4.8pt
# Illustrations
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST project --section Groups/GOSPEL --key useIllustrations --value True
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST layout --section DocumentFeatures --key useFigurePlaceHolders --value False
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST illustration --section GOSPEL/lb00135 --key position --value br
# Font
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST font --section GeneralSettings --key useRenderingSystem --value GR
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST font --section GeneralSettings --key useLanguage --value kyu
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST font --section GeneralSettings --key useMapping --value kye_renumber
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST layout --section TextElements --key bodyFontSize --value 9
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST layout --section TextElements --key bodyTextLeading --value 13
# Print output
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST layout --section DocumentFeatures --key backgroundComponents --value watermark,cropmarks
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST layout --section DocumentFeatures --key watermarkText --value "TESTING"
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST background update --group GOSPEL
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST layout --section DocumentFeatures --key docInfoText --value "Rapuma Test Render"
# Columns
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST layout --section DocumentFeatures --key columnGutterRule --value True
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST macro --section Macros/usfmTex_20150228/Columns --key columnGutterFactor --value 20
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST macro --section Macros/usfmTex_20150228/Columns --key columnGutterRuleSkip --value 4
# Verse number display
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST macro --section Macros/usfmTex_20150228/ChapterVerse --key useMarginalVerses --value True
# Binding
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST project --section Groups/FOURTEES --key startPageNumber --value 274
# Footnotes
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST macro --section Macros/usfmTex_20150228/Footnotes --key defineFootnoteRule --value "\hrule height 2pt\smallskip"

## RENDERING
# Turn off PDF viewing to avoid screen clutter
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST rapuma --section System --key pdfViewerCommand --value ""

# Component Level
~/Projects/rapuma/scripts/rapuma process KYU-MYMR-KYUMTEST component render --group GOSPEL --cid_list jhn --background --doc_info --save

# Group Level
~/Projects/rapuma/scripts/rapuma process KYU-MYMR-KYUMTEST group render --group GOSPEL
~/Projects/rapuma/scripts/rapuma process KYU-MYMR-KYUMTEST group render --group FOURTEES
~/Projects/rapuma/scripts/rapuma process KYU-MYMR-KYUMTEST group render --group FRONT

# Turn on PDF viewing so we can see the final results
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST rapuma --section System --key pdfViewerCommand --value evince

# Bind the results
~/Projects/rapuma/scripts/rapuma process KYU-MYMR-KYUMTEST project bind --save --background --doc_info

# Sharing with the cloud
# Start clean
rm -rf ~/Publishing/my_cloud
mkdir -p ~/Publishing/my_cloud
# Run share commands
~/Projects/rapuma/scripts/rapuma publication KYU-MYMR-KYUMTEST share push --path ~/Publishing/my_cloud
~/Projects/rapuma/scripts/rapuma publication KYU-MYMR-KYUMTEST share pull --path ~/Publishing/my_cloud
~/Projects/rapuma/scripts/rapuma publication KYU-MYMR-KYUMTEST share push --path ~/Publishing/my_cloud --replace
~/Projects/rapuma/scripts/rapuma publication KYU-MYMR-KYUMTEST share pull --path ~/Publishing/my_cloud --replace



