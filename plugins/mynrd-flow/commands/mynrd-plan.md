---
name: mynrd-plan
description: Discuss a request and produce a local plan — PLAN.md and progress.json in a `.work/` folder. No tracker, no approval gate; everything stays on this machine.
---

# /mynrd-plan

Discussion-first command. One flow: discuss a request — a chat ask, a bug report, your own observation — then write a plan into a `.work/` folder. Nothing is sent anywhere, so there is no approval gate.

**This command has no entry requirement.** Run it cold, any time, on anything — no `/mynrd-intake` first, no existing `.work/` folder. Planning a piece of work is a complete use of it on its own. Coming from intake only means Step 0.5 finds a `progress.json` already there and reads the route out of it.

It is also the **only** command that writes `PLAN.md`, which is what `/mynrd-dispatch` builds from. Everything downstream depends on this command having run at least once.

---

## Argument

| `$ARGUMENTS` | Meaning |
| --- | --- |
| empty | New plan — Step 1 opens the discussion |
| free text | New plan — the text is the topic; use it as the opening message and skip the intro |
| a path to a `.work/` folder | **Re-plan** — load the existing `PLAN.md` and revise it in place |

---

## Step 0 — Project identity check

Resolve the repo root this plan belongs to: `git rev-parse --show-toplevel`, falling back to the current working directory when not in a repo. That root is where the `.work/` folder lives. State it in one line so a session running in the wrong directory gets caught before anything is written.

---

## Step 0.5 — Open `progress.json`

Every run works against a `progress.json` in a `.work/` folder. Schema, folder naming, and status vocabularies are defined once in `commands/mynrd-intake.md` § "The `progress.json` file" — read that, don't restate it.

**Entered from `/mynrd-intake`?** The file already exists and its `intake.route` tells you what to do:

| `intake.route` | Action |
| --- | --- |
| `plan` | Continue here |
| `park` | The user parked it and came back — confirm they want to plan it now |

**`intake.findings[]` is planning input, not decoration.** When the file carries findings, read them before you ask anything: each one names a `path:line` that was already checked, so re-deriving it wastes a turn and asking the user about it wastes theirs. Open the discussion on what the findings *don't* settle. Verify one before you build an AC on it — a finding is what a past session read, not a guarantee the code still says it — and say so plainly if it no longer holds rather than silently planning around it. An empty or absent array is the normal case and means nothing was established, not that the code is fine.

**Invoked directly (intake skipped)?** Create the file yourself with `intake: null` and `workflow[intake] = skipped`, reason `"intake skipped — /mynrd-plan invoked directly"`, `endedAt` stamped now (a skipped step gets no `startedAt`). Folder name follows the same rule: `.work/<YYYY-MM-DD>-<slug>/`. Skipping intake is supported, not a mistake — don't nag about it.

Whichever way you got here, this is a local filesystem write: **no gate**.

---

## Step 1 — Usage guide

Print this short intro the first time (skip it when `$ARGUMENTS` already carries the topic):

> **`/mynrd-plan`.** Tell me what needs planning. Could be:
> - A request passed via chat
> - A bug you hit
> - Your own observation while working
>
> I'll ask a few questions to surface gaps, then we'll pick the shape of the draft (Story / Task / Bug) and write the plan together. Everything stays local — `PLAN.md` and `progress.json` in a `.work/` folder.

Wait for the user's opening message.

**Re-planning?** (a `.work/` folder path was the argument, or the folder already holds a `PLAN.md`) — read the existing `PLAN.md` first and open the discussion on what's changing. `PLAN.md` is rewritten in place — no `PLAN-v2.md`.

## Step 2 — Discussion

**Entered from `/mynrd-intake`?** Then the brief is your input — don't reprint it and don't re-ask what it already answers (What / Who-why / Signal / Urgency / Project). Open directly on its `Unknowns` row. Skip Step 1's intro entirely; the user has already seen the framing.

Read the user's input. Ask **at most 2 clarifying questions per turn**. Aim to surface:

