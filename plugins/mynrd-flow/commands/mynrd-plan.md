---
name: mynrd-plan
description: Discuss a request — a pasted chat blob, a bug report, your own observation — and produce a local plan: PLAN.md and progress.json in a `.work/` folder. The entry point of the workflow. No tracker, no approval gate; everything stays on this machine.
---

# /mynrd-plan

The front door and the planning step in one. Takes whatever came in — a pasted chat, a bug report, a "hey can we…", something you noticed — checks `.work/` for a folder that already covers it, discusses it until the gaps are closed, then writes a plan into a `.work/` folder. Nothing is sent anywhere, so there is no approval gate.

It is the **only** command that writes `PLAN.md` and the only command that creates `progress.json`. `/mynrd-dispatch` builds from those two files and refuses to run without them, so every piece of work starts here.

---

## Argument

| `$ARGUMENTS` | Meaning |
| --- | --- |
| empty | New plan — Step 1 opens the discussion |
| free text | New plan — the text is the raw request; use it as the opening message and skip the intro |
| a path to a `.work/` folder | **Re-plan** — load the existing `PLAN.md` and revise it in place |

Never plan from a filename or a folder name alone. If the request references a file the user has on disk, ask for the path and read it.

---

## Step 0 — Project identity check

Resolve the repo root this plan belongs to: `git rev-parse --show-toplevel`, falling back to the current working directory when not in a repo. That root is where the `.work/` folder lives. State it in one line so a session running in the wrong directory gets caught before anything is written.

---

## Step 0.5 — Existing-work check

Skip this step on a re-plan (the folder was given). Otherwise, before opening a discussion, look in `.work/` for a folder that already covers the request.

Pull the 3-6 most distinctive nouns/verbs from the request (feature names, error strings, screen names — not "fix", "issue", "user") and match them against the folder names under `.work/` and each folder's `progress.json` `title`. Match on different term combinations rather than one long clause. Don't read `PLAN.md` contents to match — titles are enough.

- **Nothing found** — say `no .work/ folder mentions <terms>` in one line and continue. Don't pad with unrelated folders.
- **Something plausible found** — show up to 5 as `<folder> · <status> · <title>`, one line each on why it might be the same thing, and ask once whether to re-plan that folder or start new. Re-plan → treat the rest of this run as if that folder were the argument.

**Findings.** If this session already knows something about the code — a debugging thread, a stack trace the user pasted, a file you read before this command ran — keep it. One line each, ending in the `path:line` that proves it:

```text
Findings:
  BackgroundJobControlRegistry.ReportFailureAsync returns early when StopOnError is false — src/server/.../BackgroundJobControlRegistry.cs:88
  background-job-list.component.ts:164 uses modal--sm (400px); modal--md already exists in src/styles.scss
```

Don't go looking to fill this in — it exists to keep what the session already established, so the plan doesn't re-derive it. Nothing known yet means no block, which is the normal case. Anything you can't point at a file for is an open question for Step 2, not a finding. Findings go to `findings[]` in Step 4, and every one is verified once before an AC is built on it — a finding is what a past turn read, not a guarantee the code still says it.

---

## Step 1 — Usage guide

Print this short intro the first time (skip it when `$ARGUMENTS` already carries the request):

> **`/mynrd-plan`.** Tell me what needs planning. Could be:
> - A request passed via chat
> - A bug you hit
> - Your own observation while working
>
> I'll ask a few questions to surface gaps, then write the plan. Everything stays local — `PLAN.md` and `progress.json` in a `.work/` folder.

Wait for the user's opening message.

**Re-planning?** (a `.work/` folder path was the argument, or Step 0.5 picked one) — read the existing `PLAN.md` and `progress.json` first and open the discussion on what's changing. `PLAN.md` is rewritten in place — no `PLAN-v2.md`.

---

## Step 2 — Discussion

Read the request. Restate it in one or two sentences so the user sees what you understood before either of you invests in discussion. Quote, don't paraphrase, any urgency signal ("'need this before Friday's demo'" is evidence; "high priority" is your interpretation).

Then ask **at most 2 clarifying questions per turn**. Aim to surface:

