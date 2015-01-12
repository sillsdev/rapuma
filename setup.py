#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Copyright 2014, SIL International
#    All rights reserved.
#
#    This library is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation; either version 2.1 of License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should also have received a copy of the GNU Lesser General Public
#    License along with this library in the file named "LICENSE".
#    If not, write to the Free Software Foundation, 51 Franklin Street,
#    suite 500, Boston, MA 02110-1335, USA or visit their web page on the 
#    internet at http://www.fsf.org/licenses/lgpl.html.

# Import modules
import os
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

setup(name = 'rapuma',
        version = systemVersion,
        description = systemName,
        long_description = systemAbout,
        maintainer = daMan,
        maintainer_email = daMansEmail,
        package_dir = {'':'lib'},
        packages = ["rapuma", 'rapuma.core', 'rapuma.group', 'rapuma.manager', 'rapuma.project'],
        scripts = glob("scripts/rapuma*"),
        license = 'LGPL',
        data_files = datafiles
     )


