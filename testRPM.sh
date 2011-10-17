#!/bin/sh

rpm project_remove  -i vwxyz
rpm project_create  -t bookTex -n "Simple test project" -i vwxyz -d .

rpm auxiliary_add   -a contentFont      -t fontSets
rpm auxiliary_add   -a mapFont          -t fontSets
rpm auxiliary_add   -a system           -t illustrationsUsfm
rpm auxiliary_add   -a hyp              -t hyphenTex
rpm auxiliary_add   -a contentComp      -t pageCompSets
rpm auxiliary_add   -a contentStyle     -t styleSets
rpm component_add   -c jas              -t usfmTex
rpm component_add   -c apa              -t adminMSEAG
rpm component_add   -c m01              -t vMapper
rpm component_add   -c simpleNotes      -t projectNotes
rpm set_font        -a contentFont      -f CharisSIL            -r primary

#rpm component_render -c apa
#rpm component_render -c m01
#rpm component_render -c simpleNotes

rpm component_render -c jas



