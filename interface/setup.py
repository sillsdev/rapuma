#!/usr/bin/python
# -*- coding: utf-8 -*-

# Installer script for Rapuma Ubuntu interfaces such as color syntax
# in Gedit as well as the RapumaIPE plugin for Gedit.

import os, sys, shutil, difflib, subprocess


# Install plugin files for RapumaIPE
pDir        = os.path.expanduser('~/.local/share/gedit/plugins')
rpDir       = os.path.join(pDir, 'rapuma-ipe')
pFiles      = [os.path.join('rapuma-ipe', '__init__.py'), 
                    os.path.join('rapuma-ipe', 'rapuma.py'), 
                        'rapuma-ipe.gedit.plugin']

print '\nRapuma Gedit plugin install/update'

if not os.path.exists(rpDir) :
    os.makedirs(rpDir)
    print 'Created rapuma-ipe plugin folder'

for f in pFiles :
    target      = os.path.join(pDir, f)
    source      = os.path.join(os.getcwd(), 'RapumaIPE', f)

    if os.path.exists(target) :
        # Do a simple diff to see if the file needs to be copied
        if subprocess.call(['diff', '--suppress-common-lines', source, target]) > 0 :
            shutil.copy(source, target)
            print '\tUpdated: ' + os.path.basename(source)
        else :
            print '\tPlugin file update not necessary: ' + os.path.basename(source)
    else :
        shutil.copy(source, target)
        print '\tCopied: ' + os.path.basename(source)


# Install lang files for Gedit color syntax
lDir            = '/usr/share/gtksourceview-3.0/language-specs'
lFiles          = ['RapumaConf.lang', 'usfmtex.lang']

print '\nRapuma Gedit color syntax install/update'

for f in lFiles :
    target      = os.path.join(lDir, f)
    source      = os.path.join(os.getcwd(), 'ColorSyntax', f)

    if os.path.exists(target) :
        # Do a simple diff to see if the file needs to be copied
        if subprocess.call(['diff', '--suppress-common-lines', source, target]) > 0 :
            shutil.copy(source, target)
            print '\tUpdated: ' + os.path.basename(source)
        else :
            print '\tPlugin file update not necessary: ' + os.path.basename(source)
    else :
        shutil.copy(source, target)
        print '\tCopied: ' + os.path.basename(source)

