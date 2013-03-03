#!/usr/bin/python
# -*- coding: utf_8 -*-


###############################################################################
############################## Setup Environment ##############################
###############################################################################

import os, sys, shutil, re, codecs

from rapuma.core.tools import *

###############################################################################
################################# Process Code ################################
###############################################################################

source = sys.argv[1]
tempFile = source + '.tmp'

# Read in the source file
contents = codecs.open(source, "rt", encoding="utf_8_sig").read()

# Do stuff here

# Write out a temp file so we can do some checks
codecs.open(tempFile, "wt", encoding="utf_8_sig").write(contents)

# Finish by copying the tempFile to the source
if not shutil.copy(tempFile, source) :
    # Take out the trash
    os.remove(tempFile)
    sys.exit(0)
else :
    terminal('\nSCRIPT: Error: Failed to copy: [' + tempFile + '] to: [' + source + ']')


