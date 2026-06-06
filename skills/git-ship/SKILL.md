---
name: git-ship
description: Clean up the working tree and ship changes to GitHub in well-formed commits. Smart-stages real changes (skipping junk and secrets), fixes .gitignore, splits the work into logical Conventional-Commit commits with messages generated from the diff, then pushes after one confirmation. Use when the user asks to commit and push, "clean up git and ship my code", or wrap up and get changes onto GitHub.
---

# git-ship

End-to-end "commit my work to GitHub" flow: tidy the working tree, group the
changes into clean commits with generated messages, and push — with exactly one
confirmation before anything leaves the machine.

## When to use

- "Commit and push my changes."
- "Clean up git and ship this."
- "Wrap this up and get it on GitHub."

## Guardrails (always)

- **Never stage secrets or junk:** `.env*`, key/credential files, tokens,
  `node_modules/`, build output (`dist/`, `build/`, `target/`), logs, caches,
  OS cruft (`.DS_Store`). If any look already committed, flag it.
- **Never push to `main`/`master`** (or the repo's default branch). If that's
  the current branch, stop and offer to create a feature branch first.
- **One confirmation** covering the whole plan before committing/pushing. Do not
  silently proceed.

## Steps

1. **Survey state** in one batch:

   ```bash
   git branch --show-current
   git status --short
   git diff            # unstaged
   git diff --staged   # already staged
   git log --oneline -5
   ```

2. **Branch guard.** If on `main`/`master`/default, propose a descriptive
   feature branch name and create it (`git switch -c <name>`) once confirmed —
   before committing.

3. **Fix `.gitignore`.** From the untracked set, identify junk/secrets/build
   artifacts and add the right patterns to `.gitignore`. If such files are
   *already tracked*, propose `git rm --cached <path>` (keeps the local file) —
   call this out explicitly since it changes the index.

4. **Smart-stage.** Decide which remaining files are genuine source changes.
   Exclude anything matched by the guardrails above. If a file is ambiguous,
   ask rather than assume.

5. **Split into logical commits.** Group staged changes by concern (feature vs.
   fix vs. refactor vs. docs, or by component). For each group, generate a
   **Conventional Commits** message following the `commit-craft` skill's rules
   (`type(scope): subject`, imperative, body explaining *why*).

6. **Present the plan and get ONE confirmation.** Show:
   - `.gitignore` / `rm --cached` changes to be made
   - Each planned commit: its files + its message
   - Push target: `origin/<current-branch>`

   ```
   Plan:
   1. .gitignore  += node_modules/, .env
   2. commit  feat(api): add rate limiting    [src/api/limit.ts, src/api/index.ts]
   3. commit  test(api): cover rate limiter    [tests/limit.test.ts]
   → push to origin/feature-rate-limit
   Proceed? (yes / edit / cancel)
   ```

7. **Execute in order** once confirmed: apply `.gitignore` changes, then for each
   group stage exactly its files and commit with its message, then
   `git push -u origin <branch>`. If push fails on a network error, retry with
   backoff.

8. **Report**: commits created (hashes + subjects) and the pushed branch. Do
   **not** open a pull request unless the user explicitly asks.

## Composes with

- **commit-craft** — message generation rules (reused per commit).
- **release-notes** / **pr-describe** — natural follow-ups after shipping.
