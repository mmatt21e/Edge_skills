---
name: dotnet-db-modernizer
description: Analyze and modernize database-access code in legacy .NET projects (Web Forms, WinForms, .NET Framework, both C# and VB.NET). Use this whenever the user wants to audit, assess, refactor, or modernize data-access / ADO.NET / DAL code, fix SQL injection from concatenated SQL, fix undisposed connections or sync-over-async, migrate off System.Data.SqlClient, OleDb, Odbc, System.Data.OracleClient, classic SqlHelper, Enterprise Library DAAB, or typed DataSets, adopt Dapper / EF Core / EF6, or move connection strings out of source — even if they just say "clean up our database code", "our data layer is a mess", or point you at a .sln / .csproj / .vbproj. Follows a strict analyze, then plan, then approve, then implement workflow and never edits source files before a written plan has been reviewed and approved.
---

# .NET Database Modernizer

Modernize the data-access layer of old .NET Framework apps (Web Forms, WinForms,
class libraries; C# and VB.NET) without breaking them. The whole point is to be
*safe on legacy code you don't fully understand yet*, so the work is split into
four phases with a hard gate in the middle.

## The non-negotiable workflow

```
1. ANALYZE  →  2. PLAN  →  [ STOP for approval ]  →  3. IMPLEMENT
```

**Never edit, create, or delete a source file during phases 1–2.** The only file
you may write before approval is `DB-MODERNIZATION-PLAN.md` (and a throwaway JSON
inventory). Reading, grepping, and running the read-only crawler are fine. This
matters because legacy data layers are full of load-bearing weirdness; the user
needs to see and approve the plan before anything changes. If the user says
"just fix it," still produce the plan first and get a yes — it takes a moment and
prevents irreversible damage to code they depend on.

---

## Phase 1 — Analyze

1. **Run the crawler** over the project root. It only reads files, redacts
   passwords, and prints a report:

   ```bash
   python scripts/inventory.py <project-root> --json /tmp/db-inventory.json
   ```

   It inventories solutions/projects, providers, connection strings, inline vs.
   parameterized SQL, stored procs, legacy DAL (SqlHelper, DAAB, typed
   DataSets), and risk flags. Use the JSON for detail and the printed report for
   the overview.

2. **Read the inventory critically.** The crawler finds touchpoints; *you*
   interpret them. Open the most significant files it flagged to confirm
   patterns and understand the real shape of the data layer — don't plan from
   counts alone.

3. **Account for messy reality.** Half-finished migrations, two patterns living
   side by side, dead code, copy-pasted helpers. When a partial modernization
   already exists (e.g. someone started moving to Dapper in one folder),
   **extend that** rather than introducing a third parallel pattern. See
   `references/detection.md` for the patterns to look for and how to read a
   half-refactored codebase.

4. **Identify providers precisely.** A project may use several at once. For
   per-provider detection notes, connection-string shapes, and the package
   upgrade map (e.g. `System.Data.SqlClient` → `Microsoft.Data.SqlClient`), read
   `references/providers.md`.

5. **Optional live schema inspection.** *Only if* the user supplies a connection
   string and the database is reachable, connect **read-only** to inspect the
   real schema so the plan matches reality. Detect the provider from the
   connection string. The connection string is a **secret**: never write it into
   source, the plan, generated config, or chat. Follow `references/schema-inspection.md`
   exactly. Everything works without a live connection — just note the schema as
   "not inspected" in the plan.

---

## Phase 2 — Plan

Write **`DB-MODERNIZATION-PLAN.md` at the project root** using the structure in
`references/plan-template.md`. It must contain: a summary, what was found
(including the risk flags), the proposed target stack *with rationale and
alternatives*, ordered incremental steps, risks/manual decisions, and
out-of-scope items.

Choosing the target stack is a **judgment call, not a default**. The framework
constrains the options (EF Core needs modern .NET; .NET Framework realistically
gets Dapper, modernized ADO.NET, or EF6). When more than one option genuinely
fits, present them with trade-offs and let the user choose. A full Web Forms
platform migration is a separate, much larger decision — never bundle it
silently into a data-layer plan; call it out as out-of-scope. See
`references/target-stacks.md` for the decision guide.

Then **summarize the plan in chat and STOP for approval.** Do not start
implementing.

---

## Phase 3 — Implement (only after approval)

Proceed only on explicit approval, and **respect partial approvals exactly** —
if the user approves steps 1–3 but not 4, do only 1–3.

Work **one logical unit at a time** with a build/diff checkpoint after each, so
problems surface early and stay easy to revert. Apply the modernization
fundamentals (parameterize all SQL, `using`-based disposal, async where the call
site allows, keep pooling on, move secrets/config out of source, dependency
injection where the framework supports it, update provider packages). The full
implementation playbook — including how to sequence changes and what "one unit"
means — is in `references/implementation.md`.

---

## Reference index

Read these as needed (progressive disclosure — don't load them all up front):

| File | When to read |
|------|--------------|
| `references/detection.md` | Phase 1: what to inventory, legacy patterns, reading messy/half-migrated code |
| `references/providers.md` | Phase 1: per-provider detection, connection-string shapes, package upgrade map |
| `references/schema-inspection.md` | Phase 1: optional read-only live schema inspection + secret handling |
| `references/target-stacks.md` | Phase 2: choosing Dapper vs. EF Core vs. EF6 vs. modernized ADO.NET |
| `references/plan-template.md` | Phase 2: exact structure of `DB-MODERNIZATION-PLAN.md` |
| `references/implementation.md` | Phase 3: incremental migration playbook + fundamentals |

## Guardrails (always)

- No source edits before the plan is approved.
- Connection strings are secrets — inspect read-only, never persist or echo them.
- A project may use multiple providers; handle each independently.
- Extend an existing partial migration; don't start a competing pattern.
- Platform migration (e.g. Web Forms → ASP.NET Core) is out of scope unless the
  user explicitly asks — flag it, don't do it silently.
