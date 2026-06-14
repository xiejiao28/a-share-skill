# Directory Structure

> How frontend code is organized in this project.

## Current Reality

There is no frontend source tree in the current repository. No `src/`,
`components/`, `pages/`, or browser bundle configuration exists.

What does exist:

- `docs/` for Markdown documentation
- `README.md` for top-level project documentation
- Markdown-based skill reference files inside each skill directory

## Current Rule

Do not invent a frontend directory structure in tasks that only touch the
current Python/Markdown toolchain.

## If Frontend Code Is Added Later

Use a dedicated top-level app directory and document it explicitly here. Until
then, treat frontend work as documentation work only.
