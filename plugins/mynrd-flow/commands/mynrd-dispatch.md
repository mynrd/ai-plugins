---
name: mynrd-dispatch
description: Run the build loop for planned work to completion — dispatch implementation to the right specialist agents, start the local stack when a check needs it, run the test tiers named in the plan (unit / UI), and keep looping across every AC until the development is done or genuinely blocked. Records every AC and every test case in the work folder's progress.json and writes the handoff report to BUILD.md beside it; post-handoff changes in the same conversation get REVISED_NN.md. Fully local — it reads a plan, edits code, runs tests, updates the work folder.
---

# /mynrd-dispatch

The build loop between planning and human verification. Reads the plan, implements against it, runs the test tiers, loops on failure, and records all state in `progress.json` — so any later session can see what's done, what's pending, and which AC actually has a passing test behind it.

**One git operation, and only one: `git commit`** (Step 7b). It commits a task's work once that task is green, on the current feature branch, staging only the files it changed. **It never pushes** — pushing is the developer's, always, and every other git verb stays off limits: no branch, no checkout, no merge, no rebase, no amend, no reset, no tag, no `--no-verify`. Read-only inspection (`status`, `diff`, `log`) is free.

---

## What this command is for

**It runs the development to completion and then hands off.** One invocation takes the plan from wherever it is to every AC terminal — implemented, tested, and recorded — and ends with *"development is done, go try it"* plus notes. It does not stop halfway to ask whether to keep going, which task to pick up next, whether to start a server, or whether to run the tests. Those are its decisions.

Two consequences that shape every step below:

- **You may start local dev processes without asking** (Step 5b) — the backend host, the UI dev server, a local database container. A check that needs the app running is a check you perform, not a request you hand to the user.
- **You commit each task as it finishes** (Step 7b), so a long run leaves reviewable history instead of one enormous diff. Commits only — never a push.
- **A blocker blocks one AC, not the command** (Step 7). You take everything else as far as it goes, then report the blockers together at the end.

The only full stop before the plan is finished is a **real blocker** — a decision the plan doesn't cover, scope that outgrew the AC, or infrastructure you cannot bring up yourself. Everything else is work.

### The end-of-turn invariant

**`workflow[build]` is never `in_progress` when your turn ends.** It is `in_progress` only while you are actively working inside the turn; the turn itself ends in exactly one of two states, and there is no third:

| End state | `workflow[build]` | `human-verification` | `humanVerification.unlocked` | The message opens with |
| --- | --- | --- | --- | --- |
| Finished | `done` | `in_progress` | `true` | `Development is done — try it now.` |
| Blocked | `blocked` | `pending` | `false` | `Blocked — I need a decision before I can finish.` |

**Human verification does not start until the build is finished.** `workflow[human-verification]` moves off `pending` only in the first row — build `done` and everything green. While build is `in_progress` or `blocked`, the human-verification step has not begun and you must not behave as though it has.

**Therefore: never invite the user to test while the build is unfinished.** Not "have a look at this while I carry on", not "try the API and I'll do the docs next", not a slice-by-slice demo. A turn that ends with `build: in_progress` and a message saying "try it" is the specific failure this invariant exists to prevent — it reads as a handoff the state file flatly contradicts, and the user goes and exercises half-built work.

**If you need the app exercised to prove an AC, that is your job, not the user's** — it's `live` evidence (Step 6), and Step 5b starts the stack for you. Needing a browser click is not a reason to hand off early; it's a reason to run it yourself and write down what you saw.

---

## Argument

| Given | Meaning |
| --- | --- |
| *(empty)* | Resolve the work folder: the slug in the branch (`feature/e2e-standard` → `.work/*-e2e-standard/`), else the single `.work/*/` folder whose `progress.json` has an unfinished `workflow[build]`. |
| `<slug>` | Use `.work/*-<slug>/` — suffix match, per `${CLAUDE_PLUGIN_ROOT}/PROGRESS-SCHEMA.md` § Folder. |
| a path to a `.work/` folder | Use that folder. |
| a path ending in `.md` | Use that file as the plan, and the `progress.json` beside it. |

**More than one candidate folder, or none:** list what you found and ask once. Never guess from the directory name, and never pick the most recently modified one silently.

---

## Step 1 — Load the plan

The work folder is resolved from the argument above; `PLAN.md` lives in it, and `progress.json`'s `plan` field names it.

