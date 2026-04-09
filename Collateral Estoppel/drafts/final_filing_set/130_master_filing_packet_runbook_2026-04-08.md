# Master Filing Packet Runbook (2026-04-08)

Case: `26PR00641`

## Current packet (available now)

```bash
"/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/129_build_master_filing_packet_pdf.sh"
```

Output:
- `/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/print_build_2026-04-08/Master_Filing_Packet_26PR00641.pdf`
- Rendering mode: court-style US Letter pleading pages (line numbers + pleading margin).

## Full packet (after certified Exhibits 8-10 are obtained)

```bash
EX8="/ABS/PATH/TO/Exhibit_8_Certified_Docket_Register_26PR00641.pdf"
EX9="/ABS/PATH/TO/Exhibit_9_Certified_Signed_Order_25PO11530.pdf"
EX10="/ABS/PATH/TO/Exhibit_10_Certified_Hearing_Appearance_Record.pdf"

"/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/129_build_master_filing_packet_pdf.sh" "$EX8" "$EX9" "$EX10"
```

Output (full variant generated when all 3 args are provided):
- `/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/print_build_2026-04-08/Exhibit_Booklet_Full_Exhibits_1_10.pdf`
- `/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/print_build_2026-04-08/Master_Filing_Packet_26PR00641.pdf`

## Integrity checks

```bash
pdfinfo "/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/print_build_2026-04-08/Master_Filing_Packet_26PR00641.pdf" | sed -n '1,20p'
ls -lh "/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/print_build_2026-04-08"/*.pdf
```
