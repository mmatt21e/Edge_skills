#!/usr/bin/env python3
"""
inventory.py — Whole-project database-access crawler for legacy .NET projects.

Walks a .NET solution/project tree (C# and VB.NET) and inventories every
database touchpoint: connection strings, ADO.NET connection/command objects,
inline vs. parameterized SQL, stored-proc calls, DAL/helper classes, typed
DataSets, provider packages, and common risk patterns (concatenated SQL,
undisposed connections, disabled pooling, secrets in source).

This is the deterministic first pass of the dotnet-db-modernizer skill. It only
READS files and prints a report — it never modifies anything, and it redacts
any secrets it finds (passwords in connection strings are never echoed).

Usage:
    python inventory.py [PROJECT_ROOT] [--json OUT.json]

Defaults to the current directory. Exit code is always 0 unless the root is
missing, so the skill can rely on the report rather than the status code.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Directories that never contain hand-written source worth scanning.
SKIP_DIRS = {
    "bin", "obj", "packages", ".git", ".vs", "node_modules",
    "TestResults", "_ReSharper.Caches", "dist", "build",
}

SOURCE_EXTS = {".cs", ".vb"}
CONFIG_NAMES_SUFFIX = (".config",)  # web.config, app.config, *.config
JSON_CONFIG_GLOB = "appsettings*.json"

# --- Provider fingerprints -------------------------------------------------
# Maps a regex (matched against source/imports) to a provider label.
PROVIDER_PATTERNS = {
    "SQL Server (System.Data.SqlClient - legacy)": r"\bSystem\.Data\.SqlClient\b|\bSqlConnection\b|\bSqlCommand\b",
    "SQL Server (Microsoft.Data.SqlClient - modern)": r"\bMicrosoft\.Data\.SqlClient\b",
    "OLE DB": r"\bSystem\.Data\.OleDb\b|\bOleDbConnection\b|\bOleDbCommand\b",
    "ODBC": r"\bSystem\.Data\.Odbc\b|\bOdbcConnection\b|\bOdbcCommand\b",
    "Oracle (System.Data.OracleClient - deprecated)": r"\bSystem\.Data\.OracleClient\b",
    "Oracle (ODP.NET)": r"\bOracle\.(ManagedDataAccess|DataAccess)\b|\bOracleConnection\b",
    "MySQL": r"\bMySql\.Data\b|\bMySqlConnection\b|\bMySqlConnector\b",
    "PostgreSQL (Npgsql)": r"\bNpgsql\b|\bNpgsqlConnection\b",
    "SQLite": r"\bSystem\.Data\.SQLite\b|\bMicrosoft\.Data\.Sqlite\b|\bSQLiteConnection\b|\bSqliteConnection\b",
}

# --- Legacy DAL / pattern fingerprints -------------------------------------
DAL_PATTERNS = {
    "Microsoft SqlHelper (Data Access Application Block)": r"\bSqlHelper\b",
    "Enterprise Library DAAB": r"Microsoft\.Practices\.EnterpriseLibrary\.Data|\bDatabaseFactory\b|\bGetDatabase\(",
    "Typed DataSet / TableAdapter": r"\bTableAdapter\b|\bSystem\.Data\.DataSet\b|: *DataSet\b",
    "Generic DataAdapter fill": r"\bDataAdapter\b|\.Fill\(",
}

# --- SQL + risk patterns ---------------------------------------------------
SQL_KEYWORD = r"(?:SELECT|INSERT\s+INTO|UPDATE|DELETE\s+FROM|MERGE|EXEC(?:UTE)?)\b"
# A string literal that looks like SQL.
SQL_LITERAL = re.compile(r'(?:"|@")[^"]*\b' + SQL_KEYWORD, re.IGNORECASE)
# String concatenation building SQL: a SQL-looking literal followed by + or & then a non-literal token.
CONCAT_SQL = re.compile(
    r'(?:"|@")[^"]*\b' + SQL_KEYWORD + r'[^"]*"\s*[+&]\s*[A-Za-z_@]',
    re.IGNORECASE,
)
PARAM_USE = re.compile(r"\.Parameters\.(Add|AddWithValue)\b|new\s+Sql(?:Db)?Parameter\b|\bDbParameter\b")
STORED_PROC = re.compile(r"CommandType\.StoredProcedure|\bEXEC(?:UTE)?\s+\w", re.IGNORECASE)
ASYNC_CALL = re.compile(r"\b(ExecuteReaderAsync|ExecuteNonQueryAsync|ExecuteScalarAsync|OpenAsync)\b")
SYNC_CALL = re.compile(r"\b(ExecuteReader|ExecuteNonQuery|ExecuteScalar)\s*\(")
USING_BLOCK = re.compile(r"\busing\s*\(|\bUsing\b")  # C# using( ... ) and VB Using
CONN_CREATE = re.compile(r"new\s+\w*Connection\b")
POOLING_OFF = re.compile(r"Pooling\s*=\s*false", re.IGNORECASE)

# Hardcoded connection string in source (heuristic): a literal containing two
# of the usual connection-string keywords.
CONN_KEYWORDS = r"(?:Data Source|Server|Initial Catalog|Database|User Id|Uid|Password|Pwd|Integrated Security|Provider|Host|Port)"
HARDCODED_CONN = re.compile(
    r'"(?=[^"]*' + CONN_KEYWORDS + r'\s*=)(?=[^"]*[;=])[^"]{12,}"',
    re.IGNORECASE,
)

# Secret-bearing keys, for redaction.
SECRET_KEY = re.compile(r"(password|pwd)\s*=\s*[^;\"']+", re.IGNORECASE)


def redact(s: str) -> str:
    """Mask password/pwd values so secrets are never echoed in the report."""
    return SECRET_KEY.sub(lambda m: m.group(0).split("=")[0] + "=***REDACTED***", s)


def iter_files(root: Path):
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        yield p


def scan_config(path: Path, findings: dict):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return
    # connectionStrings entries in XML config
    for m in re.finditer(r'connectionString\s*=\s*"([^"]+)"', text, re.IGNORECASE):
        findings["connection_strings"].append({
            "file": str(path),
            "value": redact(m.group(1)),
            "source": "config",
        })
    # appsettings.json connection strings
    if path.name.lower().startswith("appsettings"):
        for m in re.finditer(r'"([^"]*onnection[^"]*)"\s*:\s*"([^"]+)"', text):
            findings["connection_strings"].append({
                "file": str(path),
                "value": redact(m.group(2)),
                "source": "appsettings.json",
            })


def scan_source(path: Path, findings: dict):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return
    lang = "VB.NET" if path.suffix == ".vb" else "C#"
    lines = text.splitlines()

    def add(bucket, line_no, snippet, **extra):
        item = {"file": str(path), "lang": lang, "line": line_no,
                "snippet": snippet.strip()[:200]}
        item.update(extra)
        findings[bucket].append(item)

    # Whole-file provider + DAL fingerprints (cheap, report once per file).
    for label, pat in PROVIDER_PATTERNS.items():
        if re.search(pat, text):
            findings["providers"].setdefault(label, []).append(str(path))
    for label, pat in DAL_PATTERNS.items():
        if re.search(pat, text):
            findings["dal_patterns"].setdefault(label, []).append(str(path))

    # Line-level patterns + risk flags.
    file_has_conn = bool(CONN_CREATE.search(text))
    file_has_using = bool(USING_BLOCK.search(text))
    for i, line in enumerate(lines, start=1):
        if CONCAT_SQL.search(line):
            add("risks", i, line, kind="SQL built by string concatenation (injection risk)")
        elif SQL_LITERAL.search(line):
            add("inline_sql", i, line)
        if STORED_PROC.search(line):
            add("stored_procs", i, line)
        if HARDCODED_CONN.search(line):
            add("risks", i, redact(line), kind="Hardcoded connection string / secret in source")
            add("connection_strings", i, redact(line), source="hardcoded")
        if POOLING_OFF.search(line):
            add("risks", i, redact(line), kind="Connection pooling disabled (Pooling=false)")

    # File-level signals.
    if PARAM_USE.search(text):
        findings["parameterized_files"].append(str(path))
    if SYNC_CALL.search(text) and not ASYNC_CALL.search(text):
        findings["sync_only_files"].append(str(path))
    # A connection created in a file with no using/Using is a disposal smell.
    if file_has_conn and not file_has_using:
        findings["risks"].append({
            "file": str(path), "lang": lang, "line": 0,
            "kind": "Connection object created without a using/Using block (possible undisposed connection)",
            "snippet": "",
        })


def dedupe(seq):
    seen, out = set(), []
    for x in seq:
        k = json.dumps(x, sort_keys=True)
        if k not in seen:
            seen.add(k); out.append(x)
    return out


def build_inventory(root: Path) -> dict:
    findings = {
        "root": str(root),
        "solutions": [], "projects": [],
        "connection_strings": [], "providers": {}, "dal_patterns": {},
        "inline_sql": [], "stored_procs": [], "parameterized_files": [],
        "sync_only_files": [], "typed_datasets": [], "risks": [],
    }
    for p in iter_files(root):
        suffix = p.suffix.lower()
        if suffix == ".sln":
            findings["solutions"].append(str(p))
        elif suffix in (".csproj", ".vbproj"):
            findings["projects"].append(str(p))
        elif suffix == ".xsd":
            findings["typed_datasets"].append(str(p))
        elif suffix in SOURCE_EXTS:
            scan_source(p, findings)
        elif p.name.endswith(CONFIG_NAMES_SUFFIX) or p.match(JSON_CONFIG_GLOB):
            scan_config(p, findings)

    findings["connection_strings"] = dedupe(findings["connection_strings"])
    findings["risks"] = dedupe(findings["risks"])
    return findings


def print_report(inv: dict):
    def n(key):
        v = inv[key]
        return len(v) if isinstance(v, list) else sum(len(x) for x in v.values())

    print("=" * 70)
    print("  .NET DATABASE-ACCESS INVENTORY")
    print(f"  root: {inv['root']}")
    print("=" * 70)
    print(f"Solutions: {len(inv['solutions'])}   Projects: {len(inv['projects'])}")
    print()

    print("PROVIDERS DETECTED")
    if inv["providers"]:
        for label, files in sorted(inv["providers"].items()):
            print(f"  - {label}  ({len(files)} file(s))")
    else:
        print("  (none detected)")
    print()

    print("LEGACY DAL / PATTERNS")
    if inv["dal_patterns"]:
        for label, files in sorted(inv["dal_patterns"].items()):
            print(f"  - {label}  ({len(files)} file(s))")
    if inv["typed_datasets"]:
        print(f"  - Typed DataSet .xsd files: {len(inv['typed_datasets'])}")
    if not inv["dal_patterns"] and not inv["typed_datasets"]:
        print("  (none detected)")
    print()

    print("TOUCHPOINT COUNTS")
    print(f"  Connection strings found ...... {len(inv['connection_strings'])} (passwords redacted)")
    print(f"  Inline SQL literals ........... {len(inv['inline_sql'])}")
    print(f"  Stored-proc call sites ........ {len(inv['stored_procs'])}")
    print(f"  Files using parameters ........ {len(inv['parameterized_files'])}")
    print(f"  Sync-only data files .......... {len(inv['sync_only_files'])}")
    print()

    print(f"RISK FLAGS ({len(inv['risks'])})")
    if inv["risks"]:
        # Group by kind.
        by_kind: dict[str, list] = {}
        for r in inv["risks"]:
            by_kind.setdefault(r["kind"], []).append(r)
        for kind, items in sorted(by_kind.items(), key=lambda kv: -len(kv[1])):
            print(f"  [{len(items)}] {kind}")
            for it in items[:5]:
                loc = f"{it['file']}:{it['line']}" if it.get("line") else it["file"]
                print(f"        {loc}")
            if len(items) > 5:
                print(f"        ... and {len(items) - 5} more")
    else:
        print("  (none detected)")
    print()
    print("Next: read the relevant references/ files, then write "
          "DB-MODERNIZATION-PLAN.md. Do NOT edit source before the plan is approved.")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Inventory .NET database-access code.")
    ap.add_argument("root", nargs="?", default=".", help="Project root (default: .)")
    ap.add_argument("--json", metavar="OUT", help="Also write full findings as JSON")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"Error: root not found: {root}", file=sys.stderr)
        return 2

    inv = build_inventory(root)
    print_report(inv)
    if args.json:
        Path(args.json).write_text(json.dumps(inv, indent=2))
        print(f"\nFull findings written to {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