**Missing?** Say exactly this and stop:

> No `PLAN.md` in `<folder>`. Run `/mynrd-plan` to write one.

Never invent one and proceed.

Extract: **Acceptance Criteria** (the exit condition), **Implementation notes** (approach, files, sequencing), **Testing** (which tiers run).

---

## Step 2 — Open `progress.json`

State lives beside the plan, in the same folder: `<plan folder>/progress.json`. Single source of truth.

**This command never creates it.** `/mynrd-plan` creates it alongside `PLAN.md`. Dispatch opens what's already there and owns the build-side fields only.

**Missing?** Say exactly this and stop:

> No `progress.json` in `<folder>`. It's created by `/mynrd-plan` — run it.

**Exists:** load it, report where things stand in three lines, and **resume from the first workflow step that is neither `done` nor `skipped`**. Don't redo finished work — it burns tokens and can undo hand edits made in between. A `blocked` build you're resuming goes back to `in_progress` with a fresh `startedAt` and its stale `endedAt` cleared (the timestamp rule in `PROGRESS-SCHEMA.md`).

Two things to check before doing anything else:

- **`workflow[plan]` is not `done`** — there's no plan to build from. Tell the user to run `/mynrd-plan` and stop.
- **`acceptanceCriteria[]` is empty** — same problem; the plan exists but nothing was decomposed into AC. Say so and stop rather than inventing criteria.

**Neither is worked around.** Not by planning inline in this command, and not by inferring criteria from the code or the branch name. `/mynrd-plan` is the only command that writes `PLAN.md`, and a build with no definition of done has no way to report one honestly.

### Schema

The full schema, folder rules, and status vocabularies are defined once, in `${CLAUDE_PLUGIN_ROOT}/PROGRESS-SCHEMA.md`. Read that exact path with the Read tool — never search for it (`find`, `ls ~/.claude`, a glob): the path is already resolved, and a search outside the project triggers a permission prompt. Don't restate them and don't diverge from them. The fields **this command owns** look like this mid-loop:

```json
{
  "status": "in_progress",
  "updated": "2026-08-14T15:42:00+08:00",

  "workflow": [
    { "step": "plan",               "status": "done",
      "startedAt": "2026-08-14T10:01:00+08:00", "endedAt": "2026-08-14T10:40:00+08:00" },
    { "step": "build",              "status": "in_progress",
      "startedAt": "2026-08-14T15:02:00+08:00" },
    { "step": "human-verification", "status": "pending" }
  ],

  "tasks": [
    { "slice": "test-data-host", "ac": [1, 2],
      "state": "committed", "commits": ["853ecc3"],
      "startedAt": "2026-08-14T15:02:10+08:00", "endedAt": "2026-08-14T15:28:44+08:00" },
    { "slice": "harness-lifecycle", "ac": [3],
      "state": "in_progress", "commits": [],
      "startedAt": "2026-08-14T15:30:02+08:00" }
  ],

  "acceptanceCriteria": [
    { "id": 1, "text": "PDFs with > 10 pages export successfully",
      "status": "pass", "task": "test-data-host",
      "implementedIn": ["server/pdf/exporter.py:render_pages"] },
    { "id": 2, "text": "PageBufferOverflow no longer occurs for any invoice",
      "status": "fail", "task": "test-data-host",
      "implementedIn": ["server/pdf/exporter.py:_flush_chunk"] },
    { "id": 3, "text": "Large sample invoice round-trips",
      "status": "implemented", "task": "harness-lifecycle",
      "implementedIn": ["server/pdf/exporter.py"] }
  ],

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
    "ui":  { "enabled": false, "reason": "no frontend change in plan",
             "status": "skipped", "cases": [] }
  },

  "humanVerification": { "unlocked": false, "unlockedAt": null },

  "runs": [
    { "startedAt": "2026-08-14T15:30:02+08:00",
      "endedAt": "2026-08-14T15:41:20+08:00",
      "tasks": ["test-data-host"],
      "agents": [ { "agent": "mynrd-python-dev", "task": "chunk-guard in exporter",
                    "ac": [1, 2], "files": ["server/pdf/exporter.py"] } ],
      "unit": { "command": "pytest tests/pdf", "passed": 1, "failed": 1 },
      "outcome": "looping",
      "notes": "off-by-one in the final chunk flush" }
  ]
}
```

