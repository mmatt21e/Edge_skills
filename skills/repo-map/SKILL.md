---
name: repo-map
description: Produce a concise architecture and onboarding map of a repository — entry points, key directories, build/test/run commands, and how the pieces fit together. Use when the user is new to a codebase, asks for an overview or map of the repo, or wants onboarding notes. Useful context for pr-describe.
---

# repo-map

Give a newcomer (human or agent) a fast, accurate mental model of a repository:
what it is, how it's organized, and how to build, test, and run it.

## When to use

- "Give me an overview of this repo."
- "I'm new here — where do I start?"
- "Map out the architecture."

## Steps

1. **Identify the project type** from manifests and config: language(s),
   framework, package manager, monorepo vs single package. Read `README`,
   `CONTRIBUTING`, and any `docs/` index first — don't restate what they already
   document, build on it.

2. **Locate the important paths**, not every file:
   - Entry points (`main`, `index`, `cmd/`, `app/`, server bootstrap).
   - Core domain/logic directories vs. plumbing (config, build, generated).
   - Where tests live, where config lives, where docs live.
   Use `git ls-files` and directory listings; skip vendored/generated trees.

3. **Extract the real commands** from `package.json` scripts, `Makefile`,
   `justfile`, `pyproject.toml`, CI workflows, or the README — install, build,
   test, lint, run. Quote them verbatim; flag any you couldn't confirm.

4. **Output a compact map**, e.g.:

   ```markdown
   # <Repo> — Map

   **What it is:** <one line>
   **Stack:** <languages / frameworks / pkg manager>

   ## Layout
   - `src/api/`     — HTTP handlers, request validation
   - `src/core/`    — domain logic (start here)
   - `src/db/`      — persistence, migrations
   - `tests/`       — pytest suite

   ## Commands
   - Install:  `<cmd>`
   - Test:     `<cmd>`
   - Run:      `<cmd>`

   ## Data / control flow
   <2–4 sentences: request → handler → core → db, or equivalent>

   ## Good first files to read
   1. `src/core/<x>` — <why>
   ```

5. **Keep it skimmable** — a screenful, not an exhaustive inventory. Prefer the
   ~20% of structure that explains 80% of the codebase. Offer to save it as
   `docs/REPO_MAP.md` if the user wants it persisted.
