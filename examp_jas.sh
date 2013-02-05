#!/bin/sh

rapuma project ENG-LATN-JAS -r

rapuma project ENG-LATN-JAS -m book -n "The Book of James in English" -g ~/Publishing/testArea

rapuma component ENG-LATN-JAS usfm james -a -i jas -s ~/Publishing/testArea/MBJAS

rapuma component ENG-LATN-JAS usfm james -e
