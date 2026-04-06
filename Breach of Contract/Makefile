.PHONY: regen-hacc regen-quantum check-title18 check-title18-hacc check-title18-quantum prep-title18-overrides audit-title18-overrides status-title18 doctor-title18 contract-breach-report

PYTHON ?= $(if $(wildcard .venv/bin/python),./.venv/bin/python,python3)

regen-hacc:
	bash ./regen_title18_hacc.sh

regen-quantum:
	bash ./regen_title18_quantum.sh

check-title18:
	$(PYTHON) -m formal_logic.title18_readiness --merged-order-track hacc --override-file title18_render_context_overrides.json --override-file title18_hacc_context_overrides.json

check-title18-hacc:
	$(PYTHON) -m formal_logic.title18_readiness --merged-order-track hacc --override-file title18_render_context_overrides.json --override-file title18_hacc_context_overrides.json

check-title18-quantum:
	$(PYTHON) -m formal_logic.title18_readiness --merged-order-track quantum --override-file title18_render_context_overrides.json --override-file title18_quantum_context_overrides.json

prep-title18-overrides:
	$(PYTHON) -m formal_logic.title18_override_templates

audit-title18-overrides:
	$(PYTHON) -m formal_logic.title18_override_audit

status-title18:
	$(PYTHON) -m formal_logic.title18_status

doctor-title18: prep-title18-overrides audit-title18-overrides status-title18 check-title18-hacc check-title18-quantum

contract-breach-report:
	$(PYTHON) -m formal_logic.contract_breach_analysis