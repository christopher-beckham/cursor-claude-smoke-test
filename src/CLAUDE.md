SMOKE_SRC_CLAUDE_MD

This CLAUDE.md is scoped to the src/ subdirectory. It contains more detailed conventions
than the root CLAUDE.md, relevant only when working on source files.

## src/ conventions

- `ingest.py` is the only entry point. Do not add a second top-level script.
- All new functions must have a corresponding test in `tests/test_ingest.py`.
- The `Row` dataclass is the canonical data structure. Do not introduce a second one.
- If adding a new CSV column, update `Row`, `load_csv`, and `write_csv` together — never
  partially.
- `run.sh` must remain the sole orchestration entry point. Do not add a Makefile target
  or second shell script that duplicates its logic.