- **What's being asked for** in plain language
- **Who needs it / why it matters** (the driver)
- **Scope and out-of-scope** boundaries
- **Acceptance criteria** — how done is judged
- **Bug specifics** (if it's a bug): repro steps, actual vs expected, impact

Don't over-interview. If the user signals "draft it" / "let's write it" / "go ahead," stop asking and move to Step 3.

## Step 3 — Pick the type

The type — Task / User Story / Bug — shapes the draft; it isn't sent anywhere. Ask **one question**. Call `AskUserQuestion`. Only a host missing the tool entirely falls back to a single plain-text message with the question and one reply.

- `question`: `"What shape should this plan take?"`
- `multiSelect`: `false`
- `options`:
  1. The type **you (the AI) recommend** as the first option, with label `<Type> (Recommended)` and a 1-line description summarizing the drafted content (e.g. `User Story (Recommended) — the export-PDF flow needs to handle multi-page invoices`). Pick the type based on signals in the discussion:
     - User-facing capability / value → User Story
     - Implementation step under existing work → Task
     - Defect / unexpected behavior → Bug
  2. The other two types as plain options without `(Recommended)`, each with a short hint of how it'd shape the draft.

Wait for the selection. If they pick a type other than your recommendation, that's fine — go with their pick.

## Step 4 — Draft the content

Based on the chosen type, draft the plan content using the locked formats below.

### Story / Task — Description (markdown)

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

### Story / Task — Acceptance Criteria (markdown numbered list)

```markdown
1. [Specific, independently testable condition]
2. [Next condition]
```

### Bug — Repro Steps (markdown)

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

### Bug — Acceptance Criteria

For Bugs, AC is typically the inverse of Expected Result. Keep the same markdown numbered-list format. May be omitted if Expected Result fully covers the fix criterion.

## Step 5 — Write

No preview, **no gate, no approval prompt of any kind** — neither `AskUserQuestion` nor a typed `Approve …` reply. There is nothing external to approve, and gating a local file write teaches nothing. Show what you wrote after the fact.

1. **`PLAN.md`** per [The `.work` plan folder](#the-work-plan-folder), in `.work/<YYYY-MM-DD>-<slug>/`.
2. **`progress.json`** in the same folder:
   - `type`, `title`, `slug`, `plan` set. `status = "planned"`, `workflow[plan] = done` with its `startedAt` (when the planning discussion opened) and `endedAt` (now) — per `mynrd-intake.md` § "Every step records when it started and when it ended".
   - `acceptanceCriteria[]` — one entry per AC in the drafted list, `{ "id": <n>, "text": "<AC text>", "status": "pending", "implementedIn": [] }`. Numbering matches the drafted AC list exactly; `/mynrd-dispatch` and every test case reference these ids.
   - `tests.unit` / `.ui` — `enabled` and `command` from the plan's `## Testing` section. A tier the plan says `no` to gets `enabled: false` and a `reason`. Never leave `enabled: null` here; that's the marker for "nobody resolved this yet".
3. **`.gitignore`** must cover `.work/` before either write — see the gitignore rule below.

Report the paths and stop:

```text
Planned locally.
  Plan:     .work/2026-08-14-invoice-export-fails/PLAN.md
  Progress: .work/2026-08-14-invoice-export-fails/progress.json
  AC:       3 criteria, all pending
  Tests:    unit yes (pytest tests/pdf) · ui no

Next: /mynrd-dispatch .work/2026-08-14-invoice-export-fails
```

---

## The `.work` plan folder

The plan lives on disk; the local copy is what `/mynrd-dispatch` reads.

**Layout** — relative to the repo root resolved in Step 0:

```text
.work/<YYYY-MM-DD>-<slug>/PLAN.md
```

- `<slug>` — lowercased title, alphanumerics collapsed to single hyphens, trimmed, max 40 chars. Same rule used for branch names, so `.work/2026-08-14-pdf-export-pagebufferoverflow/` pairs with `bugfix/pdf-export-pagebufferoverflow`. Before a title exists, the slug comes from the intake brief's `What` line.
- One directory per unit of work. Re-planning rewrites `PLAN.md` in place; it does not create a second directory or a `PLAN-v2.md`.
- `progress.json` lives beside `PLAN.md` in the same directory — see `commands/mynrd-intake.md` § "The `progress.json` file".
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

**Type:** <Task|User Story|Bug>

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

Skip sections that don't apply (a Bug uses Repro Steps / Actual / Expected instead of "What needs to happen"). Never leave `Implementation notes` empty — if the discussion produced none, write what you'd tell the next dev about where to start.

**The `Testing` section is what `/mynrd-dispatch` reads to decide which test tiers its build loop runs.** Fill it from the discussion and what the repo actually has — don't ask a question for it. Defaults: Unit `yes` for backend work, UI `yes` for frontend work. **Those two tiers are all there is** — don't add an `E2E:` row or name a browser suite here; `/mynrd-dispatch` runs neither.

---

## Failure handling

If any tool call or file write errors, show the error verbatim, don't retry automatically. Ask the user whether to fix and retry or abort.