- **What's being asked for** in plain language
- **Who needs it / why it matters** (the driver)
- **Scope and out-of-scope** boundaries
- **Acceptance criteria** — how done is judged
- **Bug specifics** (if it's a defect): repro steps, actual vs expected, impact

Skip anything the request or the findings already answer. If the request is a question rather than a piece of work, say so and answer it — don't manufacture a plan. If it's real but not for now, say so and stop; not planning something is how it gets parked.

Don't over-interview. If the user signals "draft it" / "let's write it" / "go ahead," stop asking and move to Step 3.

---

## Step 3 — Draft the content

**The shape follows from the discussion; don't ask for it.** A defect (something that used to work or was expected to work and doesn't) gets the Bug format. Everything else — new capability, change to existing behavior, an implementation step — gets the Description format. Say which you're using in one line and move on.

### Description (non-bug work)

```markdown
## Context
[Why this work exists — problem, user need, driver. 1-3 sentences.]

## What needs to happen
[Plain-language description.]

## Out of scope
[Explicit exclusions, or "None"]

## Dependencies
[Other work, systems, or "None"]
```

### Repro Steps (bug)

```markdown
## Steps to Reproduce
1. [step]

## Actual Result
[what's happening]

## Expected Result
[what should happen — also serves as fix-definition]

## Impact
[who/severity/workaround]

## Environment
[browser / config / production-only / etc.]
```

### Acceptance Criteria (both)

```markdown
1. [Specific, independently testable condition]
2. [Next condition]
```

For a bug, AC is typically the inverse of Expected Result. Keep the numbered list even if it has one entry — `/mynrd-dispatch` and every test case reference these ids.

---

## Step 4 — Write

No preview, **no gate, no approval prompt of any kind** — neither `AskUserQuestion` nor a typed `Approve …` reply. There is nothing external to approve, and gating a local file write teaches nothing. Show what you wrote after the fact.

