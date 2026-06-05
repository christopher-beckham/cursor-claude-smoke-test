# cursor-smoke-test

A minimal repo for testing what Cursor's agent picks up from various rule and context artifacts.

**Test environment:** Cursor Composer 2.5

**Use case:** A Python CSV ingestion pipeline with shell scripts for orchestration. Rules are
grounded in real conventions for that kind of project.

Directory structure is as follows:

```
.
├── .claude
│   ├── commands
│   │   ├── diagnose.md
│   │   └── hello.md
│   └── settings.json
├── .cursor
│   ├── commands
│   │   └── test-skill.md
│   └── rules
│       ├── agent-requested.mdc
│       ├── always-on.mdc
│       ├── py-scoped.mdc
│       └── sh-scoped.mdc
├── .cursorrules
├── CLAUDE.md
├── README.md
├── README_CLAUDE_CODE.md
└── src
    ├── CLAUDE.md
    ├── ingest.py
    └── run.sh
```

---

## 1. Sentinel index

Each artifact in this repo has a unique sentinel string. Ask the agent "what rules are you
following?" and grep the response for which sentinels appear.

| Sentinel | File | Mechanism | Purpose |
|---|---|---|---|
| `SMOKE_CURSOR_LEGACY` | `.cursorrules` | Cursor legacy rules file | Always-on; older projects use this flat file instead of `.cursor/rules/` |
| `SMOKE_RULE_ALWAYS_ON` | `.cursor/rules/always-on.mdc` | `alwaysApply: true` | Always-on; the modern equivalent of `.cursorrules` |
| `SMOKE_RULE_SH_SCOPED` | `.cursor/rules/sh-scoped.mdc` | `globs: **/*.sh` | Injected only when a `.sh` file is open or referenced |
| `SMOKE_RULE_PY_SCOPED` | `.cursor/rules/py-scoped.mdc` | `globs: **/*.py` | Injected only when a `.py` file is open or referenced |
| `SMOKE_RULE_AGENT_REQUESTED` | `.cursor/rules/agent-requested.mdc` | agent fetches on demand | Agent sees only the `description:` field; fetches the body when it judges the topic relevant |
| `SMOKE_CLAUDE_MD` | `CLAUDE.md` | Claude Code native; also ambient in Cursor | Project instructions for Claude Code; Cursor reads it as ambient context too |
| `SMOKE_CLAUDE_COMMAND_HELLO` | `.claude/commands/hello.md` | Claude Code slash command | Invokable as `/hello` in Claude Code; readable as context by Cursor but not executable |
| `SMOKE_CLAUDE_COMMAND_DIAGNOSE` | `.claude/commands/diagnose.md` | Claude Code slash command | Invokable as `/diagnose` in Claude Code; readable as context by Cursor but not executable |
| `SMOKE_CURSOR_COMMAND` | `.cursor/commands/test-skill.md` | Cursor slash command | Invokable as `/test-skill` in Cursor; confirmed working |

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

**On-demand rules explained:** Cursor's agent doesn't have open-ended tool access to read
arbitrary files mid-conversation the way Claude Code does. On-demand rules are a structured
workaround: the agent always sees each rule's `description:` field (a one-line summary), and
fetches the full body only when it decides the description matches what the user is asking about.
The `description:` field is the retrieval key. Claude Code doesn't need this pattern because it
can call `Read` on any file directly.

---

## 3. Probe results (Composer 2.5)

### Probe 1 — Always-on rules (no file open)

Ask:
> "What rules or coding conventions are you following right now?"

**Expect:** `SMOKE_RULE_ALWAYS_ON` and possibly `SMOKE_CURSOR_LEGACY`. No scoped or on-demand sentinels.

**Actual:**
> I'm operating under several layers of rules and conventions. Here's what applies in this workspace:
>
> Workspace / project conventions — from `.cursorrules`, `.cursor/rules/always-on.mdc`, and `CLAUDE.md`:

Notable: Cursor read `CLAUDE.md` as ambient context without being prompted — treating it as a
first-class rule source alongside `.cursorrules` and `always-on.mdc`.

---

### Probe 2 — Glob-scoped rules (open src/run.sh)

Open `src/run.sh`, then ask:
> "What rules are you following for this file?"

