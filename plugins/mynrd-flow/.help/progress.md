# The `.work/` folder and `progress.json`

Where the workflow's state lives, what it tracks, and who is allowed to write it.

---

## The folder

One directory per unit of work, relative to the repo root:

```text
.work/<YYYY-MM-DD>-<slug>/
  progress.json     the state file - the whole workflow's memory
  PLAN.md           written by /mynrd-plan - what /mynrd-dispatch builds from
```

- `<slug>` - lowercased plan title, non-alphanumerics collapsed to single hyphens, trimmed, max 40 chars. Set once at creation and never renamed. `/mynrd-dispatch <slug>` and `/mynrd-verified <slug>` find the folder by suffix match.
- **`.gitignore` must cover `.work/`** - the first command to write there adds the entry if it's missing. The folder is machine-local state and never gets committed, so a fresh clone starts without it.

---

## What `progress.json` tracks

The state of the whole workflow, so a later session knows exactly where things stand.

| Field | What it holds |
|---|---|
| `id`, `title`, `slug`, `status` | Identity of the work; `status` runs `planned` → `in_progress` → `green` / `blocked` → `verified` |
| `findings[]` | What the session already knew about the code when planning started, each line ending in a `path:line` |
| `workflow[]` | Three steps - `plan`, `build`, `human-verification` - each `pending` / `in_progress` / `done` / `blocked` / `skipped`, with `startedAt` / `endedAt` stamped at each transition |
| `acceptanceCriteria[]` | Each AC `pending` / `in_progress` / `implemented` / `pass` / `fail`, with its `evidence` type and the files that implement it |
| `tests.unit` / `tests.ui` | Same shape each: `enabled`, the resolved `command`, and a **list of individual test cases**, every case `pass` / `fail` / `skipped` and naming the AC it covers |
| `tasks[]` | The ordered task list the build loop decomposed the AC into, each with the AC it owns, its `state` (`pending` / `in_progress` / `built` / `blocked` / `committed`), `startedAt` / `endedAt`, and the commit SHAs the loop made for it |
| `runs[]` | One entry per loop round, bounded by `startedAt` / `endedAt`: agents used, services started, test result, live checks, commits, what was actually wrong |
| `humanVerification.unlocked` | `false` until it's earned; `verifiedAt` (+ optional `note`) stamped by `/mynrd-verified` when you close the work |

### `findings[]`

What the code actually says when planning starts, one short line each, ending in the `path:line` that proves it. Optional and often empty - `/mynrd-plan` never goes looking to fill it. Two rules: every entry names a file (a finding with no path is an opinion, and belongs in the discussion instead), and nothing goes here that wasn't actually read. `/mynrd-plan` treats the array as input and verifies each one before building an AC on it.

### `implemented` is not `pass`

Code written makes an AC `implemented`; only its evidence makes it `pass`:

- `test` - a named passing test case linked to that AC
- `live` - a check run against the running app, with a `verified` line naming the exact command
- `review` - the change itself (a docs sweep, a config removal), with a `verified` line naming the file read

An AC stuck at `implemented` is a coverage gap and gets reported as one, never counted as done.

---

## Who writes it

| Writer | When |
|---|---|
| `/mynrd-plan` | Creates the file: identity, `findings[]`, `workflow[]`, `acceptanceCriteria[]`, and the test tiers from `PLAN.md`'s `## Testing` section. On re-plan, reconciles the AC list without losing build state |
| `/mynrd-dispatch` | Everything from there - **during the build, only the dispatch command writes this file** |
| `/mynrd-verified` | The last write, on your say-so only: `human-verification: done`, `verifiedAt` + optional note, `status: verified` |

**The specialist agents never touch it.** `mynrd-backend-dev`, `mynrd-front-dev`, `mynrd-node-dev`, `mynrd-python-dev`, and `mynrd-designer` return a structured report of what they implemented and which tests they wrote; `/mynrd-dispatch` transcribes that into `progress.json` itself. The same rule covers `PLAN.md` - agents read it, never edit it.

`/mynrd-dispatch` also **never creates** the file. No `progress.json` beside the plan means the workflow never started - run `/mynrd-plan`.

---

## Reading it

- `workflow[]` answers "where am I" - see [workflow.md](workflow.md) § "Reading where you are".
- `runs[]` answers "what happened last round" - which agents ran, what failed, what was fixed.
- `tasks[]` answers "what got committed for what" - each task lists its commit SHAs.
- A `skipped` step is normal, not an error: `build` is `skipped` when you drove the edits by hand.
