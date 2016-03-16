#!/bin/sh

##### Rapuma KYUM Test/Example Script #####

# This script is for testing the Rapuma publishing system. For a more
# detailed explanation of commands used, refer to the totorial document
# (File: KYUM_Example_Totorial.odt). This will give information on how
# to set up the test environment so the commands below will work.
#
# NOTE: This script is desined to work with Rapuma version v0.7.202 or
# higher and on the Linux operating system, Ubuntu 14.04 or higher.

# This allows the command to be echoed
set -v


## PROJECT REMOVAL (For a clean start)
rapuma publication KYU-MYMR-KYUMTEST project remove


## CREATING A PROJECT
rapuma publication KYU-MYMR-KYUMTEST project create


## ADDING/REMOVING GROUPS
rapuma content KYU-MYMR-KYUMTEST group add --group GOSPEL --comp_type usfm
rapuma content KYU-MYMR-KYUMTEST group remove --group GOSPEL
rapuma content KYU-MYMR-KYUMTEST group add --group FOURTEES --comp_type usfm
rapuma content KYU-MYMR-KYUMTEST group add --group GOSPEL --comp_type usfm
rapuma content KYU-MYMR-KYUMTEST group add --group FRONT --comp_type pdf

## PROJECT SETTINGS: Set some important values
rapuma setting KYU-MYMR-KYUMTEST project --section ProjectInfo --key languageCode --value KYU
rapuma setting KYU-MYMR-KYUMTEST project --section ProjectInfo --key scriptCode --value MYMR

## ASSET MANAGEMENT: Macros, Fonts, and Preprocess scripts
# Macros
rapuma asset KYU-MYMR-KYUMTEST macro add --path ~/Publishing/my_source/KYUM/updates/usfmTex_20160312.zip --component_type usfm
rapuma asset KYU-MYMR-KYUMTEST macro remove --component_type usfm
rapuma asset KYU-MYMR-KYUMTEST macro add --path ~/Publishing/my_source/assets/macros/usfmTex_20150225.zip --component_type usfm
rapuma asset KYU-MYMR-KYUMTEST macro update --path ~/Publishing/my_source/KYUM/updates/usfmTex_20160312.zip --component_type usfm
# Fonts
rapuma asset KYU-MYMR-KYUMTEST font add --path ~/Publishing/my_source/assets/fonts/Charis\ SIL_4.106.zip --component_type usfm
rapuma asset KYU-MYMR-KYUMTEST font add --path ~/Publishing/my_source/assets/fonts/Padauk_2.701.zip --component_type usfm
rapuma asset KYU-MYMR-KYUMTEST font remove --package_id "Charis SIL_4.106"
rapuma asset KYU-MYMR-KYUMTEST font update --path ~/Publishing/my_source/assets/fonts/Padauk_2.701.zip
# Scripts
rapuma asset KYU-MYMR-KYUMTEST script add --group GOSPEL --path ~/Publishing/my_source/KYUM/process/kyum_textPreprocess.py --preprocess
rapuma asset KYU-MYMR-KYUMTEST script update --group GOSPEL --path ~/Publishing/my_source/KYUM/updates/kyum_textPreprocess-v2.py --preprocess
# Turn on preprocessing
rapuma setting KYU-MYMR-KYUMTEST project --section Groups/GOSPEL --key usePreprocessScript --value True
# Hyphenation
rapuma asset KYU-MYMR-KYUMTEST hyphenation add
rapuma asset KYU-MYMR-KYUMTEST hyphenation remove
rapuma asset KYU-MYMR-KYUMTEST hyphenation add --path ~/Publishing/my_source/KYUM/hyphenation
rapuma asset KYU-MYMR-KYUMTEST hyphenation update --path ~/Publishing/my_source/KYUM/updates

## ADDING/REMOVING/UPDATING COMPONENTS IN GROUPS
rapuma content KYU-MYMR-KYUMTEST component add --group GOSPEL --cid_list "mat luk jhn" --path ~/Publishing/my_source/KYUM/PT-source
rapuma content KYU-MYMR-KYUMTEST component add --group GOSPEL --cid_list "act mrk" --path ~/Publishing/my_source/KYUM/PT-source
rapuma content KYU-MYMR-KYUMTEST component remove --group GOSPEL --cid_list act
rapuma content KYU-MYMR-KYUMTEST component add --group FOURTEES --cid_list "1th 2th 1ti 2ti" --path ~/Publishing/my_source/KYUM/PT-source
rapuma content KYU-MYMR-KYUMTEST component update --group GOSPEL --cid_list jhn --path ~/Publishing/my_source/KYUM/updates
rapuma content KYU-MYMR-KYUMTEST component add --group FRONT --cid_list "cover title copyright toc introduction" --path ~/Publishing/my_source/KYUM/FRONT-source
rapuma content KYU-MYMR-KYUMTEST component remove --group FRONT --cid_list "cover"
rapuma content KYU-MYMR-KYUMTEST component update --group FRONT --cid_list "title" --path ~/Publishing/my_source/KYUM/updates

## ASSET MANAGEMENT: Macros and Fonts
# Illustrations
rapuma asset KYU-MYMR-KYUMTEST illustration add --group GOSPEL --path ~/Publishing/my_source/assets/illustrations
rapuma asset KYU-MYMR-KYUMTEST illustration remove --group GOSPEL  
rapuma asset KYU-MYMR-KYUMTEST illustration add --group GOSPEL --path ~/Publishing/my_source/assets/illustrations
rapuma asset KYU-MYMR-KYUMTEST illustration update --group GOSPEL --path ~/Publishing/my_source/KYUM/updates

