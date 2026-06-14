# Directory Structure

> How backend code is organized in this project.

## Overview

There is no monolithic backend app in this repository. Code is organized by
skill directory at the repo root, and each skill keeps its own entrypoints and
supporting modules nearby.

## Actual Layout

```text
repo/
├── a-share-data/
│   ├── SKILL.md
│   ├── references/
│   └── scripts/
├── a-share-paper-trading/
│   ├── SKILL.md
│   ├── README.md
│   └── scripts/
│       ├── paper_trade_cli.py
│       ├── paper_trading_service.py
│       ├── paper_trading_ctl.py
│       └── paper_trading/
├── a-share-strategy-mainboard-multi-swing-defensive/
│   ├── SKILL.md
│   └── scripts/
│       ├── daily_decisions.py
│       ├── realtime_quotes.py
│       ├── paper_trading/
│       └── strategy_lab/
├── macd-second-golden-cross/
├── macd-trend-resonance-stock-picker/
├── tuige-shortline-trading/
├── docs/
└── experiments/
```

## Module Organization Rules

### 1. Keep code inside the owning skill directory

If behavior only belongs to one skill, put the code under that skill's
`scripts/` directory rather than creating a cross-repo utility package.

Examples:

- `a-share-paper-trading/scripts/paper_trading/` holds the engine, service, and
  market-data logic for the paper trading skill.
- `a-share-strategy-mainboard-multi-swing-defensive/scripts/strategy_lab/`
  holds strategy-specific indicators and params, not shared repo-wide modules.

### 2. Separate entrypoints from reusable modules

Use thin executable scripts as entrypoints and keep reusable logic in nearby
modules.

Examples:

- Entry CLI: `a-share-paper-trading/scripts/paper_trade_cli.py`
- Entry service: `a-share-paper-trading/scripts/paper_trading_service.py`
- Reusable engine: `a-share-paper-trading/scripts/paper_trading/engine.py`

### 3. Prefer local imports with explicit path bootstrapping when needed

Many scripts add their own `scripts/` directory to `sys.path` before importing
neighbor modules. Follow the existing pattern instead of introducing packaging
machinery unless the repo is intentionally being restructured.

Examples:

- `a-share-paper-trading/scripts/full_function_smoke_check.py`
- `a-share-strategy-mainboard-multi-swing-defensive/scripts/daily_decisions.py`
- `a-share-data/scripts/fetch_history.py`

## Naming Conventions

- Executable entry scripts use verb- or role-based names:
  - `fetch_history.py`
  - `paper_trade_cli.py`
  - `paper_trading_service.py`
  - `daily_decisions.py`
- Reusable internal modules use nouns:
  - `engine.py`
  - `service.py`
  - `market_data.py`
  - `strategy_params.py`
- Strategy or skill docs live in `SKILL.md`; extra operator docs live in
  `README.md` or `references/`.

## Anti-Patterns

- Do not add a fake `src/` tree just to satisfy a generic template.
- Do not move skill-local code into `.trellis/` or `docs/`.
- Do not split a tiny script into many abstraction layers unless that pattern
  already exists nearby.
