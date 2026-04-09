# Exhibit Booklet Print Command Sheet (2026-04-08)

Case: `26PR00641`

Environment checks passed on this machine:
- `python3` present
- `pdfunite` present
- `gs` present

## Output folder

```bash
OUT="/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/print_build_2026-04-08"
mkdir -p "$OUT"
```

## Render front matter + exhibit source files to court-style PDF (US Letter)

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/131_render_pleading_pdf.py" \
  "/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/123_exhibit_booklet_cover_sheet_2026-04-08.md" \
  "$OUT/123_exhibit_booklet_cover_sheet_2026-04-08.pdf" \
  "Exhibit Booklet Cover Sheet"
```

Repeat the same renderer command pattern for each `.md`, `.txt`, and `.json` source listed in the manifest, then merge with `pdfunite`.

## Build current-print booklet (Exhibits 1-7)

```bash
pdfunite \
  "$OUT/123_exhibit_booklet_cover_sheet_2026-04-08.pdf" \
  "$OUT/00_exhibit_legend_global.pdf" \
  "$OUT/124_exhibit_proof_and_reliance_summary_matrix_2026-04-08.pdf" \
  "$OUT/125_exhibit_tab_sheets_1_10_header_only_2026-04-08.pdf" \
  "$OUT/sam_barber_restraining_order_ocr.pdf" \
  "$OUT/solomon_motion_for_guardianship_ocr.pdf" \
  "$OUT/solomon_evidence_graph_feed.pdf" \
  "$OUT/deontic_reasoning_report.pdf" \
  "$OUT/motion_support_map.pdf" \
  "$OUT/protective_order_and_hacc_notice_timeline.pdf" \
  "/home/barberb/HACC/evidence/paper documents/HACC vawa violation.pdf" \
  "$OUT/Exhibit_Booklet_Current_Exhibits_1_7.pdf"
```

## Optional full-print booklet (add Exhibits 8-10 once certified PDFs exist)

```bash
EX8="/ABS/PATH/TO/Exhibit_8_Certified_Docket_Register_26PR00641.pdf"
EX9="/ABS/PATH/TO/Exhibit_9_Certified_Signed_Order_25PO11530.pdf"
EX10="/ABS/PATH/TO/Exhibit_10_Certified_Hearing_Appearance_Record.pdf"

pdfunite \
  "$OUT/123_exhibit_booklet_cover_sheet_2026-04-08.pdf" \
  "$OUT/00_exhibit_legend_global.pdf" \
  "$OUT/124_exhibit_proof_and_reliance_summary_matrix_2026-04-08.pdf" \
  "$OUT/125_exhibit_tab_sheets_1_10_header_only_2026-04-08.pdf" \
  "$OUT/sam_barber_restraining_order_ocr.pdf" \
  "$OUT/solomon_motion_for_guardianship_ocr.pdf" \
  "$OUT/solomon_evidence_graph_feed.pdf" \
  "$OUT/deontic_reasoning_report.pdf" \
  "$OUT/motion_support_map.pdf" \
  "$OUT/protective_order_and_hacc_notice_timeline.pdf" \
  "/home/barberb/HACC/evidence/paper documents/HACC vawa violation.pdf" \
  "$EX8" "$EX9" "$EX10" \
  "$OUT/Exhibit_Booklet_Full_Exhibits_1_10.pdf"
```

## Quick integrity checks

```bash
ls -lh "$OUT"/Exhibit_Booklet_*.pdf
pdfinfo "$OUT/Exhibit_Booklet_Current_Exhibits_1_7.pdf" | sed -n '1,20p'
```

## One-command build script

- Use: `/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/128_build_exhibit_booklet_pdf.sh`
