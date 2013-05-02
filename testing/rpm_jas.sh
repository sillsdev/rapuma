#!/bin/sh

cp ~/Projects/rapuma/resources/examples/MBJAS.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/MBJAS.zip -d ~/Publishing/testArea

rpm project ENG-LATN-JAS --manage remove-project

rpm project ENG-LATN-JAS --manage add-project --media_type book --name "The Book of James in English" --target_path ~/Publishing/testArea

rpm group ENG-LATN-JAS james --component_type usfm --manage add-group --cid_list jas --source_id mb --source_path ~/Publishing/testArea/MBJAS

rpm group ENG-LATN-JAS james --manage render-draft
