# SMOKE_CLAUDE_MD

This file is read natively by Claude Code. Cursor may or may not surface it.

## Project: CSV ingestion pipeline

A Python pipeline that ingests raw CSV files from `$DATA_DIR/input/`, validates and
transforms each row, and writes clean output to `$DATA_DIR/output/`. Shell scripts
handle scheduling and orchestration.

## How to run

```bash
export DATA_DIR=/tmp/pipeline-data
bash src/run.sh
```

## How to test

```bash
python3 -m pytest tests/ -v
```

## Key conventions

- Python: type hints on all public functions, `pathlib.Path` over `os.path`, `logging`
  not `print`.
- Shell: `set -euo pipefail` at the top of every script. Quote all variable expansions.
- No hardcoded credentials. Secrets come from environment variables only.
- Commit messages: imperative mood, max 72 chars, reference ticket if one exists.

## Repo layout

```
src/
  ingest.py     # main pipeline entry point
  run.sh        # orchestration wrapper
tests/
  test_ingest.py
```
