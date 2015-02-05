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
# At the end of the intro part insert a blank line, a horizontal rule and 
# \cl-space-zwsp before the chapterheader \c 1 
contents = re.sub(ur'(\\c\s1\r\n)', ur'\skipline\n\hrule\n\cl \u200b\r\n\1', contents)

# Write out a temp file so we can do some checks
codecs.open(tempFile, "wt", encoding="utf_8_sig").write(contents)

# Finish by copying the tempFile to the source
if not shutil.copy(tempFile, source) :
    # Take out the trash
    os.remove(tempFile)
    sys.exit(0)
else :
    tools.terminal('\nSCRIPT: Error: Failed to copy: [' + tempFile + '] to: [' + source + ']')


