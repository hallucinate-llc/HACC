# Evidence Binder Duplicate Analysis

This note compares exhibit sources across the evidence binder using exact-source grouping plus text/OCR and image fingerprinting.

Method:

1. parse original `SOURCE FILE` values from exhibit cover pages;
2. extract text from `.md`, `.txt`, `.eml`, and `.pdf`;
3. OCR images and image-based PDFs where needed;
4. compute normalized-text hashes, text simhashes, and image perceptual hashes;
5. report exact duplicates and likely near duplicates.

Records analyzed: `89`
Existing path-backed exhibit sources analyzed: `84`

## 1. Exact Source Reuse

### message.eml

Source: [/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml](/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml)

- `Exhibit AA` in `core_housing`
- `Exhibit V` in `core_housing`
- `Exhibit X` in `core_housing`
- `Exhibit W` in `shared_motion_probate_batch4`

### uid_660753_Mon--17-Nov-2025-22-59-36--0000_New-text-message-from-solomon--503--381-6911.eml

Source: [/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_660753_Mon--17-Nov-2025-22-59-36--0000_New-text-message-from-solomon--503--381-6911.eml](/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_660753_Mon--17-Nov-2025-22-59-36--0000_New-text-message-from-solomon--503--381-6911.eml)

- `Exhibit C` in `shared_motion_probate_batch1`
- `Exhibit D` in `shared_motion_probate_batch1`

## 2. Exact Text/OCR Duplicates

### Text group anchored by `message.eml`

- `Exhibit AA` in `core_housing`: [message.eml](/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml)
- `Exhibit V` in `core_housing`: [message.eml](/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml)
- `Exhibit X` in `core_housing`: [message.eml](/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml)
- `Exhibit W` in `shared_motion_probate_batch4`: [message.eml](/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml)

Excerpt: `subject re allegations of fraud jc household from benjamin barber starworks5 gmail com to ferron ashley aferron clackamas us cc date mon 02 feb 2026 16 42 27 0800 i just witnessed a clackamas county official threatening `

### Text group anchored by `waterleaf_application.png`

- `Exhibit W` in `core_housing`: [waterleaf_application.png](/home/barberb/HACC/evidence/history/waterleaf_application.png)
- `Exhibit B-1` in `supplemental_background_appendix`: [waterleaf_application.png](/home/barberb/HACC/evidence/paper documents/waterleaf_application.png)

Excerpt: `mig bia cg g g 1o gigi gi4 g6 gioaeaeeaeei scioooio ff ih x oo x es 23 waterleafbrighthaven securecafe com onlineleasing waterleaf1 multiloginwrapper aspx allowredirect 1 e ce 3 8 sk ssr sse cs sg hi benjamin see account`

### Text group anchored by `uid_660753_Mon--17-Nov-2025-22-59-36--0000_New-text-message-from-solomon--503--381-6911.eml`

- `Exhibit C` in `shared_motion_probate_batch1`: [uid_660753_Mon--17-Nov-2025-22-59-36--0000_New-text-message-from-solomon--503--381-6911.eml](/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_660753_Mon--17-Nov-2025-22-59-36--0000_New-text-message-from-solomon--503--381-6911.eml)
- `Exhibit D` in `shared_motion_probate_batch1`: [uid_660753_Mon--17-Nov-2025-22-59-36--0000_New-text-message-from-solomon--503--381-6911.eml](/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_660753_Mon--17-Nov-2025-22-59-36--0000_New-text-message-from-solomon--503--381-6911.eml)

Excerpt: `subject new text message from solomon 503 381 6911 from solomon sms 19712700855 15033816911 t6hsc2dvkz txt voice google com to starworks5 gmail com cc date mon 17 nov 2025 22 59 36 0000 https voice google com yes and fra`

## 3. Likely Near-Text Duplicates

### Near-text cluster 1

- `Exhibit AA` in `core_housing`: [message.eml](/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml)
  - normalized text length: `39481`
  - text simhash: `ee3236e7f8210062`
- `Exhibit V` in `core_housing`: [message.eml](/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml)
  - normalized text length: `39481`
  - text simhash: `ee3236e7f8210062`
- `Exhibit X` in `core_housing`: [message.eml](/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml)
  - normalized text length: `39481`
  - text simhash: `ee3236e7f8210062`
- `Exhibit T` in `secondary_housing`: [message.eml](/home/barberb/HACC/evidence/email_imports/starworks5-fraud-reimport-20260404/0047-Re-Allegations-of-Fraud---JC-Household-CAMTdTS-00cFTv4dFf8yZ3NpPztCKwr2LB-on4Xxz-BFEv9_5jA-mail.gmail.com/message.eml)
  - normalized text length: `40459`
  - text simhash: `6e3a36e7f8210042`
