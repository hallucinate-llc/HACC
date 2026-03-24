## HACC Complaint Email Download Plan

### Current complaint theory

The grounded complaint artifacts currently point to a grievance / hearing / due-process theory, not a generic housing search.

Core support already identified:
- `ADMINISTRATIVE PLAN`
- `ADMISSIONS AND CONTINUED OCCUPANCY POLICY`
- `24 CFR Part 966 Subpart B -- Grievance Procedures and Requirements`

Current blocker objectives:
- `hearing_request_timing`
- `exact_dates`
- `response_dates`

### What emails matter most

Prioritize emails that help prove:
1. When notice was given
2. When a hearing / review / grievance was requested
3. Whether HACC or related staff responded, denied, or failed to respond
4. Who the staff / decision-makers were
5. Which uploaded documents should become exhibits

### Highest-value search themes

Primary themes:
- grievance
- hearing request
- informal review
- appeal
- notice of decision
- denial
- retaliation
- accommodation
- due process

Chronology themes:
- date
- timeline
- chronology
- response
- follow up
- decision

Policy / exhibit themes:
- administrative plan
- occupancy policy
- lease
- housing assistance

### Recommended preview-first command

```bash
python3 /home/barberb/HACC/import_gmail_evidence.py \
  --auth-mode gmail_app_password \
  --prompt-credentials \
  --dry-run \
  --limit 150 \
  --address-file /home/barberb/HACC/target_addresses_starworks5.txt \
  --since-date 2026-01-01 \
  --complaint-query "retaliation grievance complaint appeal hearing due process tenant policy adverse action hearing request notice denial response dates chronology" \
  --complaint-keyword-file /home/barberb/HACC/hacc_complaint_email_keywords.txt \
  --min-relevance-score 2.0 \
  --case-slug starworks5-hacc-complaint-preview
```

### Recommended full import command

```bash
python3 /home/barberb/HACC/import_gmail_evidence.py \
  --auth-mode gmail_app_password \
  --prompt-credentials \
  --limit 150 \
  --address-file /home/barberb/HACC/target_addresses_starworks5.txt \
  --since-date 2026-01-01 \
  --complaint-query "retaliation grievance complaint appeal hearing due process tenant policy adverse action hearing request notice denial response dates chronology" \
  --complaint-keyword-file /home/barberb/HACC/hacc_complaint_email_keywords.txt \
  --min-relevance-score 2.0 \
  --upload-to-workspace \
  --review-after-upload \
  --generate-after-upload \
  --export-packet-after-upload \
  --export-markdown-after-upload \
  --case-slug starworks5-hacc-complaint-import
```

### How to tighten further if too many emails match

Raise the threshold:
- `--min-relevance-score 3.0`

Add a date window:
- `--before-date 2026-03-01`

Add a subject hint:
- `--subject-contains grievance`
- `--subject-contains hearing`
- `--subject-contains notice`

Use sender-only or recipient-only filters:
- `--from-address ...`
- `--to-address ...`

### What to review in the dry run

Keep emails that show:
- notice dates
- hearing / grievance request dates
- denial or review decisions
- follow-up messages asking for response
- staff names and titles
- attachments like notices, letters, PDFs, lease or policy extracts

Deprioritize emails that are:
- newsletters
- promotions
- social / notifications
- unrelated scheduling or subscriptions
