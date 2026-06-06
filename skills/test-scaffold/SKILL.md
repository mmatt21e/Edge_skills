---
name: test-scaffold
description: Generate a test-file skeleton that mirrors a source file's public functions and classes, matching the project's existing test framework and conventions. Use when the user asks to scaffold tests, create a test file for a module, or stub out unit tests for new code.
---

# test-scaffold

Create a ready-to-fill test file for a given source module, following the
conventions already used in the project. Standalone.

## When to use

- "Scaffold tests for src/parser.py."
- "Create a test file for this module."
- "Stub out unit tests for the new functions."

## Steps

1. **Identify the framework and layout** by looking at existing tests, not by
   guessing:
   - JS/TS: Jest, Vitest, or Mocha? Where do test files live (`__tests__/`,
     `*.test.ts` alongside source)? ESM or CJS imports?
   - Python: pytest or unittest? `tests/` dir or `test_*.py` alongside?
     How are fixtures shared (`conftest.py`)?
   - Go: standard `*_test.go` with table-driven tests.
   Match the dominant style; do not introduce a new framework.

2. **Enumerate the public surface** of the target file — exported functions,
   classes, and their methods. Skip private/underscore-prefixed and obvious
   trivial getters unless the user wants full coverage.

3. **Generate one test stub per unit** with:
   - The correct import path (relative to where the test file will live).
   - A descriptive test name stating the expected behavior.
   - Arrange / Act / Assert structure with a `TODO` marking where real
     assertions go — plus at least one happy-path and one edge-case stub
     (empty input, error path) per function.

4. **Write the file** to the conventional location and tell the user the path,
   then **run the suite once** to confirm the file is discovered and the stubs
   execute (they may be `skip`-marked or failing-by-TODO — that's expected).

## Example (pytest)

```python
from myapp.parser import parse_config


def test_parse_config_reads_valid_file():
    # Arrange
    # Act
    result = parse_config("fixtures/valid.toml")
    # Assert
    assert result  # TODO: assert specific keys

def test_parse_config_raises_on_missing_file():
    # TODO: assert the documented exception is raised
    ...
```
