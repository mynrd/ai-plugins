---
name: mynrd-intake
description: Triage a raw incoming request — a pasted chat blob, a bug report, your own observation — into a short brief, check `.work/` for an existing folder already covering it, open the local progress.json that tracks the work from here on, and route to the right next command. Local only — writes nothing outside `.work/`.
---

# /mynrd-intake

The front door. Takes whatever just landed — a pasted chat, a support message, a "hey can we…", something you noticed — and answers three questions:

1. **What is this, actually?** A short brief in plain language.
2. **Is it already on disk?** A scan of `.work/` for a folder — a brief, a `PLAN.md`, a `progress.json` — that already covers it.
3. **What's the next command?** `/mynrd-plan`, `/mynrd-refine`, `/mynrd-dispatch`, or nothing at all.

Then it **creates `progress.json`** — the local file every later stage reads and updates. This command is where the workflow starts, so this command is where that file is born.

**Local only.** It writes nothing outside `.work/`: no tracker, no network calls, no source files. No approval gate, because there's nothing to approve — the only writes are `progress.json` (Step 4) and, on the park route, `BRIEF.md`.

Most intake ends by handing off to `/mynrd-plan`. That's the intended outcome, not a failure to do something here.

**Running this command puts the work on rails.** Once intake has happened, the sequence below is enforced for the rest of the session — nothing builds until a plan exists. See [Intake enforces the sequence](#intake-enforces-the-sequence).

---

## Argument

`$ARGUMENTS` is the raw request, pasted inline. Optional.

- **Text given** — use it as the raw input.
- **Empty** — use what's already in this session (the conversation you've been having). If the session has nothing to triage either, ask once: `What came in? Paste it, or describe what you noticed.`

Never triage from a filename or a folder name. If the request references a file the user has on disk, ask for the path and read it.

---

## Step 1 — Write the brief

Read the raw input and restate it. Do **not** ask questions yet — the whole value of this step is showing the user what you understood before either of you invests in discussion.

```text
Intake brief
  What:      <one sentence, plain language — no jargon from the source text>
  Who/why:   <who's affected and what it costs them; "unclear" is an honest answer>
  Signal:    <Bug | new capability | change to existing behavior | question | not actionable>
  Urgency:   <this week | soon | unclear — quote the words that told you>
  Project:   <slug, resolved the same way /mynrd-plan resolves it: named in the text → git remote → folder>
  Unknowns:  <the 1-3 things that must be answered before this can be planned>
```

Rules for the brief:

- **Quote, don't paraphrase, the urgency signal.** "'need this before Friday's demo'" is evidence; "high priority" is your interpretation.
- **`Unknowns` is the most useful row.** It's what `/mynrd-plan` will spend its questions on. If you list none, you're claiming the request is complete — be sure.
- **`Signal: question`** means someone wants an answer, not a piece of work. Say so; don't manufacture one.
- Keep the whole brief under ~10 lines. This is triage, not analysis.

**If this session already knows something about the code, add a `Findings` block under the brief** — one line each, ending in the `path:line` that proves it:

```text
  Findings:  BackgroundJobControlRegistry.ReportFailureAsync returns early when StopOnError
             is false, so failures on non-stopping jobs are never persisted — src/server/.../BackgroundJobControlRegistry.cs:88
             background-job-list.component.ts:164 uses modal--sm (400px); modal--md already exists in src/styles.scss
```

**Don't go looking.** No greps, no file reads, no investigation to fill this in — the block exists to keep what a debugging thread or the user's own paste already established, so `/mynrd-plan` doesn't re-derive it. Nothing known yet means no block, which is the normal case. Anything you can't point at a file for is an unknown, not a finding, and belongs in the `Unknowns` row. It goes to `intake.findings[]` in Step 4.

---

## Step 2 — Duplicate & plan check

Search `.work/` before anything new gets started. This is two checks in one pass: **does an existing work folder already cover the request**, and **does that folder already hold a `PLAN.md`**? `/mynrd-dispatch` builds from `PLAN.md` — not from the brief — so whether that file exists is what decides every route below.

Pull the 3-6 most distinctive nouns/verbs from the brief (feature names, error strings, screen names — not "fix", "issue", "user") and match them against:

