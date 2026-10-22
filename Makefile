.DEFAULT_GOAL := help
SHELL := /bin/bash

PYTHON ?= python3
# The ShadowScan revision this companion was migrated from. The harness tests
# import the scanner, so it is installed from exactly this commit (see README).
SCANNER_REPO := https://github.com/aisecnomad/Nexus-ShadowScan.git
SCANNER_COMMIT := 0792106b8d2cc09517f7f4ee2eeabf4f8eb8da2d
SCANNER_DIR := scanner-source

CASES_CORPUS := benchmarks/shadowbench/cases/corpus.json
CASES_RUN := benchmarks/shadowbench/cases/results/2026-10-11
ESTATE_RUN := benchmarks/shadowbench/estate/results/2026-10-11
CODE_CORPUS := benchmarks/shadow-ai-discovery/corpus.json
CODE_RUN := benchmarks/shadow-ai-discovery/results/2026-10-09

# --- Setup -----------------------------------------------------------------

.PHONY: install
install: ## Install the hash-locked dependencies and the pinned scanner checkout (idempotent)
	@$(PYTHON) -c 'import sys; sys.exit(None if (3, 11) <= sys.version_info[:2] < (3, 15) else "ShadowBench needs CPython 3.11 to 3.14; this python is " + sys.version.split()[0])'
	@if [ -d "$(SCANNER_DIR)/.git" ]; then \
		head=$$(git -C "$(SCANNER_DIR)" rev-parse HEAD); \
		if [ "$$head" != "$(SCANNER_COMMIT)" ]; then \
			echo "$(SCANNER_DIR) is at $$head, not $(SCANNER_COMMIT); check it out or remove it" >&2; exit 1; \
		fi; \
	else \
		git clone --filter=blob:none --no-checkout "$(SCANNER_REPO)" "$(SCANNER_DIR)" && \
		git -C "$(SCANNER_DIR)" checkout --detach "$(SCANNER_COMMIT)"; \
	fi
	$(PYTHON) -m pip install --require-hashes --only-binary=:all: \
		-r requirements.lock -r requirements-ci.lock -r requirements-build.lock
	$(PYTHON) -m pip install --no-deps --no-build-isolation -e ./$(SCANNER_DIR)

# --- Quality gates (CI order) ----------------------------------------------

.PHONY: audit
audit: ## Audit the installed environment and every hash-locked dependency set, as CI does
	pip-audit --skip-editable --progress-spinner off
	set -e; for lock in requirements.lock requirements-ci.lock requirements-build.lock; do \
		pip-audit --require-hashes --strict --progress-spinner off --disable-pip -r "$$lock"; \
	done

.PHONY: verify
# With the pinned scanner checkout present, every MIGRATION.json record is also checked against its
# source tree; SINCE=<commit> also requires MIGRATION.json unchanged, the ledger only appended to and
# every committed attestation file kept since that commit (CI passes the commit a change builds on).
verify: ## Check migrated files against MIGRATION.json and attested results against their Sigstore bundles
	$(PYTHON) -m tools.verify_migration $(if $(wildcard $(SCANNER_DIR)/.git),--source $(SCANNER_DIR)) \
		$(if $(SINCE),--since $(SINCE))
	$(PYTHON) -m tools.attest verify $(if $(SINCE),--since $(SINCE))

.PHONY: test
test: ## Run the harness test suite
	$(PYTHON) -m pytest -q

.PHONY: lint
lint: ## Run the ruff linter
	ruff check tests tools benchmarks

.PHONY: format-check
format-check: ## Check ruff formatting without changes
	ruff format --check tests tools benchmarks

.PHONY: typecheck
typecheck: ## Type-check the harness against the pinned scanner checkout
	MYPYPATH=$(SCANNER_DIR) mypy tools benchmarks

.PHONY: secrets
secrets: ## Scan every tracked file for credential-shaped strings
	git ls-files -z | xargs -0 $(PYTHON) tools/check_secrets.py

# Committed results of the live tracks, checked for machine paths a scrub missed;
# paths the corpora themselves contain (echoed by tools) are not findings.
RESULTS_DIRS := benchmarks/shadow-ai-discovery/results benchmarks/shadowbench/cases/results \
	benchmarks/shadowbench/estate/results
