#!/usr/bin/python

from distutils.core import setup
from glob import glob
import os

datafiles = []
# This sets the path for usr/local/share/rapuma
dataprefix = "share/rapuma"

for subdir in ('doc', 'resource', 'config') :
    for (dp, dn, fn) in os.walk(subdir) :
        datafiles.append((os.path.join(dataprefix, dp), [os.path.join(dp, f) for f in fn]))

setup(name = 'rapuma',
        version = '0.6.r790',
        description = "Rapid Publication Manager",
        long_description = "Rapuma is a publication management application.",
        maintainer = "Dennis Drescher",
        maintainer_email = "dennis_drescher@sil.org",
        package_dir = {'':'lib'},
        packages = ["rapuma", 'rapuma.core', 'rapuma.project', 'rapuma.group', 'rapuma.manager'],
        scripts = glob("scripts/rapuma*"),
        license = 'LGPL',
        data_files = datafiles
     )


