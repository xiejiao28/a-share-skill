# Logging Guidelines

> How logging is done in this project.

## Overview

This repository currently uses very little structured logging. Most tools are
local scripts that either:

- print explicit user-facing output, or
- stay silent unless an error occurs

There is no repo-wide logging framework such as `logging.config`,
structlog, or OpenTelemetry.

## Current Conventions

### 1. CLIs print results, not logs

Examples:

- `paper_trade_cli.py` prints JSON or plain results
- `full_function_smoke_check.py` prints a final `PASS ...` summary
- `fetch_history.py` prints direct compatibility warnings/errors

### 2. Local HTTP services suppress request spam by default

`TradingRequestHandler.log_message()` returns immediately, which disables the
default noisy `BaseHTTPRequestHandler` access logging.

### 3. Background loops are intentionally quiet

Matching and valuation loops in `paper_trading/service.py` suppress exceptions
instead of logging them. This is the current project behavior, even though it
reduces observability.

## When To Print

Print when one of these is true:

- The user needs an actionable next step
- A script is being used as a standalone CLI
- A smoke/regression check needs a final pass/fail marker

## When Not To Print

- Do not add debug chatter inside strategy scans or market-data loops unless it
  is guarded or explicitly requested.
- Do not emit request-per-line access logs for local services by default.
- Do not print secrets, credentials, account identifiers beyond what current
  user-facing CLIs already expose intentionally.

## If You Need More Logging

If a future change needs observability:

1. Prefer Python's standard `logging` module over introducing a third-party
   logger.
2. Keep logging local to the owning skill/runtime.
3. Preserve clean CLI output modes such as `--json`.
