# cursor-smoke-test — Claude Code edition

A probe sequence for understanding what Claude Code picks up from this repo's rule and
context artifacts. See `README.md` for the equivalent Cursor results.

**Test environment:** Claude Code 2.1.165

---

## 1. Sentinel index

| Sentinel | File | Mechanism | Purpose |
|---|---|---|---|
| `SMOKE_CLAUDE_MD` | `CLAUDE.md` | Claude Code always-on | Project-level instructions; always loaded at session start |
| `SMOKE_SRC_CLAUDE_MD` | `src/CLAUDE.md` | Subdirectory CLAUDE.md | Tests whether Claude Code loads subdirectory CLAUDE.md files, and when |
| `SMOKE_CLAUDE_COMMAND_HELLO` | `.claude/commands/hello.md` | Slash command | Tests whether `/hello` is invokable |
| `SMOKE_CLAUDE_COMMAND_DIAGNOSE` | `.claude/commands/diagnose.md` | Slash command | Tests whether `/diagnose` is invokable |
| `SMOKE_CURSOR_LEGACY` | `.cursorrules` | Cursor-only | Not auto-loaded; readable via tool use if asked |
| `SMOKE_RULE_ALWAYS_ON` | `.cursor/rules/always-on.mdc` | Cursor-only | Not auto-loaded; readable via tool use if asked |
| `SMOKE_CURSOR_COMMAND` | `.cursor/commands/test-skill.md` | Cursor slash command | Not executable in Claude Code |

---

## 2. TL;DR — Claude Code vs Cursor concept map

| Concept | Claude Code | Cursor |
|---|---|---|
| Always-on rules (user-level) | `~/.claude/CLAUDE.md` — loaded at startup, applies across all projects | No equivalent |
| Always-on rules (project) | `CLAUDE.md` at repo root — loaded at startup | `.cursor/rules/*.mdc` (`alwaysApply: true`), `.cursorrules`, and `CLAUDE.md` (all loaded at startup) |
| File-scoped rules | Subdirectory `CLAUDE.md` — lazy, agent decides when to fetch; not triggered automatically by file type or open file | `.cursor/rules/*.mdc` with `globs:` — injected automatically when a matching file is open |
| On-demand rules | No structured catalog; subdirectory `CLAUDE.md` files and any repo file are fetched via `Read` tool when the agent decides they're relevant | `.cursor/rules/*.mdc` with no globs and `alwaysApply: false` — agent sees only the `description:` field, fetches full body when relevant |
| Slash commands / skills | `.claude/commands/*.md` — user-invoked; agent executes with full tool access (bash, file reads, etc.) | `.cursor/commands/*.md` — user-invoked; acts as a prompt prefix |
| Cross-tool visibility | `.cursor/rules/` and `.cursorrules` not auto-loaded but readable via tool use if asked | `CLAUDE.md` loaded as ambient context; `.claude/commands/` readable as context but not executable |

---

## 3. Probe results

### Probe A — CLAUDE.md always-on

> "What does SMOKE_CLAUDE_MD say about this project?"

Answered immediately from `CLAUDE.md` content — project purpose, run/test commands,
conventions, and repo layout. No fetch announcement. Confirmed always-on.

---

### Probe B — Cursor artifacts not auto-loaded

> "What does SMOKE_RULE_ALWAYS_ON say?"
> "What does SMOKE_CURSOR_LEGACY say?"

Not passively aware of either. For both, Claude Code first said it didn't see any reference
in current context, then proactively searched the repo, found the files, and reported their
contents correctly.

Notable: `.cursor/rules/` and `.cursorrules` are not auto-loaded as rules but are not
invisible — the agent reads them via tool use the same way it would read any other repo
file.

---

### Probe C — Slash commands

`/hello` — returned a one-sentence project summary as instructed.

`/diagnose` — ran bash commands to check `$DATA_DIR`, `python3 --version`, and whether the
required subdirectories exist, reporting each result.

Notable: Claude Code slash commands execute with full tool access — `/diagnose` behaved like
a small autonomous script. Cursor's `.cursor/commands/` are closer to prompt prefixes with
no direct tool execution.

---

### Probe D — Subdirectory CLAUDE.md (src/CLAUDE.md)

#### D1 — without referencing src/

> "What does SMOKE_SRC_CLAUDE_MD say?"

Lazy fetch — Claude Code said "Let me check for a CLAUDE.md in the src/ directory" then
read the file before answering. Not pre-loaded.

#### D2 — while referencing src/ingest.py

> "I am working on src/ingest.py. What does SMOKE_SRC_CLAUDE_MD say?"

Same lazy fetch as D1. Mentioning `src/ingest.py` did not trigger pre-loading.

**Conclusion:** Subdirectory `CLAUDE.md` files are consistently lazy regardless of file
context. Only the root `CLAUDE.md` is always-on. There is no automatic directory scoping —
the agent fetches when it decides the file is relevant, the same as any other repo file.

---

### Probe E — User-level CLAUDE.md (~/.claude/CLAUDE.md)

Add `SMOKE_USER_CLAUDE_MD` to `~/.claude/CLAUDE.md`, open a fresh session, then ask:

> "What does SMOKE_USER_CLAUDE_MD say?"

Answered immediately with no fetch announcement, correctly identifying the file as
`/Users/chris/.claude/CLAUDE.md`. Confirmed always-on, loaded at session start alongside
the root `CLAUDE.md`.
