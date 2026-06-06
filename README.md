# Edge_skills

A small, organized collection of **Claude Code Agent Skills**. Each skill lives
in its own folder under [`skills/`](skills/) as a `SKILL.md` (plus optional
`scripts/` and `references/`) that Claude Code discovers automatically. Some
skills stand alone; a few compose into a git/release workflow.

---

## ⚡ Install into local Claude Code

Skills are loaded from two locations:

- `~/.claude/skills/<name>/SKILL.md` — available in **every** project (user scope)
- `<project>/.claude/skills/<name>/SKILL.md` — available in **that project only**

Clone this repo first, then pick an option:

```bash
git clone https://github.com/mmatt21e/edge_skills.git
cd edge_skills
```

**A) Install ALL skills for every project (symlink — edits here flow through):**

```bash
mkdir -p "$HOME/.claude/skills"
for d in skills/*/; do
  ln -sfn "$(pwd)/${d%/}" "$HOME/.claude/skills/$(basename "$d")"
done
```

**B) Install ALL skills for every project (copy — independent of this repo):**

```bash
mkdir -p "$HOME/.claude/skills"
cp -R skills/* "$HOME/.claude/skills/"
```

**C) Install ONE skill (user scope):**

```bash
ln -sfn "$(pwd)/skills/commit-craft" "$HOME/.claude/skills/commit-craft"
# or copy:  cp -R skills/commit-craft "$HOME/.claude/skills/"
```

**D) Install ONE skill into a single project:**

```bash
mkdir -p /path/to/project/.claude/skills
ln -sfn "$(pwd)/skills/git-ship" /path/to/project/.claude/skills/git-ship
```

**E) Install a packaged `.skill` bundle** (see [`dist/`](dist/)): upload the
`.skill` file in the Claude app's skill UI, or unzip it into `~/.claude/skills/`:

```bash
unzip dist/dotnet-db-modernizer.skill -d "$HOME/.claude/skills/"
```

After installing, **restart Claude Code** (or run `/skills`) so it picks up the
new skills. Verify with `/skills` — each installed skill should be listed.

---

## ▶️ Usage

Once installed, invoke a skill two ways:

1. **Slash command** — type `/` and the skill name, e.g. `/commit-craft`,
   `/repo-map`, `/git-ship`.
2. **Just ask naturally** — Claude reads each skill's `description` and triggers
   the right one automatically. e.g. *"write me a good commit message"* →
   `commit-craft`; *"clean up git and ship this"* → `git-ship`.

