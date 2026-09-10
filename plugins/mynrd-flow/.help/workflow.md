# Workflow

The intended sequence, why it's enforced, and how to tell where you are.

---

## The sequence

```text
/mynrd-plan  →  /mynrd-dispatch  →  human verification
   PLAN.md         build loop       you + /mynrd-verified
```

| Stage | Command | Produces |
|---|---|---|
| Plan | `/mynrd-plan` | `.work/<date>-<slug>/` with `PLAN.md` (approach, AC, `## Testing`) and `progress.json` (AC, test tiers, findings) |
| Build | `/mynrd-dispatch` | Source edits by the specialist agents, test runs, local commits, `progress.json` updated round by round |
| Human verification | you, then `/mynrd-verified` | You exercise the change, review the commits, push - then `/mynrd-verified` records it: `human-verification: done`, `status: verified` |

Two commands fit **anywhere** in that sequence:

- `/mynrd-refine` - turn the current discussion into a formatted draft (Description + AC, or Repro Steps + AC for a bug). Writes nothing unless you ask it to; useful as a checkpoint before planning, or on its own.
- `/mynrd-help` - answer questions about the plugin from `.help/`.

---

## Nothing builds without a plan

The order is fixed:

```text
plan  →  build  →  human verification
```

- **`plan` is not skippable.** `/mynrd-plan` is the only command that writes `PLAN.md` and creates `progress.json`. Re-running it on an existing folder re-opens the plan.
- **`build` is `/mynrd-dispatch`,** and it builds from `PLAN.md` and `acceptanceCriteria[]`. Nothing else in this plugin builds.

### When you ask to start development anyway

If you say *"start the development"*, *"just build it"*, *"go ahead and code it"* mid-plan, or point `/mynrd-dispatch` at a folder without a plan - `progress.json` gets checked first:

- **`workflow[plan]` is `done` and `acceptanceCriteria[]` is non-empty** → fine, `/mynrd-dispatch` runs.
- **Otherwise → no build.** Not with `/mynrd-dispatch`, not with an agent, not by editing files inline. You'll get pointed at `/mynrd-plan` instead.

This is not a judgment call and there is no "just this once". A discussion is not a plan: without AC, implementation notes, and a `## Testing` section a build has no definition of done and no way to record one.

---

## Reading where you are

Open `.work/<date>-<slug>/progress.json` and look at `workflow[]` - one entry per stage, each `pending` / `in_progress` / `done` / `blocked` / `skipped`.

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
4. Run `/mynrd-verified <slug>` (optionally with a one-line note of what you checked) - it closes the `human-verification` step and marks the work `verified`. No command does this for you; without it the file sits at `human-verification: in_progress` forever.
