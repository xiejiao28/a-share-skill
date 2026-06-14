# Error Handling

> How errors are handled in this project.

## Overview

The dominant pattern in this repository is lightweight validation with
`ValueError`/`RuntimeError` plus user-facing error messages at the script or
HTTP boundary. There is no custom exception hierarchy shared across the repo.

Representative files:

- `a-share-paper-trading/scripts/paper_trade_cli.py`
- `a-share-paper-trading/scripts/paper_trading/service.py`
- `a-share-paper-trading/scripts/paper_trading/engine.py`
- `a-share-data/scripts/fetch_history.py`

## Error Types

### Domain validation

Use `ValueError` for invalid user or runtime inputs.

Examples:

- Invalid price tick in `validate_price_tick()`
- Unsupported strategy in `run_backtest()`
- Duplicate account creation in `create_account()`
- Unsupported `--freq` in `a-share-data/scripts/fetch_history.py`

### Boundary/runtime failures

Use `RuntimeError` when a script wraps lower-level transport issues into a more
actionable operator message.

Example:

- `paper_trade_cli.py` turns `urllib` connection failures into a message that
  tells the user how to start the service.

## Error Propagation Patterns

### 1. Validate early, fail with a direct message

Most scripts validate inputs before doing work and either:

- `raise ValueError(...)`, or
- `print(...)` + `sys.exit(1)` for CLI argument normalization paths

### 2. Convert exceptions at the outer boundary

Service handlers and CLIs convert thrown exceptions into transport-appropriate
responses:

- HTTP layer: `TradingRequestHandler` returns JSON `{"status":"error", ...}`
  with a `400/404`
- CLI layer: `print_result()` prints `ERROR: ...` and exits non-zero

### 3. Avoid silent continuation on request paths

Request/command handlers should surface bad inputs clearly. Silent swallowing is
only used in background loops where best-effort behavior is intentional.

## Intentional Exceptions To The Rule

Background threads in `paper_trading/service.py` swallow generic exceptions:

- `MatchingLoop.run()`
- `ValuationLoop.run()`

This is a resilience tradeoff for local daemon loops. If you change this
behavior, also decide how to report failures without killing the thread.

## Common Mistakes

- Do not add broad `except Exception: pass` around primary CLI or HTTP request
  logic.
- Do not return mixed error shapes from the same service family.
- Do not hide actionable validation detail behind generic `"failed"` messages
  when the current codebase already reports exact cause strings.
