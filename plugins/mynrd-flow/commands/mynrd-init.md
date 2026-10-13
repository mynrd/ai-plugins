---
name: mynrd-init
description: Check a project's setup for the mynrd-flow workflow and fix what's missing — `.claude/settings.local.json` permissions so /mynrd-plan and /mynrd-dispatch run without permission prompts, a `CLAUDE.local.md` block holding the default rules for planning and building, and the `.gitignore` entries that keep all of it local. Safe to re-run; it merges, never overwrites.
---

# /mynrd-init

One-time setup per project, re-runnable any time. `/mynrd-dispatch` is built to run the development to completion and report once — but the harness still stops for every shell command and file edit that isn't allowlisted, so an hour-long build turns into an hour of pressing accept. This command writes the allowlist once, plus the standing rules every later session in this project should follow, and tells you what it found.

It writes **three files, all personal and all git-ignored**: `.claude/settings.local.json`, `CLAUDE.local.md`, and `.gitignore` (entries only). Nothing shared with the team changes — never `.claude/settings.json`, never `CLAUDE.md`.

---

## Argument

| `$ARGUMENTS` | Meaning |
| --- | --- |
| empty | Check, show what would change, confirm once, write. |
| `check` | Check and report only. Writes nothing, asks nothing. |

---

## Step 1 — Resolve the project

Resolve the repo root: `git rev-parse --show-toplevel`, falling back to the current working directory when not in a repo. Every path below is relative to that root. State it in one line so a session running in the wrong directory gets caught before anything is written.

Not a git repo → say so and carry on. The settings and rules still apply; only the `.gitignore` step is skipped, and `/mynrd-dispatch` will have nothing to commit to.

---

## Step 2 — Check

Read, don't write. Collect one row per item:

| Item | OK when |
| --- | --- |
| `.claude/settings.local.json` | Exists, parses, `permissions.allow` / `permissions.deny` contain every rule in § Permissions, and `permissions.additionalDirectories` contains the plugin directory (§ Permissions) |
| `CLAUDE.local.md` | Exists and holds a managed block (§ Rules) whose content matches the current one |
| `.gitignore` | Ignores `.work/`, `.claude/settings.local.json`, and `CLAUDE.local.md` (the exact line or a broader glob) |
| Test commands | A unit and/or UI test command was found in the repo (`package.json` scripts, a `*.sln` / test `*.csproj`, `pyproject.toml` / `pytest.ini`, …) — informational, never a failure |

**A `settings.local.json` that doesn't parse is a stop, not a fix.** Report the parse error with the file path and write nothing to it — hand-fixing the file beats losing what's in it. The other items still proceed.

With `check`, print the report (Step 5 format, statuses only) and stop here.

---

## Step 3 — Show the changes and confirm once

List exactly what will be written — the rules to be added to `permissions.allow` and `permissions.deny`, the directory to be added to `permissions.additionalDirectories`, whether the `CLAUDE.local.md` block is being created or replaced, the `.gitignore` lines to append. Then one yes/no.

This is the only question the command asks, and it is not skippable: the allowlist lets every later session in this project run shell commands and edit files without asking, and that is the user's call to make with the list in front of them. Everything already OK is listed as such and not touched.

Nothing to change → say the project is already set up and skip to Step 5.

---

## Step 4 — Write

### Permissions — `.claude/settings.local.json`

Create the file (and `.claude/`) if absent. Otherwise **merge**: add the missing rules to the existing arrays, keep every key and every rule already there, in its existing order. Never remove or rewrite a rule this command didn't add, never touch any key outside `permissions.allow`, `permissions.deny`, and `permissions.additionalDirectories`.

```json
{
  "permissions": {
    "allow": [
      "Bash",
      "PowerShell",
      "Edit",
      "Write",
      "WebFetch"
    ],
    "deny": [
      "Bash(git push)",
      "Bash(git push *)"
    ],
    "additionalDirectories": [
      "<plugin directory, absolute>"
    ]
  }
}
```

- **`allow`** is what the loop and its agents actually use: shell commands (tests, dev servers, `git commit`), file edits, and doc lookups. The specialist agents inherit these rules — and an agent running in the background can't prompt at all, so a missing rule there is a silent failure, not a question.
- **`deny`** holds the one line the workflow never crosses: pushing is the developer's. Deny wins over allow, so the broad `Bash` rule can't push even by accident. To push from a Claude session in this project, the user removes those two lines themselves.
- **`additionalDirectories`** holds the one place outside the project the workflow reads: the plugin's own files (`PROGRESS-SCHEMA.md`, `.help/`). Without it, a machine with `permissions.blockReadsOutsideWorkingDirectories` on prompts every time a command opens its own schema. The plugin root is `${CLAUDE_PLUGIN_ROOT}`; write it as an absolute path (on Windows, with forward slashes or escaped backslashes so the JSON stays valid), and when its last segment is a version number (`…/mynrd-flow/1.4.2`) write the **parent** instead, so the entry survives a plugin update. An entry that already covers the path (the same directory or an ancestor of it) counts as present — add nothing.
- **An existing `deny` or `ask` rule that conflicts with the allowlist** (e.g. `Bash(npm *)` under `ask`) is left exactly as is and named in the report — it will still prompt, and removing it is the user's decision.