**Expect:** Same always-on trio plus `SMOKE_RULE_SH_SCOPED`. No `SMOKE_RULE_PY_SCOPED`.

**Actual:**
Same always-on trio plus `sh-scoped.mdc` (`SMOKE_RULE_SH_SCOPED`). `SMOKE_RULE_PY_SCOPED` absent. Correct.

Notable: Cursor cited the shell-specific section of `CLAUDE.md` as a distinct rule layer. It also
cross-referenced the `sh-scoped` rules against the actual file, producing a compliance table
mapping each rule to specific line numbers in `run.sh`.

---

### Probe 3 — Glob-scoped rules (open src/ingest.py)

Open `src/ingest.py`, then ask:
> "What rules are you following for this file?"

**Expect:** Same always-on trio plus `SMOKE_RULE_PY_SCOPED`. `SMOKE_RULE_SH_SCOPED` drops out.

**Actual:**
Same always-on trio plus `py-scoped.mdc` (`SMOKE_RULE_PY_SCOPED`). `sh-scoped.mdc` absent. Correct.

Notable: Cursor proactively named the rules that do NOT apply and why — it explicitly stated
`sh-scoped.mdc` is shell-only and `agent-requested.mdc` is demand-fetched, without being asked.
Again produced a compliance table mapping each py-scoped rule to specific lines in `ingest.py`.

---

### Probe 4 — On-demand rule

Without any file open, ask:
> "How do I deploy this pipeline to production?"

**Expect:** Agent fetches and cites `SMOKE_RULE_AGENT_REQUESTED`.

**Actual:**
Cursor announced the fetch explicitly ("I'll pull the deployment runbook and project docs") before
answering, then cited `SMOKE_RULE_AGENT_REQUESTED` by name. Correct.

Notable: the on-demand fetch is visible to the user — Cursor announces its intent to retrieve
before using it. Always-on and glob-scoped rules are injected silently.

---

### Probe 5 — CLAUDE.md visibility

Ask:
> "What does SMOKE_CLAUDE_MD say about this project?"

**Expect:** Confirms whether Cursor reads `CLAUDE.md` at all.

**Actual:**
Cursor announced "Checking CLAUDE.md (SMOKE_CLAUDE_MD)" and answered correctly. Same
explicit-fetch announcement pattern as probe 4 — raising the question of whether `CLAUDE.md`
is ambient or on-demand.

#### Probe 5a — CLAUDE.md ambient vs. on-demand (follow-up)

Ask, without mentioning CLAUDE.md:
> "What command do I run to execute the test suite?"

The answer (`python3 -m pytest tests/ -v`) exists only in `CLAUDE.md`.

**Actual:**
Cursor answered correctly with no fetch announcement.

**Conclusion:** `CLAUDE.md` is ambient — always injected, equivalent to `alwaysApply: true`.
The announcement in probe 5 was Cursor narrating its source when directly questioned, not a
real fetch. Fetch announcements reliably indicate on-demand rules only.

---

### Probe 6 — Are .claude/commands/ files visible to Cursor?

Ask:
> "What slash commands are available in this project?"

**Expect:** Cursor reports no Cursor commands. Ideally ignores `.claude/commands/`.

**Actual:**
Cursor correctly reported no Cursor slash commands and explained that its own convention is
`.cursor/commands/*.md`. It then volunteered the contents of `.claude/commands/` as project
context.

Notable: `.claude/commands/` is not invisible to Cursor — it reads the files as context but
correctly does not treat them as executable Cursor commands. The agent's claim about
`.cursor/commands/` turned out to be accurate (confirmed in probe 7).

---

### Probe 7 — Does Cursor have slash commands? (.cursor/commands/)

Probe 6 raised the question of whether `.cursor/commands/` is a real Cursor feature or a
hallucination. A file was added at `.cursor/commands/test-skill.md` with sentinel
`SMOKE_CURSOR_COMMAND`.

Type `/test-skill` in the Cursor chat input.

**Actual:**
`/test-skill` appeared as an autocomplete option and executed, replying "SMOKE_CURSOR_COMMAND executed."

**Conclusion:** `.cursor/commands/` is a real, working Cursor slash command system. The
conventions are directly parallel: `.claude/commands/*.md` for Claude Code,
`.cursor/commands/*.md` for Cursor.
