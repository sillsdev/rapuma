#!/bin/sh

hg pull http://dennis_drescher:kokou@hg.palaso.org/pub-rpm

echo Pulled updated version from the main repository

hg update --repository ~/Projects/rapuma

echo Updated the local repository version of Rapuma

~/Projects/rapuma/setup.py build

echo Built the local version of Rapuma with the latest version

sudo ~/Projects/rapuma/setup.py install

echo Installed Rapuma
