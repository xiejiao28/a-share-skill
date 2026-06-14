# Frontend Development Guidelines

> Frontend guidance for the current repository state.

## Overview

This repository currently does **not** contain an application frontend such as
React, Vue, Svelte, or a browser UI codebase. The repo is primarily:

- Markdown skill definitions
- Python CLI/service/runtime scripts
- Experimental docs and results folders

Therefore the frontend spec layer is kept only as a reserved future slot. It
should describe the current absence of frontend code instead of
pretending a frontend architecture exists.

## Guidelines Index

| Guide | Description | Status |
| --- | --- | --- |
| [Directory Structure](./directory-structure.md) | Current frontend scope and future placement rules | Project-specific |
| [Component Guidelines](./component-guidelines.md) | Current non-applicability of component rules | Project-specific |
| [Hook Guidelines](./hook-guidelines.md) | Current non-applicability of hook rules | Project-specific |
| [State Management](./state-management.md) | Current non-applicability of app-state rules | Project-specific |
| [Quality Guidelines](./quality-guidelines.md) | Documentation/UI quality expectations if frontend code is introduced | Project-specific |
| [Type Safety](./type-safety.md) | Current non-applicability of TS rules | Project-specific |

## Current Rule

If a future task adds real frontend code, update this entire layer from the
actual implementation rather than copying generic SPA guidance.
