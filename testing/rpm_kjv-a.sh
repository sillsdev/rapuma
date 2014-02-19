#!/bin/sh

cp ~/Projects/rapuma/resources/examples/KJV.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/KJV.zip -d ~/Publishing/testArea
echo
echo

echo COMMAND: rapuma project ENG-LATN-KJVA project remove
rapuma project ENG-LATN-KJVA project remove

echo COMMAND: rapuma project ENG-LATN-KJVA project add --media_type book --name "The Gospels in King James English" --target_path ~/Publishing/testArea
rapuma project ENG-LATN-KJVA project add --media_type book --name "The Gospels in King James English" --target_path ~/Publishing/testArea

echo COMMAND: rapuma group ENG-LATN-KJVA GOSPELS group add --component_type usfm --cid_list "mat mrk luk jhn" --source_id kjv --source_path ~/Publishing/testArea/KJV/pt_environ
rapuma group ENG-LATN-KJVA GOSPELS group add --component_type usfm --cid_list "mat mrk luk jhn" --source_id kjv --source_path ~/Publishing/testArea/KJV/pt_environ

echo COMMAND: rapuma settings ENG-LATN-KJVA project Groups/GOSPELS tocInclude True
rapuma settings ENG-LATN-KJVA project Groups/GOSPELS tocInclude True

echo COMMAND: rapuma group ENG-LATN-KJVA GOSPELS group draft
rapuma group ENG-LATN-KJVA GOSPELS group draft

echo COMMAND: rapuma group ENG-LATN-KJVA TOC group add --component_type toc
rapuma group ENG-LATN-KJVA TOC group add --component_type toc

#echo rapuma group ENG-LATN-KJVA TOC group draft
#rapuma group ENG-LATN-KJVA TOC group draft

