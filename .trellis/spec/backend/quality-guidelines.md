# Quality Guidelines

> Code quality standards for backend development.

## Overview

Quality in this repository is enforced more by executable smoke/regression
scripts and consistency with existing skill structure than by a heavyweight test
framework.

Representative validation files:

- `a-share-paper-trading/scripts/full_function_smoke_check.py`
- `a-share-paper-trading/scripts/rule_regression_check.py`
- `a-share-paper-trading/scripts/backtest_batch_validation.py`
- `a-share-paper-trading/scripts/real_stock_rule_validation.py`

## Required Patterns

### 1. Preserve executable entrypoints

Scripts intended to run directly should keep:

- `#!/usr/bin/env python3`
- a `main()` function when practical
- `if __name__ == "__main__": main()`

### 2. Keep user-facing behavior deterministic

- JSON-producing paths should stay machine-readable
- CLI argument validation should fail fast
- Service responses should keep the `status/data/message` pattern already used
  by `paper_trading/service.py`

### 3. Add or update validation scripts for behavior changes

When changing trading rules, service behavior, or backtest logic, extend the
existing smoke/regression scripts instead of only relying on manual reasoning.

## Forbidden Patterns

- Do not introduce a new framework stack (FastAPI, SQLAlchemy, Celery, etc.)
  for a small local skill change.
- Do not mix unrelated repo-wide abstractions into a single shared `utils.py`
  when the current repo prefers skill-local modules.
- Do not leave template-style empty docs in `.trellis/spec/` once a task claims
  the bootstrap guidelines are complete.

## Testing Requirements

- For paper-trading runtime changes:
  - run `full_function_smoke_check.py`
  - run the narrower regression script when applicable
- For CLI/service contract changes:
  - verify the corresponding CLI command or HTTP route still behaves as before
- For strategy-scan script changes:
  - at minimum, run the script on representative inputs or add a targeted check

## Code Review Checklist

- Does the change stay within the owning skill's structure?
- Are input validation and user-visible errors still clear?
- If persistence changed, is SQLite schema/runtime behavior still coherent?
- Is there a validation script or smoke path covering the change?
