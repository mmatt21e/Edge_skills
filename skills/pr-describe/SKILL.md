---
name: pr-describe
description: Draft a pull request title and description from the diff between the current branch and a base branch. Use when the user asks to open a PR, write a PR description, or summarize their branch's changes for review. Can consume release-notes output and repo-map context.
---

# pr-describe

Produce a reviewer-friendly PR title and description from what the current
branch changes relative to its base.

## When to use

- "Write a PR description for this branch."
- "Summarize my changes for review."
- "Help me open a PR." (Draft the text; only create the PR if explicitly asked.)

## Steps

1. **Find the base branch.** Ask if unsure; otherwise default to `main` (fall
   back to `master`). Determine the merge base and inspect the diff:

   ```bash
   base=main
   git log --no-merges --oneline "$base"..HEAD
   git diff --stat "$base"...HEAD
   ```

2. **Title:** one line, imperative, no trailing period. Reuse the dominant
   Conventional Commit type if the branch is single-purpose
   (e.g. `feat: add dark-mode toggle`).

3. **Description** — fill this template, omitting empty sections:

   ```markdown
   ## Summary
   <1–3 sentences: what this does and why it's needed.>

   ## Changes
   - <key change, grouped logically — not a raw commit dump>
   - <...>

   ## Testing
   <how it was verified, or what reviewers should run>

   ## Notes for reviewers
   <risk areas, follow-ups, intentional omissions, screenshots>
   ```

4. **Ground every claim in the diff.** Do not invent tests or behavior that
   isn't present. If you can't tell how something was tested, say "Testing:
   _not yet verified_" rather than guessing.

5. **Output the title and body in a code block** for the user to copy. Only call
   a PR-creation tool if the user explicitly asks to open the PR.

## Composes with

- **repo-map** — for unfamiliar codebases, use it first to describe *where* the
  change lands.
- **release-notes** — reuse its categorized output as the **Changes** section.
