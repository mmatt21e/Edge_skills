# Plan Template — `DB-MODERNIZATION-PLAN.md`

Write this file at the project root during Phase 2. Fill every section from the
actual inventory and code reading. Keep it concrete (real file paths, real
provider names). This is the artifact the user reviews and approves — nothing
gets implemented until they do.

```markdown
# Database Modernization Plan

## 1. Summary
<2–4 sentences: what this codebase's data layer looks like today, the proposed
direction, and the expected benefit. Plain language.>

## 2. What was found
- **Projects / frameworks:** <e.g. WebApp.csproj (.NET Framework 4.7.2, Web Forms, C#), Data.vbproj (VB.NET)>
- **Providers:** <each provider + where used>
- **Data-access patterns:** <SqlHelper / DAAB / typed DataSets / inline SQL / Dapper-in-progress / …>
- **Connection strings:** <count + locations, e.g. "2 in web.config, 1 hardcoded" — NO values>
- **Live schema:** <inspected read-only / not inspected (no connection supplied)>

### Risk flags
<From the crawler + your review. Be specific with file:line.>
- [ ] SQL injection via concatenated SQL — `path:line`
- [ ] Undisposed connections (no using/Using) — `path`
- [ ] Sync-over-async I/O — `path`
- [ ] Connection pooling disabled — `path:line`
- [ ] Secrets in source — `path:line`

## 3. Proposed target stack
**Recommendation:** <stack> — <one-line rationale tied to the framework constraint>.

**Alternatives considered:**
- <Option A> — <trade-off>
- <Option B> — <trade-off>

<If more than one genuinely fits, ask the user to choose here.>

## 4. Migration steps (ordered, incremental)
Each step is one logical unit with a build/diff checkpoint after it.
1. <e.g. Move connection strings out of source into config + secret store>
2. <e.g. Replace concatenated SQL in OrderDao with parameterized queries>
3. <e.g. Introduce Dapper in the Orders module, converging with the existing partial migration>
4. <e.g. Swap System.Data.SqlClient → Microsoft.Data.SqlClient (note Encrypt default)>
5. <...>

## 5. Risks & manual decisions
- <e.g. Microsoft.Data.SqlClient defaults Encrypt=true — needs cert/TrustServerCertificate decision>
- <e.g. Typed DataSet removal changes designer-bound UI — needs verification>
- <Anything requiring a human call before/while implementing>

## 6. Out of scope
- <e.g. Web Forms → ASP.NET Core platform migration (separate, larger effort)>
- <Dead code deletion pending confirmation, etc.>
```

After writing it, **summarize in chat and stop for approval.** Make clear that
implementation begins only on the user's go-ahead, and that they can approve a
subset of the steps.
