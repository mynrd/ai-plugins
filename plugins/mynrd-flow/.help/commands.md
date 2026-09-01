# Command reference

6 slash commands. Everything is local - no command talks to any external service.

For each command:

- **Arg** - what you type after the command name (or "none")
- **Writes files?** - what it puts on disk
- **What it does** - summary
- **Notes** - gotchas, related commands

---

## `/mynrd-intake`

- **Arg:** `[raw text?]` - the request, pasted inline. With no arg it triages what you've already been discussing in the session.
- **Writes files?** One - `.work/<slug>/progress.json` (and `.gitignore` gets a `.work/` entry if it lacks one).
- **What it does:** The front door for anything that hasn't been triaged yet, and the command that starts the state file everything else uses.
  1. **Brief** - restates the request as What / Who-why / Signal / Urgency / **Unknowns**, before asking you anything. Urgency quotes the actual words ("before Friday"), not an interpretation. When the session already knows something about the code (you were debugging, you pasted a stack trace), a **Findings** block keeps it - one line each, ending in the `path:line` that proves it, so `/mynrd-plan` doesn't re-derive it. Intake never goes looking to fill that in, and an empty block is the normal case.
  2. **Existing-work check** - looks in `.work/` for a folder that already covers this, and for a `PLAN.md` in it. Says in one line what it found. That answer decides which routes you get offered.
  3. **Route** - a pick. **Plan found:** build it (`/mynrd-dispatch`) or refine the plan (`/mynrd-plan`). **No plan:** plan it, refine it first, park it, or not actionable.
  4. **`progress.json`** - writes `.work/<slug>/progress.json` holding the brief, any findings, the route you picked, and the `workflow[]` steps. Every later command reads and updates this file. See [progress.md](progress.md).
- **Notes:**
  - **Handing off to `/mynrd-plan` is the normal ending.** Intake decides *what this is*; `/mynrd-plan` decides *what gets built*. The plan route continues inline, carrying the brief so you don't retype it.
  - **Running intake puts the work on rails.** For the rest of that session nothing builds until a plan exists. Ask it to "start the development" with no `PLAN.md` on disk and it declines and points you at `/mynrd-plan` - the brief has no acceptance criteria and no `## Testing` section, so there'd be no definition of done. See [workflow.md](workflow.md).
  - **"Build it" only appears when a `PLAN.md` was found.** It stops and tells you to run `/mynrd-dispatch` - that command edits files, runs tests, and commits, which shouldn't arrive as the tail of a triage.
  - **Park it** leaves the folder with `status: "parked"` and the brief as `BRIEF.md`. Nothing picks it back up automatically - re-run `/mynrd-plan` when you're ready.
  - **Re-triaging existing work won't clobber its state.** If a `progress.json` is already there, intake reports it and leaves it alone.
  - It won't interrogate you. One brief, one existing-work check, one routing question; deeper questions belong to `/mynrd-plan`.

---

## `/mynrd-plan`

