# The `progress.json` file

**This is the canonical schema.** `/mynrd-plan` creates the file, `/mynrd-dispatch` and `/mynrd-verified` update it. None of the three defines it. When a command file disagrees with this document, this document wins.

## Folder

Relative to the repo root (`git rev-parse --show-toplevel`; fall back to the current working directory when not in a repo). Same folder that holds `PLAN.md` — one directory per unit of work:

```text
.work/<YYYY-MM-DD>-<slug>/
  progress.json     this file
  PLAN.md           written by /mynrd-plan
  BUILD.md          written by /mynrd-dispatch at exit — the handoff report on disk; later runs of the same folder add BUILD_02.md, BUILD_03.md, …
  REVISED_01.md …   one per post-handoff change made in the dispatch conversation, numbered in order
```

`BUILD*.md` and `REVISED_*.md` are narrative — they record what a run reported and what changed afterwards. They never carry state this file holds, and nothing reads them back to decide a step. Their rules live in `commands/mynrd-dispatch.md` § "`BUILD.md`" and § "After the handoff".

- `<slug>` — lowercased, non-alphanumerics collapsed to single hyphens, trimmed, max 40 chars. Taken from the plan's title.
- **The dated folder name is permanent** — it is the work's local `id`, and everything downstream refers to it. Don't rename it once anything has been written into it. `slug` is set once, at creation, and never rewritten — it must always equal the folder name minus its date prefix.
- **Resolving a folder from a bare slug** (`/mynrd-dispatch <slug>`, `/mynrd-verified <slug>`, a branch name): match `.work/*-<slug>/` — exact suffix first, then prefix. More than one match → list them and ask; never pick silently.
- **`.gitignore` must cover `.work/` before the first write** — same rule and same procedure as the plan folder, see `commands/mynrd-plan.md` § "The `.work` plan folder".

## Schema

As `/mynrd-plan` leaves it, before any build:

```json
{
  "schemaVersion": 4,
  "id": "2026-08-14-pdf-export-dies-on-invoices",
  "title": "PDF export dies on invoices past 10 pages",
  "slug": "pdf-export-dies-on-invoices",
  "branch": null,
  "plan": "PLAN.md",
  "status": "planned",
  "created": "2026-08-14T09:12:00+08:00",
  "updated": "2026-08-14T10:40:00+08:00",

  "findings": [
    "PdfChunkWriter.Flush() drops the final buffer when pageCount % 10 == 0 — src/server/Pdf/PdfChunkWriter.cs:212"
  ],

  "workflow": [
    { "step": "plan",               "status": "done",
      "startedAt": "2026-08-14T09:12:00+08:00", "endedAt": "2026-08-14T10:40:00+08:00" },
    { "step": "build",              "status": "pending" },
    { "step": "human-verification", "status": "pending" }
  ],

  "tasks": [],

  "acceptanceCriteria": [
    { "id": 1, "text": "Invoices past 10 pages export without error", "status": "pending", "implementedIn": [] }
  ],

  "tests": {
    "unit": { "enabled": true,  "status": "not_run", "command": "pytest tests/pdf", "cases": [] },
    "ui":   { "enabled": false, "reason": "no frontend change in plan", "status": "skipped", "cases": [] }
  },

  "humanVerification": { "unlocked": false, "unlockedAt": null },

  "runs": []
}
```

**`id`** is the folder name (`<YYYY-MM-DD>-<slug>`) and never changes — it's how `runs[]` and later sessions refer to this work.

`branch` stays `null` until `/mynrd-dispatch` fills it. `tasks` starts empty and stays empty on anything that isn't broken into slices.

**`findings[]`** holds what the code actually says, one short line each, ending in the `path:line` that proves it. It's optional and often empty. Record it when the session **already** established something before planning started — a debugging thread, a read-only investigation, the user pasting a stack trace. Two rules: every entry names a file (a finding with no path is an opinion, and belongs in the discussion instead), and nothing is written here that wasn't actually read. `/mynrd-plan` treats the array as input, so a wrong line here becomes a wrong AC later.

## `tasks[]` — the slices of a larger piece of work

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

## `acceptanceCriteria[]` — the three optional fields

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

## `tests` — the two tiers, one shape

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

## Status vocabularies — these exact strings, no others

