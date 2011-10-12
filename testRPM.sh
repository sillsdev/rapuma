#!/bin/sh

rpm project_remove -i vwxyz
rpm project_create -t bookTex -n "Simple test project" -i vwxyz -d .

rpm auxiliary_add -a bodySet        -t fontSets
rpm auxiliary_add -a mapSet         -t fontSets
rpm auxiliary_add -a system         -t illustrationsUsfm
rpm auxiliary_add -a hyp            -t hyphenTex
rpm component_add -c jas            -t usfmTex
rpm component_add -c apa            -t adminMSEAG
rpm component_add -c m01            -t vMapper
rpm component_add -c simpleNotes    -t projectNotes

#rpm component_render -c bodySet
#rpm component_render -c mapSet
#rpm component_render -c hyp
#rpm component_render -c system
#rpm component_render -c apa
#rpm component_render -c m01
#rpm component_render -c simpleNotes
#rpm component_render -c jas