**Leave everything else alone.** `findings`, `slug`, `plan`, `created`, and the `workflow` steps other commands own are read-only here — carry them through every rewrite untouched. Dropping a field because this command doesn't use it destroys another stage's state. `tasks[].slice` / `title` / `ac` belong to whoever wrote them; only `state`, `commits[]`, and the `startedAt` / `endedAt` stamps are yours.

**`implemented` and `pass` are different claims.** `implemented` = the code is written. `pass` = the AC's evidence exists and is green. Only Step 6 promotes an AC to `pass`.

**Not every AC is provable by a test, and pretending otherwise strands finished work.** `acceptanceCriteria[].evidence` says which kind an AC takes — `test` (default), `live` (a check you ran against the running app), `review` (the change is the evidence: a docs sweep, a config removal, a command file that now exists). `live` and `review` require a `verified` string naming exactly what you ran or read. Full definition in `PROGRESS-SCHEMA.md`; the promotion rules are Step 6.

### Both tiers have one shape

`unit` and `ui` are identical objects — full shape (`lastRun`, `reason`, per-case `durationMs` / `message`, the `truncated` marker for large suites) in `PROGRESS-SCHEMA.md` § "`tests` — the two tiers, one shape". The two rules the loop lives by:

- **Tier `status` is derived, never hand-set:** `fail` if any case failed · `pass` if there's ≥1 case and none failed · `not_run` if `cases` is empty · `skipped` if the tier is disabled.
- **The AC↔test link lives on the case only** (`ac: [1, 2]`). An AC's `pass` is computed from the cases pointing at it. One direction, so nothing drifts.

### Write rules

- **Write it with the Write or Edit tool — never through the shell.** No helper script, no heredoc or PowerShell here-string, no `python -c` / `node -e` / `jq` / `Set-Content` / `ConvertTo-Json` rewriting the file. A shell command carrying an inline script is one the harness can't analyze, so it stops and asks the user on every single write — and this file is written dozens of times a build.
- **Rewrite the whole file on every transition** — step or task started, agent dispatched, agent returned, tier run, round closed, step or task ended. It's small; a stale `updated` is worse than the write.
- **Every start and end is stamped in the write that caused it.** `workflow[]` steps, `tasks[]`, and `runs[]` all carry `startedAt` / `endedAt` per `PROGRESS-SCHEMA.md` § "Every step records when it started and when it ended" — written at the moment of the transition, never back-filled at the end of the turn.
- `updated` is local ISO-8601 with offset.
- **Never write a status better than the evidence.** A tier is `pass` only if its command exited 0 in this session. An AC is `pass` only if a passing case names it. This file outlives the conversation — an optimistic status here is a lie with a long tail.
- `.gitignore` must cover `.work/` before the first write (same rule as the plan folder, `commands/mynrd-plan.md` § "The `.work` plan folder").

---

## Step 3 — Resolve the test tiers

The plan's `## Testing` section decides what runs, and `/mynrd-plan` already wrote that decision into `tests.*.enabled` + `command`. Verify it against the repo (below), correct it where it's stale, and record the outcome in `tests` immediately — including tiers that won't run, and why. Set `workflow[build] = in_progress` here, stamping its `startedAt` in the same write; it stays that way until Step 8. This write also fills the top-level `branch` with the current branch name (`git branch --show-current`) — dispatch owns that field and nothing earlier knows it.

`enabled: null` means `/mynrd-plan` never resolved that tier (an older file, or a plan written by hand). Resolve it now from the plan text and the repo, and say which tiers you filled in.

| Tier | Runs when | Typical command |
| --- | --- | --- |
| **Unit** | plan says `Unit: yes` | `dotnet test`, `pytest`, `npm test` |
| **UI** | plan says `UI: yes` | `ng test`, `npm run test:ui`, `vitest` |

- **These two tiers are the whole loop.** There is no e2e tier — browser suites (Playwright, Cypress) are not run here, however installed the repo is. Work needing one is verified by the human in the stage after this.
- **Verify each enabled command exists** (`*.csproj` / `package.json` scripts / `pyproject.toml`) before looping. Plans written weeks ago name scripts that were since renamed. Fix it, record the corrected command, say so in one line.
- **No runnable command → `skipped` with a `reason`,** never a silent drop. `Unit: yes` with no test project means the loop can't verify backend work; say so up front.
- **No `Testing` section** (older plan): infer from the repo, state the inference, record it as the `reason`.

