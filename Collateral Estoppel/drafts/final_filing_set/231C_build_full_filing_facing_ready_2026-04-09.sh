#!/usr/bin/env bash
set -euo pipefail

BASE="/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set"
OUT="$BASE/print_build_2026-04-08"
RENDER="$BASE/131_render_pleading_pdf.py"
BINDER="$OUT/Court_Ready_Single_Filing_Binder_26PR00641_2026-04-09_rev4_full_ready.pdf"
MANIFEST="$BASE/231D_full_ready_binder_included_files_2026-04-09.txt"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

need_cmd python3
need_cmd pdfunite
need_cmd pdfinfo
[[ -f "$RENDER" ]] || {
  echo "Missing renderer: $RENDER" >&2
  exit 1
}

mkdir -p "$OUT"

python3 - "$BASE" "$MANIFEST" <<'PY'
from pathlib import Path
import re
import sys

base = Path(sys.argv[1])
manifest = Path(sys.argv[2])

include_tokens = [
    "motion",
    "declaration",
    "memorandum",
    "objection",
    "response",
    "notice_of_filing",
    "certificate_of_service",
    "proposed_order",
    "oregon_authority_table",
]

exclude_name_tokens = [
    "prefill",
    "template",
    "runbook",
    "audit",
    "review",
    "weakness",
    "gap",
    "matrix",
    "checklist",
    "tracker",
    "playbook",
    "command",
    "protocol",
    "guide",
    "quickstart",
    "calendar",
    "send_queue",
    "send_log",
    "conversion_sheet",
    "versioning_note",
    "readiness",
    "one_page",
    "bench",
    "cheat_sheet",
    "desk_card",
    "outline",
    "likely_court_questions",
]

exclude_content_phrases = [
    "[INSERT]",
    "not filing-ready",
    "template form",
    "this draft is a prefill",
    "ready_to_serve",
]

def is_numbered_md(p: Path) -> bool:
    return bool(re.match(r"^\d+[A-Za-z_].*\.md$", p.name))

def include_name(name: str) -> bool:
    lo = name.lower()
    return any(t in lo for t in include_tokens)

def exclude_name(name: str) -> bool:
    lo = name.lower()
    return any(t in lo for t in exclude_name_tokens)

selected = [base / "231A_full_filing_facing_binder_cover_26PR00641_2026-04-09.md"]

for p in sorted(base.glob("*.md")):
    if p.name == selected[0].name:
        continue
    if not is_numbered_md(p):
        continue
    if not include_name(p.name):
        continue
    if exclude_name(p.name):
        continue
    txt = p.read_text(encoding="utf-8", errors="replace")
    lo = txt.lower()
    if any(phrase.lower() in lo for phrase in exclude_content_phrases):
        continue
    selected.append(p)

manifest.write_text("\n".join(str(p) for p in selected) + "\n", encoding="utf-8")
print(f"Selected {len(selected)} files")
for p in selected:
    print(p)
PY

mapfile -t FILES < "$MANIFEST"
[[ ${#FILES[@]} -gt 1 ]] || {
  echo "No filing-ready files selected." >&2
  exit 1
}

PDFS=()
for src in "${FILES[@]}"; do
  f="$(basename "$src")"
  out_pdf="$OUT/${f%.md}.pdf"
  python3 "$RENDER" "$src" "$out_pdf"
  PDFS+=("$out_pdf")
done

pdfunite "${PDFS[@]}" "$BINDER"

echo "Built full-ready binder: $BINDER"
pdfinfo "$BINDER" | sed -n '1,18p'
echo "Included-file manifest: $MANIFEST"

