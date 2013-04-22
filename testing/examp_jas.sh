#!/bin/sh

cp ~/Projects/rapuma/resources/examples/MBJAS.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/MBJAS.zip -d ~/Publishing/testArea

rpm project ENG-LATN-JAS -d

rpm project ENG-LATN-JAS -m book -n "The Book of James in English" -t ~/Publishing/testArea

rpm group ENG-LATN-JAS james -c usfm -a -i jas -d mb -s ~/Publishing/testArea/MBJAS

rpm group ENG-LATN-JAS james -e
