#!/bin/sh

rpm project_remove -i PUB-MYMR-JAS
rpm project_create -i PUB-MYMR-JAS -t book -n "SPT Test Book Project" -d PUB-MYMR-JAS

rpm component_add -i PUB-MYMR-JAS -c jas -t usfm
#rpm component_add   -c apa                  -t adminMSEAG
#rpm component_add   -c simpleNotes          -t projectNotes

#rpm auxiliary_add   -a contentMacros        -t usfmTex
#rpm auxiliary_add   -a contentFont          -t fontsTex
#rpm auxiliary_add   -a frontFont            -t fontsTex
#rpm auxiliary_add   -a contentIllustrations -t illustrationsUsfm
#rpm auxiliary_add   -a contentHyphen        -t hyphenTex
#rpm auxiliary_add   -a contentFormat        -t pageFormat
#rpm auxiliary_add   -a contentStyle         -t stylesUsfm


#rpm font_set        -a frontFont            -f Padauk               -r primary
#rpm font_set        -a contentFont          -f Padauk               -r primary
#rpm font_set        -a contentFont          -f CharisSIL

#rpm component_render -i PUB-MYMR-JAS -c jas
#rpm component_render -c apa
#rpm component_render -c simpleNotes