- `Exhibit W` in `shared_motion_probate_batch4`: [message.eml](/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml)
  - normalized text length: `39481`
  - text simhash: `ee3236e7f8210062`

### Near-text cluster 2

- `Exhibit W` in `core_housing`: [waterleaf_application.png](/home/barberb/HACC/evidence/history/waterleaf_application.png)
  - normalized text length: `564`
  - text simhash: `da8f1e3f7c06a6e2`
- `Exhibit B-1` in `supplemental_background_appendix`: [waterleaf_application.png](/home/barberb/HACC/evidence/paper documents/waterleaf_application.png)
  - normalized text length: `564`
  - text simhash: `da8f1e3f7c06a6e2`

## 4. Exact Image Duplicates

### Image group anchored by `waterleaf_application.png`

- `Exhibit W` in `core_housing`: [waterleaf_application.png](/home/barberb/HACC/evidence/history/waterleaf_application.png)
- `Exhibit B-1` in `supplemental_background_appendix`: [waterleaf_application.png](/home/barberb/HACC/evidence/paper documents/waterleaf_application.png)

## 5. Likely Near-Image Duplicates

### Near-image cluster 1

- `Exhibit B-11` in `supplemental_background_appendix`: [FAQ _ OHSU.pdf](/home/barberb/HACC/evidence/paper documents/FAQ _ OHSU.pdf)
  - image hash: `7f030080ffffffff`
- `Exhibit B-2` in `supplemental_background_appendix`: [Waterleaf to 3338 S Moody Ave, Portland, OR 97239 - Google Maps.pdf](/home/barberb/HACC/evidence/paper documents/Waterleaf to 3338 S Moody Ave, Portland, OR 97239 - Google Maps.pdf)
  - image hash: `ff010100ffffffff`
- `Exhibit B-3` in `supplemental_background_appendix`: [Waterleaf to OTRADI - Google Maps.pdf](/home/barberb/HACC/evidence/paper documents/Waterleaf to OTRADI - Google Maps.pdf)
  - image hash: `ff010000cfffffff`
- `Exhibit B-4` in `supplemental_background_appendix`: [Waterleaf to Metro Region Innovation Hub - Google Maps.pdf](/home/barberb/HACC/evidence/paper documents/Waterleaf to Metro Region Innovation Hub - Google Maps.pdf)
  - image hash: `ff0100008fffffff`
- `Exhibit B-5` in `supplemental_background_appendix`: [Waterleaf to Safeway - Google Maps.pdf](/home/barberb/HACC/evidence/paper documents/Waterleaf to Safeway - Google Maps.pdf)
  - image hash: `ff010001bfffffff`
- `Exhibit B-6` in `supplemental_background_appendix`: [Waterleaf to St. James Lutheran Church - Google Maps.pdf](/home/barberb/HACC/evidence/paper documents/Waterleaf to St. James Lutheran Church - Google Maps.pdf)
  - image hash: `ff0100009fffffff`
- `Exhibit B-7` in `supplemental_background_appendix`: [Waterleaf to Multnomah County Central Library - Google Maps.pdf](/home/barberb/HACC/evidence/paper documents/Waterleaf to Multnomah County Central Library - Google Maps.pdf)
  - image hash: `ff000001ffffffff`

### Near-image cluster 2

- `Exhibit W` in `core_housing`: [waterleaf_application.png](/home/barberb/HACC/evidence/history/waterleaf_application.png)
  - image hash: `00ffff3f3ffff806`
- `Exhibit B-1` in `supplemental_background_appendix`: [waterleaf_application.png](/home/barberb/HACC/evidence/paper documents/waterleaf_application.png)
  - image hash: `00ffff3f3ffff806`

### Near-image cluster 3

- `Exhibit C` in `final_housing`: [HACC 90 day notice 2.pdf](/home/barberb/HACC/evidence/paper documents/HACC 90 day notice 2.pdf)
  - image hash: `999bbf8381838700`
- `Exhibit D` in `final_housing`: [HACC 90 day notice.pdf](/home/barberb/HACC/evidence/paper documents/HACC 90 day notice.pdf)
  - image hash: `9f9bbf8381a38700`

### Near-image cluster 4

- `Exhibit A-1` in `supplemental_background_appendix`: [assistive technology 2014.pdf](/home/barberb/HACC/evidence/paper documents/assistive technology 2014.pdf)
  - image hash: `c3c3c3c3c3ffffff`
- `Exhibit A-2` in `supplemental_background_appendix`: [assistive technology 2.pdf](/home/barberb/HACC/evidence/paper documents/assistive technology 2.pdf)
  - image hash: `c7c3c3c3c3ffffff`

## 6. Best Practical Use

Use exact-source and exact-text groups as the safest dedup targets first.
Use near-text and near-image groups as review targets before removing anything.
Where a duplicate is removed, keep the tab cover page and exhibit cover page and incorporate the master source by reference.
