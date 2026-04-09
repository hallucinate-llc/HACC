# All Outputs Runbook (2026-04-08)

Case: `26PR00641`

## One Command: Build Main + Supplemental (Current Variants)

```bash
"/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/145_build_all_filing_outputs_26PR00641.sh"
```

Builds:

1. `Master_Filing_Packet_26PR00641.pdf`
2. `Exhibit_Booklet_Current_Exhibits_1_7.pdf`
3. `Supplemental_Cross_Forum_Core_Packet_26PR00641.pdf`

## One Command: Build Full Variants (when all pending exhibits exist)

```bash
EX8="/ABS/PATH/TO/Exhibit_8_Certified_Docket_Register_26PR00641.pdf"
EX9="/ABS/PATH/TO/Exhibit_9_Certified_Signed_Order_25PO11530.pdf"
EX10="/ABS/PATH/TO/Exhibit_10_Certified_Hearing_Appearance_Record.pdf"
CF1="/ABS/PATH/TO/CF1_JusticeCourt_Docket_26FE0586.pdf"
CF2="/ABS/PATH/TO/CF2_JusticeCourt_Orders_26FE0586.pdf"
CF3="/ABS/PATH/TO/CF3_DistrictOfOregon_Docket.pdf"
CF4="/ABS/PATH/TO/CF4_Federal_Complaint_and_Orders.pdf"

"/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/145_build_all_filing_outputs_26PR00641.sh" \
  "$EX8" "$EX9" "$EX10" "$CF1" "$CF2" "$CF3" "$CF4"
```

Additional outputs when args are supplied:

1. `Exhibit_Booklet_Full_Exhibits_1_10.pdf`
2. `Supplemental_Cross_Forum_Full_Packet_26PR00641.pdf`