### Rules — `CLAUDE.local.md`

The rules live in a managed block between two markers. Create the file with just the block if absent. If the file exists without the markers, append the block after a blank line. If the markers exist, replace everything between them. **Nothing outside the markers is ever read as yours to edit** — that's the user's own content.

```markdown
<!-- mynrd-flow:start -->
## mynrd-flow defaults

Planning
- Any request to plan, scope, or "figure out how to do" something goes through `/mynrd-plan`. The plan is `.work/<date>-<slug>/PLAN.md` with `progress.json` beside it — no ad-hoc plan documents anywhere else.
- Don't ask what shape a plan takes; decide it from the discussion. At most 2 clarifying questions per turn.
- A plan is not a build. Stop after writing it.

Building
- Nothing builds without a plan on disk. Asked to "just build it" with no `PLAN.md`, point at `/mynrd-plan`.
- Building goes through `/mynrd-dispatch`, which delegates to the `mynrd-*` specialist agents and runs to completion without check-ins. Don't stop to ask "shall I continue" — stop only for a real blocker: new scope, a missing credential, a schema decision.
- Never edit a test to make it pass.

Git
- Commit only as `/mynrd-dispatch` does: one commit per green task, files staged by name, never `git add -A`.
- No `Co-Authored-By: Claude` trailer and no "Generated with Claude Code" line — in commit messages or PR descriptions.
- Never push, amend, rebase, reset, branch, or tag. Never `--no-verify`.
- No commits on `main`, `master`, `dev`, `develop`, `release/*`, `hotfix/*`.

Shell
- One plain command per shell call, Bash or PowerShell (`npm test`, `git status`). No heredocs, here-strings, inline scripts, shell variables, or `$(…)`.
- Read files with Read, change them with Edit / Write — never `cat`, `sed`, `Get-Content`, `Set-Content`, or a script. That includes `progress.json` and `PLAN.md`.

Verification
- Green tests are not done. Verification is the user's; never run `/mynrd-verified` on your own initiative.

Tests
- Unit: <command, or "none found">
- UI: <command, or "none found">
<!-- mynrd-flow:end -->
```

Fill the two `Tests` lines from what Step 2 found — the real command as it would be typed at the repo root. On a re-run where the block already carries a command the user changed by hand, **keep theirs**; only fill a line that is empty or `none found`.

### `.gitignore`

Git repos only. Read `.gitignore` at the repo root (create it if absent) and append whichever of these no existing line already covers:

```gitignore
# mynrd-flow local files (not committed)
.work/
.claude/settings.local.json
CLAUDE.local.md
```

If `git ls-files` shows `settings.local.json` or `CLAUDE.local.md` already tracked, say so — ignoring a tracked file does nothing, and untracking it is a git write this command doesn't make.

---

## Step 5 — Report

One table, then stop:

```text
mynrd-flow setup — <repo root>

  .claude/settings.local.json   updated   (+5 allow, +2 deny, +1 dir)
  CLAUDE.local.md               created
  .gitignore                    ok
  Tests                         unit: dotnet test · ui: none found

Permissions are read when a session starts — restart Claude Code before running /mynrd-plan or /mynrd-dispatch.
```

Statuses are `ok` / `created` / `updated` / `skipped` (with the reason) / `needs attention` (with the reason). Add a line for each conflicting `deny`/`ask` rule left in place and each tracked file that should be ignored. Drop the restart line when no setting changed.

---

## What `/mynrd-init` NEVER does

- Writes `.claude/settings.json`, `CLAUDE.md`, or anything in `~/.claude/` — shared and global config stay the user's
- Sets `defaultMode`, `bypassPermissions`, or any key outside `permissions.allow` / `permissions.deny` / `permissions.additionalDirectories`
- Removes or reorders a rule, or edits `CLAUDE.local.md` outside its markers
- Overwrites a settings file it can't parse
- Runs any git write — no commit, no `git rm --cached`
- Creates `.work/`, plans, or starts a build — `/mynrd-plan` is still the first step of actual work

---

## Failure handling

- **`settings.local.json` won't parse:** report the error and the path, leave the file alone, finish the other items, and mark it `needs attention`.
- **Any other file write errors:** show the error verbatim, don't retry automatically. Ask whether to fix and retry or abort.
