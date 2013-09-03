#!/bin/sh

RAPUMA=~/Projects/rapuma/scripts/rapuma
cp ~/Projects/rapuma/resource/example/MBJAS.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/MBJAS.zip -d ~/Publishing/testArea
rm -rf ~/Publishing/testArea/ENG-LATN-JAS

echo $RAPUMA project ENG-LATN-JAS project remove
$RAPUMA project ENG-LATN-JAS project remove

echo $RAPUMA project ENG-LATN-JAS backup restore --source_path ~/Publishing/testArea/MBJAS --target_path ~/Publishing/testArea
$RAPUMA project ENG-LATN-JAS backup restore --source_path ~/Publishing/testArea/MBJAS --target_path ~/Publishing/testArea

echo $RAPUMA settings ENG-LATN-JAS rapuma Projects/ENG-LATN-JAS mb_sourcePath ~/Publishing/testArea/MBJAS
$RAPUMA settings ENG-LATN-JAS rapuma Projects/ENG-LATN-JAS mb_sourcePath ~/Publishing/testArea/MBJAS

echo $RAPUMA group ENG-LATN-JAS james group final
$RAPUMA group ENG-LATN-JAS james group final

