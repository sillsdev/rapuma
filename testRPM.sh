#!/bin/sh

# This assumes we are starting in the "My Paratext Projects" folder

rpm_demo test -s SPT    && cd SPT   && rpm_demo test -d PUB-MYMR-JAS
cd ..
rpm_demo test -s KYUL   && cd KYUL  && rpm_demo test -d PUB-KYUL-JAS
cd ..
rpm_demo test -s ThiWB  && cd ThiWB && rpm_demo test -d PUB-ThiWB-NT
cd ..
rpm_demo test -s NOD    && cd NOD   && rpm_demo test -d PUB-THAI-ACT
                                    && rpm_demo test -d PUB-LANA-ACT

