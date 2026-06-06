# Providers Guide

A single project may target several databases at once — detect and plan for each
independently. For every provider found, the plan should name the current
package, the recommended modern package, and any behavior changes the upgrade
implies.

## Detection cues & connection-string shapes

| Provider | Code/namespace cues | Connection-string smell |
|----------|---------------------|--------------------------|
| **SQL Server (legacy)** | `System.Data.SqlClient`, `SqlConnection` | `Data Source=`/`Server=`, `Initial Catalog=`/`Database=`, `Integrated Security=` |
| **SQL Server (modern)** | `Microsoft.Data.SqlClient` | same as above |
| **OLE DB** | `System.Data.OleDb`, `OleDbConnection` | `Provider=…;Data Source=` |
| **ODBC** | `System.Data.Odbc`, `OdbcConnection` | `Driver={…};Server=` or `DSN=` |
| **Oracle (deprecated)** | `System.Data.OracleClient` | `Data Source=…;User Id=` (TNS) |
| **Oracle (ODP.NET)** | `Oracle.ManagedDataAccess`, `OracleConnection` | TNS or EZConnect `host:port/service` |
| **MySQL** | `MySql.Data`, `MySqlConnector`, `MySqlConnection` | `Server=…;Uid=;Pwd=;Database=` |
| **PostgreSQL** | `Npgsql`, `NpgsqlConnection` | `Host=…;Username=;Password=;Database=` |
| **SQLite** | `System.Data.SQLite`, `Microsoft.Data.Sqlite`, `SQLiteConnection` | `Data Source=app.db` |

The crawler reports these automatically; use this table to confirm and to read
hand-rolled connection strings.

## Package upgrade map

| Current (legacy) | Recommended modern | Notes |
|------------------|--------------------|-------|
| `System.Data.SqlClient` | **`Microsoft.Data.SqlClient`** | Drop-in for most code, but **`Encrypt=true` is the default** in newer versions — connections can start failing without `TrustServerCertificate`/a valid cert. Call this out as a manual decision. |
| `System.Data.OracleClient` (deprecated, removed from modern .NET) | **`Oracle.ManagedDataAccess[.Core]`** | API is close but not identical; types move to the `Oracle.*` namespace. |
| `MySql.Data` | `MySql.Data` (current) or **`MySqlConnector`** | `MySqlConnector` is more standards-compliant and async-friendly; namespace differs. |
| `System.Data.SQLite` | **`Microsoft.Data.Sqlite`** | Lighter; some pragmas/behaviors differ. |
| `Npgsql` (old) | **`Npgsql`** (current) | Watch major-version breaking changes (timestamp handling). |
| OLE DB / ODBC to SQL Server | **native `Microsoft.Data.SqlClient`** | Prefer a native provider over OLE DB/ODBC where a first-party one exists. |

## Provider-specific cautions

- **OLE DB / ODBC** are sometimes the *only* option (Access, legacy/exotic
  sources). Don't propose ripping them out unless a native provider truly exists
  for that backend — verify before recommending.
- **Oracle**: `System.Data.OracleClient` does not exist in modern .NET, so any
  future framework move forces ODP.NET — note this even on an EF6/Framework plan.
- **Multiple providers**: keep each migration as a separate step in the plan so
  the user can approve them independently.
