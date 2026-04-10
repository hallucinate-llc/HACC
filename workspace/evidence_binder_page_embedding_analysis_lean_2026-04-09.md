# Evidence Binder Page Embedding Analysis

Binder: [evidence_binder_full_lean_2026-04-09.pdf](/home/barberb/HACC/workspace/evidence_binder_full_lean_2026-04-09.pdf)

Device: `cuda`
Total binder pages scanned: `1123`
Source pages embedded: `945`

Method:

1. scan the merged binder page-by-page;
2. map each page back to exhibit/component using the build manifest;
3. extract page text with PyMuPDF and OCR fallback with Tesseract;
4. compute text embeddings with `all-MiniLM-L6-v2` on CUDA;
5. compute image embeddings with `clip-ViT-B-32` on CUDA;
6. cluster likely duplicates by cosine similarity.

## 1. Exact Text Page Duplicates

### exact text cluster 1

- binder page `733`: `Exhibit C` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_C_source.pdf` page `2`
- binder page `737`: `Exhibit D` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_D_source.pdf` page `2`

## 2. Exact Image Page Duplicates

### exact image cluster 1

- binder page `31`: `Exhibit M` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_M_source.pdf` page `1`
- binder page `49`: `Exhibit R` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_R_source_note.pdf` page `1`
- binder page `53`: `Exhibit T` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_T_source.pdf` page `1`
- binder page `79`: `Exhibit V` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_V_source.pdf` page `1`
- binder page `107`: `Exhibit X` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_X_source.pdf` page `1`
- binder page `111`: `Exhibit Y` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Y_source.pdf` page `1`
- binder page `115`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `1`
- binder page `680`: `Exhibit AA` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_AA_source.pdf` page `1`
- binder page `732`: `Exhibit C` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_C_source.pdf` page `1`
- binder page `736`: `Exhibit D` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_D_source.pdf` page `1`
- binder page `740`: `Exhibit E` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_E_source.pdf` page `1`
- binder page `744`: `Exhibit F` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_F_source.pdf` page `1`
- binder page `748`: `Exhibit G` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_G_source.pdf` page `1`
- binder page `752`: `Exhibit H` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_H_source.pdf` page `1`
- binder page `762`: `Exhibit K` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_K_source.pdf` page `1`
- binder page `794`: `Exhibit P` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_P_source_note.pdf` page `1`
- binder page `798`: `Exhibit Q` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_Q_source_note.pdf` page `1`
- binder page `805`: `Exhibit S` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_S_source.pdf` page `1`
- binder page `833`: `Exhibit V` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_V_source.pdf` page `1`
- binder page `854`: `Exhibit W` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_W_source.pdf` page `1`
- binder page `876`: `Exhibit AC` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_AC_source.pdf` page `1`
- binder page `1009`: `Exhibit A-18` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_18_source_note.pdf` page `1`
- binder page `1013`: `Exhibit A-19` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_19_source_note.pdf` page `1`
- binder page `1017`: `Exhibit A-20` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_20_source_note.pdf` page `1`
- binder page `1021`: `Exhibit B-1` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_B_1_source.pdf` page `1`

### exact image cluster 2

- binder page `264`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `150`
- binder page `265`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `151`
- binder page `266`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `152`
- binder page `267`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `153`
- binder page `268`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `154`
- binder page `271`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `157`
- binder page `273`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `159`
- binder page `274`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `160`

### exact image cluster 3

- binder page `190`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `76`
- binder page `335`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `221`
- binder page `403`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `289`
- binder page `413`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `299`
- binder page `424`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `310`
- binder page `493`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `379`
- binder page `669`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `555`

### exact image cluster 4

