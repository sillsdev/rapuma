#!/bin/sh

rpm project_remove  -i vwxyz
rpm project_create  -t bookTex -n "Simple test project" -i vwxyz -d .

rpm auxiliary_add   -a content      -t fontsTex
rpm auxiliary_add   -a map          -t fontsTex
rpm auxiliary_add   -a system       -t illustrationsUsfm
rpm auxiliary_add   -a content      -t hyphenTex
rpm auxiliary_add   -a content      -t pageCompTex
rpm auxiliary_add   -a content      -t stylesUsfm
rpm component_add   -c jas          -t usfm
rpm component_add   -c apa          -t adminMSEAG
rpm component_add   -c m01          -t vMapper
rpm component_add   -c simpleNotes  -t projectNotes
rpm set_font        -a content      -f CharisSIL            -r primary

#rpm component_render -c apa
#rpm component_render -c m01
#rpm component_render -c simpleNotes

rpm component_render -c jas



