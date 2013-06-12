#!/bin/sh

cp ~/Projects/rapuma/resources/examples/KJV.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/KJV.zip -d ~/Publishing/testArea

rpm project ENG-LATN-KJVA project remove

rpm project ENG-LATN-KJVA project add --media_type book --name "The Gospels in King James English" --target_path ~/Publishing/testArea

rpm group ENG-LATN-KJVA GOSPELS group add --component_type usfm --cid_list "mat mrk luk jhn" --source_id kjv --source_path ~/Publishing/testArea/KJV/pt_environ

rpm settings ENG-LATN-KJVA project Groups/GOSPELS tocInclude True

rpm group ENG-LATN-KJVA TOC group add --component_type toc

rpm group ENG-LATN-KJVA GOSPELS group draft
