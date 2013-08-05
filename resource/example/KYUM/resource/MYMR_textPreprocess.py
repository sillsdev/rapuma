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
bakFile = source + '.bak'
# Make backup and temp file
shutil.copy(source, bakFile)

# Read in the source file
contents = codecs.open(source, "rt", encoding="utf_8_sig").read()

# At the end of the intro part insert a blank line, a horizontal rule and 
# \cl-space-zwsp before the chapterheader \c 1 
#contents = re.sub(ur'(\\c\s1\r\n)', ur'\eject\n\cl \u200b\r\n\1', contents)
contents = re.sub(ur'(\\c\s1\r\n)', ur'\cl \u200b\r\n\1', contents)

# change cross reference into footnotes
contents = re.sub(ur'\\x(\s.+?)\\xo(\s\d+:\d+)(.+?)\\x\*', ur'\\f\1\\fr\2 \\ft\3\\f*', contents)





# Function to insert \nbsp in front of short words at the end of a paragraph
def insertNBSP (mobj) :
    line = mobj.group(1)
    footnote = ''
    try :
        # This looks for lines ending with a footnote and
        # stores it for later.
        if line[-4:].find('\\f*') >= 0 :
            fnConts = re.search(r'(\\f\s.+?\\f\*)', line)
            footnote = fnConts.group(1)
            line = re.sub(r'(\\f\s.+?\\f\*)', '', line)
    except :
        pass
    # Break the line into words
    words = line.split()
    numWords = len(words)
    # look at the last word in the line to see if it is
    # less than n characters. If it is, put an \nbsp in
    # front of the word and store it
    if len(words[-1:]) < 10 :
        newLine = []
        modWord = ''.join(words[-1:])
        modWord = '\\nbsp ' + modWord
        # Remove the word from the line
        words.pop(numWords-1)
        # Add the word list to the new lines list
        newLine.extend(words)
        # Turn the list into a string separated by normal spaces
        reLine = ' '.join(newLine)
        # Reasemble all the pieces and return them to the calling regex
        return reLine + modWord + footnote + '\n'
    else :
        return line

def testing (mobj) :
    print 'found: ', mobj.group(1)[:20]

# On a match, this calls the insertNBSP function to insert a \nbsp in front
# a short word at the end of a line. This uses the MULTILINE mode (?m) which
# makes it possible to do line-by-line processing without a loop. This will
# look for a \v at the start of a line and will match if the next line does
# not contain a \v, meaning this should be the last line of a paragraph.
contents = re.sub(r"(?m)^(\\v.*)$\s(?!\\v)", insertNBSP, contents)

# FIXME: Need to check \q lines too. This does it partly but many are missed.
# A \q(n) marker is different from \p in that it is often starts inside a verse.
# A \p can be in a verse too, but nearly as often.
#contents = re.sub(r"(?m)^(\\q.*)$\s(?!\\q)", testing, contents)




# Write out a temp file so we can do some checks
codecs.open(tempFile, "wt", encoding="utf_8_sig").write(contents)

# Finish by copying the tempFile to the source
if not shutil.copy(tempFile, source) :
    # Take out the trash
    os.remove(tempFile)
    sys.exit(0)
else :
    terminal('\nSCRIPT: Error: Failed to copy: [' + tempFile + '] to: [' + source + ']')


