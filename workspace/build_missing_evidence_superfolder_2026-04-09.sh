#!/usr/bin/env bash
set -euo pipefail

BASE="/home/barberb/HACC/workspace"
SUPER="$BASE/working-missing-evidence-superfolder-2026-04-09"
HOUSING_SRC="$BASE/working-housing-missing-evidence-2026-04-09"
PROBATE_SRC="$BASE/working-probate-missing-evidence-2026-04-09"

mkdir -p "$SUPER"
rm -rf "$SUPER/housing" "$SUPER/probate"
cp -R "$HOUSING_SRC" "$SUPER/housing"
cp -R "$PROBATE_SRC" "$SUPER/probate"

cat > "$SUPER/README.md" <<'EOF'
# Working Missing Evidence Superfolder

This folder combines the two compact missing-evidence working packets:

- `housing/`
- `probate/`

Each subfolder is a self-contained packet with:

- core artifacts
- support notes
- branch-specific staging materials
EOF

printf 'Built superfolder at: %s\n' "$SUPER"
find "$SUPER" -maxdepth 2 -type d | sort
