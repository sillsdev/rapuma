#!/bin/sh

rapuma project ENG-LATN-JAS -r

rapuma project ENG-LATN-JAS -m book -n "The Book of James in English" -g ~/Publishing/testArea

rapuma group ENG-LATN-JAS james -c usfm -a -i jas -d mb -s ~/Publishing/testArea/MBJAS

rapuma group ENG-LATN-JAS james -e
