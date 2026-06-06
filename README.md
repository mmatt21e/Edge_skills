# Edge_skills

A small, organized collection of **Claude Code Agent Skills**. Each skill lives
in its own folder under [`skills/`](skills/) with a `SKILL.md` that Claude Code
discovers automatically. Some skills stand alone; a few are designed to compose
into a release workflow.

## Catalog

| Skill | What it does | Stands alone | Composes with |
|-------|--------------|:---:|---|
| [`commit-craft`](skills/commit-craft/SKILL.md) | Write Conventional-Commit messages from your current changes | ✓ | → `release-notes`, `git-ship` |
| [`git-ship`](skills/git-ship/SKILL.md) | Clean up the tree, split into logical commits, push to GitHub, and optionally merge the branch (one confirmation) | ✓ | ← `commit-craft` |
| [`release-notes`](skills/release-notes/SKILL.md) | Build categorized changelog / release notes between two refs | ✓ | ← `commit-craft` · → `pr-describe` |
| [`pr-describe`](skills/pr-describe/SKILL.md) | Draft a PR title + description from your branch diff | ✓ | ← `release-notes`, `repo-map` |
| [`dep-check`](skills/dep-check/SKILL.md) | Audit dependencies for outdated & vulnerable packages (npm/pip/cargo) | ✓ | — |
| [`test-scaffold`](skills/test-scaffold/SKILL.md) | Generate a test-file skeleton matching the project's framework | ✓ | — |
| [`repo-map`](skills/repo-map/SKILL.md) | Produce a concise architecture / onboarding map of a repo | ✓ | → `pr-describe` |
| [`context-handoff`](skills/context-handoff/SKILL.md) | Capture the conversation to `.claude/handoff.md` + emit a restart prompt for a clean `/clear` | ✓ | — |
| [`dotnet-db-modernizer`](skills/dotnet-db-modernizer/SKILL.md) | Audit & modernize DB-access code in legacy .NET (Web Forms/WinForms, C#/VB) via analyze→plan→approve→implement | ✓ | — |
| [`iterative-improver`](skills/iterative-improver/SKILL.md) | Improve anything (code/prose/prompt/…) via an autonomous improver+critic refine loop for N rounds, on a copy/branch | ✓ | — |

### The "ship a release" chain

These three work together but are useful individually too:

```
commit-craft  →  release-notes  →  pr-describe
(good commits)   (changelog)       (PR write-up)
```

## Layout

```
skills/
  <skill-name>/
    SKILL.md          # required: frontmatter (name, description) + instructions
    scripts/          # optional: helper scripts the skill calls
```

A `SKILL.md` is just Markdown with YAML frontmatter:

```yaml
---
name: my-skill          # lowercase, hyphens, ≤ 64 chars, matches the folder
description: What it does and WHEN to use it — this is how Claude decides to invoke it.
---
```

## Installing into Claude Code

Skills are picked up from `~/.claude/skills/` (all projects) or a project's
`.claude/skills/` (that project only). Symlink so updates here flow through:

```bash
# All projects:
for d in skills/*/; do
  ln -s "$(pwd)/$d" "$HOME/.claude/skills/$(basename "$d")"
done

# Or a single project:
ln -s "$(pwd)/skills/commit-craft" /path/to/project/.claude/skills/commit-craft
```

Then start (or restart) Claude Code and invoke a skill with `/` or just ask for
the task it describes — Claude matches on the `description`.

### Packaged `.skill` files

Some skills are also distributed as a single `.skill` bundle in [`dist/`](dist/)
(a zip produced by skill-creator's `package_skill.py`). Install a `.skill` by
uploading it in the Claude apps' skill UI, or unzip it into `~/.claude/skills/`.
Re-package after editing a skill:

```bash
python3 -m scripts.package_skill /abs/path/to/skills/<name> /abs/path/to/dist
# run from the skill-creator directory
```

## Adding a new skill

1. `mkdir -p skills/<name>` and add a `SKILL.md` with the frontmatter above.
2. Write the `description` to say **what it does and when to use it** — that text
   is what triggers the skill.
3. Add the skill to the catalog table above.
4. Keep helper scripts inside the skill's own `scripts/` folder and reference
   them by relative path from the repo root.
