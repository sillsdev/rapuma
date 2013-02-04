#!/bin/sh

# For this to work the following path is needed: ~/Publishing/testArea

cp ~/Projects/rapuma/resources/examples/KYUM.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/KYUM.zip -d ~/Publishing/testArea
rapuma project KYU-MYMR-MRKB -r
rapuma project KYU-MYMR-MRKB -t KYU-MYMR-MRKB -n 'Book of Mark Testing' -g ~/Publishing/testArea -o ~/Publishing/testArea/KYUM
rapuma component KYU-MYMR-MRKB usfm mark -e 
