#!/bin/sh

RAPUMA=~/Projects/rapuma/scripts/rapuma
cp ~/Projects/rapuma/resource/example/MBJAS.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/MBJAS.zip -d ~/Publishing/testArea
rm -rf ~/Publishing/testArea/ENG-LATN-JAS

echo $RAPUMA project ENG-LATN-JAS project remove
$RAPUMA project ENG-LATN-JAS project remove

echo $RAPUMA project ENG-LATN-JAS project add --media_type book --name "The Book of James in English" --target_path ~/Publishing/testArea
$RAPUMA project ENG-LATN-JAS project add --media_type book --name "The Book of James in English" --target_path ~/Publishing/testArea

echo $RAPUMA group ENG-LATN-JAS james group add --component_type usfm --cid_list jas --source_id mb --source_path ~/Publishing/testArea/MBJAS
$RAPUMA group ENG-LATN-JAS james group add --component_type usfm --cid_list jas --source_id mb --source_path ~/Publishing/testArea/MBJAS

echo $RAPUMA group ENG-LATN-JAS james group draft
$RAPUMA group ENG-LATN-JAS james group draft

