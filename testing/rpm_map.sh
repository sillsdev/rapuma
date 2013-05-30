#!/bin/sh

cp ~/Projects/rapuma/resources/examples/MAPS.zip ~/Publishing/testArea
unzip -o ~/Publishing/testArea/MAPS.zip -d ~/Publishing/testArea

rpm project MAPTEST project remove

rpm project MAPTEST project add --media_type book --name "Map render testing project" --target_path ~/Publishing/testArea

rpm group MAPTEST maps group add --component_type map --cid_list "HolyLand.png PaulsJourneys.png" --source_id maps --source_path ~/Publishing/testArea/MAPS

rpm group MAPTEST maps group draft
