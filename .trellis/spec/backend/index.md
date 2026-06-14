# Backend Development Guidelines

> Project-specific backend guidance for this repository.

## Overview

This repository is a Python-first skills/tooling project, not a web app with a
separate `src/` service layer. The backend surface here mainly means:

- Python CLI entrypoints under skill `scripts/`
- Small HTTP services such as the paper trading service
- SQLite-backed local runtime state
- Data-fetch / strategy / simulation utilities used by agents

The goal of these docs is to help future agents extend the existing scripting
style instead of inventing a generic FastAPI/Django structure that does not
exist in this repo.

## Guidelines Index

| Guide | Description | Status |
| --- | --- | --- |
| [Directory Structure](./directory-structure.md) | How Python scripts and skill folders are organized | Project-specific |
| [Database Guidelines](./database-guidelines.md) | SQLite usage and persistence rules | Project-specific |
| [Error Handling](./error-handling.md) | How scripts and services validate and surface errors | Project-specific |
| [Quality Guidelines](./quality-guidelines.md) | Validation scripts, review focus, and forbidden patterns | Project-specific |
| [Logging Guidelines](./logging-guidelines.md) | Current low-logging conventions for CLIs and local services | Project-specific |

## Pre-Development Checklist

Before changing backend code in this repository:

1. Identify which skill owns the behavior you are changing.
2. Prefer following the skill-local `scripts/` layout instead of creating a new
   shared framework.
3. Check whether a CLI, service, and validation script already exist for the
   same area before adding new entrypoints.
4. Keep new behavior consistent with the existing local-runtime assumptions:
   Python scripts, standard library first, JSON over HTTP, and SQLite for
   lightweight persistence.

## Source Anchors

Use these as representative examples when extending the repo:

- `a-share-paper-trading/scripts/paper_trade_cli.py`
- `a-share-paper-trading/scripts/paper_trading/engine.py`
- `a-share-paper-trading/scripts/paper_trading/service.py`
- `a-share-paper-trading/scripts/full_function_smoke_check.py`
- `a-share-strategy-mainboard-multi-swing-defensive/scripts/daily_decisions.py`
- `a-share-data/scripts/fetch_history.py`
