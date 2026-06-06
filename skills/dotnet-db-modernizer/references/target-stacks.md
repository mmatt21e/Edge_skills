# Choosing a Target Stack

The target is a **judgment call constrained by the framework**, not a default.
Present real options when more than one fits, with trade-offs, and let the user
decide. Record the choice and rationale in the plan.

## The framework constraint comes first

| Project target | Realistic data-access options |
|----------------|-------------------------------|
| **.NET Framework 4.x** (Web Forms, WinForms, old class libs) | Modernized **ADO.NET**, **Dapper**, or **EF6**. **EF Core is *not* a fit** without first migrating the platform. |
| **.NET (Core) / modern .NET** | **EF Core**, **Dapper**, modernized ADO.NET. |

Most legacy Web Forms / WinForms apps are on .NET Framework, so the honest menu
is usually **Dapper vs. modernized ADO.NET vs. EF6** — *not* EF Core. Don't
recommend EF Core on a .NET Framework app without explicitly tying it to a
separate platform-migration decision.

## Option trade-offs

- **Modernized ADO.NET** — keep raw ADO.NET but make it correct: parameterized,
  `using`-disposed, async, pooled. *Lowest risk, smallest diff.* Best when the
  team wants minimal change or has heavy stored-proc usage. Most boilerplate.
- **Dapper** — thin micro-ORM over ADO.NET. *Great middle ground:* keeps SQL
  explicit (familiar to a stored-proc/inline-SQL team), removes mapping
  boilerplate, async-friendly, works on .NET Framework. Best default for most
  legacy modernizations that aren't ready for a full ORM.
- **EF6** — full ORM that runs on .NET Framework. Good if the team wants
  entities/LINQ and the schema is relationally clean. Heavier; change-tracking
  and lazy loading can surprise. A real adoption effort, not a refactor.
- **EF Core** — modern, capable, but **requires modern .NET**. Only on the table
  if a platform migration is already in scope.

## Selection guidance

1. Start from the framework constraint — eliminate impossible options.
2. Match the team's existing grain: heavy stored procs / SQL-comfortable → Dapper
   or ADO.NET; desire for entities/LINQ and willing to invest → EF6/EF Core.
3. Honor any **partial migration** already present — converging on it usually
   beats introducing a new stack.
4. Lowest-risk path that meets the goal wins; modernizing fundamentals (see
   `implementation.md`) often delivers most of the value without a new ORM.

## Platform migration is separate

Moving Web Forms → ASP.NET (Core) MVC/Razor, or WinForms → something modern, is a
**much larger, separate decision** with its own risks. Never bundle it silently
into a data-layer plan. If the data-layer goal would benefit from it (e.g. the
user really wants EF Core), name it explicitly as out-of-scope and let the user
decide to open that as its own effort.
