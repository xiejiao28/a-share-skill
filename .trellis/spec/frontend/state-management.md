# State Management

> How state is managed in this project.

## Current Reality

There is no browser-side or SPA state layer in this repository.

The meaningful stateful systems today are backend/runtime concerns:

- SQLite state in the paper trading engine
- Trellis runtime state under `.trellis/.runtime/`
- Task/session artifacts under `.trellis/tasks/` and `.trellis/workspace/`

## Current Rule

Do not introduce Redux/React Query/Zustand-style guidance into this file until
there is actual frontend code that uses those tools.