- binder page `991`: `Exhibit A-15` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_15_source.pdf` page `9`
- binder page `1030`: `Exhibit B-3` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_B_3_source.pdf` page `3`
- binder page `1035`: `Exhibit B-4` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_B_4_source.pdf` page `3`
- binder page `1040`: `Exhibit B-5` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_B_5_source.pdf` page `3`
- binder page `1045`: `Exhibit B-6` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_B_6_source.pdf` page `3`

### exact image cluster 5

- binder page `211`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `97`
- binder page `227`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `113`
- binder page `380`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `266`
- binder page `503`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `389`

### exact image cluster 6

- binder page `236`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `122`
- binder page `430`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `316`
- binder page `478`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `364`
- binder page `507`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `393`

### exact image cluster 7

- binder page `258`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `144`
- binder page `364`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `250`
- binder page `438`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `324`
- binder page `666`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `552`

### exact image cluster 8

- binder page `356`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `242`
- binder page `399`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `285`
- binder page `437`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `323`
- binder page `479`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `365`

### exact image cluster 9

- binder page `108`: `Exhibit X` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_X_source.pdf` page `2`
- binder page `681`: `Exhibit AA` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_AA_source.pdf` page `2`
- binder page `855`: `Exhibit W` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_W_source.pdf` page `2`

### exact image cluster 10

- binder page `146`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `32`
- binder page `633`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `519`
- binder page `649`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `535`

### exact image cluster 11

- binder page `149`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `35`
- binder page `303`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `189`
- binder page `460`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `346`

### exact image cluster 12

- binder page `160`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `46`
- binder page `410`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `296`
- binder page `449`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `335`

### exact image cluster 13

- binder page `172`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `58`
- binder page `239`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `125`
- binder page `341`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `227`

### exact image cluster 14

- binder page `177`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `63`
- binder page `241`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `127`
- binder page `635`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `521`

### exact image cluster 15

- binder page `248`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `134`
- binder page `340`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `226`
- binder page `619`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `505`

### exact image cluster 16

- binder page `253`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `139`
- binder page `367`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `253`
- binder page `629`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `515`

### exact image cluster 17

- binder page `284`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `170`
- binder page `475`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `361`
- binder page `618`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `504`

### exact image cluster 18

- binder page `288`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `174`
- binder page `617`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `503`
- binder page `645`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `531`

### exact image cluster 19

- binder page `342`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `228`
- binder page `407`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `293`
- binder page `434`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `320`

### exact image cluster 20

- binder page `446`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `332`
- binder page `583`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `469`
- binder page `672`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `558`

### exact image cluster 21

- binder page `1010`: `Exhibit A-18` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_18_source_note.pdf` page `2`
- binder page `1014`: `Exhibit A-19` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_19_source_note.pdf` page `2`
- binder page `1018`: `Exhibit A-20` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_20_source_note.pdf` page `2`

### exact image cluster 22

- binder page `9`: `Exhibit C` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_C_source.pdf` page `3`
- binder page `13`: `Exhibit D` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_D_source.pdf` page `2`

### exact image cluster 23

- binder page `57`: `Exhibit T` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_T_source.pdf` page `5`
- binder page `90`: `Exhibit V` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_V_source.pdf` page `12`

### exact image cluster 24

- binder page `62`: `Exhibit T` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_T_source.pdf` page `10`
- binder page `81`: `Exhibit V` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_V_source.pdf` page `3`

### exact image cluster 25

- binder page `156`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `42`
- binder page `183`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `69`

### exact image cluster 26

- binder page `166`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `52`
- binder page `290`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `176`

### exact image cluster 27

- binder page `170`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `56`
- binder page `611`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `497`

### exact image cluster 28

- binder page `176`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `62`
- binder page `214`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `100`

### exact image cluster 29

- binder page `185`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `71`
- binder page `807`: `Exhibit S` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_S_source.pdf` page `3`

### exact image cluster 30

- binder page `187`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `73`
- binder page `602`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `488`

### exact image cluster 31

- binder page `189`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `75`
- binder page `599`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `485`

### exact image cluster 32

- binder page `197`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `83`
- binder page `429`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `315`

### exact image cluster 33

- binder page `205`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `91`
- binder page `471`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `357`

### exact image cluster 34

- binder page `207`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `93`
- binder page `450`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `336`

### exact image cluster 35

- binder page `208`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `94`
- binder page `252`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `138`

### exact image cluster 36

- binder page `218`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `104`
- binder page `400`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `286`

### exact image cluster 37

- binder page `226`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `112`
- binder page `485`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `371`

### exact image cluster 38

- binder page `233`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `119`
- binder page `418`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `304`

### exact image cluster 39

- binder page `234`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `120`
- binder page `501`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `387`

### exact image cluster 40

- binder page `235`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `121`
- binder page `558`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `444`

### exact image cluster 41

- binder page `237`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `123`
- binder page `361`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `247`

