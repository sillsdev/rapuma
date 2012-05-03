#!/bin/sh

rpm test -s SPT && cd SPT && rpm test -d PUB-MYMR-JAS
cd ..
rpm test -s KYUL && cd KYUL && rpm test -d PUB-KYUL-JAS