---

## Step 4 — Decompose

**If `tasks[]` has entries, that is the decomposition** — the slices the plan already cut, each owning a set of AC. Build them one at a time, in dependency order, and each one ends at Step 7b with a commit. Don't re-cut the breakdown; a task whose `ac` list looks wrong is a plan problem to report, not to silently re-slice.

**If `tasks[]` is empty** (a lone Task or Bug), decompose yourself: one task per AC, split further where the Implementation notes call for it, grouped into slices that each make a sensible commit. Record each slice as a `tasks[]` entry with a `slice` handle so the commits have something to hang off. A single small unit of work is one slice and one commit at the end — don't manufacture five.

Either way, mirror it with `TodoWrite` so progress is visible live, and order by dependency rather than AC number: schema before the code using it, endpoint before the frontend calling it.

`acceptanceCriteria[]` already exists — `/mynrd-plan` wrote it. Decomposing does not rewrite that array; it produces the task list you dispatch from. If an AC is missing or wrong, that's a plan problem: build the AC that are sound, mark that one blocked with the reason, and raise it in the final report rather than editing the AC here or stopping the run over it.

---

## Step 5 — Dispatch

| Work | Agent |
| --- | --- |
| .NET / ASP.NET Core / EF Core / SQL / Azure | `mynrd-backend-dev` |
| Angular / AngularJS / React / Ionic | `mynrd-front-dev` |
| Node / TypeScript services, CLIs, tooling | `mynrd-node-dev` |
| Python services, scripts, data | `mynrd-python-dev` |
| Visual design, component styling, design systems | `mynrd-designer` |
| Docs - README, help pages, runbooks, decision records, doc comments | `mynrd-docs-writer` |
| Small obvious single-file edits | do it yourself |

All six ship with the plugin (`agents/`), so they exist on every machine that installed it — never dispatch to an unprefixed `backend-dev` / `designer` / etc., which are whatever that developer happens to have in their own `~/.claude/agents` and are absent on a fresh install. A project's own agent under `.claude/agents/` wins over the table when it is compatible: it covers the work's stack and ends with a `## Result` block you can transcribe. Otherwise use the `mynrd-*` agent and say in one line why the project agent was skipped.

- **Independent tasks go out in parallel**, one message. Tasks touching the same files run sequentially — two agents in one file is a merge conflict you pay for later.
- **Hand each agent the plan text it needs** — its AC items, the relevant notes, the file paths. An agent rediscovering the plan wastes a context.
- **Update `progress.json` around each dispatch:** when the task goes out, its `tasks[]` entry → `in_progress` with `startedAt` stamped and its AC → `in_progress`; when the agent returns, AC → `implemented` with `implementedIn` filled. Never `pass` here, and `endedAt` waits for `built` / `blocked` / `committed`.
- **Each agent ends with a `## Result` block** — AC coverage, files changed, tests added with the AC each covers, test command, blockers. `mynrd-docs-writer` reports a `Verified` line instead of tests; its ACs carry `evidence: review`, so you read what that line names before promoting. Transcribe it; don't re-derive it by reading the diff. The agents report `implemented` or `blocked` and never `pass`, because only Step 6 promotes an AC to `pass`.

**Guide the agent; don't hand it the AC and hope.** Each dispatch message carries: the exact AC text it owns, the implementation notes and file paths from the plan, the conventions it must follow (the patterns already in the repo, the test project it writes into), what is explicitly out of its slice, and — when a live check is part of the AC — the URL the stack is already answering on (Step 5b), so it verifies instead of reporting infra as a blocker. An agent that has to rediscover the plan spends its context on rediscovery.

**An agent blocked on infrastructure is your problem, not the user's.** `mynrd-backend-dev`, `mynrd-front-dev`, and `mynrd-designer` are told to stop and report when a database, API, or dev server isn't running — that contract is deliberate, because a slice worker shouldn't own a process that outlives it. When one comes back with that blocker: run Step 5b, bring the thing up, and **re-dispatch that one task with the URL**. Don't relay "the API isn't running" to the user.

---

## Step 5b — Run the stack yourself when something needs it