1. **`.gitignore`** must cover `.work/` before either write — see the gitignore rule below.
2. **`PLAN.md`** per [The `.work` plan folder](#the-work-plan-folder), in `.work/<YYYY-MM-DD>-<slug>/`.
3. **`progress.json`** in the same folder. Schema, folder naming, and status vocabularies are defined once in `${CLAUDE_PLUGIN_ROOT}/PROGRESS-SCHEMA.md` — read that exact path with the Read tool, don't restate it. Never search for it (`find`, `ls ~/.claude`, a glob): the path is already resolved, and a search outside the project triggers a permission prompt.

### New plan

Create the file. `id` is the folder name, `slug` its non-date part, `title` the plan's title, `plan` = `"PLAN.md"`, `status = "planned"`. `findings[]` from Step 0.5 (empty array when there were none). `workflow[]` is three steps: `plan` = `done` with `startedAt` (when the discussion opened) and `endedAt` (now); `build` and `human-verification` = `pending`.

- `acceptanceCriteria[]` — one entry per AC in the drafted list, `{ "id": <n>, "text": "<AC text>", "status": "pending", "implementedIn": [] }`. Numbering matches the drafted AC list exactly. Add `"evidence": "live"` or `"review"` where an AC plainly can't have a unit test (a docs change, a config removal); default `test` needs no field.
- `tests.unit` / `.ui` — `enabled` and `command` from the plan's `## Testing` section. A tier the plan says `no` to gets `enabled: false` and a `reason`. Never leave `enabled: null` here; that's the marker for "nobody resolved this yet".

### Re-plan

Rewrite `PLAN.md` in place, then reconcile `progress.json` without losing build state:

- **AC are matched by text.** An existing AC whose text is unchanged (or trivially reworded — same condition) keeps its `status`, `implementedIn`, `evidence`, `verified`, and `task`. A new AC is `pending`. A removed AC is dropped, and every `tests.*.cases[].ac` entry that pointed at it is dropped too — say which, out loud. Then renumber `id` to match the new list and rewrite the `ac` references on cases and `tasks[]` to follow.
- **Never touch** `tasks[].state`, `tasks[].commits[]`, task stamps, `runs[]`, `branch`, or the `human-verification` step. Those record what happened.
- **If `workflow[build]` was `done` and the AC list changed** — added, removed, or reworded so a `pass` no longer holds — set `build` back to `pending` (drop its old stamps; a fresh run will stamp it), `humanVerification.unlocked = false`, `status = "planned"`, and say so. A green build against an old plan is not a green build against this one.
- `workflow[plan]` gets a fresh `endedAt`; `slug`, `id`, `created` never change.

### Report

Report the paths and stop:

```text
Planned locally.
  Plan:     .work/2026-08-14-invoice-export-fails/PLAN.md
  Progress: .work/2026-08-14-invoice-export-fails/progress.json
  AC:       3 criteria, all pending
  Tests:    unit yes (pytest tests/pdf) · ui no

Next: cut a branch if you want one, then /mynrd-dispatch .work/2026-08-14-invoice-export-fails
```

Stop here. **Don't continue into the build**, not with `/mynrd-dispatch`, not with a subagent, not by editing files yourself — dispatch edits source, runs tests, starts local processes, and commits, which shouldn't arrive as the tail of a planning turn. The user runs it.

---

## The `.work` plan folder

The plan lives on disk; the local copy is what `/mynrd-dispatch` reads.

**Layout** — relative to the repo root resolved in Step 0:

```text
.work/<YYYY-MM-DD>-<slug>/PLAN.md
```

- `<slug>` — lowercased title, non-alphanumerics collapsed to single hyphens, trimmed, max 40 chars. Same rule used for branch names, so `.work/2026-08-14-pdf-export-pagebufferoverflow/` pairs with `bugfix/pdf-export-pagebufferoverflow`. Set once at creation; a re-plan that changes the title does **not** rename the folder or the `slug` field.
- One directory per unit of work. Re-planning rewrites `PLAN.md` in place; it does not create a second directory or a `PLAN-v2.md`.
- `progress.json` lives beside `PLAN.md` in the same directory — see `${CLAUDE_PLUGIN_ROOT}/PROGRESS-SCHEMA.md`.
- The directory is a container for this item's local working files, so anything else you drop in there is yours to manage. Only `PLAN.md` and `progress.json` are written and read by these commands.

**Gitignore, every time.** Before writing the file, make sure the repo ignores the folder:

1. Read `.gitignore` at the repo root (create it if absent).
2. If no line already ignores `.work` (`.work/`, `.work`, or a broader glob), append:

   ```gitignore
   # Local plan files from /mynrd-plan (not committed)
   .work/
   ```

3. Say in one line that you added it. Never commit the change unless asked.

**Content of `PLAN.md`** — everything the planning discussion produced, in one markdown file:

```markdown
# <title>

## Context
## What needs to happen
## Out of scope
## Dependencies
## Acceptance Criteria
## Implementation notes
[approach, files likely touched, sequencing, risks — everything from the
discussion that didn't fit the sections above. This is the section that makes
the file worth reading at build time.]

## Testing
- Unit: <yes|no> — <framework / project, e.g. dotnet test src/Api.Tests>
- UI: <yes|no> — <framework, e.g. ng test>
```

Skip sections that don't apply (a bug uses Steps to Reproduce / Actual / Expected / Impact / Environment instead of "What needs to happen"). Never leave `Implementation notes` empty — if the discussion produced none, write what you'd tell the next dev about where to start.

**The `Testing` section is what `/mynrd-dispatch` reads to decide which test tiers its build loop runs.** Fill it from the discussion and what the repo actually has — don't ask a question for it. Defaults: Unit `yes` for backend work, UI `yes` for frontend work. **Those two tiers are all there is** — don't add an `E2E:` row or name a browser suite here; `/mynrd-dispatch` runs neither.

---

## What this command does not do

- **No writes outside `.work/` and `.gitignore`.** No source files, no tracker, no network.
- **No git operations.** Branching is yours to do by hand — `<type>/<slug>` when you want one.
- **No build.** No source edits, no subagent dispatch, no tests — even when the user says "just build it". Point at `/mynrd-dispatch` once the plan is written.

---

## Failure handling

- **A `.work/` folder won't scan** (unreadable, or its `progress.json` doesn't parse): show the error, skip that folder, and say the existing-work check ran partial. Don't repair or overwrite the broken file from here.
- **Re-plan lands on a `progress.json` that won't parse:** don't overwrite it — report the corruption, name the file, and stop. Hand-fixing the file beats losing its build state.
- **Any other tool call or file write errors:** show the error verbatim, don't retry automatically. Ask the user whether to fix and retry or abort.
