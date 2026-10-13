# Command reference

6 slash commands. Everything is local - no command talks to any external service.

For each command:

- **Arg** - what you type after the command name (or "none")
- **Writes files?** - what it puts on disk
- **What it does** - summary
- **Notes** - gotchas, related commands

---

## `/mynrd-init`

- **Arg:** `[check]` - optional. With no arg it checks, shows what would change, asks once, and writes. `check` reports only.
- **Writes files?** `.claude/settings.local.json` (permission rules), `CLAUDE.local.md` (a managed rules block), and `.gitignore` entries for both plus `.work/`. All personal, all git-ignored.
- **What it does:** Per-project setup so `/mynrd-dispatch` runs without permission prompts. Adds `Bash`, `PowerShell`, `Edit`, `Write`, `WebFetch` to `permissions.allow` and `git push` to `permissions.deny`, and writes the default rules for planning, building, git, and verification - plus the repo's detected unit / UI test commands - into `CLAUDE.local.md` between `<!-- mynrd-flow:start -->` and `<!-- mynrd-flow:end -->`.
- **Notes:**
  - **It merges, never overwrites.** Existing settings keys and rules stay as they are; in `CLAUDE.local.md` only the text between the markers is replaced. Safe to re-run after a plugin update.
  - **One confirmation, always.** It lists the exact rules before writing - the allowlist lets every later session in the project run commands and edit files without asking.
  - **Pushing stays blocked.** The `deny` rule wins over the broad `Bash` allow. Remove those two lines yourself if you want to push from a Claude session.
  - **Restart Claude Code afterwards** - permissions are read when a session starts.
  - It never touches `.claude/settings.json`, `CLAUDE.md`, or `~/.claude/`, never sets `defaultMode` or `bypassPermissions`, and won't overwrite a settings file it can't parse.
  - Claude Code only - Cursor doesn't read `settings.local.json`.

---

## `/mynrd-plan`

- **Arg:** `[raw text | .work folder path]` - optional. Paste the request inline to skip the intro; give a `.work/` folder path to re-plan it; give nothing and it asks what needs planning.
- **Writes files?** `.work/<date>-<slug>/PLAN.md` + `progress.json` (creates it), and `.gitignore` gets a `.work/` entry if it lacks one.
- **What it does:** The front door and the planning step. Checks `.work/` for a folder that already covers the request (and offers to re-plan it), keeps any findings the session already established (one line each with the `path:line` that proves it), restates the request, surfaces gaps via 1-2 clarifying questions per turn, then writes `PLAN.md`: approach, file hints, sequencing, a numbered acceptance-criteria list, and a `## Testing` section naming the tiers and commands. `progress.json` in the same folder gets every AC as `pending`, the test tiers resolved from `## Testing`, and the findings.
- **Notes:**
  - **It never asks what shape the plan takes.** A defect gets the Repro Steps format, everything else gets the Description format, decided from the discussion.
  - **It is the only command that writes `PLAN.md` and creates `progress.json`,** which is what `/mynrd-dispatch` builds from. Nothing builds without them.
  - **It stops after writing.** It never continues into the build - run `/mynrd-dispatch` yourself.
  - **Re-running it on existing work re-opens the plan.** Editing the AC remaps the test links in `progress.json`: existing criteria are matched by text and carry their pass/fail state across; any test case whose AC disappeared has its link dropped and named out loud rather than left pointing at a renumbered criterion. If the build was already `done` and the AC changed, `build` goes back to `pending` and verification is locked again.
  - **Parking is just not planning.** If something is real but not for now, say so; nothing needs to be written.

---

## `/mynrd-refine`

