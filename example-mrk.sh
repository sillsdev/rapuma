#!/bin/sh

# For this to work the following path is needed: ~/Publishing/testArea

# Copy into the testArea folder and extract the files
cp ~/Projects/rapuma/resource/example/KYUM.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/KYUM.zip -d ~/Publishing/testArea

# Remove any exsiting project of the same ID
rapuma project KYU-MYMR-MRKA project remove

# Create the project
rapuma project KYU-MYMR-MRKA project add --target_path ~/Publishing/testArea --media_type book --name 'Kayah Book of Mark example in the Burmese script'

# Install groups to render
rapuma group KYU-MYMR-MRKA Mark group add --component_type usfm --cid_list mrk --source_id MYMR --source_path ~/Publishing/testArea/KYUM/pt_environ
rapuma group KYU-MYMR-MRKA Intro group add --component_type usfm --cid_list int --source_id MYMR --source_path ~/Publishing/testArea/KYUM/pt_environ

# Turn on preprocessing for Mark group
rapuma group KYU-MYMR-MRKA Mark preprocess add

# Turn on hyphenation for Mark group
rapuma group KYU-MYMR-MRKA Mark hyphenation add

# Install the correct macro package for this job
rapuma package KYU-MYMR-MRKA Mark ptx2pdf macro remove --force
rapuma package KYU-MYMR-MRKA Mark usfmTex macro add

# Install and switch font (Padauk 2.95 has a bug)
rapuma package KYU-MYMR-MRKA Mark Padauk_2.701 font add
rapuma package KYU-MYMR-MRKA Mark Padauk_2.701 font primary --force
rapuma package KYU-MYMR-MRKA Mark Padauk_2.95 font remove --force

# Turn on font features in Padauk & adjust default settings
rapuma settings KYU-MYMR-MRKA usfmTex FontSettings useRenderingSystem GR
rapuma settings KYU-MYMR-MRKA usfmTex FontSettings useLanguage kyu
rapuma settings KYU-MYMR-MRKA usfmTex FontSettings useMapping kye_renumber
rapuma settings KYU-MYMR-MRKA usfmTex FontSettings fontSizeUnit 0.82pt
rapuma settings KYU-MYMR-MRKA usfmTex FontSettings lineSpacingFactor 1.3

# Adjust the publication format
rapuma settings KYU-MYMR-MRKA usfmTex TeXBehavior vFuzz 4.8pt
rapuma settings KYU-MYMR-MRKA usfmTex Illustrations useFigurePlaceHolders False
rapuma settings KYU-MYMR-MRKA project Groups/Mark usePreprocessScript True
rapuma settings KYU-MYMR-MRKA project Groups/Mark useIllustrations True
rapuma settings KYU-MYMR-MRKA project Groups/Mark bindingOrder 2
rapuma settings KYU-MYMR-MRKA project Groups/Intro bindingOrder 1

# Copy (system) some preset setting files into the project
echo copying: MYMR_textPreprocess.py
cp ~/Publishing/testArea/KYUM/resource/MYMR_textPreprocess.py ~/Publishing/testArea/KYU-MYMR-MRKA/Script/MYMR_textPreprocess.py
echo copying: usfmTex-ext.sty
cp ~/Publishing/testArea/KYUM/resource/usfmTex-ext.sty ~/Publishing/testArea/KYU-MYMR-MRKA/Style/usfmTex-ext.sty

# Now update the text so the customized (edited) prprocess is used
rapuma group KYU-MYMR-MRKA Mark group update --force

# Render the component
rapuma group KYU-MYMR-MRKA Intro group draft
rapuma group KYU-MYMR-MRKA Mark group proof
rapuma project KYU-MYMR-MRKA project bind

## Backup the project
#rapuma project KYU-MYMR-MRKA backup save