CORPORA := benchmarks/shadowbench/estate/artifacts benchmarks/shadowbench/cases/corpus.json \
	benchmarks/shadow-ai-discovery/corpus.json

.PHONY: paths
paths: ## Check committed results for machine paths left unscrubbed
	$(PYTHON) -m tools.shadowbench.scrub check $(addprefix --corpus ,$(CORPORA)) $(RESULTS_DIRS)

.PHONY: check
check: audit verify test lint format-check typecheck secrets paths ## Run every CI gate, in CI's order

# --- Evidence ---------------------------------------------------------------

.PHONY: integrity
integrity: ## Rebuild the cases corpus and check the estate corpus and freeze (no third-party tool runs)
	$(PYTHON) -m tools.shadowbench cases verify --corpus $(CASES_CORPUS)
	$(PYTHON) -m tools.shadowbench estate validate
	$(PYTHON) -m tools.shadowbench estate verify-freeze

# Scoring and rendering the committed rows with the scorers at this commit
# reproduces each run's metrics.json and REPORT.md byte for byte, so any
# difference means the scorer, the report or the committed evidence changed.
# The 2026-10-09 code-surface baseline re-scores its metrics.json byte for
# byte; its REPORT.md differs in four cells (docs/results.md). Nothing is
# written outside a temporary directory.
.PHONY: rescore
rescore: ## Re-score the committed cases, estate and code-surface runs and compare them byte for byte
	@tmp=$$(mktemp -d) && trap 'rm -rf "$$tmp"' EXIT && \
	$(PYTHON) -m tools.shadowbench.cases score --corpus $(CASES_CORPUS) \
		--results $(CASES_RUN) --out "$$tmp/cases-metrics.json" >/dev/null && \
	$(PYTHON) -m tools.shadowbench.cases report --corpus $(CASES_CORPUS) \
		--metrics "$$tmp/cases-metrics.json" --out "$$tmp/cases-REPORT.md" >/dev/null && \
	cmp "$$tmp/cases-metrics.json" $(CASES_RUN)/metrics.json && \
	cmp "$$tmp/cases-REPORT.md" $(CASES_RUN)/REPORT.md && \
	echo "cases: re-scored metrics.json and REPORT.md match $(CASES_RUN) byte for byte" && \
	$(PYTHON) -m tools.shadowbench.estate score --runs $(ESTATE_RUN)/runs.json \
		--out "$$tmp/estate-metrics.json" >/dev/null && \
	$(PYTHON) -m tools.shadowbench.estate report --metrics "$$tmp/estate-metrics.json" \
		--out "$$tmp/estate-REPORT.md" >/dev/null && \
	cmp "$$tmp/estate-metrics.json" $(ESTATE_RUN)/metrics.json && \
	cmp "$$tmp/estate-REPORT.md" $(ESTATE_RUN)/REPORT.md && \
	echo "estate: re-scored metrics.json and REPORT.md match $(ESTATE_RUN) byte for byte" && \
	$(PYTHON) -m tools.discovery_benchmark score --corpus $(CODE_CORPUS) --runs $(CODE_RUN)/runs.json \
		--out "$$tmp/code-metrics.json" >/dev/null && \
	cmp "$$tmp/code-metrics.json" $(CODE_RUN)/metrics.json && \
	echo "code surface: re-scored metrics.json matches $(CODE_RUN) byte for byte"

# --- Housekeeping -----------------------------------------------------------

.PHONY: clean
clean: ## Remove caches (never touches scanner-source or committed evidence)
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage .coverage.*
	find . -path ./scanner-source -prune -o -path ./.git -prune -o \
		-type d -name __pycache__ -exec rm -rf {} +

.PHONY: help
help: ## Show this help
	@awk 'BEGIN { FS = ":.*## "; if (system("test -t 1") == 0) { b = "\033[1m"; c = "\033[36m"; r = "\033[0m" } } /^# --- / { t = $$0; gsub(/^# --- | -+$$/, "", t); printf "\n%s%s%s\n", b, t, r; next } /^[a-zA-Z_-]+:.*## / { printf "  %s%-14s%s %s\n", c, $$1, r, $$2 }' $(MAKEFILE_LIST)