| Field | Allowed values |
| --- | --- |
| top-level `status` | `planned` · `in_progress` · `green` · `blocked` · `verified` |
| `workflow[].status` | `pending` · `in_progress` · `done` · `blocked` · `skipped` |
| `acceptanceCriteria[].status` | `pending` · `in_progress` · `implemented` · `pass` · `fail` |
| `acceptanceCriteria[].evidence` | `test` (default) · `live` · `review` |
| `tasks[].state` | `pending` · `in_progress` · `built` · `blocked` · `committed` |
| `tests.<tier>.status` | `not_run` · `pass` · `fail` · `skipped` |
| `tests.<tier>.cases[].status` | `pass` · `fail` · `skipped` |

`tasks[].state` reads: **`built`** = code written and its AC green, not yet committed · **`committed`** = a commit exists and its SHA is in `commits[]`. Nothing in this plugin pushes, so there is no `pushed` state; `git status` is the truth about the remote.

## Every step records when it started and when it ended

`workflow[]` steps, `tasks[]`, and `runs[]` all carry `startedAt` / `endedAt`, written **at the moment of the transition** by whichever command caused it — never reconstructed at the end of a turn. All are local ISO-8601 with offset, same as `updated`.

- **`workflow[].startedAt`** — the moment the step enters `in_progress`. **`workflow[].endedAt`** — the moment it leaves to `done`, `blocked`, or `skipped`. A step that starts and finishes inside one turn gets both stamps; a step that's still `pending` has neither.
- A **`skipped`** step gets `endedAt` only — the moment the skip was decided. It never started, so `startedAt` stays absent.
- **`human-verification`** gets its `startedAt` from `/mynrd-dispatch` at unlock (Step 8). Its `endedAt` is written only by `/mynrd-verified`, and only on the human's say-so — that command also stamps `humanVerification.verifiedAt` (and `note`, if the human gave one) and sets top-level `status` to `verified`.
- **`tasks[]`** and **`runs[]`** stamps are defined in their own sections above and below — same clock, same rule.
- A **`blocked`** step that later resumes goes back to `in_progress` with a fresh `startedAt`, and its stale `endedAt` is cleared — the stamps bound the most recent span, not the sum of them; `runs[]` holds the full history.
- Each stamp lands in the same write as the status change it belongs to. A step marked `done` with no `endedAt`, or `in_progress` with no `startedAt`, is an invalid file.

## Every stage after plan is optional

The three `workflow[]` steps are the stages that *can* run, not the ones that must. A step the user chose not to run is **`skipped` with a `reason`**, never left `pending` and never faked as `done`:

```json
{ "step": "build", "status": "skipped", "reason": "edits driven by hand",
  "endedAt": "2026-08-16T11:03:00+08:00" }
```

Concretely: someone who drives the edits themselves skips `build`. Someone who ships a docs tweak without a walkthrough skips `human-verification`. **The only step that can't be skipped is `plan`** — it's what creates the file, and nothing builds without `PLAN.md`.

## A stage never starts before the one it depends on finishes

`human-verification` leaves `pending` **only** when `build` is `done`. Not while `build` is `in_progress`, not while it's `blocked`. The same rule runs the whole array: `build` stays `pending` until `plan` is `done`.

**No command may end its turn with a step left `in_progress`.** `in_progress` means "an agent is working on this right now, inside this turn". When the turn ends the step is `done`, `blocked`, or `skipped` — the one exception being `human-verification`, which is `in_progress` precisely because the actor is the human and the turn is over. A `build` left `in_progress` between turns is a command that stopped mid-work without saying so, and it's exactly the state that produces a "go test it" message the file contradicts.

## Who writes what

| Command | Fields it owns |
| --- | --- |
| `/mynrd-plan` | creates the file · `id` · `slug` · `title` · `plan` · `findings[]` · `acceptanceCriteria[]` (incl. `task` + `evidence`) · `tasks[]` entries it creates · `tests.*.enabled` + `command` · `workflow[plan]` |
| `/mynrd-dispatch` | `branch` · `acceptanceCriteria[].status` + `implementedIn` + `verified` · `tasks[].state` + `commits[]` + `startedAt`/`endedAt` · `tests.*` results · `runs[]` · `humanVerification.unlocked` + `unlockedAt` · `workflow[build]` · `workflow[human-verification].status` + `startedAt` at unlock only · beside the file: `BUILD*.md` at exit, `REVISED_NN.md` for post-handoff changes (neither touches this file) |
| `/mynrd-verified` | `workflow[human-verification].status = done` + `endedAt` · `humanVerification.verifiedAt` + `note` · top-level `status = "verified"` — on the human's say-so only |

`tasks[].state`, `tasks[].commits[]`, and the task stamps are **`/mynrd-dispatch`'s alone** — it is the only command in this plugin that commits. Everything else treats them as read-only.

## `runs[]` — one entry per loop round

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
