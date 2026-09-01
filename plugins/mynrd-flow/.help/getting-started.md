# Getting started

You're using **mynrd-flow**, a personal workflow plugin for Claude Code - 6 slash commands that take a raw request from "someone asked for this" to "built and tested", entirely on your machine. No external services, no boards, no credentials. The only things it ever writes are files in your repo (`.work/` state + the source edits you asked for) and local git commits.

---

## Install

```bash
claude plugin marketplace add https://github.com/mynrd/ai-plugins.git
claude plugin install mynrd-flow@mynrd-ai-plugins
```

That's it. **No setup step, no env vars, no sign-in.** The five specialist agents ship inside the plugin, so there's nothing else to configure.

---

## The mental model in 30 seconds

Every piece of work moves through the same sequence:

```text
/mynrd-intake  →  /mynrd-plan  →  /mynrd-dispatch  →  you verify
   triage           PLAN.md         build loop
```

- **Intake** turns a raw request into a short brief and opens the state file (`.work/<slug>/progress.json`).
- **Plan** is a discussion that ends in a `PLAN.md` - approach, acceptance criteria, a `## Testing` section.
- **Dispatch** builds the plan to completion: specialist agents write the code, tests run, `progress.json` records everything.
- **You verify** - green loop ≠ done. You exercise the change yourself before pushing anything, then `/mynrd-verified` records that you did.

`/mynrd-refine` (format a discussion into a Story/Task/Bug draft) and `/mynrd-help` (this help system) fit anywhere in that sequence.

Full detail in [workflow.md](workflow.md); every command in [commands.md](commands.md).

---

## Your first run

### Step 1 - Got a request? Start at the front door

```
/mynrd-intake <paste the request>
```

It writes a short brief of what you were asked for, checks `.work/` for an existing folder that already covers it, and routes you to the next step - usually `/mynrd-plan`. It also creates `.work/<slug>/progress.json`, the state file every later command reads and updates.

If you already know what you want and don't need the triage, run `/mynrd-plan` cold - no intake required.

### Step 2 - Plan it

```
/mynrd-plan
```

Tell it what you're building. It surfaces gaps, asks 1-2 clarifying questions per turn, then writes `.work/<slug>/PLAN.md` and fills `progress.json` with the acceptance criteria and test tiers. This is the only command that writes `PLAN.md`, and nothing builds without one.

### Step 3 - Let the build loop do it

```
/mynrd-dispatch
```

Reads `PLAN.md`, sends the work to the right specialist agents, starts your local stack when a check needs the app running, and runs the test tiers the plan names (unit → UI), fixing and re-running until the whole plan is done. It commits each task as it goes green - **never pushes** - and reports once at the end with what it built and what to look at.

### Step 4 - Verify it yourself

Green isn't done: exercise the change, review the commits, then push when you're satisfied. Then close it out:

```
/mynrd-verified .work/<slug>
```

It marks the `human-verification` step `done` and the work `verified` in `progress.json` - add free text after the path to keep a one-line note of what you checked.

---

## What to read next

- [commands.md](commands.md) - every command and what it does, in detail
- [workflow.md](workflow.md) - the sequence, why it's enforced, how to read where you are
- [progress.md](progress.md) - the `.work/` folder and `progress.json`
- [faq.md](faq.md) - common questions

If you're not sure what to read, type `/mynrd-help` and ask your question directly.

---

## Things to know upfront

- **Everything is local.** No command talks to any external service. State lives in `.work/` (gitignored), plans live in `PLAN.md`, and the only side effects are file edits and local commits.
- **Nothing builds without a plan.** Ask to "just build it" with no `PLAN.md` on disk and `/mynrd-dispatch` declines and points you at `/mynrd-plan` - a brief has no acceptance criteria, so there'd be no definition of done.
- **The specialist agents are on rails.** `mynrd-backend-dev`, `mynrd-front-dev`, `mynrd-node-dev`, `mynrd-python-dev`, and `mynrd-designer` implement exactly the ACs they're handed. They never run git and never edit `progress.json` or `PLAN.md` - that bookkeeping belongs to `/mynrd-dispatch`.
- **Dispatch commits, and only commits.** Never pushes, never amends, never branches. The commits are yours to squash or drop before you push.
- **`/mynrd-refine` and `/mynrd-help` write nothing.** Run them anytime.
