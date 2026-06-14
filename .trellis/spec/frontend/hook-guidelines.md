# Hook Guidelines

> How hooks are used in this project.

## Current Reality

There are no React hooks or equivalent frontend hook abstractions in this
repository.

## Current Rule

Any mention of “hooks” in the current repo refers to platform integration hooks
under `.codex/hooks/` or Trellis runtime hooks, not UI hooks. Do not mix those
concepts.

Examples of existing non-frontend hooks:

- `.codex/hooks/session-start.py`
- `.codex/hooks/inject-workflow-state.py`

If a browser/frontend layer is added later, rewrite this file from the actual
hook usage there.