### exact image cluster 42

- binder page `238`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `124`
- binder page `623`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `509`

### exact image cluster 43

- binder page `244`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `130`
- binder page `447`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `333`

### exact image cluster 44

- binder page `246`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `132`
- binder page `325`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `211`

### exact image cluster 45

- binder page `257`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `143`
- binder page `487`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `373`

### exact image cluster 46

- binder page `287`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `173`
- binder page `571`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `457`

### exact image cluster 47

- binder page `320`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `206`
- binder page `477`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `363`

### exact image cluster 48

- binder page `327`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `213`
- binder page `549`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `435`

### exact image cluster 49

- binder page `332`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `218`
- binder page `468`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `354`

### exact image cluster 50

- binder page `339`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `225`
- binder page `415`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `301`

### exact image cluster 51

- binder page `346`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `232`
- binder page `509`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `395`

### exact image cluster 52

- binder page `347`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `233`
- binder page `603`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `489`

### exact image cluster 53

- binder page `370`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `256`
- binder page `428`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `314`

### exact image cluster 54

- binder page `374`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `260`
- binder page `620`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `506`

### exact image cluster 55

- binder page `386`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `272`
- binder page `594`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `480`

### exact image cluster 56

- binder page `404`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `290`
- binder page `656`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `542`

### exact image cluster 57

- binder page `439`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `325`
- binder page `600`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `486`

### exact image cluster 58

- binder page `452`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `338`
- binder page `568`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `454`

### exact image cluster 59

- binder page `453`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `339`
- binder page `553`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `439`

### exact image cluster 60

- binder page `462`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `348`
- binder page `490`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `376`

### exact image cluster 61

- binder page `464`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `350`
- binder page `647`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `533`

### exact image cluster 62

- binder page `469`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `355`
- binder page `676`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `562`

### exact image cluster 63

- binder page `481`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `367`
- binder page `674`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `560`

### exact image cluster 64

- binder page `482`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `368`
- binder page `646`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `532`

### exact image cluster 65

- binder page `546`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `432`
- binder page `562`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `448`

### exact image cluster 66

- binder page `554`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `440`
- binder page `1121`: `Exhibit C-7` / `source` / `Housing Duty Appendix`
  source: `housing_duty_appendix_exhibit_C_7_source.pdf` page `1`

### exact image cluster 67

- binder page `580`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `466`
- binder page `637`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `523`

### exact image cluster 68

- binder page `643`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `529`
- binder page `664`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `550`

### exact image cluster 69

- binder page `719`: `Exhibit A` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_A_source.pdf` page `36`
- binder page `725`: `Exhibit A` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_A_source.pdf` page `42`

### exact image cluster 70

- binder page `729`: `Exhibit B` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_B_source.pdf` page `2`
- binder page `873`: `Exhibit AB` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_AB_source.pdf` page `2`

### exact image cluster 71

- binder page `733`: `Exhibit C` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_C_source.pdf` page `2`
- binder page `737`: `Exhibit D` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_D_source.pdf` page `2`

### exact image cluster 72

- binder page `741`: `Exhibit E` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_E_source.pdf` page `2`
- binder page `745`: `Exhibit F` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_F_source.pdf` page `2`

### exact image cluster 73

- binder page `749`: `Exhibit G` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_G_source.pdf` page `2`
- binder page `753`: `Exhibit H` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_H_source.pdf` page `2`

### exact image cluster 74

- binder page `791`: `Exhibit O` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_O_source.pdf` page `2`
- binder page `882`: `Authority Exhibit 1` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_authority_exhibit_1_source.pdf` page `3`

### exact image cluster 75

- binder page `795`: `Exhibit P` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_P_source_note.pdf` page `2`
- binder page `799`: `Exhibit Q` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_Q_source_note.pdf` page `2`

### exact image cluster 76

- binder page `986`: `Exhibit A-15` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_15_source.pdf` page `4`
- binder page `993`: `Exhibit A-15` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_15_source.pdf` page `11`

### exact image cluster 77

- binder page `1039`: `Exhibit B-5` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_B_5_source.pdf` page `2`
- binder page `1049`: `Exhibit B-7` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_B_7_source.pdf` page `2`

## 3. Likely Near-Text Page Duplicates

### near text cluster 1