- **Arg:** none
- **Writes files?** No by default - output is a markdown block in the terminal. If a `.work/` folder already exists for the thread it offers to save the draft there as `DRAFT.md`.
- **What it does:** Synthesizes the current conversation (what you've been discussing with Claude in this session) into a formatted draft - Description + AC for work, Repro Steps + AC for a bug. It decides the shape from the discussion and says so; it doesn't ask.
- **Notes:** Useful when you've been brainstorming and want structured output before deciding what to do next. It doesn't plan or build - paste the draft into `/mynrd-plan` (or wherever you track work) as a separate step. Fits anywhere in the sequence.

---

## `/mynrd-dispatch`

- **Arg:** `[slug | .work folder path?]` - optional. With no arg it finds the one `.work/` folder with unfinished build state. A bare slug matches `.work/*-<slug>/`; a path ending in `.md` also works.
- **Writes files?** Source edits (via the agents), `progress.json` updates, `BUILD.md` (the handoff report, `BUILD_02.md` and up on later runs of the same folder), `REVISED_NN.md` for each change you ask for after the handoff in the same conversation, and local git commits.
- **What it does:** The build loop between planning and your own verification. **It runs the development to completion and reports once** - no per-slice check-ins, no "shall I continue".
  1. Loads `PLAN.md` from the work folder. No plan file → it tells you to run `/mynrd-plan` and stops.
  2. Opens `progress.json` beside it. **It never creates that file** - `/mynrd-plan` does. It resumes from the first step that isn't `done` or `skipped` instead of starting over.
  3. Resolves the test tiers from the plan's `## Testing` section and checks the commands actually exist in the repo.
  4. Decomposes the AC into an ordered task list.
  5. Dispatches each task to the right specialist agent - `mynrd-backend-dev` (.NET / backend), `mynrd-front-dev` (Angular / React), `mynrd-node-dev` (Node / TypeScript), `mynrd-python-dev` (Python), `mynrd-designer` (UI/UX) - handing each the AC text, the plan notes, and the file paths; independent tasks run in parallel. These five ship inside the plugin, so there's nothing to set up.
  6. **Starts the local stack when a check needs it** - the backend host, the UI dev server - without asking you.
  7. Runs the tiers in order - unit → UI - stopping at the first failure, recording every test case and its status.
  8. Loops: diagnose, fix, re-run, then straight on to the next unfinished AC. **Two attempts per distinct failure**, after which that AC is marked blocked and the loop continues with the rest.
  9. Unlocks human verification when everything is green, writes the report to `BUILD.md` in the work folder, and hands off with what it built and what to look at. A blocked run writes `BUILD.md` too, opening with the blockers.
- **Notes:**
  - **The agents implement exactly the ACs they're handed.** They never run git and never edit `progress.json` or `PLAN.md` - they return a structured report, and `/mynrd-dispatch` transcribes it into `progress.json`. All bookkeeping and all git is the loop's own.
  - **`implemented` is not `pass`.** Code written makes an AC `implemented`; only a named passing test makes it `pass`. An AC no test covers is reported as a gap - "AC #3 is implemented but nothing tests it" - never counted as done.
  - **Some AC can't have a test, and that's expressible.** Each AC carries an `evidence` type - `test` (a named passing case), `live` (a check run against the running app), or `review` (a docs sweep, a config removal - the change itself). `live` and `review` need a `verified` line naming the exact command run or file read.
  - **Human verification unlocks only when** every AC is `pass`, every enabled tier is `pass`, and no round ended blocked. Otherwise it stays `blocked` and the command says what's holding it.
  - **It never asks you to test half-built work.** The run ends one of two ways and nothing else: `Development is done - try it now.` or `Blocked - I need a decision before I can finish.` If proving an AC needs the app clicked through, that's its job, not yours.
  - **Unit and UI are the only tiers.** There's no e2e tier - browser suites (Playwright, Cypress) aren't run here, however installed the repo is. Anything that needs one is on you in the verification step.
  - **It runs your app when it has to, and cleans up after itself.** If something already answers on the port, it uses that and leaves it alone; anything it started itself it kills - process tree and all - before it reports. Your shell may still prompt for the command the first time - that's the Bash permission on your machine, allowlisted for good by `/mynrd-init`.
  - **One blocker doesn't end the run.** Two failed fix attempts on the same failure marks that AC blocked; the loop keeps building every AC that doesn't depend on it and lists all the blockers together at the end. It stops early only for something it genuinely can't decide - new scope, a missing credential, a schema call.
  - **It never edits a test to make it pass.** If a test itself looks wrong, it leaves it red and says so in the report.
  - **Changes you ask for after the handoff get written down.** Still in the dispatch conversation, once the build is green, every request that changes files ends with a `REVISED_01.md`, `REVISED_02.md`, ... in the work folder: what you asked, which files changed and why, which tests ran, and whether it was committed (it isn't unless you say so). Questions and declined requests get no file. A request while the build is `blocked` is the loop resuming, not a revision - that ends in the next `BUILD_NN.md`.
  - **It commits, and only commits.** One commit per task as that task goes green, staging only the files its agents changed - never `git add -A`. **It never pushes**, never amends, never branches: the commits are yours to squash or drop before you push. On a protected branch (`main`, `master`, `dev`, `develop`, `release/*`, `hotfix/*`) it commits nothing all run and says so. A pre-commit hook that rejects it is reported, never bypassed with `--no-verify`.
  - Green loop ≠ done. The next step is you exercising the change, reviewing its commits, then pushing yourself - and closing the work with `/mynrd-verified` when you're satisfied.

---

## `/mynrd-verified`

- **Arg:** `[slug | .work folder path?]` - optional; any free text after it is kept as a one-line note of what you checked. With no arg it lists the folders awaiting verification and asks which.
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