- **Arg:** `[.work folder path?]` - optional. With no arg it continues from the folder intake opened this session, or starts fresh.
- **Writes files?** `.work/<slug>/PLAN.md` + fills in `progress.json` (acceptance criteria, test tiers).
- **What it does:** A discussion that ends in a plan. Takes the request (from intake's brief, or cold - just tell it), surfaces gaps via 1-2 clarifying questions per turn, then writes `PLAN.md`: approach, file hints, sequencing, a numbered acceptance-criteria list, and a `## Testing` section naming the tiers and commands. `progress.json` in the same folder gets every AC as `pending` and the test tiers resolved from `## Testing`.
- **Notes:**
  - **No entry requirement.** Run it cold whenever you want - no `/mynrd-intake` first, no existing `.work/` folder. Run cold, it creates the folder itself and marks the `intake` step `skipped`.
  - **It is the only command that writes `PLAN.md`,** which is what `/mynrd-dispatch` builds from. That's why intake sends you here before any build.
  - **Re-running it on existing work re-opens the plan.** Editing the AC remaps the test links in `progress.json`: existing criteria are matched by text and carry their pass/fail state across; any test case whose AC disappeared has its link dropped and named out loud rather than left pointing at a renumbered criterion.

---

## `/mynrd-refine`

- **Arg:** none
- **Writes files?** No - output is a markdown block in the terminal.
- **What it does:** Synthesizes the current conversation (what you've been discussing with Claude in this session) into a formatted **Story / Task / Bug** draft - Description + AC for a Story or Task, Repro Steps + AC for a Bug - with the recommended type pre-flagged.
- **Notes:** Useful when you've been brainstorming and want structured output before deciding what to do next. It doesn't plan or build - paste the draft into `/mynrd-plan` (or wherever you track work) as a separate step. Fits anywhere in the sequence.

---

## `/mynrd-dispatch`

- **Arg:** `[.work folder path?]` - optional. With no arg it finds the one `.work/` folder with unfinished build state. A path ending in `.md` also works.
- **Writes files?** Source edits (via the agents), `progress.json` updates, and local git commits.
- **What it does:** The build loop between planning and your own verification. **It runs the development to completion and reports once** - no per-slice check-ins, no "shall I continue".
  1. Loads `PLAN.md` from the work folder. No plan file → it tells you to run `/mynrd-plan` and stops.
  2. Opens `progress.json` beside it. **It never creates that file** - `/mynrd-intake` does, `/mynrd-plan` fills it in. It resumes from the first step that isn't `done` or `skipped` instead of starting over.
  3. Resolves the test tiers from the plan's `## Testing` section and checks the commands actually exist in the repo.
  4. Decomposes the AC into an ordered task list.
  5. Dispatches each task to the right specialist agent - `mynrd-backend-dev` (.NET / backend), `mynrd-front-dev` (Angular / React), `mynrd-node-dev` (Node / TypeScript), `mynrd-python-dev` (Python), `mynrd-designer` (UI/UX) - handing each the AC text, the plan notes, and the file paths; independent tasks run in parallel. These five ship inside the plugin, so there's nothing to set up.
  6. **Starts the local stack when a check needs it** - the backend host, the UI dev server - without asking you.
  7. Runs the tiers in order - unit → UI - stopping at the first failure, recording every test case and its status.
  8. Loops: diagnose, fix, re-run, then straight on to the next unfinished AC. **Two attempts per distinct failure**, after which that AC is marked blocked and the loop continues with the rest.
  9. Unlocks human verification when everything is green, and hands off with what it built and what to look at.
- **Notes:**
  - **The agents implement exactly the ACs they're handed.** They never run git and never edit `progress.json` or `PLAN.md` - they return a structured report, and `/mynrd-dispatch` transcribes it into `progress.json`. All bookkeeping and all git is the loop's own.
  - **`implemented` is not `pass`.** Code written makes an AC `implemented`; only a named passing test makes it `pass`. An AC no test covers is reported as a gap - "AC #3 is implemented but nothing tests it" - never counted as done.
  - **Some AC can't have a test, and that's expressible.** Each AC carries an `evidence` type - `test` (a named passing case), `live` (a check run against the running app), or `review` (a docs sweep, a config removal - the change itself). `live` and `review` need a `verified` line naming the exact command run or file read.
  - **Human verification unlocks only when** every AC is `pass`, every enabled tier is `pass`, and no round ended blocked. Otherwise it stays `blocked` and the command says what's holding it.
  - **It never asks you to test half-built work.** The run ends one of two ways and nothing else: `Development is done - try it now.` or `Blocked - I need a decision before I can finish.` If proving an AC needs the app clicked through, that's its job, not yours.
  - **Unit and UI are the only tiers.** There's no e2e tier - browser suites (Playwright, Cypress) aren't run here, however installed the repo is. Anything that needs one is on you in the verification step.
  - **It runs your app when it has to, and cleans up after itself.** If something already answers on the port, it uses that and leaves it alone; anything it started itself it kills - process tree and all - before it reports. Your shell may still prompt for the command the first time - that's the Bash permission on your machine, allowlisted once in the repo's `.claude/settings.json`.
  - **One blocker doesn't end the run.** Two failed fix attempts on the same failure marks that AC blocked; the loop keeps building every AC that doesn't depend on it and lists all the blockers together at the end. It stops early only for something it genuinely can't decide - new scope, a missing credential, a schema call.
  - **It never edits a test to make it pass.** If a test itself looks wrong, it leaves it red and says so in the report.
  - **It commits, and only commits.** One commit per task as that task goes green, staging only the files its agents changed - never `git add -A`. **It never pushes**, never amends, never branches: the commits are yours to squash or drop before you push. On a protected branch (`main`, `master`, `dev`, `develop`, `release/*`, `hotfix/*`) it commits nothing all run and says so. A pre-commit hook that rejects it is reported, never bypassed with `--no-verify`.
  - Green loop ≠ done. The next step is you exercising the change, reviewing its commits, then pushing yourself - and closing the work with `/mynrd-verified` when you're satisfied.

---

## `/mynrd-verified`

- **Arg:** `[.work folder path or slug?]` - optional; any free text after it is kept as a one-line note of what you checked. With no arg it lists the folders awaiting verification and asks which.
- **Writes files?** One - the folder's `progress.json`.
- **What it does:** Records that **you** verified the work. Running it is your statement "I exercised this and I'm satisfied" - the command verifies nothing itself. It sets `workflow[human-verification]` to `done` with its `endedAt`, stamps `humanVerification.verifiedAt` (+ your note, if given), and sets the top-level `status` to `verified` - the workflow's terminal state.
- **Notes:**
  - **It only runs on work `/mynrd-dispatch` unlocked** (`human-verification: in_progress`). Anything still building, blocked, or unplanned gets a refusal naming what's holding it - it never overrides the dispatch gate.
  - **One exception:** work whose `build` step was `skipped` (you drove the edits by hand) can be marked verified after a single confirmation, since dispatch never ran to unlock it.
  - Runs no tests, starts nothing, touches no AC or test results, and runs no git writes. If dispatch's commits are still unpushed it says so - pushing stays yours.

---

## `/mynrd-help`

- **Arg:** none
- **Writes files?** No (edits to `.help/` only with your explicit confirmation).
- **What it does:** Loads `.help/INDEX.md`, asks what you need help with, routes to the relevant topic files in `.help/`, synthesizes a focused answer. Does not invoke other commands.
- **Notes:** If your question isn't covered by the help docs, the command will say so directly (rather than guess). It can offer to add the content to the relevant `.help/` file, but only with your confirmation.
