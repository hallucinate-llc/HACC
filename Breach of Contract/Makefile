.PHONY: regen-hacc regen-quantum check-title18 prep-title18-overrides

regen-hacc:
	bash ./regen_title18_hacc.sh

regen-quantum:
	bash ./regen_title18_quantum.sh

check-title18:
	python3 -m formal_logic.title18_readiness

prep-title18-overrides:
	python3 -m formal_logic.title18_override_templates