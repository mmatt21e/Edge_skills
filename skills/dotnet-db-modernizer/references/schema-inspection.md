# Optional Live Schema Inspection (read-only)

If — and only if — the user supplies a connection string and the database is
reachable, you may connect to inspect the real schema so the plan matches
reality (actual table/column names, types, keys, stored procs). This is always
optional; everything works without it.

## Hard rules

- **Read-only.** Run only `SELECT` against catalog/`INFORMATION_SCHEMA` views.
  Never `INSERT/UPDATE/DELETE/CREATE/ALTER/DROP`, never modify data or schema.
- **The connection string is a secret.** Never write it into source files, the
  plan, generated config, logs, or chat. Pass it via an environment variable or
  a prompt input; do not persist it. When referencing it in the plan, refer to
  "the supplied connection string", never its value.
- **Detect the provider from the connection string** (see `providers.md` shapes)
  and use the matching client/CLI.
- **Fail soft.** If the DB is unreachable, credentials fail, or no driver is
  available, note "schema not inspected (connection unavailable)" in the plan
  and continue with static analysis only. Do not block the workflow.

## What to collect

Tables and views, columns (name, type, nullability), primary/foreign keys, and
stored-procedure names/signatures. This lets the plan flag mismatches between the
code's assumptions and the real schema (e.g. code reading a column that no longer
exists, or `string` mapping where the column is `decimal`).

## How to connect

Prefer a provider CLI if present, else a tiny throwaway query script. Read the
connection string from the environment so it never lands on disk:

- **SQL Server**: `sqlcmd -C` or a short script over `Microsoft.Data.SqlClient`.
  Catalog: `INFORMATION_SCHEMA.TABLES`, `INFORMATION_SCHEMA.COLUMNS`,
  `sys.foreign_keys`, `sys.procedures`.
- **PostgreSQL**: `psql "$CONN"` then `\dt`, `\d+`, or query `information_schema`.
- **MySQL**: `mysql` client or `information_schema`.
- **Oracle**: `ALL_TAB_COLUMNS`, `USER_PROCEDURES` via ODP.NET / `sqlplus`.
- **SQLite**: `sqlite3 file.db ".schema"` — local file, still read-only.

Example (SQL Server, secret stays in the env):

```bash
export DBCONN='...'        # provided by the user, never committed
sqlcmd -C -S "$SERVER" -Q "SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE \
  FROM INFORMATION_SCHEMA.COLUMNS ORDER BY TABLE_NAME"
```

Summarize findings in the plan's "What was found" section in redacted,
schema-only terms (no credentials, no data rows).
