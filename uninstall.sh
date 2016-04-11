#!/bin/sh

# A simple uninstall script for Rapuma that may, or may not work. :-)

# Remove the main script
cd /usr/local/bin
sudo find . -name "rapuma*" -exec rm -rfv {} \;

# Go on to remove the supporting files
sudo rm -r /usr/local/share/rapuma

# Next we should remove the Python libs
sudo rm -r /usr/local/lib/python2.7/dist-packages/rapuma
cd /usr/local/lib/python2.7/dist-packages
sudo find . -name "rapuma*" -exec rm -rfv {} \;

# Finally we remove the user/system config file (both server and desktop)
sudo rm -r ~/.config/rapuma
sudo rm -r /var/lib/rapuma/config

# What we don't do is remove the project folder
