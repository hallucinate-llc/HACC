#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/home/barberb/HACC/complaint-generator"
if [[ $# -gt 0 ]]; then
	exec "${ROOT_DIR}/scripts/run_cli_mediator.sh" "$1"
fi

exec "${ROOT_DIR}/scripts/run_cli_mediator.sh"
