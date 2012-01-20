#!/bin/sh

rpm PUB-MYMR-JAS project_remove
rpm PUB-MYMR-JAS project_create  -t book -n "SPT Test Book Project" -d PUB-MYMR-JAS

#rpm PUB-MYMR-JAS component_add   -c jas                  -t usfm
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

#rpm component_render -c jas
#rpm component_render -c apa
#rpm component_render -c simpleNotes



