#!/bin/sh

RAPUMA=~/Projects/rapuma/scripts/rapuma
cp ~/Projects/rapuma/resource/example/MBJAS.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/MBJAS.zip -d ~/Publishing/testArea
rm -rf ~/Publishing/testArea/ENG-LATN-JAS

# Remove any residual project data (start fresh)
echo    $RAPUMA project ENG-LATN-JAS project remove
        $RAPUMA project ENG-LATN-JAS project remove
# Create project based on template
echo    $RAPUMA project ENG-LATN-JAS template restore --source_path ~/Publishing/testArea/MBJAS/eng-latn-tmpl.zip --target_path ~/Publishing/testArea
        $RAPUMA project ENG-LATN-JAS template restore --source_path ~/Publishing/testArea/MBJAS/eng-latn-tmpl.zip --target_path ~/Publishing/testArea
# Add MB source text
echo    $RAPUMA group ENG-LATN-JAS mb group add --component_type usfm --cid_list jas --source_id mb --source_path ~/Publishing/testArea/MBJAS/sources/mb
        $RAPUMA group ENG-LATN-JAS mb group add --component_type usfm --cid_list jas --source_id mb --source_path ~/Publishing/testArea/MBJAS/sources/mb
# Add KJV source text
echo    $RAPUMA group ENG-LATN-JAS kjv group add --component_type usfm --cid_list jas --source_id kjv --source_path ~/Publishing/testArea/MBJAS/sources/kjv
        $RAPUMA group ENG-LATN-JAS kjv group add --component_type usfm --cid_list jas --source_id kjv --source_path ~/Publishing/testArea/MBJAS/sources/kjv
# Add KYU source text
echo    $RAPUMA group ENG-LATN-JAS kyu group add --component_type usfm --cid_list jas --source_id kyu --source_path ~/Publishing/testArea/MBJAS/sources/kyu
        $RAPUMA group ENG-LATN-JAS kyu group add --component_type usfm --cid_list jas --source_id kyu --source_path ~/Publishing/testArea/MBJAS/sources/kyu
# Render MB text
echo    $RAPUMA group ENG-LATN-JAS mb group proof
        $RAPUMA group ENG-LATN-JAS mb group proof
# Render KJV text
echo    $RAPUMA group ENG-LATN-JAS kjv group proof
        $RAPUMA group ENG-LATN-JAS kjv group proof
# Render KYU text
echo    $RAPUMA group ENG-LATN-JAS kyu group proof
        $RAPUMA group ENG-LATN-JAS kyu group proof

