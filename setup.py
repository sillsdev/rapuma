#!/usr/bin/python
# -*- coding: utf-8 -*-

# By Dennis Drescher (sparkycbr at gmail dot com)

# Import modules
import os, sys
from distutils.core                     import setup
from glob                               import glob
from configobj                          import ConfigObj

# Grab some app/system info
projBase                                = os.getcwd()
sysConfig                               = ConfigObj(os.path.join(projBase, 'config', 'system.ini'), encoding='utf-8')
systemName                              = sysConfig['Rapuma']['systemName']
systemAbout                             = sysConfig['Rapuma']['systemAbout']
systemVersion                           = sysConfig['Rapuma']['systemVersion']
daMan                                   = sysConfig['Rapuma']['maintainer']
daMansEmail                             = sysConfig['Rapuma']['maintainerEmail']

datafiles = []
# This sets the path for usr/local/share/rapuma
dataprefix = "share/rapuma"

for subdir in ('doc', 'resource', 'config', 'xetex-64') :
    for (dp, dn, fn) in os.walk(subdir) :
        datafiles.append((os.path.join(dataprefix, dp), [os.path.join(dp, f) for f in fn]))

# The location of the user config file (rapuma.conf) is different depending
# on if it is a server or desktop instalation. This next bit sorts that
# out and creates a folder for it in the right place depending on what the
# user indicates when passing the install command. It is expected that
# when doing the install, the user will send either '--type server' or
# '--type desktop', nothing more, nothing less.
dtLocal = os.path.expanduser(os.path.join('~', '.config', 'rapuma'))
srLocal = os.path.join('/var', 'lib', 'rapuma', 'config')
installType = 0
if sys.argv[1] == 'install' :
    if '--type' in sys.argv :
        # find the location of the --type argv
        index = sys.argv.index('--type')
        # Remove it
        sys.argv.pop(index)
        # Capture the type here
        installType = sys.argv.pop(index)
    else :
        sys.exit('\nERROR: No system type was indicated (--type desktop|server). See installation documentation for more information. Process halted!\n')

    # Now create the config folder in the right place
    # Set permissions so Rapuma can access the conf file
    os.umask(0000)
    if installType.lower() == 'server' :
        if not os.path.exists(srLocal) :
            os.makedirs(srLocal)
    elif installType.lower() == 'desktop' :
        if not os.path.exists(dtLocal) :
            # This needs to be for the local user (not root)
            os.makedirs(dtLocal)
    else :
        sys.exit('\nERROR: Wrong type indicated, use either desktop or server as the --type. See installation documentation for more information. Process halted!\n')

# Install or build starts here
setup(name = 'rapuma',
        version = systemVersion,
        description = systemName,
        long_description = systemAbout,
        maintainer = daMan,
        maintainer_email = daMansEmail,
        package_dir = {'':'lib'},
        packages = ["rapuma", 'rapuma.core', 'rapuma.group', 'rapuma.manager', 'rapuma.project'],
        scripts = glob("scripts/rapuma*"),
        license = 'GPL',
        data_files = datafiles
     )

