#!/bin/sh

cp ~/Projects/rapuma/resources/examples/KJV.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/KJV.zip -d ~/Publishing/testArea
echo
echo

echo COMMAND: rpm project ENG-LATN-KJVA project remove
rpm project ENG-LATN-KJVA project remove

echo COMMAND: rpm project ENG-LATN-KJVA project add --media_type book --name "The Gospels in King James English" --target_path ~/Publishing/testArea
rpm project ENG-LATN-KJVA project add --media_type book --name "The Gospels in King James English" --target_path ~/Publishing/testArea

echo COMMAND: rpm group ENG-LATN-KJVA GOSPELS group add --component_type usfm --cid_list "mat mrk luk jhn" --source_id kjv --source_path ~/Publishing/testArea/KJV/pt_environ
rpm group ENG-LATN-KJVA GOSPELS group add --component_type usfm --cid_list "mat mrk luk jhn" --source_id kjv --source_path ~/Publishing/testArea/KJV/pt_environ

echo COMMAND: rpm settings ENG-LATN-KJVA project Groups/GOSPELS tocInclude True
rpm settings ENG-LATN-KJVA project Groups/GOSPELS tocInclude True

echo COMMAND: rpm group ENG-LATN-KJVA GOSPELS group draft
rpm group ENG-LATN-KJVA GOSPELS group draft

echo COMMAND: rpm group ENG-LATN-KJVA TOC group add --component_type toc
rpm group ENG-LATN-KJVA TOC group add --component_type toc

#echo rpm group ENG-LATN-KJVA TOC group draft
#rpm group ENG-LATN-KJVA TOC group draft

