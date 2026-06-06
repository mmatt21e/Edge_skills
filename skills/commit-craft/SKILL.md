---
name: commit-craft
description: Generate clear, Conventional Commits-style commit messages from the current git changes. Use when the user asks to write a commit message, commit staged changes with a good message, or improve a commit description. Pairs with release-notes, which parses these prefixes.
---

# commit-craft

Turn the current git changes into a clean, well-structured commit message that
follows the [Conventional Commits](https://www.conventionalcommits.org) spec.

## When to use

- "Write a commit message for this."
- "Commit my staged changes with a good message."
- "Clean up this commit description."

## Steps

1. **Inspect the changes.** Run `git diff --staged`. If nothing is staged, run
   `git diff` and tell the user you're describing unstaged work (offer to stage
   it). Also check `git status` for the set of touched files.

2. **Group the change into one logical unit.** If the diff clearly spans several
   unrelated concerns, say so and suggest splitting into multiple commits rather
   than one vague message.

3. **Pick a type and optional scope:**
   - `feat` – a new user-facing capability
   - `fix` – a bug fix
   - `refactor` – behavior-preserving restructuring
   - `perf` – performance improvement
   - `docs`, `test`, `build`, `ci`, `chore` – as named
   - Scope is the area touched, e.g. `feat(auth):`.

4. **Write the message:**
   - Subject line: `type(scope): summary` — imperative mood, lowercase, no
     trailing period, aim for ≤ 50 characters.
   - Blank line, then a body that explains **why** (not just what), wrapped at
     ~72 columns. Skip the body only for truly trivial changes.
   - Footer for `BREAKING CHANGE:` notes or issue refs (`Closes #123`).

5. **Do not run `git commit` unless the user explicitly asks.** Default to
   showing the proposed message in a code block so they can review it.

## Example output

```
fix(parser): handle empty config files without crashing

An empty config previously raised KeyError because the loader assumed at
least one section. Treat a missing section as an empty dict and fall back
to defaults.

Closes #214
```
