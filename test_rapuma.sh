#!/bin/sh

rpm_demo test -s MBJAS && cd MBJAS   && rpm_demo test -d ENG-LATN-JAS
cd ..
rpm_demo test -s KYUM && cd KYUM   && rpm_demo test -d KYU-MYMR-MRK
cd ..

