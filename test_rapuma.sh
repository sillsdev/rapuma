#!/bin/sh

rapuma_demo test -s MBJAS && cd MBJAS   && rapuma_demo test -d ENG-LATN-JAS
cd ..
rapuma_demo test -s KYUM && cd KYUM   && rapuma_demo test -d KYU-MYMR-MRK
cd ..

