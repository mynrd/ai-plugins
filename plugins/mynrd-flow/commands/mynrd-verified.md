---
name: mynrd-verified
description: Record that you verified a green build yourself — close the human-verification step in the work folder's progress.json, stamp when, and optionally keep a one-line note of what you checked. Local only — one JSON file changes, nothing else.
---

# /mynrd-verified

The last write of the workflow. `/mynrd-dispatch` ends with *"Development is done — try it now"* and moves `workflow[human-verification]` to `in_progress`; the verifying itself is the human's, and this command is how they say it happened. It closes the step, stamps `verifiedAt`, and sets the work's terminal status — so a later session reading `progress.json` sees finished work instead of a verification stuck `in_progress` forever.

**This command verifies nothing itself.** It doesn't run tests, doesn't start the app, doesn't read the diff. Running it *is* the user's statement "I exercised this and I'm satisfied" — the command just writes that down. Never run it on your own initiative, never suggest the user "just run /mynrd-verified" to make a state file green, and never run it as the tail of a dispatch turn.

---

## Argument

| Given | Meaning |
| --- | --- |
| *(empty)* | Find the candidates and ask which (below). |
| `<slug>` | Use `.work/*-<slug>/` — suffix match, per `PROGRESS-SCHEMA.md` § Folder. |
| a path to a `.work/` folder | Use that folder. |
| path or slug, then free text | The folder as above; everything after it is the **note** — one line on what was checked, stored verbatim. Example: `/mynrd-verified e2e-standard ran the playwright suite against a real seed, commits squashed and pushed`. |

**No argument:** scan `.work/*/progress.json` for folders where `workflow[human-verification]` is `in_progress` (the awaiting-verification state).

- **Exactly one** → name it — title, slug, when it unlocked — and ask one yes/no: this one?
- **Several** → list them (slug · title · unlocked when) and ask which.
- **None** → say so, and list any folders sitting at `green` or `blocked` so the user can see why nothing is awaiting verification. Stop. Never widen the search to "probably meant this one".

---

## Step 1 — Load and gate

Open `<folder>/progress.json`. Missing file → say the workflow never started here (`/mynrd-plan` creates it) and stop.

Then exactly one of these paths:

| State | Action |
| --- | --- |
| `workflow[human-verification]` is `in_progress` (and `humanVerification.unlocked` is `true`) | Proceed to Step 2. |
| `workflow[human-verification]` is already `done` | Say so — when it was verified, the note if one exists — and stop. Nothing to write. |
| `workflow[build]` is `skipped` (edits driven by hand, dispatch never ran, so unlock never happened) | Confirm once: *"Build was skipped — mark this verified anyway?"* On yes, proceed to Step 2; this path also stamps the step's `startedAt` (same timestamp as `endedAt`), since nothing else ever did. |
| Anything else — build `in_progress`, `blocked`, or `pending` | Refuse. Name exactly what's holding it: the blocked ACs, the unfinished build, the missing plan. Point at the command that resolves it (`/mynrd-dispatch`, `/mynrd-plan`). The gate is `/mynrd-dispatch`'s Step 8, and this command never reproduces its checks or overrides its verdict. |

**Never work around the gate.** Not by setting `humanVerification.unlocked` yourself, not by "the tests look green so it's fine". A refusal here means the build isn't finished, and the fix is finishing it.

---

## Step 2 — Write

One edit to `progress.json`, all fields in the same write:

- `workflow[human-verification].status = "done"` with `endedAt` = now (local ISO-8601 with offset, same clock as every other stamp)
- `humanVerification.verifiedAt` = the same timestamp
- `humanVerification.note` = the note text, only if one was given — never invent one
- top-level `status = "verified"`
- `updated` = the same timestamp

Nothing else changes. No AC is touched, no test result, no `runs[]` entry, no `tasks[]` state — those record what the build did, and the build is over.

---

## Step 3 — Report

Three or four lines, then stop:

```text
Verified — <title> is closed.

  State:  .work/<YYYY-MM-DD>-<slug>/progress.json  (status: verified)
  Note:   <the note, or "none">
```

If `git log` shows the dispatch commits still unpushed on the feature branch, add one line saying so — pushing stays the user's, this command runs no git writes.

---

## What `/mynrd-verified` NEVER does

- Runs tests, starts services, or inspects the diff — it records a verdict, it doesn't produce one
- Sets `humanVerification.unlocked` or re-derives `/mynrd-dispatch`'s exit conditions
- Touches `acceptanceCriteria[]`, `tests`, `tasks[]`, or `runs[]`
- Runs any git write — no commit, no push
- Marks work verified that no human asked it to
