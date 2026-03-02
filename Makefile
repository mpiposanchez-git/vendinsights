decision-log-docs:
	python scripts/generate_decision_log_markdown.py

check-decision-log-docs:
	python scripts/generate_decision_log_markdown.py
	git diff --exit-code -- docs/decision_log.md
