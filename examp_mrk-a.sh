#!/bin/sh

# For this to work the following path is needed: ~/Publishing/testArea

cp ~/Projects/rapuma/resources/examples/KYUM.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/KYUM.zip -d ~/Publishing/testArea
rapuma project KYU-MYMR-MRKA -r
rapuma project KYU-MYMR-MRKA -c -g ~/Publishing/testArea -o ~/Publishing/testArea/KYUM
rapuma component KYU-MYMR-MRKA usfm mark -e
