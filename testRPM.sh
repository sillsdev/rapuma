#!/bin/sh

rpm test -s SPT && cd SPT && rpm test -d PUB-MYMR-JAS
cd ..
rpm test -s KYUL && cd KYUL && rpm test -d PUB-KYUL-JAS
cd ..
rpm test -s ThiWB && cd ThiWB && rpm test -d PUB-ThiWB-NT

