---
name: release-notes
description: Build categorized release notes or a CHANGELOG section from git history between two refs or tags. Use when the user asks for release notes, a changelog entry, "what changed since vX", or to prepare a release. Reads Conventional Commit prefixes produced by commit-craft and feeds pr-describe.
---

# release-notes

Generate human-readable release notes grouped by change type from the commits
between two git refs, formatted to the [Keep a Changelog](https://keepachangelog.com)
convention.

## When to use

- "Write release notes for v2.1.0."
- "What changed since the last tag?"
- "Add a changelog entry for this release."

## Steps

1. **Determine the range.** Default `from` is the most recent tag
   (`git describe --tags --abbrev=0`) and `to` is `HEAD`. If the user names two
   refs, use those.

2. **Collect the commits.** Run the bundled helper:

   ```bash
   bash skills/release-notes/scripts/collect.sh <from> <to>
   ```

   It prints one `subject<TAB>hash` per line. (You can also run the equivalent
   `git log --no-merges --pretty=format:'%s%x09%h' <from>..<to>` directly.)

3. **Categorize** each commit by its Conventional Commit prefix into these
   sections, dropping any that end up empty:
   - **Added** ← `feat`
   - **Fixed** ← `fix`
   - **Changed** ← `refactor`, `perf`, `build`, plain messages
   - **Deprecated / Removed** ← anything noting removal
   - **Security** ← `fix` commits mentioning a CVE or vuln
   - Anything marked `BREAKING CHANGE` gets a bold **⚠ Breaking** callout at top.

4. **Rewrite each line for a reader**, not a committer: strip the `type(scope):`
   prefix, capitalize, keep the short hash as a reference. Skip noise like
   `chore`, `ci`, version-bump, and merge commits.

5. **Emit the section** under a version heading with today's date:

   ```
   ## [2.1.0] - 2026-06-06

   ### Added
   - Dark-mode toggle in settings (a1b2c3d)

   ### Fixed
   - Crash when opening empty config files (e4f5g6h)
   ```

If a CHANGELOG.md already exists, insert the new section directly under the
top heading rather than appending at the end.
