IN THE CIRCUIT COURT OF THE STATE OF OREGON
FOR THE COUNTY OF CLACKAMAS
PROBATE DEPARTMENT

Case No. 26PR00641

In the Matter of:
Jane Kay Cortez,
Protected Person.

CROSS-FORUM AND SERVICE-RETURN FOLLOW-UP SEND QUEUE
Date: 2026-04-09

Purpose:
1. Stage a same-day send queue for unresolved certified-record and service-return targets.
2. Keep dispositive preclusion asks evidence-gated until certified packets are received.

I. SEND QUEUE (READY NOW)

1. `REQ-26FE0586-001` (Clackamas Justice Court; target case `26FE0586`)
   a. Send initial request using file `135`.
   b. If no response by 2026-04-11, send follow-up text from file `203`.
2. `REQ-FED-HAQC-001` (District of Oregon; HACC/Quantum track)
   a. Send initial request using file `136`.
   b. Run same-day PACER/public docket search by party name and preserve retrieval metadata.
   c. If no response by 2026-04-11, send follow-up text from file `203`.
3. `REQ-SHERIFF-RETURN-001` (Clackamas Sheriff; April 9 service-return request)
   a. Send initial request using file `187`.
   b. If no response by 2026-04-10, send follow-up text from file `203`.

II. TRACKER UPDATE RULES

4. After each send:
   a. Update `137_cross_forum_request_send_and_status_tracker_2026-04-08.csv` from `ready_to_send` to `submitted`.
   b. Add send timestamp and any fee/ETA notes in the `notes` field.
5. On any response:
   a. set `response_received` to `yes`;
   b. set `records_received` to `yes` only when actual documents are received and staged.
6. Mirror high-level entries in `158_records_request_and_subpoena_tracker_rows_2026-04-09.csv`.

III. DEONTIC CONTROL (PROOF GATING)

7. `O` Keep preclusion dismissal framing conditional until certified finality/identity packets are lodged.
8. `O` Lodge sheriff return immediately once received before converting "reported service event" to formal proved-service statement.
9. `F` Do not represent cross-forum issues as finally adjudicated without certified order/docket support.
10. `P` Use currently located repository scans for timeline/context support only.

IV. NEXT CHECKPOINTS

11. 2026-04-10: first response check and sheriff follow-up if needed.
12. 2026-04-11: cross-forum follow-up send if no response.
13. 2026-04-14: second follow-up wave and fee/ETA escalation call.
14. 2026-04-21: due-date status review against existing clerk-request tracker.

DATED: April 9, 2026

Prepared by:
____________________________________
Benjamin Barber, Pro Se (working send-queue sheet)
