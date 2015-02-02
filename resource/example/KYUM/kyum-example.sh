#!/bin/sh

##### Rapuma KYUM Test/Example Script #####

# This script will both test the Rapuma publishing system. For a more
# detailed explanation of commands used, refer to the totorial document
# (File: KYUM_ExampleAndTotorial.odt). This will give information on how
# to set up the test environment so the commands below will work.
#
# NOTE: This script is desined to work with Rapuma version v0.7.202 or
# higher and on the Linux operating system, Ubuntu 14.04 or higher.

set -v

## PROJECT REMOVAL (For a clean start)
~/Projects/rapuma/scripts/rapuma publication KYU-MYMR-KYUMTEST project remove


## CREATING A PROJECT
~/Projects/rapuma/scripts/rapuma publication KYU-MYMR-KYUMTEST project create


## ADDING/REMOVING/UPDATING GROUPS AND COMPONENTS
~/Projects/rapuma/scripts/rapuma content KYU-MYMR-KYUMTEST GOSPEL group add --comp_type usfm
~/Projects/rapuma/scripts/rapuma content KYU-MYMR-KYUMTEST GOSPEL component add --cid_list "mat luk jhn" --path ~/Publishing/my_source/KYUM
~/Projects/rapuma/scripts/rapuma content KYU-MYMR-KYUMTEST GOSPEL component update --cid_list jhn --path ~/Publishing/my_source/KYUM
~/Projects/rapuma/scripts/rapuma content KYU-MYMR-KYUMTEST GOSPEL component add --cid_list "act mrk" --path ~/Publishing/my_source/KYUM
~/Projects/rapuma/scripts/rapuma content KYU-MYMR-KYUMTEST GOSPEL component remove --cid_list act
~/Projects/rapuma/scripts/rapuma content KYU-MYMR-KYUMTEST FOURTEES group add --comp_type usfm
~/Projects/rapuma/scripts/rapuma content KYU-MYMR-KYUMTEST FOURTEES component add --cid_list "1th 2th 1ti 2ti" --path ~/Publishing/my_source/KYUM


## ASSET MANAGEMENT
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST GOSPEL macro update --package_id usfmTex
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST GOSPEL macro remove --package_id usfmTex
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST GOSPEL macro add --package_id usfmTex
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST GOSPEL font add --file_name "Charis SIL_4.106.zip" --path ~/Publishing/my_source/assets --primary
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST GOSPEL font add --file_name Padauk_2.701.zip --path ~/Publishing/my_source/assets --primary
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST GOSPEL font remove --package_id "Charis SIL_4.106"
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST GOSPEL font update --file_name Padauk_2.701.zip --path ~/Publishing/my_source/assets
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST GOSPEL illustration add --path ~/Publishing/my_source/assets
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST GOSPEL illustration remove
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST GOSPEL illustration add --path ~/Publishing/my_source/assets
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST GOSPEL illustration update --path ~/Publishing/my_source/assets/updates


## SETTINGS
# General
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST usfmTex --section TeXBehavior --key vFuzz --value 4.8pt
# Illustrations
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST project --section Groups/GOSPEL --key useIllustrations --value True
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST layout --section DocumentFeatures --key useFigurePlaceHolders --value False
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST illustration --section GOSPEL/lb00135 --key position --value br
# Font
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST usfmTex --section FontSettings --key useRenderingSystem --value GR
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST usfmTex --section FontSettings --key useLanguage --value kyu
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST usfmTex --section FontSettings --key useMapping --value kye_renumber
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST usfmTex --section FontSettings --key fontSizeUnit --value 0.82
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST usfmTex --section FontSettings --key lineSpacingFactor --value 1.3
# Print output
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST layout --section DocumentFeatures --key backgroundComponents --value watermark,cropmarks
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST layout --section DocumentFeatures --key watermarkText --value "SF Test"
~/Projects/rapuma/scripts/rapuma asset KYU-MYMR-KYUMTEST GOSPEL background update
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST layout --section DocumentFeatures --key docInfoText --value "ScriptureForge Test Render"
# Columns
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST layout --section DocumentFeatures --key columnGutterRule --value True
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST usfmTex --section Columns --key columnGutterFactor --value 20
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST usfmTex --section Columns --key columnGutterRuleSkip --value 4
# Verse number display
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST usfmTex --section ChapterVerse --key useMarginalVerses --value True
# Binding
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST project --section Groups/FOURTEES --key startPageNumber --value 274
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST project --section Groups/GOSPEL --key bindingOrder --value 1
~/Projects/rapuma/scripts/rapuma setting KYU-MYMR-KYUMTEST project --section Groups/FOURTEES --key bindingOrder --value 2



# Stopping here for now


~/Projects/rapuma/scripts/rapuma process KYU-MYMR-KYUMTEST component render GOSPEL --cid_list jhn




