#!/bin/sh

cp ~/Projects/rapuma/resource/example/MBJAS.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/MBJAS.zip -d ~/Publishing/testArea

rpm project ENG-LATN-JAS project remove

rpm project ENG-LATN-JAS project add --media_type book --name "The Book of James in English" --target_path ~/Publishing/testArea

rpm group ENG-LATN-JAS james group add --component_type usfm --cid_list jas --source_id mb --source_path ~/Publishing/testArea/MBJAS

rpm group ENG-LATN-JAS james group draft
