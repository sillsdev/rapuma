#!/usr/bin/python
# -*- coding: utf_8 -*-


###############################################################################
############################## Setup Environment ##############################
###############################################################################

import os, sys, shutil, re, codecs

from rapuma.core.tools import Tools

###############################################################################
################################# Process Code ################################
###############################################################################

tools = Tools()

source = sys.argv[1]
tempFile = source + '.tmp'
bakFile = source + '.bak'
# Make backup and temp file
shutil.copy(source, bakFile)

# Read in the source file
contents = codecs.open(source, "rt", encoding="utf_8_sig").read()

# Do stuff here

# Please delete this warning message when you start modifying this script.
tools.terminal('\nThe group preprocess script has not been modified yet. It is in its defaul form. Nothing has been done to the component data.\n(This anoying little message can be found in a file in your project Script folder.)\n')

# Examples:
# Change cross reference into footnotes
#contents = re.sub(ur'\\x(\s.+?)\\xo(\s\d+:\d+)(.+?)\\x\*', ur'\\f\1\\fr\2 \\ft\3\\f*', contents)

# Insert horizontal rule after intro section
#contents = re.sub(ur'(\\c\s1\r\n)', ur'\skipline\n\hrule\r\n\1', contents)

# Insert a chapter label marker with zwsp to center the chapter number
#contents = re.sub(ur'(\\c\s1\r\n)', ur'\cl \u200b\r\n\1', contents)

# Write out a temp file so we can do some checks
codecs.open(tempFile, "wt", encoding="utf_8_sig").write(contents)

# Finish by copying the tempFile to the source
if not shutil.copy(tempFile, source) :
    # Take out the trash
    os.remove(tempFile)
    sys.exit(0)
else :
    tools.terminal('\nSCRIPT: Error: Failed to copy: [' + tempFile + '] to: [' + source + ']')


