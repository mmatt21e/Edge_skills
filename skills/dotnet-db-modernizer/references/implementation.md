# Implementation Playbook (Phase 3 — after approval only)

Begin only on explicit approval. **Respect partial approvals exactly:** implement
the steps the user approved and no others. If they approved steps 1–3, stop after
3 and check back before touching 4.

## Work in small, checkpointed units

Legacy code hides surprises, so make each change cheap to verify and revert:

1. Pick **one logical unit** — a single DAO/class, one module, or one step from
   the plan. Not "all of the data layer at once."
2. Make the change.
3. **Checkpoint:** build the project (or the affected project). If a test suite
   exists, run the relevant tests. Show the diff.
4. Only then move to the next unit. If a checkpoint fails, fix or revert before
   proceeding — don't pile changes on a broken build.

This rhythm (one unit → build → diff → next) is what keeps a modernization from
turning into an unreviewable, unrevertible mess.

## Modernization fundamentals

Apply these as you touch each unit — they're the core value, independent of which
target stack was chosen:

- **Parameterize all SQL.** Replace every concatenated/interpolated query with
  parameters (`@p` + `Parameters.Add`, or Dapper's anonymous-object params).
  This kills injection risk and improves plan caching. Highest priority.
- **Deterministic disposal.** Wrap connections, commands, readers, and
  transactions in `using` (C#) / `Using … End Using` (VB). Prefer one connection
  per logical operation; let pooling handle reuse.
- **Async where the call site allows.** Use `OpenAsync`/`ExecuteReaderAsync`/etc.
  *only* where the calling code can be async end-to-end. Forcing async into a
  synchronous Web Forms event handler via `.Result`/`.Wait()` causes deadlocks —
  if the call site can't go async cleanly, leave it sync and note it.
- **Leave pooling on.** Remove `Pooling=false` unless there's a documented reason.
- **Move secrets/config out of source.** Hardcoded connection strings → config +
  a secret store (env vars, user-secrets, Key Vault, etc. — match the
  environment). Never commit a real connection string.
- **Dependency injection where the framework supports it.** Modern .NET: register
  the connection/context in DI. .NET Framework / Web Forms: DI is limited — don't
  force a container in; a connection-factory class is often the pragmatic move.
- **Update provider packages** per `providers.md` (e.g. `System.Data.SqlClient` →
  `Microsoft.Data.SqlClient`), watching for the behavior changes noted there
  (notably the `Encrypt=true` default).

## Converge, don't fork

If a partial migration exists, extend it. Don't introduce a third pattern. The
end state should be *fewer* ways of doing data access than you started with, not
more.

## Preserve behavior

Modernization is not a feature change. Keep query results, ordering, null
handling, and transaction boundaries equivalent unless the user explicitly asked
to change them. When you must make a judgment call (a type mismatch, an ambiguous
null), surface it rather than silently "fixing" it.
