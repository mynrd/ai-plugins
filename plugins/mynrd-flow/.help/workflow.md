# Workflow

The intended sequence, why it's enforced, and how to tell where you are.

---

## The sequence

```text
/mynrd-intake  →  /mynrd-plan  →  /mynrd-dispatch  →  human verification
    triage          PLAN.md          build loop       you + /mynrd-verified
```

| Stage | Command | Produces |
|---|---|---|
| Intake | `/mynrd-intake` | A brief of the request + `.work/<slug>/progress.json` |
| Plan | `/mynrd-plan` | `PLAN.md` (approach, AC, `## Testing`) + AC and test tiers filled into `progress.json` |
| Build | `/mynrd-dispatch` | Source edits by the specialist agents, test runs, local commits, `progress.json` updated round by round |
| Human verification | you, then `/mynrd-verified` | You exercise the change, review the commits, push - then `/mynrd-verified` records it: `human-verification: done`, `status: verified` |

Two commands fit **anywhere** in that sequence:

- `/mynrd-refine` - turn the current discussion into a formatted Story / Task / Bug draft. Writes nothing; useful as a checkpoint before planning, or on its own.
- `/mynrd-help` - answer questions about the plugin from `.help/`.

---

## Intake enforces the sequence

**Running `/mynrd-intake` opts this work into the workflow, and the rest of that session honors it.** The order is fixed:

```text
intake  →  plan  →  build  →  human verification
```

- **`plan` is not skippable - a `PLAN.md` is.** If intake's existing-work check found one, planning is already done and `/mynrd-plan` is optional (re-running it re-opens the plan). If it found none, `/mynrd-plan` runs before anything builds. There is no third way to produce that file.
- **`build` is `/mynrd-dispatch`,** and it builds from `PLAN.md` and `acceptanceCriteria[]`. Nothing else in this plugin builds.

### When you ask to start development anyway

If, after intake, you say *"start the development"*, *"just build it"*, *"go ahead and code it"* - `progress.json` gets checked first:

- **`workflow[plan]` is `done` and `acceptanceCriteria[]` is non-empty** → fine, `/mynrd-dispatch` runs.
- **Otherwise → no build.** Not with `/mynrd-dispatch`, not with an agent, not by editing files inline. You'll get pointed at `/mynrd-plan` instead.

This is not a judgment call and there is no "just this once". The brief is a triage note: it has no acceptance criteria, no implementation notes, and no `## Testing` section, so a build started from it has no definition of done and no way to record one. Writing code straight off a brief is the specific failure this rule exists to stop.

**This applies to intake's own session only.** `/mynrd-plan` is entry-point-free - run it cold, with no intake, whenever you want to plan a piece of work. Nothing restricts that.

---

## Reading where you are

Open `.work/<slug>/progress.json` and look at `workflow[]` - one entry per stage, each `pending` / `in_progress` / `done` / `blocked` / `skipped`.

- `intake: skipped` - you ran `/mynrd-plan` cold. Normal.
- `plan: done`, `build: pending` - ready for `/mynrd-dispatch`.
- `build: in_progress` - a dispatch run didn't finish; re-run `/mynrd-dispatch` and it resumes from the first unfinished step instead of starting over.
- `build: blocked` - the loop ended with at least one blocker; the run's report (and `runs[]`) says what's holding it.
- `build: done`, `human-verification: in_progress` - the loop is green and it's your turn. When you're satisfied, `/mynrd-verified` closes it.
- `human-verification: done`, `status: verified` - the work is finished; nothing left to run.

Full schema and status meanings in [progress.md](progress.md).

---

## Green loop ≠ done

`/mynrd-dispatch` ending with `Development is done - try it now.` means every AC passed its evidence and every enabled test tier is green. It does not mean the work is finished:

1. Exercise the change yourself - the loop has no e2e tier, and "the test passes" is not "it feels right".
2. Review the commits the loop made - they're yours to squash or drop.
3. Push when satisfied. The loop never pushes.
4. Run `/mynrd-verified .work/<slug>` (optionally with a one-line note of what you checked) - it closes the `human-verification` step and marks the work `verified`. No command does this for you; without it the file sits at `human-verification: in_progress` forever.
