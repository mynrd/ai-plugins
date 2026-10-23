# Glossary

Plugin-specific terms in plain language.

---

### AC (acceptance criteria)

The numbered list in `PLAN.md` that defines what "done" means for a piece of work - each entry a checkable statement. `/mynrd-plan` writes them; `progress.json` tracks each one through `pending` / `in_progress` / `implemented` / `pass` / `fail`; `/mynrd-dispatch` builds and verifies them one by one. The specialist agents implement exactly the ACs they are handed - no more.

### Blocked

An AC (or the whole build step) that the loop couldn't finish. Two failed fix attempts on the same distinct failure marks the AC blocked; the loop keeps building everything that doesn't depend on it and lists all blockers together at the end.

### Dispatch loop (build loop)

What `/mynrd-dispatch` runs: decompose the plan's AC into tasks, hand each task to a specialist agent, run the test tiers, diagnose-fix-re-run on failure, commit each task as it goes green, and report once at the end. Its state lives in `progress.json`.

### Evidence

How an AC gets from `implemented` to `pass`. Three types: `test` (a named passing test case), `live` (a check against the running app, with the exact command recorded), `review` (the change itself - a docs sweep, a config removal - with the file read recorded).

### Findings

`findings[]` in `progress.json` - what the session already established about the code before planning started, one line each ending in the `path:line` that proves it. Optional, often empty. A finding with no path is an opinion and belongs in the discussion.

### Human verification

The last workflow step, and yours. Unlocks only when every AC is `pass`, every enabled test tier is `pass`, and no round ended blocked. Green loop ≠ done - you exercise the change, review the commits, and push. When you're satisfied, `/mynrd-verified` records it: the step goes `done` and the work's status becomes `verified`.

### `implemented` vs `pass`

Code written makes an AC `implemented`; only evidence makes it `pass`. An AC nothing tests is a reported gap, never counted as done.

### `PLAN.md`

The plan file in `.work/<date>-<slug>/` - approach, file hints, sequencing, the AC list, and a `## Testing` section naming tiers and commands. Written only by `/mynrd-plan`; read (never edited) by the agents; what `/mynrd-dispatch` builds from.

### `BUILD.md`

The handoff report `/mynrd-dispatch` prints at exit, saved in `.work/<date>-<slug>/` before it's printed. First run writes `BUILD.md`; each later dispatch of the same folder writes the next `BUILD_02.md`, `BUILD_03.md`, ... - earlier ones are never overwritten. Both exits write it: green opens with `Development is done - try it now.`, blocked with `Blocked - I need a decision before I can finish.`

### `REVISED_NN.md`

One file per change you ask for after a green handoff, in the same conversation - `REVISED_01.md`, `REVISED_02.md`, ... in the work folder. Records the ask in your words, every file changed and why, the tests run, and the commit if you asked for one (otherwise `not committed`). Written only when files actually changed; `progress.json` isn't touched.

### `progress.json`

The state file in `.work/<date>-<slug>/` - the whole workflow's memory: findings, workflow steps, ACs, tasks, test cases, runs. Created by `/mynrd-plan`, updated during the build only by `/mynrd-dispatch`, closed by `/mynrd-verified`. Agents never write it. See [progress.md](progress.md).

### Protected branches

Branches `/mynrd-dispatch` will not commit on: `main`, `master`, `dev`, `develop`, `release/*`, `hotfix/*`. On one of these the loop still builds but commits nothing all run, and says so. Branch off first.

### Run

One round of the dispatch loop, recorded in `runs[]`: agents used, services started, test result, live checks, commits, what was actually wrong.

### Slug

The non-date part of the folder name under `.work/` (`.work/<YYYY-MM-DD>-<slug>/`) - lowercased plan title, non-alphanumerics collapsed to single hyphens, max 40 chars. Set once; `/mynrd-dispatch <slug>` and `/mynrd-verified <slug>` resolve it by suffix match.

### Specialist agent

One of the six agents shipped in the plugin: `mynrd-backend-dev` (.NET / backend), `mynrd-front-dev` (Angular / React), `mynrd-node-dev` (Node / TypeScript), `mynrd-python-dev` (Python), `mynrd-designer` (UI/UX), `mynrd-docs-writer` (plan drafts and docs). Each implements exactly the ACs it is handed, writes the tests that cover them, and returns a structured report that `/mynrd-dispatch` transcribes into `progress.json`. Agents never run git and never edit `progress.json` or `PLAN.md`.

### Test tiers

The ordered test levels the loop runs: **unit → UI**. Resolved from the plan's `## Testing` section, which names the actual commands. Unit and UI are the only tiers - no e2e; browser suites are part of human verification.

### `workflow[]`

The three-step ladder in `progress.json` - `plan`, `build`, `human-verification` - each `pending` / `in_progress` / `done` / `blocked` / `skipped`. How any session tells where the work stands.

### `.work/`

The gitignored folder at the repo root holding one directory per unit of work (`.work/<date>-<slug>/`). Machine-local state - never committed, so a fresh clone starts without it.