Per-skill invocation examples and outputs are in the [Skill reference](#-skill-reference)
below. Tips:

- Skills that **edit or push** (e.g. `git-ship`) ask for confirmation first.
- `iterative-improver` takes a round count — *"improve README.md, 5 rounds"*.
- `dotnet-db-modernizer` always produces a written plan and waits for approval
  before changing any source.

---

## 📚 Catalog

| Skill | What it does | Stands alone | Composes with |
|-------|--------------|:---:|---|
| [`commit-craft`](#commit-craft) | Write Conventional-Commit messages from your current changes | ✓ | → `release-notes`, `git-ship` |
| [`git-ship`](#git-ship) | Clean the tree, split into logical commits, push, and optionally merge (one confirmation) | ✓ | ← `commit-craft` |
| [`release-notes`](#release-notes) | Build a categorized changelog / release notes between two refs | ✓ | ← `commit-craft` · → `pr-describe` |
| [`pr-describe`](#pr-describe) | Draft a PR title + description from your branch diff | ✓ | ← `release-notes`, `repo-map` |
| [`repo-map`](#repo-map) | Concise architecture / onboarding map of a repo | ✓ | → `pr-describe` |
| [`dep-check`](#dep-check) | Audit dependencies for outdated & vulnerable packages (npm/pip/cargo) | ✓ | — |
| [`test-scaffold`](#test-scaffold) | Generate a test-file skeleton matching the project's framework | ✓ | — |
| [`context-handoff`](#context-handoff) | Capture the conversation to `.claude/handoff.md` + emit a restart prompt | ✓ | — |
| [`dotnet-db-modernizer`](#dotnet-db-modernizer) | Audit & modernize DB code in legacy .NET via analyze→plan→approve→implement | ✓ | — |
| [`iterative-improver`](#iterative-improver) | Improve anything via an autonomous improver+critic loop for N rounds | ✓ | — |

### Composition chains

```
Ship a release:   commit-craft  →  release-notes  →  pr-describe
Onboard + PR:     repo-map      →  pr-describe
Commit + push:    commit-craft  →  git-ship
```

Each composing skill is still fully useful on its own.

---

## 🔍 Skill reference

### commit-craft
**What:** Generates a clean [Conventional Commits](https://www.conventionalcommits.org)
message from your current git changes.
**Triggers when:** you ask to write/improve a commit message or commit staged work.
**Use it:**
```
/commit-craft
"write a commit message for my staged changes"
```
**Produces:** a `type(scope): subject` line + body explaining *why*, shown for
review (it does **not** commit unless you ask). **Deps:** git.
**Install one skill:** `ln -sfn "$(pwd)/skills/commit-craft" "$HOME/.claude/skills/commit-craft"`

### git-ship
**What:** End-to-end "get my work onto GitHub": smart-stages real changes (skips
junk/secrets), fixes `.gitignore`, splits into logical Conventional-Commit
commits, pushes after **one** confirmation, and optionally merges the branch.
**Triggers when:** "commit and push", "clean up git and ship", "merge this into main".
**Use it:**
```
/git-ship
"clean up git and ship my code"
"ship this and merge it into main"
```
**Produces:** a plan (gitignore changes + each commit + push target) for one
confirmation, then commits + push. Never pushes to `main`/`master` (offers a
branch); never stages secrets. **Deps:** git. **Composes:** uses `commit-craft`
message rules.
**Install one skill:** `ln -sfn "$(pwd)/skills/git-ship" "$HOME/.claude/skills/git-ship"`

### release-notes
**What:** Builds categorized release notes / a CHANGELOG section from git history
between two refs, in [Keep a Changelog](https://keepachangelog.com) style.
**Triggers when:** "release notes for vX", "what changed since the last tag",
"add a changelog entry".
**Use it:**
```
/release-notes
"write release notes from v1.2.0 to HEAD"
```
**Produces:** a dated, sectioned (Added/Fixed/Changed/…) version block; inserts
into `CHANGELOG.md` if present. **Deps:** git (+ bundled `scripts/collect.sh`).
**Composes:** ← `commit-craft`, → `pr-describe`.
**Install one skill:** `ln -sfn "$(pwd)/skills/release-notes" "$HOME/.claude/skills/release-notes"`

### pr-describe
**What:** Drafts a PR title and description from the diff between your branch and
its base.
**Triggers when:** "write a PR description", "summarize my branch for review",
"help me open a PR".
**Use it:**
```
/pr-describe
"write a PR description for this branch against main"
```
**Produces:** a copy-paste PR title + Summary/Changes/Testing/Notes body, grounded
in the diff (only opens a PR if you explicitly ask). **Deps:** git.
**Composes:** ← `release-notes`, `repo-map`.
**Install one skill:** `ln -sfn "$(pwd)/skills/pr-describe" "$HOME/.claude/skills/pr-describe"`

### repo-map
**What:** Produces a concise architecture/onboarding map — what the repo is, key
directories, real build/test/run commands, and how the pieces fit.
**Triggers when:** "give me an overview of this repo", "I'm new here, where do I
start", "map out the architecture".
**Use it:**
```
/repo-map
"give me an onboarding overview of this codebase"
```
**Produces:** a screenful map (layout, commands, data flow, good first files);
offers to save as `docs/REPO_MAP.md`. **Deps:** none.
**Composes:** → `pr-describe`.
**Install one skill:** `ln -sfn "$(pwd)/skills/repo-map" "$HOME/.claude/skills/repo-map"`

### dep-check
**What:** Audits dependencies for outdated and known-vulnerable packages across
npm/pnpm, pip/Poetry, and cargo.
**Triggers when:** "are my deps up to date", "run a security audit on packages",
"what should I upgrade".
**Use it:**
```
/dep-check
"check my dependencies for vulnerabilities"
```
**Produces:** a prioritized table (security fixes vs. routine updates, major-bump
warnings); recommends commands but doesn't upgrade unless asked. **Deps:** the
ecosystem's own tools (npm/pip-audit/cargo-audit) where present.
**Install one skill:** `ln -sfn "$(pwd)/skills/dep-check" "$HOME/.claude/skills/dep-check"`

### test-scaffold
**What:** Generates a test-file skeleton mirroring a source file's public surface,
matching the project's existing framework and layout.
**Triggers when:** "scaffold tests for X", "create a test file for this module",
"stub out unit tests".
**Use it:**
```
/test-scaffold
"scaffold tests for src/parser.py"
```
**Produces:** a test file in the conventional location with happy-path + edge-case
stubs (TODO-marked), then runs the suite once to confirm discovery. **Deps:** the
project's test framework.
**Install one skill:** `ln -sfn "$(pwd)/skills/test-scaffold" "$HOME/.claude/skills/test-scaffold"`

### context-handoff
**What:** Captures the live conversation into `.claude/handoff.md` (goal, status,
decisions, files/git state, commands/results, open questions, next steps) and
prints a ready-to-paste restart prompt — so you can `/clear` or restart without
losing context. A skill can't clear its own window, so this preserves everything
across the clear.
**Triggers when:** context is filling up, before `/clear` or `/compact`, "save
the context / hand this off / capture and restart".
**Use it:**
```
/context-handoff
"capture the context and give me a restart prompt"
```
Then run `/clear` and paste the restart prompt it prints.
**Produces:** `.claude/handoff.md` (gitignored) + a restart prompt. Doesn't clear
or commit anything itself. **Deps:** git (for state capture).
**Install one skill:** `ln -sfn "$(pwd)/skills/context-handoff" "$HOME/.claude/skills/context-handoff"`

### dotnet-db-modernizer
**What:** Audits and modernizes database-access code in legacy .NET projects (Web
Forms/WinForms, .NET Framework, C# **and** VB.NET) using a strict
**analyze → plan → approve → implement** workflow — it never edits source before
you approve a written plan.
**Triggers when:** "clean up our database code", "modernize the data layer", "fix
SQL injection / undisposed connections", "migrate off SqlHelper / OleDb / typed
DataSets", or pointed at a `.sln`/`.csproj`/`.vbproj`.
**Use it:**
```
/dotnet-db-modernizer
"audit and modernize the data access in ./src"
```
**Produces:** a read-only inventory (via `scripts/inventory.py`), a
`DB-MODERNIZATION-PLAN.md` with risk flags + target-stack options, then stops for
approval; implements incrementally only on approval. Optional read-only live
schema inspection; treats connection strings as secrets. Covers SQL Server,
MySQL, PostgreSQL, Oracle, SQLite, OleDb/Odbc. **Deps:** Python 3 (crawler);
.NET toolchain for the implement phase.
**Packaged:** [`dist/dotnet-db-modernizer.skill`](dist/).
**Install one skill:** `ln -sfn "$(pwd)/skills/dotnet-db-modernizer" "$HOME/.claude/skills/dotnet-db-modernizer"`

### iterative-improver
**What:** A general-purpose, autonomous improvement engine. Point it at anything
(code, prose, a prompt, a config, a design) with a round count; it evaluates the
target, researches what excellent looks like, builds a measurable weighted
rubric + baseline, then runs an **improver + critic** multi-agent loop for N
rounds — keeping the best version each round and showing a diff + score per pass.
**Triggers when:** "improve this", "make X better", "run 5 improvement passes on Y",
"keep refining until it's great".
**Use it:**
```
/iterative-improver
"improve README.md, run 5 rounds"
```
**Produces:** a rubric + baseline, per-round diff/score reports, and the best
result applied at the end (on a copy or git branch, reversibly) with a score
trajectory. **Deps:** subagents (Agent/Task tool); for code targets, the build/test
toolchain so verifiable criteria can be checked.
**Install one skill:** `ln -sfn "$(pwd)/skills/iterative-improver" "$HOME/.claude/skills/iterative-improver"`

---

## 🗂️ Repo layout

```
skills/
  <skill-name>/
    SKILL.md          # required: YAML frontmatter (name, description) + instructions
    scripts/          # optional: helper scripts the skill runs
    references/       # optional: docs loaded by the skill only when needed
dist/                 # optional: packaged .skill bundles
```

A `SKILL.md` is Markdown with YAML frontmatter:

```yaml
---
name: my-skill          # kebab-case, ≤ 64 chars, matches the folder name
description: What it does and WHEN to use it — this is how Claude decides to invoke it.
---
```

The `description` is the **trigger** — Claude only loads a skill when the
description matches the task, so it must say *what it does AND when to use it*.

---

## ➕ Adding / packaging a new skill

1. `mkdir -p skills/<name>` and add a `SKILL.md` with the frontmatter above.
2. Write the `description` to say **what it does and when to use it**.
3. Put helper scripts in the skill's own `scripts/`, long docs in `references/`.
4. Add the skill to the [Catalog](#-catalog) and a [Skill reference](#-skill-reference)
   entry.
5. (Optional) Package it as a distributable `.skill` bundle — run from the
   skill-creator directory:

   ```bash
   python3 -m scripts.package_skill /abs/path/to/skills/<name> /abs/path/to/dist
   ```
