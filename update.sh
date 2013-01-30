#!/bin/sh

hg pull http://dennis_drescher:kokou@hg.palaso.org/pub-rpm

echo Pulled updated version from the main repository

hg update --repository /home/nancy/Projects/rapuma

echo Updated the local repository version of Rapuma

./setup.py build

echo Built the local version of Rapuma with the latest version

sudo ./setup.py install

echo Installed Rapuma