- binder page `31`: `Exhibit M` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_M_source.pdf` page `1`
  top text similarity: `1.0`
- binder page `49`: `Exhibit R` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_R_source_note.pdf` page `1`
  top text similarity: `1.0`
- binder page `53`: `Exhibit T` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_T_source.pdf` page `1`
  top text similarity: `1.0`
- binder page `79`: `Exhibit V` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_V_source.pdf` page `1`
  top text similarity: `1.0`
- binder page `107`: `Exhibit X` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_X_source.pdf` page `1`
  top text similarity: `1.0`
- binder page `111`: `Exhibit Y` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Y_source.pdf` page `1`
  top text similarity: `1.0`
- binder page `115`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `1`
  top text similarity: `1.0`
- binder page `680`: `Exhibit AA` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_AA_source.pdf` page `1`
  top text similarity: `1.0`
- binder page `732`: `Exhibit C` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_C_source.pdf` page `1`
  top text similarity: `1.0`
- binder page `736`: `Exhibit D` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_D_source.pdf` page `1`
  top text similarity: `1.0`
- binder page `740`: `Exhibit E` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_E_source.pdf` page `1`
  top text similarity: `1.0`
- binder page `744`: `Exhibit F` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_F_source.pdf` page `1`
  top text similarity: `1.0`
- binder page `748`: `Exhibit G` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_G_source.pdf` page `1`
  top text similarity: `1.0`
- binder page `752`: `Exhibit H` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_H_source.pdf` page `1`
  top text similarity: `1.0`
- binder page `762`: `Exhibit K` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_K_source.pdf` page `1`
  top text similarity: `1.0`
- binder page `794`: `Exhibit P` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_P_source_note.pdf` page `1`
  top text similarity: `1.0`
- binder page `798`: `Exhibit Q` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_Q_source_note.pdf` page `1`
  top text similarity: `1.0`
- binder page `805`: `Exhibit S` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_S_source.pdf` page `1`
  top text similarity: `1.0`
- binder page `833`: `Exhibit V` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_V_source.pdf` page `1`
  top text similarity: `1.0`
- binder page `854`: `Exhibit W` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_W_source.pdf` page `1`
  top text similarity: `1.0`
- binder page `876`: `Exhibit AC` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_AC_source.pdf` page `1`
  top text similarity: `1.0`
- binder page `1009`: `Exhibit A-18` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_18_source_note.pdf` page `1`
  top text similarity: `1.0`
- binder page `1013`: `Exhibit A-19` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_19_source_note.pdf` page `1`
  top text similarity: `1.0`
- binder page `1017`: `Exhibit A-20` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_20_source_note.pdf` page `1`
  top text similarity: `1.0`
- binder page `1021`: `Exhibit B-1` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_B_1_source.pdf` page `1`
  top text similarity: `1.0`

### near text cluster 2

- binder page `985`: `Exhibit A-15` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_15_source.pdf` page `3`
  top text similarity: `0.9998`
- binder page `986`: `Exhibit A-15` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_15_source.pdf` page `4`
  top text similarity: `0.9994`
- binder page `991`: `Exhibit A-15` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_15_source.pdf` page `9`
  top text similarity: `0.9998`
- binder page `992`: `Exhibit A-15` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_15_source.pdf` page `10`
  top text similarity: `0.9998`
- binder page `993`: `Exhibit A-15` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_15_source.pdf` page `11`
  top text similarity: `0.9998`

### near text cluster 3

- binder page `66`: `Exhibit T` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_T_source.pdf` page `14`
  top text similarity: `0.9924`
- binder page `68`: `Exhibit T` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_T_source.pdf` page `16`
  top text similarity: `1.0`
- binder page `90`: `Exhibit V` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_V_source.pdf` page `12`
  top text similarity: `1.0`
- binder page `840`: `Exhibit V` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_V_source.pdf` page `8`
  top text similarity: `1.0`

### near text cluster 4

- binder page `1003`: `Exhibit A-17` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_17_source.pdf` page `4`
  top text similarity: `0.9978`
- binder page `1004`: `Exhibit A-17` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_17_source.pdf` page `5`
  top text similarity: `0.9979`
- binder page `1005`: `Exhibit A-17` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_17_source.pdf` page `6`
  top text similarity: `0.9979`