Some checks can't be made from source: an endpoint that has to answer, a host that has to boot without a DI error, a UI tier that needs its API up, a migration that has to apply. **Start the app yourself, without asking.** Telling the user to open another terminal and come back is how this loop stalls on work that was otherwise fine, and it is exactly the behavior this step exists to remove.

**Probe before you start.** Hit the health or root URL, or check the port. Something already answering is the user's own session — use it, record `"startedByDispatch": false`, and never stop it.

**Resolving the command,** in order: the plan's `## Testing` section or implementation notes → the repo (`*.AppHost/` → `aspire run` · `package.json` `start` / `serve` / `dev` → `npm run <script>` · an API `.csproj` → `dotnet run --project <path>` · a documented `docker compose` local stack → `docker compose up -d`). Say in one line which you picked and why. **Nothing identifiable → that is a real blocker** (Step 7), not a guess to try.

Rules that keep this from wedging the loop:

- **Background, never foreground.** A dev server doesn't exit; a foreground run hangs the session until it's killed.
- **Readiness is a poll, not a sleep.** Poll the probe until it answers — ceiling 180s for .NET / Aspire, 120s for a node dev server. On timeout, tail the log, report what it actually said, and treat it as a failure under the two-attempt rule. Never assume it came up.
- **Stop what you started, at every exit** — green, blocked, or interrupted. Kill the **process tree** (`taskkill /T /F /PID <pid>` on Windows; the process group on POSIX), or the port stays bound and the next round can't rebind it. Never stop a process you found already running.
- **Local only.** Local dev commands against local configuration. Never start anything pointed at a deployed environment, never run a migration or a publish against a remote connection string, never `azd up` / `az deployment` / `docker push`. That's outside this loop entirely.
- **A dependency the plan says the local stack needs** (a migration, a seed script, a container) is yours to run under the same rules.

Record it in the round's `runs[]` entry:

```json
"services": [
  { "name": "testdata-api", "command": "aspire run",
    "url": "http://localhost:17178", "startedByDispatch": true,
    "ready": true, "stoppedAt": "2026-08-15T19:20:11+08:00" }
]
```

**Keep every shell command plain, here and everywhere in the loop — Bash and PowerShell alike.** One command per shell call, typed the way a person would: `npm test`, `git status`, `dotnet build`. No heredocs or here-strings (`@'…'@`), no inline scripts, no shell variables or `$(…)`, no reading files with `cat` / `sed` / `head` / `Get-Content` / `Select-String` (that's the Read tool), no writing them with `Set-Content` / `Out-File` / `>` (that's Write or Edit), no chaining a read onto a write with `;`, `&&`, or a pipeline. The allowlist covers a command the harness can parse; one it can't parse asks the user no matter what is allowlisted. Say the same to every agent you dispatch.

**The harness may still prompt for the shell command itself.** That's a Bash permission on the user's machine, not this command asking your permission — `/mynrd-init` allowlists it in the target repo's `.claude/settings.local.json`; point at it once in the report if the run was prompted.

---

## Step 6 — Test

Run enabled tiers in order — **unit → UI** — stopping at the first failing tier. No point running the UI suite over a red unit suite.

Per tier, write back: `status`, `lastRun`, and one `cases[]` entry per test with its `status`, the `ac` it covers, and for failures the **actual assertion text**, not a paraphrase.

Then reconcile the AC, by its `evidence` type:

| `evidence` | Promotes to `pass` when | Never promotes on |
| --- | --- | --- |
| `test` (default) | a passing case in `cases[]` names it in `ac` | a failing case → `fail`; no case at all → stays `implemented` |
| `live` | you ran a check against the running app **this session** and wrote what you ran into `verified` | a `verified` string inherited from an earlier session, or one that says "works" without naming a command |
| `review` | you read the changed artifact **this session** and `verified` names the file and what you confirmed in it | "docs updated" — that's the task, not the evidence |

- **An AC whose evidence is `test` and has no case stays `implemented`** and is reported out loud: *"AC #3 is implemented but no test covers it."* Silently calling that green is the exact dishonesty this file exists to stop.
- **Before leaving it stranded, ask what kind of AC it actually is.** "CLAUDE.md no longer describes e2e as required" cannot have a unit test — it's `review`, and it's proved by a grep whose output you paste into `verified`. Set `evidence` yourself when the plan didn't, say which AC you re-typed and why, and hold the same bar: a specific command and its result, or it isn't evidence.
- **`live` evidence usually means Step 5b.** Start the stack, exercise the thing, record the actual response — *"POST /testdata/seed returned runId 41; the row exists in `__TestDataRunItems`"* — not *"the endpoint works"*.

