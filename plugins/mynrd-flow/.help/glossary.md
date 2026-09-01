# Glossary

Plugin-specific terms in plain language.

---

### AC (acceptance criteria)

The numbered list in `PLAN.md` that defines what "done" means for a piece of work - each entry a checkable statement. `/mynrd-plan` writes them; `progress.json` tracks each one through `pending` / `in_progress` / `implemented` / `pass` / `fail`; `/mynrd-dispatch` builds and verifies them one by one. The specialist agents implement exactly the ACs they are handed - no more.

### Blocked

An AC (or the whole build step) that the loop couldn't finish. Two failed fix attempts on the same distinct failure marks the AC blocked; the loop keeps building everything that doesn't depend on it and lists all blockers together at the end.

### Brief

Intake's restatement of a raw request: What / Who-why / Signal / Urgency / Unknowns. A triage note, not a plan - it has no AC and no `## Testing` section, which is exactly why nothing builds from it.

### Dispatch loop (build loop)

What `/mynrd-dispatch` runs: decompose the plan's AC into tasks, hand each task to a specialist agent, run the test tiers, diagnose-fix-re-run on failure, commit each task as it goes green, and report once at the end. Its state lives in `progress.json`.

### Evidence

How an AC gets from `implemented` to `pass`. Three types: `test` (a named passing test case), `live` (a check against the running app, with the exact command recorded), `review` (the change itself - a docs sweep, a config removal - with the file read recorded).

### Findings

`intake.findings[]` - what the session already established about the code before triage, one line each ending in the `path:line` that proves it. Optional, often empty. A finding with no path is an opinion and belongs in the brief's Unknowns.

### Human verification

The last workflow step, and yours. Unlocks only when every AC is `pass`, every enabled test tier is `pass`, and no round ended blocked. Green loop ≠ done - you exercise the change, review the commits, and push. When you're satisfied, `/mynrd-verified` records it: the step goes `done` and the work's status becomes `verified`.

### `implemented` vs `pass`

Code written makes an AC `implemented`; only evidence makes it `pass`. An AC nothing tests is a reported gap, never counted as done.

### Park

An intake route that shelves the work: the folder keeps the brief as `BRIEF.md` with `status: "parked"`. Nothing resumes it automatically - re-run `/mynrd-plan` when ready.

### `PLAN.md`

The plan file in `.work/<slug>/` - approach, file hints, sequencing, the AC list, and a `## Testing` section naming tiers and commands. Written only by `/mynrd-plan`; read (never edited) by the agents; what `/mynrd-dispatch` builds from.

### `progress.json`

The state file in `.work/<slug>/` - the whole workflow's memory: brief, workflow steps, ACs, tasks, test cases, runs. Created by `/mynrd-intake`, filled by `/mynrd-plan`, updated during the build only by `/mynrd-dispatch`. Agents never write it. See [progress.md](progress.md).

### Protected branches

Branches `/mynrd-dispatch` will not commit on: `main`, `master`, `dev`, `develop`, `release/*`, `hotfix/*`. On one of these the loop still builds but commits nothing all run, and says so. Branch off first.

### Route

The pick at the end of intake: plan it, build it (only when a `PLAN.md` already exists), refine it first, park it, or not actionable. Recorded in `progress.json`.

### Run

One round of the dispatch loop, recorded in `runs[]`: agents used, services started, test result, live checks, commits, what was actually wrong.

### Slug

The folder name under `.work/` - lowercased, non-alphanumerics collapsed to single hyphens, max 40 chars, taken from the brief's `What` line.

### Specialist agent

One of the five implementation agents shipped in the plugin: `mynrd-backend-dev` (.NET / backend), `mynrd-front-dev` (Angular / React), `mynrd-node-dev` (Node / TypeScript), `mynrd-python-dev` (Python), `mynrd-designer` (UI/UX). Each implements exactly the ACs it is handed, writes the tests that cover them, and returns a structured report that `/mynrd-dispatch` transcribes into `progress.json`. Agents never run git and never edit `progress.json` or `PLAN.md`.

### Test tiers

The ordered test levels the loop runs: **unit → UI**. Resolved from the plan's `## Testing` section, which names the actual commands. Unit and UI are the only tiers - no e2e; browser suites are part of human verification.

### `workflow[]`

The four-step ladder in `progress.json` - `intake`, `plan`, `build`, `human-verification` - each `pending` / `in_progress` / `done` / `blocked` / `skipped`. How any session tells where the work stands.

### `.work/`

The gitignored folder at the repo root holding one directory per unit of work (`.work/<slug>/`). Machine-local state - never committed, so a fresh clone starts without it.