- binder page `1006`: `Exhibit A-17` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_17_source.pdf` page `7`
  top text similarity: `0.9979`

### near text cluster 5

- binder page `9`: `Exhibit C` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_C_source.pdf` page `3`
  top text similarity: `0.9881`
- binder page `13`: `Exhibit D` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_D_source.pdf` page `2`
  top text similarity: `0.9881`

### near text cluster 6

- binder page `72`: `Exhibit T` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_T_source.pdf` page `20`
  top text similarity: `1.0`
- binder page `844`: `Exhibit V` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_V_source.pdf` page `12`
  top text similarity: `1.0`

### near text cluster 7

- binder page `733`: `Exhibit C` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_C_source.pdf` page `2`
  top text similarity: `1.0`
- binder page `737`: `Exhibit D` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_D_source.pdf` page `2`
  top text similarity: `1.0`

## 4. Likely Near-Image Page Duplicates

### near image cluster 1

- binder page `31`: `Exhibit M` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_M_source.pdf` page `1`
  top image similarity: `1.0`
- binder page `49`: `Exhibit R` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_R_source_note.pdf` page `1`
  top image similarity: `1.0`
- binder page `53`: `Exhibit T` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_T_source.pdf` page `1`
  top image similarity: `1.0`
- binder page `79`: `Exhibit V` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_V_source.pdf` page `1`
  top image similarity: `1.0`
- binder page `107`: `Exhibit X` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_X_source.pdf` page `1`
  top image similarity: `1.0`
- binder page `111`: `Exhibit Y` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Y_source.pdf` page `1`
  top image similarity: `1.0`
- binder page `115`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `1`
  top image similarity: `1.0`
- binder page `680`: `Exhibit AA` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_AA_source.pdf` page `1`
  top image similarity: `1.0`
- binder page `732`: `Exhibit C` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_C_source.pdf` page `1`
  top image similarity: `1.0`
- binder page `736`: `Exhibit D` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_D_source.pdf` page `1`
  top image similarity: `1.0`
- binder page `740`: `Exhibit E` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_E_source.pdf` page `1`
  top image similarity: `1.0`
- binder page `744`: `Exhibit F` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_F_source.pdf` page `1`
  top image similarity: `1.0`
- binder page `748`: `Exhibit G` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_G_source.pdf` page `1`
  top image similarity: `1.0`
- binder page `752`: `Exhibit H` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_H_source.pdf` page `1`
  top image similarity: `1.0`
- binder page `762`: `Exhibit K` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_K_source.pdf` page `1`
  top image similarity: `1.0`
- binder page `791`: `Exhibit O` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_O_source.pdf` page `2`
  top image similarity: `1.0`
- binder page `794`: `Exhibit P` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_P_source_note.pdf` page `1`
  top image similarity: `1.0`
- binder page `798`: `Exhibit Q` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_Q_source_note.pdf` page `1`
  top image similarity: `1.0`
- binder page `805`: `Exhibit S` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_S_source.pdf` page `1`
  top image similarity: `1.0`
- binder page `833`: `Exhibit V` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_V_source.pdf` page `1`
  top image similarity: `1.0`
- binder page `854`: `Exhibit W` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_W_source.pdf` page `1`
  top image similarity: `1.0`
- binder page `869`: `Exhibit AA` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_AA_source.pdf` page `2`
  top image similarity: `1.0`
- binder page `876`: `Exhibit AC` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_AC_source.pdf` page `1`
  top image similarity: `1.0`
- binder page `891`: `Exhibit A-1` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_1_source.pdf` page `2`
  top image similarity: `1.0`
- binder page `895`: `Exhibit A-2` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_2_source.pdf` page `2`
  top image similarity: `1.0`
- binder page `923`: `Exhibit A-5` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_5_source.pdf` page `4`
  top image similarity: `1.0`
- binder page `991`: `Exhibit A-15` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_15_source.pdf` page `9`
  top image similarity: `1.0`
- binder page `1009`: `Exhibit A-18` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_18_source_note.pdf` page `1`
  top image similarity: `1.0`
- binder page `1013`: `Exhibit A-19` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_19_source_note.pdf` page `1`
  top image similarity: `1.0`
- binder page `1017`: `Exhibit A-20` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_20_source_note.pdf` page `1`
  top image similarity: `1.0`