---

## Step 7 — Loop until every AC is terminal

Failing tier → diagnose → fix → re-run that tier → continue forward. Append a `runs[]` entry per round — with `startedAt` when the round opens, `endedAt` when it closes: agents, services started, test result, one line on what was actually wrong.

**The exit condition is the whole plan, not the first slice that goes green.** A slice landing means you pick up the next unfinished AC immediately, in the same turn — decompose it, dispatch it, test it. Keep going until every AC is `pass`, `fail`, or `blocked`, and no `pending` or `implemented` one is left that you could have moved. A build that stops with eight AC untouched because one slice finished is the failure this step is written against.

**Never end a turn to ask a question you can answer.** Specifically, don't ask: whether to continue · which task to take next · whether to start a server (Step 5b) · whether to run the tests · whether to fix a failure you understand · whether to keep going after a blocked AC. Don't post a mid-loop summary and wait. The user is expecting one message at the end, not a checkpoint per slice.

Two hard limits, unchanged:

1. **Two fix attempts per distinct failure.** Still red after two? That **AC** is blocked — not the command. Record the failure output, what you tried, and your read on the cause, then **carry on with every remaining AC that doesn't depend on it.** Global one-guess-limit rule; a third guess is thrashing, but so is abandoning nine AC over one.
2. **Never edit a test to make it pass.** That converts a red build into a silent bug. If the test itself is wrong, show the assertion, leave it red, and say so in the final report.

**Real blockers — the only reasons to stop before the plan is finished:**

- the fix needs a decision the plan doesn't cover (schema, API contract, new dependency, auth model);
- the work outgrew the AC (new scope is a new `/mynrd-plan` item);
- infrastructure you cannot bring up yourself — a service that won't boot after two attempts, a credential you don't have, something remote that's down. **Not** "the API isn't running": that one is Step 5b's job.
- the plan and the code disagree badly enough that continuing would build the wrong thing.

Even then, **finish everything not downstream of the blocker first.** Stop when nothing remains that isn't blocked or waiting on a blocked thing — then report all of them at once, in Step 8's report, with honest state written first.

---

## Step 7b — Commit the task

**A task that's green gets committed before you start the next one.** A five-task story that runs for an hour and lands as one 60-file diff is unreviewable and un-revertable; five commits are both. This is the **only** git verb this command has.

**Commit when, exactly:** every AC in that task's `ac` list is `pass`, and the enabled tiers are green as of that round. Never mid-red, never on `implemented`-but-untested AC. Then `tasks[].state = "committed"`, stamp the task's `endedAt` (unless it already got one at `built` or `blocked` — the first terminal state owns it), append the short SHA to `commits[]`, and move on.

**With no `tasks[]` breakdown** — a lone Task or Bug — it's one commit at the end of the run, when the loop goes green. Same rules, same message shape.

**Before the first commit of the run, check the branch.** `main`, `master`, `dev`, `develop`, `release/*`, `hotfix/*` are off limits. On one of those: **commit nothing for the whole run**, keep building and testing, and say so in the final report — the developer branches and commits themselves. Never cut a branch to get around it; branching is the developer's.

**Staging is explicit.** `git add <path> …` naming exactly the files that task's agents reported changing, plus new files they created. **Never `git add -A`, never `git add .`** — the working tree may hold edits that aren't yours, and sweeping them into a commit is how someone loses work they hadn't finished. Run `git status --short` first; anything modified that no agent claimed is left unstaged and named in the report.

**Message shape:**

```text
<type>(<scope>): <what changed, imperative>

- <one line per AC delivered>
- <one line per AC delivered>
```

`type` is the repo's own convention (`feat` / `fix` / `chore` / `docs` / `refactor` — read `git log` and match it, don't impose one).

**Hard limits — these are not negotiable:**

- **Never push.** Not after the last commit, not "so a PR can be created". Pushing is the developer's call, always.
- **Never amend, reset, rebase, revert, cherry-pick, stash, tag, or checkout.** The developer may well rewrite these commits after reading them — that's expected, and it's why `commits[]` records what you did rather than what the branch now looks like.
- **Never `--no-verify`.** A pre-commit hook that rejects the commit is a real failure: report the hook's output, leave the task `built`, and carry on with the next task. Don't work around the hook.
- **Never commit `.work/`** — it's gitignored, and if it isn't, fix `.gitignore` rather than committing state.
- **A commit that fails** (hook, conflict, nothing staged) leaves `tasks[].state = "built"` and an honest note. It never blocks the build loop; uncommitted green work is still green work.