- the folder names under `.work/` (in the repo root resolved per [Folder](#folder) below),
- each folder's `progress.json` — the `title` and `intake.brief.what` lines — and `BRIEF.md` where there's no `progress.json`.

Rules for the scan:

- Match on **different term combinations** rather than one long clause — everything ANDed finds nothing, everything ORed finds noise.
- Don't read `PLAN.md` contents to match — titles and briefs are enough for triage.
- Cap what you show at the 5 most plausible matches. More than that means the terms were too generic — narrow and re-scan.

Show candidates as: `<folder> · <status> · <title>`.

For each, say in one line **why it might be the same thing** and whether you think it actually is. A list of folder names the user has to open one by one has done none of the work.

**Nothing found** is a real result — say "no `.work/` folder mentions <terms>" and move on. Don't pad the list with unrelated folders.

Then resolve the candidate work folder, first match wins:

1. `$ARGUMENTS` is a path to a `.md` file → that file is the plan; its folder is the work folder.
2. `$ARGUMENTS` is a path to a `.work/` folder → that folder.
3. A scan candidate the user has pointed at → that folder.
4. The brief's `What` slug → `.work/*-<slug>/`, exact match then prefix.

Report the result in one line and nothing more:

- `Plan found: .work/2026-08-10-pdf-export/PLAN.md.` — planning can be skipped; `/mynrd-plan` becomes optional.
- `No local plan for this.` — planning is mandatory before any build.

Don't read the plan's contents here and don't write one — that's `/mynrd-plan`'s job.

---

## Step 3 — Recommend a route

**This is not an approval gate.** It carries no `Approve …` label and authorizes no write. It picks a direction.

**Call `AskUserQuestion`.** If it is in your tool list, this is how you ask — the plain-text alternative below is unreachable. Call it: `question` `"What should happen with this?"`, `multiSelect: false`, your recommendation first with `(Recommended)` and a one-line reason.

**Only when `AskUserQuestion` is missing from your tool list entirely** (Cursor Agent Mode) — present the routes as a numbered list in plain text and wait for the reply; mark your recommendation `(recommended)` with the same one-line reason. Accept the number, the route name, or the `route` value.

**Which routes exist depends on Step 2.** The two sets don't mix — offer one or the other, never a blend.

### A plan was found

Planning is already done, so `/mynrd-plan` is optional here and the work can go straight to the build loop:

| Route | `route` value | When it fits | Hands off to |
| --- | --- | --- | --- |
| `Build it` | `build` | The plan covers what just came in | `/mynrd-dispatch` |
| `Refine the plan` | `refine-plan` | The plan exists but is stale, thin, or doesn't cover this request | `/mynrd-plan <folder>` |
| `Park it` | `park` | Real, but not now | Step 4 + Step 5 |
| `Not actionable` | `not-actionable` | A question, a duplicate of finished work, or already handled | nothing |

### No plan was found

**Every build goes through `/mynrd-plan`**, because it is the only command that writes `PLAN.md`, and `/mynrd-dispatch` will not build without one:

| Route | `route` value | When it fits | Hands off to |
| --- | --- | --- | --- |
| `Plan it` | `plan` | Actionable and clear enough to discuss | `/mynrd-plan` |
| `Refine it first` | `refine` | Actionable but too raw or tangled to plan — needs shaping into a structured draft | `/mynrd-refine`, then `/mynrd-plan` |
| `Park it` | `park` | Real, but not now | Step 4 + Step 5 |
| `Not actionable` | `not-actionable` | A question, a duplicate of finished work, or already handled | nothing |

**`Refine it first` is not a planning route.** It produces a formatted draft (Description/AC or Repro Steps/AC) from the conversation, and nothing more — the work still has no plan until `/mynrd-plan` runs on that draft. Say that in the option's description so the choice isn't read as "skip planning".

**Prune to the routes the findings support — at most 4.** (`AskUserQuestion` caps at 4 options; keep the same ceiling on the text path so both hosts read the same.) If the brief is already crisp — a clean bug report with repro steps — `Refine it first` doesn't belong on the list.

---

## Step 4 — Create `progress.json`

Every route except `not-actionable` writes this file. It is the state every later stage reads, updates, and resumes from — see [The `progress.json` file](#the-progressjson-file) below for the full schema and the folder rules.

Write it now, after the route is known (the route is a field in it), and before handing off.

| Route | Folder | `status` |
| --- | --- | --- |
| `plan` · `refine` | `.work/<YYYY-MM-DD>-<slug>/` | `intake` |
| `build` · `refine-plan` | the folder Step 2 resolved — the file is already there | leave it as it is |
| `park` | `.work/<YYYY-MM-DD>-<slug>/` | `parked` |
| `not-actionable` | nothing written | — |

On the `build` and `refine-plan` routes, a `progress.json` may already exist there from an earlier session. **Don't overwrite it** — report that you found it, leave `intake` and everything downstream of it alone, and hand off. Re-triaging a piece of work is not a reason to discard its build state.

A folder with a `PLAN.md` but no `progress.json` is possible (the plan was written on a machine that had an older plugin). Create the file there with `intake` filled in from this run, `workflow[intake] = done`, and `workflow[plan] = done` — the plan file is the evidence. Stamp both steps' `startedAt`/`endedAt` with now; the real planning time is unknowable and a missing stamp on a `done` step is worse.

Say the path in one line when you're done. Nothing else reads a parked folder automatically; it's there for you to find.

---

## Step 5 — Hand off

**`Plan it`** — continue inline with `/mynrd-plan`, using the brief as the opening discussion input. Don't make the user retype the request. Skip the questions the brief already answers and open on the `Unknowns` row.

**`Refine it first`** — continue inline with `/mynrd-refine`, using the conversation and the brief as its source. When the draft is done, `/mynrd-plan` turns it into a plan — say so in one line.

**`Build it`** — stop here and tell the user to run `/mynrd-dispatch <folder>`. Don't inline it: dispatch edits source files, runs tests, starts local processes, and commits, which is not something that should arrive as the tail of a triage. If no branch has been cut yet and the user wants one, say so in the same line — cut `<type>/<slug>` by hand first, then `/mynrd-dispatch`.

**`Refine the plan`** — continue inline with `/mynrd-plan` in re-plan mode for the work folder, opening with what the brief says the current plan is missing.

**`Park it`** — Step 4 already wrote the folder with `status: "parked"`. Also write the brief beside it as `BRIEF.md` so the folder is readable without parsing JSON, then stop. Nothing picks a parked item back up automatically — the user re-runs `/mynrd-plan` when they're ready.

**`Not actionable`** — say why in one line and end, having written nothing. If it's a question you can answer, answer it.

---

## Intake enforces the sequence

**Running `/mynrd-intake` opts this work into the workflow, and the rest of this session honors it.** The order is fixed:

```text
intake  →  plan  →  build  →  human verification
```

- **`plan` is not skippable — a `PLAN.md` is.** If Step 2 found one, planning is already done and `/mynrd-plan` is optional (`refine-plan` re-opens it). If it found none, `/mynrd-plan` runs before anything builds. There is no third way to produce that file.
- **Branching is not a stage.** Cut `<type>/<slug>` by hand whenever you want it; nothing in this plugin runs git branch operations for you.
- **`build` is `/mynrd-dispatch`,** and it builds from `PLAN.md` and `acceptanceCriteria[]`. Nothing else in this plugin builds.

### When the user asks to start development anyway

If, after this command, the user says *"start the development"*, *"just build it"*, *"go ahead and code it"* — or anything else that means build — check `progress.json` before doing anything:

**`workflow[plan]` is `done` and `acceptanceCriteria[]` is non-empty** → fine. Point at `/mynrd-dispatch` (see the `Build it` handoff above).

**Otherwise → don't build.** Not with `/mynrd-dispatch`, not with a subagent, and not by editing files yourself in this turn. Say exactly this and stop:

> There's no plan for this yet, so there's nothing to build from — `/mynrd-dispatch` reads `PLAN.md` and the acceptance criteria, and neither exists. Run `/mynrd-plan` and I'll take it from there.

Then run `/mynrd-plan` if the user says go. **This is not a judgment call and there is no "just this once".** The brief this command produced is a triage note: it has no acceptance criteria, no implementation notes, and no `## Testing` section, so a build started from it has no definition of done and no way to record one. Writing code straight off a brief is the specific failure this rule exists to stop.

**This applies to intake's own session only.** `/mynrd-plan` is entry-point-free — anyone can run it cold, with no intake, whenever they want to plan a piece of work. Nothing here restricts that.

---

## The `progress.json` file

**This is the canonical schema.** `/mynrd-plan` and `/mynrd-dispatch` both read and update this file; neither of them defines it. When they disagree with this section, this section wins.

### Folder

Relative to the repo root (`git rev-parse --show-toplevel`; fall back to the current working directory when not in a repo). Same folder that holds `PLAN.md` — one directory per unit of work:

```text
.work/<YYYY-MM-DD>-<slug>/progress.json
```

- `<slug>` — lowercased, non-alphanumerics collapsed to single hyphens, trimmed, max 40 chars. From the brief's `What` line here; from the plan's title once one exists.
- **The dated folder name is permanent** — it is the work's local `id`, and everything downstream refers to it. Don't rename it once anything has been written into it.
- **`.gitignore` must cover `.work/` before the first write** — same rule and same procedure as the plan folder, see `commands/mynrd-plan.md` § "The `.work` plan folder".

### Schema

```json
{
  "schemaVersion": 3,
  "id": "2026-08-14-pdf-export-dies-on-invoices",
  "title": "PDF export dies on invoices past 10 pages",
  "type": null,
  "slug": "pdf-export-dies-on-invoices",
  "branch": null,
  "plan": null,
  "status": "intake",
  "created": "2026-08-14T09:12:00+08:00",
  "updated": "2026-08-14T09:12:00+08:00",

  "intake": {
    "at": "2026-08-14T09:12:00+08:00",
    "brief": {
      "what": "PDF export fails for invoices longer than 10 pages",
      "whoWhy": "Hit it this morning — can't send invoices",
      "signal": "Bug",
      "urgency": "this week",
      "project": "account-manager",
      "unknowns": ["Which renderer version", "Page count or byte size"]
    },
    "findings": [
      "PdfChunkWriter.Flush() drops the final buffer when pageCount % 10 == 0 — src/server/Pdf/PdfChunkWriter.cs:212"
    ],
    "duplicateCheck": {
      "terms": ["PDF export", "PageBufferOverflow", "invoice pages"],
      "candidates": [
        { "folder": ".work/2026-07-30-pdf-letterhead-margins", "status": "green",
          "title": "PDF margins wrong on letterhead",
          "verdict": "different failure — not a duplicate" }
      ]
    },
    "route": "plan"
  },

  "workflow": [
    { "step": "intake",             "status": "done",
      "startedAt": "2026-08-14T09:10:00+08:00", "endedAt": "2026-08-14T09:12:00+08:00" },
    { "step": "plan",               "status": "pending" },
    { "step": "build",              "status": "pending" },
    { "step": "human-verification", "status": "pending" }
  ],

  "tasks": [],

  "acceptanceCriteria": [],

  "tests": {
    "unit": { "enabled": null, "status": "not_run", "command": null, "cases": [] },
    "ui":   { "enabled": null, "status": "not_run", "command": null, "cases": [] }
  },

  "humanVerification": { "unlocked": false, "unlockedAt": null },

  "runs": []
}
```

**`id`** is the folder name (`<YYYY-MM-DD>-<slug>`) and never changes — it's how `runs[]`, handoffs, and later sessions refer to this work.

`type`, `plan`, and `branch` stay `null` here — intake doesn't know them yet. Don't guess a `type` from the brief's `Signal` row; `/mynrd-plan` sets it when the user picks one (Story / Task / Bug). `tasks` starts empty and stays empty on anything that isn't broken into slices.

**`intake.findings[]`** holds what the code actually says, one short line each, ending in the `path:line` that proves it. It's optional and often empty: intake is triage, not analysis, and nothing here tells you to go read the source. Record it when the session **already** established something before intake ran — a debugging thread, a read-only investigation, the user pasting a stack trace. Two rules: every entry names a file (a finding with no path is an opinion, and belongs in `brief.unknowns` instead), and nothing is written here that wasn't actually read. `/mynrd-plan` treats the array as input, so a wrong line here becomes a wrong AC later.

### `tasks[]` — the slices of a larger piece of work

Work big enough to split is built and committed one slice at a time, so the file has to know which AC belong to which slice. **Optional and usually empty** — a lone bug fix or small task has no slices and needs no entries.

```json
"tasks": [
  { "slice": "test-data-host",
    "title": "Development-only test-data host: seed, teardown, run ledger and startup sweep",
    "ac": [7, 8, 9, 10],
    "state": "committed",
    "commits": ["853ecc3", "5f54574"],
    "startedAt": "2026-08-15T14:02:00+08:00",
    "endedAt": "2026-08-15T17:45:33+08:00" },
  { "slice": "harness-lifecycle",
    "title": "Wire seed/teardown and the smtp4dev pre-flight check into all three harnesses",
    "ac": [11, 12],
    "state": "built",
    "commits": [],
    "startedAt": "2026-08-15T17:46:01+08:00",
    "endedAt": "2026-08-15T19:20:11+08:00" }
]
```

- **`slice`** is the identity — the short handle the build loop and `runs[]` refer to. Stable for the life of the work.
- **`ac`** lists the AC ids this slice delivers. Every AC should appear in at most one slice; an AC in none is built outside the task breakdown and reported as such.
- **`commits[]`** holds the short SHAs `/mynrd-dispatch` created for this slice, in order, appended never rewritten. If the developer amends or drops a commit afterwards, the array is stale by design — it records what dispatch did, not what the branch currently looks like.
- **`startedAt` / `endedAt`** — `/mynrd-dispatch` stamps `startedAt` the moment it moves the task to `in_progress`, and `endedAt` the first time the task reaches `built`, `blocked`, or `committed`. Absent until then.
- **Who writes it:** `/mynrd-plan` when it breaks the work into slices · by hand · or `/mynrd-dispatch`, which may add entries for slices it decided on itself. `state`, `commits[]`, `startedAt`, and `endedAt` are `/mynrd-dispatch`'s alone.

### `acceptanceCriteria[]` — the three optional fields

Beyond `id` / `text` / `status` / `implementedIn`:

```json
{ "id": 7, "text": "A dedicated test-data host exposes seed and teardown endpoints...",
  "status": "pass", "task": "test-data-host",
  "implementedIn": ["src/server/TestData.Api/Program.cs"],
  "evidence": "live",
  "verified": "booted the API locally — /health returned 200, so DI validation passed; grep found no reference in deploy scripts or CI config" }
```

- **`task`** — the `tasks[].slice` this AC belongs to. Omitted when there's no task breakdown.
- **`evidence`** — how this AC is provable: `test` (default; a named automated case), `live` (a check the build loop ran against the running app), or `review` (the change *is* the evidence — a docs sweep, a config removal, a command file that exists). **A docs-only AC can never have a unit test**, and forcing one is how a finished piece of work sits at `implemented` forever.
- **`verified`** — mandatory whenever `evidence` is `live` or `review`, and it must name **what was actually run or read**, not a claim. "verified working" is not evidence; "`npx playwright test --list` green in all three harnesses, 38 tests / 13 files" is.
- **Who fills the array.** `/mynrd-plan` normally, when it writes the plan. Re-syncing a populated array is `/mynrd-plan`'s re-plan path, which is the only thing that carries `status` and `implementedIn` across a renumbering.
- **Promotion to `pass`** follows the evidence type: `test` → a passing case names the AC · `live` / `review` → a `verified` string recorded in this session by the command that checked it. Inheriting an old `verified` across sessions doesn't promote anything.

### `tests` — the two tiers, one shape

`unit` and `ui` are identical objects, so one reader handles either. Populated mid-loop:

```json
"tests": {
  "unit": {
    "enabled": true,
    "command": "pytest tests/pdf",
    "status": "fail",
    "lastRun": "2026-08-14T15:41:12+08:00",
    "cases": [
      { "name": "tests/pdf/test_overflow.py::test_single_page",
        "status": "pass", "ac": [1], "durationMs": 40 },
      { "name": "tests/pdf/test_overflow.py::test_50_page_invoice",
        "status": "fail", "ac": [1, 2], "durationMs": 812,
        "message": "AssertionError: expected 50 pages, got 49" }
    ]
  },
  "ui": { "enabled": false, "reason": "no frontend change in plan",
          "status": "skipped", "cases": [] }
}
```

- **`enabled` + `command`** are `/mynrd-plan`'s; everything else is `/mynrd-dispatch`'s. A disabled or unresolvable tier carries a `reason`, never a silent drop.
- **Tier `status` is derived, never hand-set:** `fail` if any case failed · `pass` if there's ≥ 1 case and none failed · `not_run` if `cases` is empty · `skipped` if the tier is disabled.
- **`lastRun`** — stamped every time the tier's command runs, pass or fail.
- **Each case** carries `name` (the runner's own test id), `status`, the `ac` ids it covers, `durationMs` where the runner reports one, and — on failure — `message` with the **actual assertion text**, not a paraphrase. The AC↔test link lives on the case only; an AC's `pass` is computed from the cases pointing at it.
- **Large suites:** record every case up to 200. Past that, record all failures plus every case linked to an AC, and add `"truncated": { "totalCases": 2000, "recorded": 214 }` so the file never implies it listed everything.

### Status vocabularies — these exact strings, no others

| Field | Allowed values |
| --- | --- |
| top-level `status` | `intake` · `parked` · `planned` · `in_progress` · `green` · `blocked` · `verified` |
| `workflow[].status` | `pending` · `in_progress` · `done` · `blocked` · `skipped` |
| `acceptanceCriteria[].status` | `pending` · `in_progress` · `implemented` · `pass` · `fail` |
| `acceptanceCriteria[].evidence` | `test` (default) · `live` · `review` |
| `tasks[].state` | `pending` · `in_progress` · `built` · `blocked` · `committed` |
| `tests.<tier>.status` | `not_run` · `pass` · `fail` · `skipped` |
| `tests.<tier>.cases[].status` | `pass` · `fail` · `skipped` |

`tasks[].state` reads: **`built`** = code written and its AC green, not yet committed · **`committed`** = a commit exists and its SHA is in `commits[]`. Nothing in this plugin pushes, so there is no `pushed` state; `git status` is the truth about the remote.

### Every step records when it started and when it ended

`workflow[]` steps, `tasks[]`, and `runs[]` all carry `startedAt` / `endedAt`, written **at the moment of the transition** by whichever command caused it — never reconstructed at the end of a turn. All are local ISO-8601 with offset, same as `updated`.

- **`workflow[].startedAt`** — the moment the step enters `in_progress`. **`workflow[].endedAt`** — the moment it leaves to `done`, `blocked`, or `skipped`. A step that starts and finishes inside one turn gets both stamps; a step that's still `pending` has neither.
- A **`skipped`** step gets `endedAt` only — the moment the skip was decided. It never started, so `startedAt` stays absent.
- **`human-verification`** gets its `startedAt` from `/mynrd-dispatch` at unlock (Step 8). Its `endedAt` is written only by `/mynrd-verified`, and only on the human's say-so — that command also stamps `humanVerification.verifiedAt` (and `note`, if the human gave one) and sets top-level `status` to `verified`.
- **`tasks[]`** and **`runs[]`** stamps are defined in their own sections above and below — same clock, same rule.
- A **`blocked`** step that later resumes goes back to `in_progress` with a fresh `startedAt`, and its stale `endedAt` is cleared — the stamps bound the most recent span, not the sum of them; `runs[]` holds the full history.
- Each stamp lands in the same write as the status change it belongs to. A step marked `done` with no `endedAt`, or `in_progress` with no `startedAt`, is an invalid file.

### Every stage after intake is optional

The four `workflow[]` steps are the stages that *can* run, not the ones that must. A step the user chose not to run is **`skipped` with a `reason`**, never left `pending` and never faked as `done`:

```json
{ "step": "build", "status": "skipped", "reason": "edits driven by hand",
  "endedAt": "2026-08-16T11:03:00+08:00" }
```

Concretely: someone who drives the edits themselves skips `build`. Someone who ships a docs tweak without a walkthrough skips `human-verification`. **The only step that can't be skipped is `intake`** — it's what creates the file. (`/mynrd-plan` run cold marks it `skipped` itself — see its Step 0.5.)

### A stage never starts before the one it depends on finishes

`human-verification` leaves `pending` **only** when `build` is `done`. Not while `build` is `in_progress`, not while it's `blocked`. The same rule runs the whole array: `build` stays `pending` until `plan` is `done` (or `skipped` with a `PLAN.md` as the evidence).

**No command may end its turn with a step left `in_progress`.** `in_progress` means "an agent is working on this right now, inside this turn". When the turn ends the step is `done`, `blocked`, or `skipped` — the one exception being `human-verification`, which is `in_progress` precisely because the actor is the human and the turn is over. A `build` left `in_progress` between turns is a command that stopped mid-work without saying so, and it's exactly the state that produces a "go test it" message the file contradicts.

### Who writes what

| Command | Fields it owns |
| --- | --- |
| `/mynrd-intake` | creates the file · `intake` (incl. `findings[]`) · `workflow[intake]` |
| `/mynrd-plan` | `type` · `title` · `plan` · `acceptanceCriteria[]` (incl. `task` + `evidence`) · `tasks[]` entries it creates · `tests.*.enabled` + `command` · `workflow[plan]` |
| `/mynrd-dispatch` | `branch` · `acceptanceCriteria[].status` + `implementedIn` + `verified` · `tasks[].state` + `commits[]` + `startedAt`/`endedAt` · `tests.*` results · `runs[]` · `humanVerification.unlocked` + `unlockedAt` · `workflow[build]` · `workflow[human-verification].status` + `startedAt` at unlock only |
| `/mynrd-verified` | `workflow[human-verification].status = done` + `endedAt` · `humanVerification.verifiedAt` + `note` · top-level `status = "verified"` — on the human's say-so only |

`tasks[].state`, `tasks[].commits[]`, and the task stamps are **`/mynrd-dispatch`'s alone** — it is the only command in this plugin that commits. Everything else treats them as read-only.

### `runs[]` — one entry per loop round

`/mynrd-dispatch` appends these; nothing else touches the array. The shape is deliberately loose (a round records whatever it did), but these keys have fixed meanings:

```json
{ "startedAt": "2026-08-15T18:40:00+08:00",
  "endedAt": "2026-08-15T19:22:00+08:00",
  "tasks": ["test-data-host", "harness-lifecycle"],
  "agents": [ { "agent": "mynrd-node-dev", "task": "global setup/teardown", "ac": [11],
                "files": ["src/client/e2e/global-setup.ts"] } ],
  "services": [ { "name": "testdata-api", "command": "dotnet run --project src/server/TestData.Api",
                  "url": "http://localhost:5080", "startedByDispatch": true,
                  "ready": true, "stoppedAt": "2026-08-15T19:20:11+08:00" } ],
  "build": { "command": "dotnet build src/server/Server.slnx", "errors": 0, "warnings": 79 },
  "unit":  { "command": "dotnet test src/server/Server.slnx", "passed": 858, "failed": 0 },
  "liveChecks": ["npx playwright test --list green in all three harnesses (38 tests / 13 files)"],
  "commits": ["09b71bf"],
  "outcome": "committed",
  "notes": "off-by-one in the final chunk flush" }
```

- **`startedAt` / `endedAt`** bound the round: the entry is appended with `startedAt` when the round opens, and `endedAt` is filled when it closes — both stamps, every round, per "Every step records when it started and when it ended" above.
- **`tasks`** is a list of slice handles even when it holds one — a round can close more than one slice.
- **`services`** is what dispatch started, and every entry it started carries a `stoppedAt`. An entry with `"startedByDispatch": false` was the developer's own process and was left alone.
- **`liveChecks`** are free-text, and each one names the command that produced it. A check that didn't happen is written as such (`"NOT YET RUN: live seed/teardown round trip — needs the local stack running"`), never omitted.

`updated` is rewritten by whoever touched the file, as local ISO-8601 with offset. **Never write a status better than the evidence** — this file outlives the conversation, and an optimistic status here is a lie with a long tail.

---

## What this command does not do

- **No writes outside `.work/`.** It creates `progress.json` (and, on park, `BRIEF.md`) and touches nothing else — no source files, no tracker, no network.
- **No git operations.** Branching is yours to do by hand — `<type>/<slug>` when you want one.
- **No plan.** It writes `progress.json`, never `PLAN.md`. Acceptance criteria, implementation notes, and test tiers are `/mynrd-plan`'s job; the arrays it leaves behind are empty on purpose.
- **No build.** No source edits, no subagent dispatch, no tests. Even when the user asks for it directly — see [Intake enforces the sequence](#intake-enforces-the-sequence).
- **No deep interrogation.** One brief, one duplicate check, one routing question. If you're on your fourth clarifying question, you've already left intake and should be in `/mynrd-plan`.

---

## Failure handling

- **A `.work/` folder won't scan** (unreadable, or its `progress.json` doesn't parse): show the error, skip that folder, and say the duplicate check ran partial — flag plainly that a duplicate may exist unseen. Don't try to repair or overwrite the broken file from triage.
- **Step 4 lands on a folder whose existing `progress.json` won't parse:** don't overwrite it — report the corruption, name the file, and stop. Hand-fixing the file beats losing its build state.
