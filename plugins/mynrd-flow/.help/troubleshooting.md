# Troubleshooting

Specific refusals and errors you might hit, what they mean, how to fix. Everything here is local - there's no auth, no server, no env var to debug.

---

## Workflow refusals

### `/mynrd-dispatch` stops: "no PLAN.md"

The work folder has no plan file. `/mynrd-dispatch` builds from `PLAN.md` and nothing else - run `/mynrd-plan` first. There is no way to build straight from a brief; it has no acceptance criteria and no `## Testing` section, so there'd be no definition of done.

### `/mynrd-dispatch` stops: "acceptanceCriteria is empty"

A `progress.json` exists but `/mynrd-plan` never filled it in - usually the planning discussion was abandoned before the plan was written. Re-run `/mynrd-plan`; it writes `PLAN.md` and the AC list in the same pass.

### `/mynrd-dispatch` stops: "no progress.json"

The loop **never creates** that file - `/mynrd-intake` does (or `/mynrd-plan` run cold). If you're pointing dispatch at a bare folder or a stray `.md`, start the workflow properly first.

### "I said 'just build it' and it declined"

Sequence enforcement, working as designed. After intake, nothing builds until `workflow[plan]` is `done` and `acceptanceCriteria[]` is non-empty. See [workflow.md](workflow.md) § "Intake enforces the sequence". Run `/mynrd-plan` and then re-ask.

### "Dispatch can't find which work to build"

With no arg it looks for the one `.work/` folder with unfinished build state. Zero candidates → nothing is mid-build (start with intake or plan). More than one → pass the folder path explicitly: `/mynrd-dispatch .work/<slug>/`.

---

## Build-loop results

### An AC is stuck at `implemented`

Nothing tests it. `implemented` means code written; `pass` needs evidence - a named test case, a `live` check, or a `review` line. The report names these gaps explicitly. Either add a test (re-open the plan if the `## Testing` section is thin) or, if the AC genuinely can't have a test, give it `live` or `review` evidence via `/mynrd-plan`. See [progress.md](progress.md).

### An AC ended `blocked`

Two fix attempts failed on the same distinct failure, so the loop parked it and finished everything else. `runs[]` in `progress.json` records what was tried and what was actually wrong. Fix the cause yourself and re-run `/mynrd-dispatch` (it resumes, not restarts), or re-plan if the AC was wrong to begin with.

### Dispatch ran but committed nothing

You're on a protected branch - `main`, `master`, `dev`, `develop`, `release/*`, `hotfix/*`. The loop builds but commits nothing all run on those, and its report says so. Branch off, then either re-run or commit the working tree yourself.

### A pre-commit hook rejected the loop's commit

Reported, never bypassed - the loop won't use `--no-verify`. Fix whatever the hook flagged (or fix the hook) and re-run `/mynrd-dispatch`.

### A test looks wrong and the loop left it red

Deliberate. The loop never edits a test to make it pass. If the test itself is the bug, the report says so - fixing it is a plan change, not a loop retry. Re-open with `/mynrd-plan` so the change is on the record.

### The shell prompts for permission on every test command

That's your machine's Bash permission, not the plugin. Allowlist the repo's test and dev-server commands once in the repo's `.claude/settings.json` and the prompts stop.

### The dev server the loop started is still running

Shouldn't happen - anything the loop started itself it kills, process tree and all, before it reports. If something already answered on the port when the run began, the loop used it and left it alone on purpose; that one was yours. Kill it yourself if you didn't mean to leave it up.

---

## State and files

### `.work/` shows up in `git status`

The `.gitignore` entry is missing - the first command to write `.work/` is supposed to add it. Add `.work/` to `.gitignore` yourself; nothing in that folder should ever be committed.

### Fresh clone has no `.work/` folder

Correct - `.work/` is gitignored, machine-local state. It never leaves the machine that did the work. To continue the work elsewhere, re-run `/mynrd-plan` there; the `runs[]` history from the other machine is gone and there's no way to recover it.

### Intake found an existing `progress.json` and left it alone

Working as designed. Re-triaging existing work reports the state it found rather than clobbering it. If you genuinely want a clean start, delete the `.work/<slug>/` folder first.

### Parked work never resumed

Nothing resumes it automatically. Run `/mynrd-plan` on the folder (`/mynrd-plan .work/<slug>/`) when you're ready - the `BRIEF.md` is still there as input.

---

## Install / update

### Commands don't show up after install

Check both steps ran:

```bash
claude plugin marketplace add https://github.com/mynrd/ai-plugins.git
claude plugin install mynrd-flow@mynrd-ai-plugins
```

Then restart your editor - a running session doesn't pick up newly installed commands.

### My source edits aren't taking effect

```bash
claude plugin marketplace update mynrd-ai-plugins
claude plugin update mynrd-flow@mynrd-ai-plugins
```

Both commands needed - the marketplace metadata and plugin payload are cached separately. Restart the editor after.

---

## Recovery

### "I want to abandon a run mid-flow"

Just stop. The only persisted state is `.work/<slug>/` (resumable, harmless) and any commits the loop already made (yours to keep, squash, or drop - `git log` shows them, they were never pushed).

### "The loop's commits aren't what I want"

They're local-only and never pushed, so standard git applies: squash them, reword them, or drop them before you push. The loop never amends or force-touches anything, so the history is exactly what its report listed.