---

## Step 8 — Exit: unlock human verification

Unlocks only when all three hold:

1. every AC is `pass` — not `implemented` — each on the evidence its `evidence` type demands (Step 6),
2. every enabled tier is `pass`,
3. no round ended `blocked`.

Committing is **not** a condition. A green run on a protected branch, or one whose commits a pre-commit hook rejected, still unlocks verification — it just says so in the report.

Then, in this order: `workflow[build] = done` with its `endedAt` · `workflow[human-verification] = in_progress` with its `startedAt` — **the stage begins here and only here**, because the actor is now the human (its `endedAt` is theirs; you never write it) · `status = "green"` · `humanVerification.unlocked = true` · stamp `unlockedAt` · stop every service you started · write the report to `BUILD.md` (below) · then print the same report. **This message is the handoff** — it's the first thing the user reads since they typed the command, so it says what you built and what to poke at, not just a status line:

```text
Development is done — try it now.

  AC:      12/12 pass  (8 by test, 3 live, 1 review)
  Tests:   unit PASS (865) · ui skipped (no frontend change)
  Rounds:  4 · services started: testdata-api, web-ui (both stopped)
  Commits: 5 on feature/e2e-standard, not pushed
    test-data-host       853ecc3 5f54574
    generate-e2e-command fcc72d6
    docs-sweep           0ff2691
    harness-lifecycle    09b71bf
  State:   .work/2026-08-15-e2e-standard/progress.json

What I built
- Test-data host with seed/teardown + run ledger; swept on startup.
- Playwright global setup/teardown wired to it; SMTP guard aborts a run
  pointed anywhere but the local mail catcher.

Worth your eyes
- AC #11/#12 passed on live evidence, not unit tests — I ran the harness
  against a real seed/teardown round trip; a crashed-run sweep I couldn't
  fabricate.
- Start the project's stack as named in PLAN.md, then run the e2e suite.

Next: exercise it yourself — AI-green isn't verified. Review the commits
and rework them however you like, then push when you're happy. When you're
satisfied, /mynrd-verified e2e-standard closes this out.
```

**The commits block is mandatory whenever anything was committed** — the SHAs, the branch, and `not pushed`. They're yours to rewrite: the developer reads them and may squash, amend, or drop any of them, which is exactly why nothing was pushed and why the loop never rewrites its own history.

**If nothing was committed** (protected branch, hook rejection), say that in the block instead of the SHAs and name why.

### `BUILD.md` — the report on disk

The terminal message scrolls away; the file doesn't. **Both exits write it**, in the work folder beside `PLAN.md`, before the message is printed and after every `progress.json` write — so file and message never disagree.

- **Name:** `BUILD.md` for the first dispatch of a folder. Every later dispatch of the same folder (a blocked run resumed, a re-plan rebuilt) writes the next unused `BUILD_NN.md` — `BUILD_02.md`, `BUILD_03.md`, … zero-padded to two digits. **Never overwrite an earlier one**; each is the record of one run.
- **Content:** a two-line header, then the report verbatim — the same text you print, same summary block, same sections.

```markdown
# Build — 2026-08-15-e2e-standard
Exit: green · 2026-08-15T17:42:10+02:00 · run 1 of this folder

Development is done — try it now.

  AC:      12/12 pass  (8 by test, 3 live, 1 review)
  ...
```

`Exit:` is `green` or `blocked`. The blocked report goes in the same shape, opening with `Blocked — …`. Nothing else — no extra commentary the terminal didn't get, no fields `progress.json` already holds.

**Blocked exit** — anything unfinished, whether one AC or nine: `workflow[build] = blocked` with its `endedAt`, `human-verification` **stays `pending`** (the stage never started), `humanVerification.unlocked` stays `false`, `status = "blocked"`. Open with `Blocked — I need a decision before I can finish.` Then the same shape: what did land (with its commits), then every blocker together, each naming the AC, what you tried, and the exact decision or resource you need. Close by naming what you'll do once you have it.

