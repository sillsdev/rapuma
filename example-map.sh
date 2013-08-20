#!/bin/sh

mkdir ~/Publishing/testArea
cp resources/examples/MAPS.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/MAPS.zip -d ~/Publishing/testArea

rapuma project MAPTEST project remove

rapuma project MAPTEST project add --media_type book --name "Map render testing project" --target_path ~/Publishing/testArea

rapuma group MAPTEST maps group add --component_type map --cid_list "HolyLand.png PaulsJourneys.png" --source_id maps --source_path ~/Publishing/testArea/MAPS

rapuma group MAPTEST maps group draft
