# Supplemental Cross-Forum Packet Runbook (2026-04-08)

Case: `26PR00641`

## Build Core Packet (no CF exhibits yet)

```bash
"/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/143_build_supplemental_cross_forum_packet_pdf.sh"
```

Output:
- `/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/print_build_2026-04-08/Supplemental_Cross_Forum_Core_Packet_26PR00641.pdf`

## Build Full Packet (with CF-1..CF-4)

```bash
CF1="/ABS/PATH/TO/CF1_JusticeCourt_Docket_26FE0586.pdf"
CF2="/ABS/PATH/TO/CF2_JusticeCourt_Orders_26FE0586.pdf"
CF3="/ABS/PATH/TO/CF3_DistrictOfOregon_Docket.pdf"
CF4="/ABS/PATH/TO/CF4_Federal_Complaint_and_Orders.pdf"

"/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/143_build_supplemental_cross_forum_packet_pdf.sh" "$CF1" "$CF2" "$CF3" "$CF4"
```

Output:
- `/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/print_build_2026-04-08/Supplemental_Cross_Forum_Full_Packet_26PR00641.pdf`

## Integrity Checks

```bash
pdfinfo "/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/print_build_2026-04-08/Supplemental_Cross_Forum_Core_Packet_26PR00641.pdf" | sed -n '1,20p'
ls -lh "/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/print_build_2026-04-08"/Supplemental_Cross_Forum_*.pdf
```