**Do not invite verification in this message.** The user may well go and look at the code — that's theirs to choose — but you are asking for a decision, not handing off. "Try it now" belongs to the green exit alone. Never announce readiness the file contradicts, and never present a partial build as done.

**The command never records verification as done.** That's the human's — they record it themselves with `/mynrd-verified`, which is the only writer of `workflow[human-verification].endedAt`.

---

## After the handoff — revisions in this conversation

The green exit is not always the end of the conversation. The user reads the report, exercises the change, and often asks for more right there: *"rename that flag"*, *"the empty-state copy is wrong"*, *"drop the second query"*. Those edits are as much a part of the work as the build was, and a later session must be able to see them — so **every completed post-handoff request is written down** in the work folder as `REVISED_NN.md`.

**When it applies.** A green `BUILD*.md` exists for this folder and the user asks for a change to the files in the same conversation. Then:

- Make the change as asked — directly, or through the same specialist agents; your call.
- Run the tiers that cover what you touched. Same rules as Step 6: a test you can't run is `not run` with the reason, never silently skipped.
- **Do not commit unless the user asks.** The build loop commits per task because that's its job; a revision is the user's edit, made through you, on history they may already be reworking.
- Write `REVISED_NN.md` — the next unused number in the folder, zero-padded to two digits, starting at `REVISED_01.md`. **One file per request**, however many files it touched. Then answer.

```markdown
# Revision 02 — drop the second query on the orders list
Requested: "the orders page runs the count query twice, get rid of one"
When: 2026-08-15T18:05:41+02:00

## Changed
- src/ERP.Web/Orders/OrdersList.razor.cs — removed the standalone `CountAsync`; the page total now comes from the paged result's `TotalCount`.
- tests/ERP.Web.Tests/Orders/OrdersListTests.cs — `Loads_page_issues_single_count_query` added.

## Tests
- unit: PASS (866)
- ui: not run (no template change)

## Commit
- not committed
```

`Requested:` is the ask in the user's words, one or two lines, trimmed but not paraphrased away. `## Changed` names every file with what and why. `## Commit` is the SHA and branch with `not pushed` if the user asked you to commit, otherwise `not committed`.

**What is not a revision.**

- **A request while `workflow[build]` is `blocked`** is the loop resuming — the user is answering your blocker. Run Step 7 onward; the exit writes the next `BUILD_NN.md`, not a `REVISED` file.
- **A question, a review, a request you declined, an explanation** — nothing changed on disk, nothing to record.
- **A change the user made themselves** in their editor. You document what you did, not what they did.

`progress.json` is not touched by a revision. `acceptanceCriteria[]`, `tasks[]`, `runs[]` describe the build; the `REVISED` files describe what came after it. If a revision is large enough that the AC list no longer describes the work — new behaviour, a criterion that's now false — say so and point at `/mynrd-plan` to re-plan instead of stretching a revision note over it.

---

## Failure handling

- **Test command not found:** resolve it from the repo once (`package.json` scripts, the test `.csproj`, `pyproject.toml`) and use what's actually there, saying you corrected it. Still nothing → mark the tier `skipped` with the command and shell error verbatim, keep building the AC, and raise it in the final report. Don't stop the loop over it and don't guess a third command.
- **Agent returns unfinished:** re-dispatch that one task once with what it was missing, then the two-attempt rule applies to that AC alone.
- **Agent blocked on a dev server / database not running:** Step 5b — start it and re-dispatch. This is never a reason to stop.
- **Plan and code disagree** (named file missing, endpoint already built differently): block the AC that depends on it, finish everything else, and surface it in the final report. The plan may be stale — re-planning is `/mynrd-plan <folder>`, the user's call.
- **`progress.json` corrupt or hand-edited invalid:** don't overwrite and don't rebuild it — this command doesn't create the file. Show exactly which field is wrong and ask them to fix it, or to re-run `/mynrd-plan` if the plan-side fields are the damaged ones.
- **Pre-commit hook rejects the commit:** show the hook's output, leave the task `built`, keep going with the next task. Never `--no-verify`. If the hook is complaining about something your own change caused (a linter, a formatter), fixing that is in scope under the two-attempt rule.
- **A commit SHA in `commits[]` no longer exists** (the developer squashed or reset between runs): leave the array as it is and note it in one line. It's a record of what this command did, not a claim about the branch's current history.
