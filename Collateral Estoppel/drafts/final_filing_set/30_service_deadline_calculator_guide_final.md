# Service Deadline Calculator Guide (Final)

Case: 26PR00641

Purpose: provide a consistent method for setting and tracking three key dates once service occurs:

1. Production due date
2. Deficiency cure deadline
3. Motion-to-compel target filing date

## Inputs required per recipient

- Date served
- Service method
- Any specific date/time written on subpoena face
- Any court order modifying timing

## Baseline working rules (customize if court/order differs)

1. Production due date:
   - Use the exact date/time written on the served subpoena.
   - If blank at service, set a date certain before service and record it.

2. Deficiency notice date:
   - Send within 1 business day after identifying incomplete production.

3. Cure deadline:
   - Default: 3 business days from deficiency notice date.
   - If production is large/technical, you may set 5 business days.

4. Motion-to-compel target date:
   - Default: 1 business day after cure deadline passes without full cure.

## Business-day handling

- If any target date falls on weekend or court holiday, roll to next business day.
- Record both raw date and adjusted business date when adjustment occurs.

## Recommended tracking fields

- date_served
- production_due_raw
- production_due_adjusted
- deficiency_notice_sent
- cure_deadline_raw
- cure_deadline_adjusted
- compel_target_raw
- compel_target_adjusted
- status
- notes

## Quick workflow

1. Enter service date immediately after service.
2. Confirm production due from subpoena face.
3. When production arrives, evaluate for completeness.
4. If deficient, issue notice and compute cure deadline.
5. If cure fails, prepare declaration and motion to compel package (files 23 and 24) by compel target date.

## Related files

- 28_active_service_log_2026-04-07.csv
- 29_active_service_log_2026-04-07.md
- 26_subpoena_service_return_tracker_template.csv
- 22_subpoena_deficiency_notice_template_final.md
- 23_declaration_re_subpoena_noncompliance_final.md
- 24_motion_to_compel_subpoena_compliance_and_sanctions_final.md
