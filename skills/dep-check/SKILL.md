---
name: dep-check
description: Audit a project's dependencies for outdated and known-vulnerable packages across npm, pip, and cargo ecosystems. Use when the user asks to check dependencies, find outdated packages, run a vulnerability/security audit on libraries, or review what needs upgrading.
---

# dep-check

Report which dependencies are outdated and which have known vulnerabilities,
using each ecosystem's native tooling. Standalone — no other skill required.

## When to use

- "Are my dependencies up to date?"
- "Run a security audit on the packages."
- "What should I upgrade?"

## Steps

1. **Detect the ecosystem(s)** from manifest files present:
   - `package.json` → npm / pnpm / yarn (pick the one matching the lockfile)
   - `requirements.txt`, `pyproject.toml`, `Pipfile` → pip / Poetry / uv
   - `Cargo.toml` → cargo
   A repo may have more than one; check each.

2. **Run the audits** (read-only — never auto-upgrade):

   | Ecosystem | Outdated | Vulnerabilities |
   |---|---|---|
   | npm | `npm outdated` | `npm audit` |
   | pnpm | `pnpm outdated` | `pnpm audit` |
   | pip | `pip list --outdated` | `pip-audit` (if available) |
   | Poetry | `poetry show --outdated` | `poetry run pip-audit` |
   | cargo | `cargo outdated` (plugin) | `cargo audit` (plugin) |

   If a command's tool isn't installed, note it and suggest the install command
   rather than failing silently.

3. **Summarize as a prioritized table**, highest risk first:

   ```
   | Package | Current | Latest | Severity | Notes |
   |---------|---------|--------|----------|-------|
   | lodash  | 4.17.19 | 4.17.21| HIGH     | prototype pollution (CVE-...) |
   ```

   Separate **security fixes** (act now) from **routine updates** (when
   convenient), and flag any update that is a **major** version bump as
   potentially breaking.

4. **Recommend, don't execute.** Propose the upgrade commands but only run them
   if the user explicitly asks. After any upgrade, remind them to run the test
   suite.
