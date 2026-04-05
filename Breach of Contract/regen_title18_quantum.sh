#!/usr/bin/env bash
set -euo pipefail

cd "/home/barberb/HACC/Breach of Contract"
python3 -m formal_logic.title18_regenerate_packets \
	--merged-order-track quantum \
	--override-file title18_render_context_overrides.json \
	--override-file title18_quantum_context_overrides.json