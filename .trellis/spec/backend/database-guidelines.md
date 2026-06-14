# Database Guidelines

> Database patterns and conventions for this project.

## Overview

This repository does not use an ORM or migration framework. The only real
database-backed subsystem in the current codebase is the paper trading skill,
which uses SQLite directly through Python's `sqlite3` module.

Primary source:

- `a-share-paper-trading/scripts/paper_trading/engine.py`

## Storage Model

- Database engine: SQLite
- Access style: direct SQL executed from Python
- Initialization style: schema created in code with `CREATE TABLE IF NOT EXISTS`
- Connection style: open short-lived connections via helper methods

Representative example:

- `PaperTradingEngine._init_db()` creates schema with `conn.executescript(...)`
- `PaperTradingEngine._connect()` centralizes connection configuration

## Query Patterns

### 1. Keep SQL close to the domain logic

The current style stores SQL in the engine methods that own the behavior rather
than extracting a repository layer.

Examples:

- Account creation, cash adjustment, and order persistence live directly in
  `PaperTradingEngine`
- Task/runtime persistence for Trellis lives in `.trellis/scripts/common/`
  Python files rather than in a standalone DB layer

### 2. Use `sqlite3.Row` for structured access

`PaperTradingEngine._connect()` sets `row_factory = sqlite3.Row`, and callers
read fields by name. Keep this behavior when adding queries.

### 3. Prefer explicit transactions around stateful trading operations

For account/order/position mutations, use a connection scope that encloses the
whole operation, not multiple disconnected writes.

## Schema and Naming Conventions

- Table names are plural nouns:
  - `accounts`
  - `orders`
  - `trades`
  - `position_lots`
  - `account_snapshots`
  - `system_settings`
- Primary keys are explicit text IDs, often UUID-like strings.
- Timestamp fields are plain text columns formatted by helper functions like
  `now_ts()` and `trade_date()`.

## Migrations

There is no standalone migration tool in the current repo.

If you need schema evolution:

1. Prefer backward-compatible `CREATE TABLE IF NOT EXISTS` additions when
   possible.
2. Keep upgrade logic local to the owning engine/runtime module.
3. Add or update a smoke/regression script that exercises the changed schema.

## Common Mistakes

- Do not introduce SQLAlchemy, Django ORM, or Alembic-style tooling into this
  repo without an explicit repo-wide design decision.
- Do not assume concurrency-heavy DB semantics; the current design is a local
  simulation runtime, not a production multi-node service.
- Do not scatter SQLite files under arbitrary skill directories when a runtime
  path helper already exists, e.g. `paper_trading_runtime.py`.
