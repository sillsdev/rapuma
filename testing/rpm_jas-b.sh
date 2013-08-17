#!/bin/sh

cp ~/Projects/rapuma/resource/example/MBJAS.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/MBJAS.zip -d ~/Publishing/testArea
rm -rf ~/Publishing/testArea/ENG-LATN-JAS

echo rpm project ENG-LATN-JAS project remove
rpm project ENG-LATN-JAS project remove

echo rpm project ENG-LATN-JAS backup restore --source_path ~/Publishing/testArea/MBJAS --target_path ~/Publishing/testArea
rpm project ENG-LATN-JAS backup restore --source_path ~/Publishing/testArea/MBJAS --target_path ~/Publishing/testArea

echo rpm settings ENG-LATN-JAS rapuma Projects/ENG-LATN-JAS mb_sourcePath ~/Publishing/testArea/MBJAS
rpm settings ENG-LATN-JAS rapuma Projects/ENG-LATN-JAS mb_sourcePath ~/Publishing/testArea/MBJAS

echo rpm group ENG-LATN-JAS james group final
rpm group ENG-LATN-JAS james group final

