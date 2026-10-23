# FAQ - common questions

Anticipated questions from real-world use. Grouped by theme.

---

## Choosing the right command

### "Where do I start?"

`/mynrd-plan`, always. Paste the request, the bug report, or describe what you noticed. It checks `.work/` for existing work on it, discusses it, and writes the `PLAN.md` and `progress.json` that `/mynrd-dispatch` builds from.

### "When do I use `/mynrd-refine`?"

When you've been **brainstorming with Claude in this session** and want a structured draft to review before deciding what to do. Produces a formatted draft (Description + AC, or Repro Steps + AC for a bug) - no files written unless you ask. Useful as a checkpoint before `/mynrd-plan`.

### "What's the difference between `/mynrd-refine` and `/mynrd-plan`?"

`/mynrd-refine` formats what's already been said into a draft and stops. `/mynrd-plan` drives a discussion to a decision and writes `PLAN.md` + fills `progress.json` - it's the gateway to the build. Refine is a snapshot; plan is a commitment.

---

## Workflow situations

### "Something urgent came in. How do I capture and build it today?"

Two commands, in sequence:

1. `/mynrd-plan <paste the request>` → discuss, write `PLAN.md` with AC and `## Testing`
2. `/mynrd-dispatch` → the build loop runs to completion and reports once

Then verify the change yourself and push. See [workflow.md](workflow.md).

### "I asked it to just build the thing and it refused"

Working as designed. Nothing builds until a `PLAN.md` with acceptance criteria exists - a discussion has no definition of done. Run `/mynrd-plan`; it takes a few minutes and the build loop needs its output anyway. See [workflow.md](workflow.md) § "Nothing builds without a plan".

### "A dispatch run got interrupted. Do I start over?"

No. Re-run `/mynrd-dispatch` - it resumes from the first `workflow[]` step that isn't `done` or `skipped`, and from the first unfinished AC. `progress.json` is the memory; that's what it's for.

### "Dispatch finished but marked an AC blocked. Now what?"

Read the report (and `runs[]` in `progress.json`) - it names the failure and what was tried. The two-attempt limit exists so the loop doesn't spin on a bad guess. Typical next moves: fix the underlying issue yourself and re-run `/mynrd-dispatch`, or re-open the plan with `/mynrd-plan` if the AC itself was wrong.

### "Dispatch finished green - how do I mark the work as actually done?"

Verify it yourself first (exercise the change, review the commits, push), then:

```
/mynrd-verified <slug> <optional one-line note of what you checked>
```

It closes the `human-verification` step and sets `status: verified` in `progress.json`. Without it the file sits at `human-verification: in_progress` forever - no other command writes that closing stamp. Run with no argument, it lists the folders awaiting verification and asks which.

### "I want to shelve this for now"

Don't plan it. Nothing needs to be written for work you're not starting. If you've already got a `.work/` folder for it, leave it at `planned`; `/mynrd-dispatch` only picks up folders you point it at or that have an unfinished build.

### "Can I plan multiple pieces of work in one `/mynrd-plan` invocation?"

No. One invocation = one `.work/` folder = one plan. Run it once per piece of work.

---

## The build loop

### "Which agent builds what?"

`/mynrd-dispatch` picks per task: `mynrd-backend-dev` (.NET / backend), `mynrd-front-dev` (Angular / React), `mynrd-node-dev` (Node / TypeScript), `mynrd-python-dev` (Python), `mynrd-designer` (UI/UX), `mynrd-docs-writer` (docs). You don't choose - the plan's file hints and the AC decide. All six ship inside the plugin.

### "Can the agents commit their own work?"

No. Agents never run git and never edit `progress.json` or `PLAN.md`. `/mynrd-dispatch` does the committing - one commit per task as it goes green, staging only the files its agents changed. It never pushes.

### "Why didn't dispatch run my Playwright suite?"

Unit and UI are the only tiers. Browser e2e suites aren't run by the loop, however installed the repo is - that's part of your verification step.

### "The loop says done but an AC only shows `implemented`"

Then it's not done and the report said so - `implemented` means code written, `pass` means evidence produced (a named test, a live check, or a review line). An AC nothing tests is reported as a gap. See [progress.md](progress.md).

---

## Setup and install

### "Where do I install this plugin?"

```bash
claude plugin marketplace add https://github.com/mynrd/ai-plugins.git
claude plugin install mynrd-flow@mynrd-ai-plugins
```

No env vars, no credentials, no external services. Run `/mynrd-init` once per project to stop the permission prompts during `/mynrd-dispatch`.

### "I edited the source - how do I get the changes into my editor?"

```bash
claude plugin marketplace update mynrd-ai-plugins
claude plugin update mynrd-flow@mynrd-ai-plugins
```

Both commands needed - the marketplace metadata and plugin payload are cached separately.

---

## Where to find authoritative info

| Question type | Source |
|---|---|
| What does a specific command do | [commands.md](commands.md) (this folder) |
| The sequence and why it's enforced | [workflow.md](workflow.md) |
| The state file | [progress.md](progress.md) |
| Full step-by-step flow of a command | `commands/<command-name>.md` |
