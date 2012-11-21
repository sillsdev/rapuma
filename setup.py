#!/usr/bin/python

from distutils.core import setup
from glob import glob
import os

datafiles = []
dataprefix = "share/rapuma"
for subdir in ('resources', 'config') :
    for (dp, dn, fn) in os.walk(subdir) :
        datafiles.append((os.path.join(dataprefix, dp), [os.path.join(dp, f) for f in fn]))

setup(name = 'rapuma',
        version = '0.1.0',
        description = "Rapid Publication Manager",
        long_description = "Rapuma is a publication management application.",
        maintainer = "Dennis Drescher",
        maintainer_email = "dennis_drescher@sil.org",
        package_dir = {'':'python_lib'},
        packages = ["rapuma", 'rapuma.core', 'rapuma.project', 'rapuma.component', 'rapuma.manager'],
        scripts = glob("bin/rapuma*"),
        license = 'LGPL',
        data_files = datafiles
     )

        