## SETTINGS
# Bind order
rapuma setting KYU-MYMR-KYUMTEST project --section Groups/FRONT --key bindingOrder --value 1
rapuma setting KYU-MYMR-KYUMTEST project --section Groups/GOSPEL --key bindingOrder --value 2
rapuma setting KYU-MYMR-KYUMTEST project --section Groups/FOURTEES --key bindingOrder --value 3
# General
rapuma setting KYU-MYMR-KYUMTEST macro --section Macros/usfmTex_20160312/TeXBehavior --key vFuzz --value 4.8pt
# Illustrations
rapuma setting KYU-MYMR-KYUMTEST project --section Groups/GOSPEL --key useIllustrations --value True
rapuma setting KYU-MYMR-KYUMTEST layout --section DocumentFeatures --key useFigurePlaceHolders --value False
rapuma setting KYU-MYMR-KYUMTEST illustration --section GOSPEL/lb00135 --key position --value br
# Font
rapuma setting KYU-MYMR-KYUMTEST font --section GeneralSettings --key useRenderingSystem --value GR
rapuma setting KYU-MYMR-KYUMTEST font --section GeneralSettings --key useLanguage --value kyu
rapuma setting KYU-MYMR-KYUMTEST font --section GeneralSettings --key useMapping --value kye_renumber
rapuma setting KYU-MYMR-KYUMTEST layout --section TextElements --key bodyFontSize --value 9
rapuma setting KYU-MYMR-KYUMTEST layout --section TextElements --key bodyTextLeading --value 13
# Print output
rapuma setting KYU-MYMR-KYUMTEST layout --section DocumentFeatures --key backgroundComponents --value watermark,cropmarks
rapuma setting KYU-MYMR-KYUMTEST layout --section DocumentFeatures --key watermarkText --value "TESTING"
rapuma asset KYU-MYMR-KYUMTEST background update --group GOSPEL
rapuma setting KYU-MYMR-KYUMTEST layout --section DocumentFeatures --key docInfoText --value "Rapuma Test Render"
# Columns
rapuma setting KYU-MYMR-KYUMTEST layout --section DocumentFeatures --key columnGutterRule --value True
rapuma setting KYU-MYMR-KYUMTEST macro --section Macros/usfmTex_20160312/Columns --key columnGutterFactor --value 20
rapuma setting KYU-MYMR-KYUMTEST macro --section Macros/usfmTex_20160312/Columns --key columnGutterRuleSkip --value 4
# Verse number display
rapuma setting KYU-MYMR-KYUMTEST macro --section Macros/usfmTex_20160312/ChapterVerse --key useMarginalVerses --value True
# Binding
rapuma setting KYU-MYMR-KYUMTEST project --section Groups/FOURTEES --key startPageNumber --value 274
# Footnotes
rapuma setting KYU-MYMR-KYUMTEST macro --section Macros/usfmTex_20160312/Footnotes --key defineFootnoteRule --value "\hrule height 2pt\smallskip"
rapuma setting KYU-MYMR-KYUMTEST macro --section Macros/usfmTex_20160312/Footnotes --key footnoteRuleOn --value "[config:macroConfig|Macros|[self:macPackId]|Footnotes|defineFootnoteRule]"
# Hyphenation
rapuma setting KYU-MYMR-KYUMTEST project --section Groups/FOURTEES --key useHyphenation --value True
rapuma setting KYU-MYMR-KYUMTEST project --section Groups/GOSPEL --key useHyphenation --value True
rapuma setting KYU-MYMR-KYUMTEST project --section ProjectInfo --key hyphenationOn --value True
# Project meta-data
rapuma setting KYU-MYMR-KYUMTEST project --section ProjectInfo --key projectDescription --value "Some New Testament Scripture in an Asian language"
rapuma setting KYU-MYMR-KYUMTEST project --section ProjectInfo --key typesetters --value "Johannes Gutenberg"
rapuma setting KYU-MYMR-KYUMTEST project --section ProjectInfo --key translators --value "John Wycliffe"
rapuma setting KYU-MYMR-KYUMTEST project --section ProjectInfo --key projectTitle --value "Some Asian New Testament Scripture"
rapuma setting KYU-MYMR-KYUMTEST project --section ProjectInfo --key creatorID --value Johannes

## RENDERING
# Turn off PDF viewing to avoid screen clutter
rapuma setting KYU-MYMR-KYUMTEST project --section Managers/usfm_Xetex --key pdfViewerCommand --value "none"

# Component Level
rapuma process KYU-MYMR-KYUMTEST component render --group GOSPEL --cid_list jhn --background --doc_info --save

# Group Level
rapuma process KYU-MYMR-KYUMTEST group render --group GOSPEL
rapuma process KYU-MYMR-KYUMTEST group render --group FOURTEES
rapuma process KYU-MYMR-KYUMTEST group render --group FRONT

# Turn on PDF viewing so we can see the final results (this returns to the original default setting)
rapuma setting KYU-MYMR-KYUMTEST project --section Managers/usfm_Xetex --key pdfViewerCommand --value "default"

# Bind the results
rapuma process KYU-MYMR-KYUMTEST project bind --save --background --doc_info

# Sharing with the cloud
# Start clean
rm -rf ~/Publishing/my_cloud
mkdir -p ~/Publishing/my_cloud
# Run share commands
rapuma publication KYU-MYMR-KYUMTEST share push --path ~/Publishing/my_cloud
rapuma publication KYU-MYMR-KYUMTEST share pull --path ~/Publishing/my_cloud
rapuma publication KYU-MYMR-KYUMTEST share push --path ~/Publishing/my_cloud --replace
rapuma publication KYU-MYMR-KYUMTEST share pull --path ~/Publishing/my_cloud --replace



