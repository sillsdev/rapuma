#!/bin/sh

rpm project_remove -i vwxyz
rpm project_create -t bookTex -n "Simple test project" -i vwxyz -d .
rpm component_add -c jas            -t usfmTex
rpm component_add -c apa            -t adminMSEAG
rpm component_add -c m01            -t vMapper
rpm component_add -c simpleNotes    -t projectNotes
rpm component_add -c system         -t illustrationsUsfm
rpm component_add -c hyp            -t hyphenTex
rpm component_add -c bodySet        -t fontSets
rpm component_render -c jas