- binder page `1021`: `Exhibit B-1` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_B_1_source.pdf` page `1`
  top image similarity: `1.0`
- binder page `1030`: `Exhibit B-3` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_B_3_source.pdf` page `3`
  top image similarity: `1.0`
- binder page `1035`: `Exhibit B-4` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_B_4_source.pdf` page `3`
  top image similarity: `1.0`
- binder page `1040`: `Exhibit B-5` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_B_5_source.pdf` page `3`
  top image similarity: `1.0`
- binder page `1045`: `Exhibit B-6` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_B_6_source.pdf` page `3`
  top image similarity: `1.0`
- binder page `1050`: `Exhibit B-7` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_B_7_source.pdf` page `3`
  top image similarity: `1.0`

### near image cluster 2

- binder page `795`: `Exhibit P` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_P_source_note.pdf` page `2`
  top image similarity: `1.0`
- binder page `799`: `Exhibit Q` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_Q_source_note.pdf` page `2`
  top image similarity: `1.0`
- binder page `1010`: `Exhibit A-18` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_18_source_note.pdf` page `2`
  top image similarity: `0.9996`
- binder page `1014`: `Exhibit A-19` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_19_source_note.pdf` page `2`
  top image similarity: `0.9996`
- binder page `1018`: `Exhibit A-20` / `source` / `Supplemental Background Appendix`
  source: `supplemental_background_appendix_exhibit_A_20_source_note.pdf` page `2`
  top image similarity: `0.9994`

### near image cluster 3

- binder page `197`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `83`
  top image similarity: `0.9924`
- binder page `258`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `144`
  top image similarity: `0.9938`
- binder page `555`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `441`
  top image similarity: `0.9938`

### near image cluster 4

- binder page `60`: `Exhibit T` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_T_source.pdf` page `8`
  top image similarity: `0.9927`
- binder page `66`: `Exhibit T` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_T_source.pdf` page `14`
  top image similarity: `0.9927`

### near image cluster 5

- binder page `108`: `Exhibit X` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_X_source.pdf` page `2`
  top image similarity: `0.9944`
- binder page `681`: `Exhibit AA` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_AA_source.pdf` page `2`
  top image similarity: `0.9944`

### near image cluster 6

- binder page `187`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `73`
  top image similarity: `0.9926`
- binder page `576`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `462`
  top image similarity: `0.9926`

### near image cluster 7

- binder page `226`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `112`
  top image similarity: `0.9926`
- binder page `325`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `211`
  top image similarity: `0.9926`

### near image cluster 8

- binder page `242`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `128`
  top image similarity: `0.992`
- binder page `409`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `295`
  top image similarity: `0.992`

### near image cluster 9

- binder page `351`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `237`
  top image similarity: `0.9921`
- binder page `353`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `239`
  top image similarity: `0.9921`

### near image cluster 10

- binder page `484`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `370`
  top image similarity: `0.9933`
- binder page `562`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `448`
  top image similarity: `0.9933`

### near image cluster 11

- binder page `503`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `389`
  top image similarity: `0.9922`
- binder page `556`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `442`
  top image similarity: `0.9922`

### near image cluster 12

- binder page `520`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `406`
  top image similarity: `0.994`
- binder page `532`: `Exhibit Z` / `source` / `Shared Housing / State-Court Binder`
  source: `shared_housing_state_court_binder_exhibit_Z_source.pdf` page `418`
  top image similarity: `0.994`

### near image cluster 13

- binder page `733`: `Exhibit C` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_C_source.pdf` page `2`
  top image similarity: `1.0`
- binder page `737`: `Exhibit D` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_D_source.pdf` page `2`
  top image similarity: `1.0`

### near image cluster 14

- binder page `741`: `Exhibit E` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_E_source.pdf` page `2`
  top image similarity: `0.9924`
- binder page `745`: `Exhibit F` / `source` / `Shared Motion / Probate / Sanctions Binder`
  source: `shared_motion_probate_sanctions_binder_exhibit_F_source.pdf` page `2`
  top image similarity: `0.9924`

## 5. Use

Use exact groups first for safe deduplication.
Use near groups as review targets before removing any page or source component.
When collapsing a duplicate source, keep the tab cover page and exhibit cover page and incorporate the master source by reference.
