#!/bin/sh

##### Rapuma ScriptureForge Test/Example Script (Part 4) #####

# This is the forth in a series of example scripts that help test
# and demonstrate Rapuma running in the ScriptureForge environment.

# NOTE: This script is desined to work with Rapuma version v0.7.202 or
# higher and on the Linux operating system, Ubuntu 14.04 or higher.


## CONFIGURATION MANAGEMENT
# This example shows how configuration settings are changed using the
# Rapuma CLI. These changes will directly affect the results once we
# begin rendering the project components.

# Some general environment settings
rapuma settings SFTEST usfmTex TeXBehavior vFuzz 4.8pt
# Illustration
rapuma settings SFTEST project Groups/GOSPEL useIllustrations True
rapuma settings SFTEST layout DocumentFeatures useFigurePlaceHolders False
rapuma settings SFTEST illustration GOSPEL/lb00135 position br
# Font
rapuma settings SFTEST usfmTex FontSettings useRenderingSystem GR
rapuma settings SFTEST usfmTex FontSettings useLanguage kyu
rapuma settings SFTEST usfmTex FontSettings useMapping kye_renumber
rapuma settings SFTEST usfmTex FontSettings fontSizeUnit 0.82
rapuma settings SFTEST usfmTex FontSettings lineSpacingFactor 1.3
# Print output
rapuma settings SFTEST layout DocumentFeatures backgroundComponents watermark,cropmarks
rapuma settings SFTEST layout DocumentFeatures watermarkText "SF Test"
rapuma project SFTEST project update --update_type background
rapuma settings SFTEST layout DocumentFeatures docInfoText "ScriptureForge Test Render"
# Columns
rapuma settings SFTEST layout DocumentFeatures columnGutterRule True
rapuma settings SFTEST usfmTex Columns columnGutterFactor 20
rapuma settings SFTEST usfmTex Columns columnGutterRuleSkip 4
# Verse number display
rapuma settings SFTEST usfmTex ChapterVerse useMarginalVerses True
# Bind order
rapuma settings SFTEST project Groups/GOSPEL bindingOrder 1
rapuma settings SFTEST project Groups/FOURTEES bindingOrder 2

# All the settings necessary for resonable rendering are now "tweaked"
# in the next example script we will render the project publication.
