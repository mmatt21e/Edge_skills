# Detection & Inventory Guide

How to turn the crawler's output into a real understanding of the data layer,
and what to look for that a regex pass can miss.

## What counts as a "database touchpoint"

- **Connection strings** — in `web.config` / `app.config`
  (`<connectionStrings>`), `appsettings*.json`, or hardcoded in source.
- **Connection / command objects** — `SqlConnection`, `OleDbConnection`,
  `OdbcConnection`, `OracleConnection`, `MySqlConnection`, `NpgsqlConnection`,
  `SQLiteConnection`, and their `*Command`, `*DataReader`, `*DataAdapter` peers.
- **SQL** — string literals containing `SELECT/INSERT/UPDATE/DELETE/EXEC`.
  Distinguish **parameterized** (`.Parameters.Add…`, `@p`) from **concatenated**
  (`"... WHERE id=" + id`) — the latter is an injection risk.
- **Stored procedures** — `CommandType.StoredProcedure`, or `EXEC sp_name`.
- **Legacy DAL/helpers** — `SqlHelper`, Enterprise Library DAAB
  (`Microsoft.Practices.EnterpriseLibrary.Data`, `DatabaseFactory`), generic
  `DataAdapter.Fill`, home-grown base DAO classes.
- **Typed DataSets** — `.xsd` files plus generated `*.Designer.cs/.vb`,
  `TableAdapter`, `DataSet` subclasses. These are deceptively deep — the `.xsd`
  hides a lot of generated SQL.

## Reading the crawler output

The crawler (`scripts/inventory.py`) is a fast first pass — it locates things,
it does not judge architecture. After running it:

1. Open the files behind the **risk flags** first (injection, undisposed
   connections, secrets, disabled pooling). Confirm each is real; regexes
   produce some false positives (e.g. SQL inside a comment).
2. Open one or two files per **DAL pattern** to learn the project's house style:
   how a query is normally run, how results are mapped, how errors/transactions
   are handled. Your modernization should match the codebase's grain.
3. Note **VB.NET vs C#** mix. VB uses `Imports`, `&` for concatenation, `Using …
   End Using`, and no semicolons — keep that in mind for both detection and any
   later edits.

## Reading messy / half-migrated reality

Legacy data layers are rarely clean. Expect and explicitly catalog:

- **Two patterns at once** — e.g. most code on raw `SqlHelper`, a newer folder on
  Dapper. Decide which is the intended direction (usually the newer/partial one)
  and plan to **converge on it**, not introduce a third.
- **Abandoned migrations** — an `EntityFramework` package referenced but only one
  `DbContext` half-written. Treat it as a signal of intent, but verify it builds
  and is actually used before extending it.
- **Dead code** — DAOs no one calls. Don't spend modernization effort here; flag
  as "candidate for deletion (verify with user)".
- **Copy-paste drift** — the same query duplicated with slight differences. Note
  it; consolidation may be part of the plan but is a behavior-changing decision.
- **Hidden SQL** — inside `.xsd` TableAdapters, resource files, or string
  constants assembled far from the call site. Grep beyond what the crawler shows
  if counts seem too low for the app's size.

The deliverable of this phase is an accurate mental model, captured in the
plan's "What was found" section — not edits.
